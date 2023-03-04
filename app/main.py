import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Response, status
from twilio.twiml.messaging_response import MessagingResponse

from app.logger import configure_logs
from app.twilio import process_request

# Configure logs to appear in the terminal.
configure_logs()

# Load environment variables from a .env file.
load_dotenv()

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

    # Replaces whitespace with a plus sign.
    from_param = From.replace(" ", "+")

    # Validates the sender is authorized.
    allowed_from = os.getenv("ALLOWED_FROM").split(",")
    if from_param not in allowed_from:
        logging.error(f"From {from_param} is not authorized")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Sender {from_param} is unauthorized",
        )

    # Response properties.
    status_code = status.HTTP_202_ACCEPTED
    headers = {"Content-Type": "text/xml"}
    media_type = "text/xml"

    # Build the Twilio TwiML response.
    response = MessagingResponse()
    message = process_request(body=Body.lower())
    response.message(message)

    # Return a custom FastAPI response to set headers and avoid duplicate
    # content-type key.
    return Response(
        content=str(response),
        status_code=status_code,
        headers=headers,
        media_type=media_type,
    )
