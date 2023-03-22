from fastapi import FastAPI, Form, Response, status
from twilio.twiml.messaging_response import MessagingResponse

from app.commands import COMMANDS
from app.logger import configure_logs
from app.messages import (
    COMMAND_UNSUPPORTED_ERROR_MSG,
    UNEXPECTED_ERROR_MSG,
    USER_ORG_ERROR_MSG,
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

    message = ""
    for command in COMMANDS.values():
        # Check if the command should be executed based on its regular
        # expression.
        if not command.match(body=Body):
            continue

        # Check if the user is authorized to execute the command.
        whatsapp_phone = From.replace(" ", "+").split(":")[1]
        is_authorized, user, organization = command.is_authorized(whatsapp_phone)
        if not is_authorized:
            message = USER_ORG_ERROR_MSG.format(phone=whatsapp_phone)
            break

        # Execute the logic associated to the command.
        result = command.execute(
            organization,
            commands=list(COMMANDS.values()),
            body=Body,
            user=user,
            whatsapp_phone=whatsapp_phone,
        )

        # The command was executed successfully and there are results that
        # should be passed to the message command.
        if isinstance(result, dict):
            message = command.message(organization, user, **result)
            break

        # The command returned an error in the form of a string.
        if isinstance(result, str):
            message = result
            break

        # The command was executed successfully and there are no results that
        # should be passed to the message command.
        message = command.message(organization, user)
        break

    # The command is not supported.
    if message == "":
        message = COMMAND_UNSUPPORTED_ERROR_MSG.format(val_1=Body)

    # The final response is assembled.
    response = MessagingResponse()
    response.message(message)
    return Response(
        content=str(response),
        status_code=status_code,
        headers=headers,
        media_type=media_type,
    )
