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
    """Record a transaction to the transaction table."""

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


def retrieve_transactions(
    date: datetime,
    organization: Organization,
) -> List[Transaction]:
    """Retrieve transactions from the transactions table for the given
    organization."""

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = (
            select(Transaction)
            .join(User)
            .where(
                Transaction.created_at
                >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo),
                User.organization_id == organization.id,
            )
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


def retrieve_user(whatsapp_phone: str) -> User | None:
    """Retrieves the user based on the provided filter."""

    with Session(ENGINE) as session:
        statement = select(User).where(User.whatsapp_phone == whatsapp_phone)
        logging.info(f"executing sql statement: {statement}")
        results = session.exec(statement)
        try:
            user = results.one()
        except Exception:
            user = None

    return user


def retrieve_organization(user: User) -> Organization:
    """Retrieves the organization for the given user."""

    with Session(ENGINE) as session:
        statement = select(Organization).where(Organization.id == user.organization_id)
        logging.info(f"executing sql statement: {statement}")
        results = session.exec(statement)
        organization = results.one()

    return organization


def record_organization(
    created_at: datetime,
    name: str,
    language: Language,
    currency: Currency,
) -> int:
    """Record an organization to the organization table. Returns the id after
    successfully recording the organization."""

    organization = Organization(
        created_at=created_at,
        name=name,
        currency=currency,
        language=language,
    )
    logging.info(f"creating new organization record: {organization}")

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(organization)
        session.commit()
        session.refresh(organization)
        organization_id = organization.id

    logging.info("successfully recorded organization")

    return organization_id


def record_user(
    organization_id: int,
    created_at: datetime,
    whatsapp_phone: str,
    name: str,
    is_admin: bool,
):
    """Record a new user to the user table."""

    user = User(
        organization_id=organization_id,
        created_at=created_at,
        whatsapp_phone=whatsapp_phone,
        name=name,
        is_admin=is_admin,
    )
    logging.info(f"creating new user record: {user}")

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(user)
        session.commit()

    logging.info("successfully recorded user")


def update_user(user: User, name: str) -> User:
    """Update a table entry for a user."""

    with Session(ENGINE) as session:
        statement = select(User).where(User.id == user.id)
        logging.info(f"executing sql statement: {statement}")
        results = session.exec(statement)
        user = results.one()
        user.name = name
        session.add(user)
        session.commit()
        session.refresh(user)

    logging.info("successfully updated user")

    return user
