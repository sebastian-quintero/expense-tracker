import logging
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

# Initializes the database engine. Use env vars to pass private info.
ENGINE = create_engine(
    "mysql+mysqlconnector://{user}:{password}@{host}:{port}/expenses".format(
        user=os.environ.get("DDBB_USER"),
        password=os.environ.get("DDBB_PASSWORD"),
        host=os.environ.get("DDBB_HOST"),
        port=os.environ.get("DDBB_PORT"),
    ),
    echo=False,
)


class ExpenseType(str, Enum):
    """Type of expenses that can be recorded."""

    essential = "ess"
    non_essential = "non"

    @classmethod
    def from_str(cls, expense_type: str):
        if expense_type == "ess":
            return cls.essential

        return cls.non_essential


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
) -> str:
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

    log = f"Successfully recorded expense type: {type.name}, value: {value}, description: {description}"
    logging.info(log)

    return log


def retrieve_expenses(date: datetime) -> List[Expenses]:
    """Retrieve expenses from the expenses.expenses table."""

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = select(Expenses).where(
            Expenses.date >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo)
        )
        logging.info(f"Executing sql statement: {statement}")
        expenses = session.exec(statement)
        expenses = [expense for expense in expenses]

    logging.info("Successfully retrieved expenses")

    return expenses
