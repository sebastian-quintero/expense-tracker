import logging
import os
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Tuple

from sqlmodel import Field, Session, SQLModel, create_engine, select

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
    non_essential = "non"


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


def retrieve_expenses(
    date: datetime,
) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, float]]:
    """Retrieve expenses from the expenses.expenses table."""
    # Create empty totals.
    monthly_total = defaultdict(int)
    monthly_essential = defaultdict(int)
    monthly_non_essential = defaultdict(int)

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = select(Expenses).where(
            Expenses.date >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo)
        )
        logging.info(f"Executing sql statement: {statement}")
        expenses = session.exec(statement)

        # Tallies up expenses by category.
        for expense in expenses:
            monthly_total[expense.date.month] += expense.value
            if expense.type == ExpenseType.essential:
                monthly_essential[expense.date.month] += expense.value
            else:
                monthly_non_essential[expense.date.month] += expense.value

    logging.info(f"Tallied up expenses. monthly_totals: {monthly_total}")

    return monthly_total, monthly_essential, monthly_non_essential
