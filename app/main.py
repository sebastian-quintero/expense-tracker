import logging

from fastapi import FastAPI, Form, Response, status
from twilio.twiml.messaging_response import MessagingResponse

from app.commands import COMMANDS
from app.database import retrieve_user_organization
from app.logger import configure_logs
from app.messages import (
    COMMAND_UNSUPPORTED_ERROR_MSG,
    UNEXPECTED_ERROR_MSG,
    USER_ORG_ERROR_MSG,
    ErrorMsg,
)

# Configure logs to appear in the terminal.
configure_logs()

# Creates the FastAPI web server.
server = FastAPI()


@server.get("/", status_code=status.HTTP_200_OK)
def health_check() -> str:
    """Endpoint to check that the server is running."""
    return "ok"


@server.post("/twilio", status_code=status.HTTP_202_ACCEPTED)
def twilio(response: Response, From: str = Form(), Body: str = Form()) -> str:
    """
    Interact with the Twilio WhatsApp API. This endpoint is the callback that
    must be specified in the console. It receives a request and must respond in
    Twilio TwiML format.

    Read more about setting up a webhook endpoint at:
    https://www.twilio.com/docs/messaging/guides/webhook-request
    """

    # Return a custom FastAPI response to set headers and avoid duplicate
    # content-type key.
    status_code = status.HTTP_202_ACCEPTED
    headers = {"Content-Type": "text/xml"}
    media_type = "text/xml"

    # Build the default Twilio TwiML response.
    response = MessagingResponse()
    response.message(UNEXPECTED_ERROR_MSG)

    # Replaces whitespace with a plus sign and gets the phone number from the
    # str.
    whatsapp_phone = From.replace(" ", "+").split(":")[1]

    # Get the user's org.
    user, organization = retrieve_user_organization(whatsapp_phone=whatsapp_phone)

    # Validates the sender is authorized.
    if user is None or organization is None:
        logging.error(f"Phone number {whatsapp_phone} is not part of an authorized org")
        response = MessagingResponse()
        response.message(USER_ORG_ERROR_MSG.format(phone=whatsapp_phone))
        return Response(
            content=str(response),
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )

    message = ""
    for command in COMMANDS.values():
        # Check if the command should be executed based on its regular
        # expression.
        if not command.match(body=Body):
            continue

        # Execute the logic associated to the command.
        result = command.execute(
            organization,
            commands=list(COMMANDS.values()),
            body=Body,
            user=user,
        )

        # Check the type of message that should be returned by having executed
        # the command. For example, it may result in an error.
        if result is not None and not isinstance(result, ErrorMsg):
            message = command.message(organization, user, **result)
            break

        if isinstance(result, ErrorMsg):
            message = result.to_str(organization.language)
            break

        message = command.message(organization, user)

    # The command is not supported.
    if message == "":
        message = ErrorMsg(
            error_str=COMMAND_UNSUPPORTED_ERROR_MSG.to_str(
                organization.language, val_1=Body
            )
        ).to_str(organization.language)

    # The final response is assembled.
    response = MessagingResponse()
    response.message(message)
    return Response(
        content=str(response),
        status_code=status_code,
        headers=headers,
        media_type=media_type,
    )
