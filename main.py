import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, status
from pydantic import BaseModel

from database import ExpenseType, record_expense, retrieve_expenses
from logger import configure_logs

configure_logs()
app = FastAPI()


class Expense(BaseModel):
    """An expense received via API call."""

    date: datetime
    description: str
    value: float


class Response(BaseModel):
    """Response of an API request."""

    message: str
    metadata: Any | None = None


@app.get("/", status_code=status.HTTP_200_OK)
def health_check() -> Response:
    """Checks that the server is running."""
    return Response(message="ok")


@app.post("/expense/{expense_type}", status_code=status.HTTP_201_CREATED)
def expense(expense_type: ExpenseType, expense: Expense) -> Response:
    """Records an expense in the database."""
    logging.info(
        f"Received expense type {expense_type.name}, "
        + f"with value {expense.value}, description {expense.description}",
    )

    # Creates the database record.
    record_expense(
        date=expense.date,
        description=expense.description,
        type=expense_type,
        value=expense.value,
    )

    return Response(message="ok")


@app.get("/report", status_code=status.HTTP_200_OK)
def report() -> Response:
    """Creates an expense report for the current month and the year so far."""
    logging.info("Creating expenses report")

    # Retrieves the expenses from the database.
    monthly_total, monthly_essential, monthly_non_essential = retrieve_expenses(
        date=datetime.now(),
    )

    # Formats values to monetary units.
    monthly_total = {k: "${:,.2f}".format(v) for k, v in monthly_total.items()}
    monthly_essential = {k: "${:,.2f}".format(v) for k, v in monthly_essential.items()}
    monthly_non_essential = {
        k: "${:,.2f}".format(v) for k, v in monthly_non_essential.items()
    }

    return Response(
        message="report",
        metadata={
            "monthly_total": monthly_total,
            "monthly_essential": monthly_essential,
            "monthly_non_essential": monthly_non_essential,
        },
    )
