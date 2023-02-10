import logging
from datetime import datetime

from fastapi import FastAPI, status
from pydantic import BaseModel

from database import ExpenseType, record_expense
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
    metadata: str | None = None


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
