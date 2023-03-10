from enum import Enum
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


class Language(str, Enum):
    """Language defines all the possible languages supported by the
    application."""

    # Spanish.
    es = "ES"
    # English.
    en = "EN"


class Currency(str, Enum):
    """Currency defines all the possible currencies supported by the
    application."""

    cop = "COP"
    usd = "USD"
    eur = "EUR"


class Transactions(SQLModel, table=True):
    """Represents the transactions table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    label: str
    value: float
    currency: str
    value_converted: float
    description: str
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class Users(SQLModel, table=True):
    """Represents the users table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    whatsapp_phone: str
    name: str
    organization_id: Optional[int] = Field(default=None, foreign_key="organizations.id")


class Organizations(SQLModel, table=True):
    """Represents the organizations table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    name: str
    currency: Currency
    language: Language
    admin_user_id: Optional[int] = Field(default=None, foreign_key="users.id")


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
