from enum import Enum
import logging
import os
from datetime import datetime
from typing import List, Optional, Tuple

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


class Organization(SQLModel, table=True):
    """Represents the organization table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    name: str
    currency: Currency
    language: Language


class User(SQLModel, table=True):
    """Represents the user table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    created_at: datetime
    whatsapp_phone: str
    name: str
    is_admin: bool


class Transaction(SQLModel, table=True):
    """Represents the transaction table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
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
    user: User,
):
    """Record a transaction to the transactions table."""

    transaction = Transaction(
        created_at=created_at,
        user_id=user.id,
        label=label,
        value=value,
        currency=currency,
        value_converted=value_converted,
        description=description,
    )
    logging.info(f"creating new transaction record: {transaction}")

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(transaction)
        session.commit()

    logging.info("successfully recorded transaction")


def retrieve_transactions(date: datetime) -> List[Transaction]:
    """Retrieve transactions from the transactions table."""

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = select(Transaction).where(
            Transaction.created_at >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo)
        )
        logging.info(f"executing sql statement: {statement}")
        transactions = session.exec(statement)
        transactions = [transaction for transaction in transactions]

    logging.info("successfully retrieved transactions")

    return transactions


def retrieve_user_organization(whatsapp_phone: str) -> Tuple[User, Organization] | None:
    """Retrieves the user and organization given the provided filter."""

    with Session(ENGINE) as session:
        statement = (
            select(User, Organization)
            .where(User.organization_id == Organization.id)
            .where(User.whatsapp_phone == whatsapp_phone)
        )
        logging.info(f"executing sql statement: {statement}")
        results = session.exec(statement)
        organizations = [(user, organization) for ((user, organization)) in results]
        try:
            user, organization = organizations[0]
            logging.info("successfully retrieved user and organization")

        except IndexError:
            logging.error(
                f"no user and/or organization found for whatsapp phone {whatsapp_phone}"
            )
            user, organization = None, None

    return user, organization
