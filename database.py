import logging
import os
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine

# Initializes the database engine. Use env vars to pass private info.
ENGINE = create_engine(
    "mysql+mysqlconnector://{user}:{password}@{host}:{port}/expenses".format(
        user=os.environ.get("DDBB_USER"),
        password=os.environ.get("DDBB_PASSWORD"),
        host=os.environ.get("DDBB_HOST"),
        port=os.environ.get("DDBB_PORT"),
    ),
    echo=True,
)


class ExpenseType(str, Enum):
    """Type of expenses that can be recorded."""

    essential = "ess"
    discretionary = "disc"


class Expenses(SQLModel, table=True):
    """Represents the expenses table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    description: str
    type: ExpenseType
    value: float


def record_expense(
    date: datetime,
    description: str,
    type: ExpenseType,
    value: float,
):
    """Record an expense to the expenses.expenses table."""
    expense = Expenses(
        date=date,
        description=description,
        type=type,
        value=value,
    )
    logging.info(f"Created new expenses table record: {expense}")

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(expense)
        session.commit()
    logging.info("Successfully recorded expense")
