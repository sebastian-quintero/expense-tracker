import logging
import os
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load environment variables from a .env file.
load_dotenv()

# Initializes the database engine. Use env vars to pass private info.
ENGINE = create_engine(
    "mysql+mysqlconnector://{user}:{password}@{host}:{port}/main".format(
        user=os.getenv("DDBB_USER"),
        password=os.getenv("DDBB_PASSWORD"),
        host=os.getenv("DDBB_HOST"),
        port=os.getenv("DDBB_PORT"),
    ),
    echo=False,
)


class Transactions(SQLModel, table=True):
    """Represents the expenses table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    label: str
    value: float
    currency: str
    value_converted: float
    description: str


def record_transaction(
    created_at: datetime,
    description: str,
    label: str,
    value: float,
    currency: str,
    value_converted: float,
):
    """Record a transaction to the transactions table."""

    transaction = Transactions(
        created_at=created_at,
        label=label,
        value=value,
        currency=currency,
        value_converted=value_converted,
        description=description,
    )
    logging.info(f"creating new transactions record: {transaction}")

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(transaction)
        session.commit()

    logging.info("successfully recorded transaction")


def retrieve_transactions(date: datetime) -> List[Transactions]:
    """Retrieve transactions from the transactions table."""

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = select(Transactions).where(
            Transactions.created_at
            >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo)
        )
        logging.info(f"executing sql statement: {statement}")
        transactions = session.exec(statement)
        transactions = [expense for expense in transactions]

    logging.info("successfully retrieved transactions")

    return transactions
