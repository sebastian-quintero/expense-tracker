import calendar
import logging
from collections import defaultdict
from datetime import datetime
from math import floor
from typing import Any

from fastapi import FastAPI, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.database import ExpenseType, record_expense, retrieve_expenses
from app.logger import configure_logs

configure_logs()
server = FastAPI()

MONTHS = {
    1: "January",
    2: "February",
}


class Expense(BaseModel):
    """An expense received via API call."""

    description: str
    value: float


class Response(BaseModel):
    """Response of an API request."""

    message: Any


@server.get("/", status_code=status.HTTP_200_OK)
def health_check() -> Response:
    """Checks that the server is running."""
    return Response(message="ok")


@server.post("/expense/{expense_type}", status_code=status.HTTP_201_CREATED)
def expense(expense_type: ExpenseType, expense: Expense) -> Response:
    """Records an expense in the database."""
    log = (
        f"Recorded expense type: {expense_type.name}, "
        + f"value: {expense.value}, description: {expense.description}"
    )
    logging.info(log)

    # Creates the database record.
    record_expense(
        date=datetime.now(),
        description=expense.description,
        type=expense_type,
        value=expense.value,
    )

    return Response(message=log)


@server.get(
    "/report",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
)
def report() -> str:
    """Creates an expense report for the current month and the year so far."""
    logging.info("Creating expenses report")

    # Retrieves the expenses from the database.
    expenses = retrieve_expenses(date=datetime.now())

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
        ess_value = ess[month]
        non_value = non[month]
        ess_ratio = floor((ess_value / value) * 100)
        non_ratio = floor((non_value / value) * 100)

        # Format to monetary units.
        message += f"\n{month} = {'${:,.2f}'.format(value)} || "
        message += f"ess = {'${:,.2f}'.format(ess_value)} ({ess_ratio}%) | "
        message += f"non = {'${:,.2f}'.format(non_value)} ({non_ratio}%)\n"

    logging.info("Succesfully tallied expenses")

    return message
