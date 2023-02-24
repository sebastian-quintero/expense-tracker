import calendar
import logging
import os
from collections import defaultdict
from datetime import datetime
from math import floor
from typing import List

import pytz
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse

from app.database import ExpenseType, record_expense, retrieve_expenses
from app.logger import configure_logs

# Defines desired timezone for database entries.
TZ = pytz.timezone("America/Bogota")

# Configure logs to appear in the terminal.
configure_logs()

# Creates the FastAPI web server.
server = FastAPI()


class Expense(BaseModel):
    """An expense received via API call."""

    description: str
    value: float


@server.get("/", status_code=status.HTTP_200_OK)
def health_check() -> str:
    """Endpoint to check that the server is running."""
    return "ok"


@server.put(
    "/expense/{expense_type}",
    status_code=status.HTTP_201_CREATED,
    response_class=PlainTextResponse,
)
def expense(expense_type: ExpenseType, expense: Expense) -> str:
    """Endpoint to record an expense in the database."""
    message = record_expense(
        date=datetime.now(TZ),
        description=expense.description,
        type=expense_type,
        value=expense.value,
    )

    return message


@server.get(
    "/report",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
)
def report() -> str:
    """Endpoint to report and classiy monthly expenses for the year so far."""

    # Retrieves the expenses from the database and tallies them.
    expenses = retrieve_expenses(date=datetime.now())
    message = tally(expenses)

    return message


@server.post("/twilio", status_code=status.HTTP_202_ACCEPTED)
def twilio(request: Request) -> str:
    """
    Interact with the Twilio WhatsApp API. This endpoint is the callback that
    must be specified in the console. It processes an incoming message and can:

    1. record an expense,
    2. generate a report.

    To successfully process the message, and perform one of the aforementioned
    actions, the body should be formatted as one of the following options:

    1. ExpenseType value description. Examples: "ess 34500 gas and
      fluids", "non 3500 chocolate bar".
    2. report
    """

    # Validates necessary query params are present.
    print(request.query_params)
    print(request.headers)
    print(request.path_params)
    if request.query_params.get("From") is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From missing in query params",
        )

    if request.query_params.get("Body") is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Body missing in query params",
        )

    # Replaces whitespace with a plus sign.
    from_param = request.query_params["From"].replace(" ", "+")

    # Validates the sender is authorized.
    allowed_from = os.environ.get("ALLOWED_FROM").split(",")
    if from_param not in allowed_from:
        logging.error(f"From {from_param} is not authorized")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Sender {from_param} is unauthorized",
        )

    # If the first three characters are "ess" or "non", an expense is recorded.
    body = request.query_params["Body"].lower()
    if body[0:4] in ["ess ", "non "]:
        logging.info("Recording an expense from a Twilio message")
        request = body.split(" ")

        # Checks that there are at least 2 spaces defining the request.
        if len(request) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There should at least 2 spaces to record an expense: add a description",
            )

        # Gets request elements.
        expense_type = ExpenseType.from_str(request[0])
        value = float(request[1])
        description = " ".join(request[2:])

        # Records the expense in the database.
        message = record_expense(
            date=datetime.now(TZ),
            description=description,
            type=expense_type,
            value=value,
        )

        # Build the Twilio TwiML response.
        response = MessagingResponse()
        response.message(message)

        return str(response)

    # If the message just says "report", an expense report is requested.
    if body == "report":
        logging.info("Creating a report from a Twilio message")

        # Retrieves the expenses from the database and tallies them.
        expenses = retrieve_expenses(date=datetime.now())
        message = tally(expenses)

        # Build the Twilio TwiML response.
        response = MessagingResponse()
        response.message(message)

        return str(response)

    # A different message than what is expected results in an error.
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail='Request not allowed, use one of: expense (e. g.: "ess 4500 eggs") or report',
    )


def tally(expenses: List[Expense]) -> str:
    """Tally expenses by creating monthly totals and classifying them by type:
    essential vs. non essential. Returns a single formatted string with all the
    information."""

    # Tally expenses by type.
    total = defaultdict(int)
    ess = defaultdict(int)
    non = defaultdict(int)
    for expense in expenses:
        # Tally by month.
        key = f"{expense.date.month}-{calendar.month_name[expense.date.month]}"
        total[key] += expense.value

        if expense.type == ExpenseType.essential:
            ess[key] += expense.value
        else:
            non[key] += expense.value

    # Sort keys.
    total = dict(sorted(total.items()))
    ess = dict(sorted(ess.items()))
    non = dict(sorted(non.items()))

    # Build a single string as a message.
    message = ""
    for month, value in total.items():
        # Format to monetary units.
        message += f"\n{month} = {'${:,.2f}'.format(value)} || "

        # Only report essential and non-essential if they exist.
        if ess.get(month) is not None:
            ess_value = ess[month]
            ess_ratio = floor((ess_value / value) * 100)
            message += f"| ess = {'${:,.2f}'.format(ess_value)} ({ess_ratio}%) "

        if non.get(month) is not None:
            non_value = non[month]
            non_ratio = floor((non_value / value) * 100)
            message += f"| non = {'${:,.2f}'.format(non_value)} ({non_ratio}%) "

        message += "\n"

    logging.info("Successfully tallied expenses by month and type")

    return message
