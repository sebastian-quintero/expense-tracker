import calendar
import logging
import os
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from math import floor
from typing import List

import pytz
from dotenv import load_dotenv
from requests import get

from app.database import Transactions, record_transaction, retrieve_transactions

# Load environment variables from a .env file.
load_dotenv()

# Default currency for the app.
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY")

# Regular expression to match transaction commands.
TRANSACTION_REGEXP = (
    "(^(?=non$)|(?:non-[a-zA-z]{3})$)|"
    "(^(?=ess$)|(?:ess-[a-zA-z]{3})$)|"
    "(^(?=inc$)|(?:inc-[a-zA-z]{3})$)"
)

# Regular expression to match interface commands.
COMMANDS_REGEXP = TRANSACTION_REGEXP + "|report|help"


class TransactionSense(IntEnum):
    """TransactionSense represents the sense, or symbol, of a transaction,
    which can be positive if it debits an account or negative if it credits
    it."""

    positive = 1
    """Increases monetary value."""
    negative = -1
    """Decreases monetary value."""


@dataclass
class TransactionCommand:
    """TransactionCommand represents a financial transaction which either
    credits or debits the account."""

    command: str
    """What the string for the command actually is."""
    label: str
    """How the command is displayed to the user."""
    emoji: str
    """Graphical representation if the transaction."""
    sense: TransactionSense = TransactionSense.negative
    """Positive debits an account, negative credits it."""
    currency: str = DEFAULT_CURRENCY
    """Currency for the transaction."""

    @classmethod
    def from_command(cls, command: str):
        """Instantiates the class based on the simple string
        representation."""

        full_command = command.split("-")
        actual_command = full_command[0]
        transaction_command = deepcopy(TRANSACTION_COMMANDS.get(actual_command))

        # Includes a currency.
        if len(full_command) > 1:
            currency = full_command[1].upper()
            transaction_command.currency = currency

        return transaction_command


# The information related to the commands used for recording a transaction.
ESSENTIAL = TransactionCommand(
    command="ess",
    label="Essential",
    emoji="🌽",
    sense=TransactionSense.negative,
)
NON_ESSENTIAL = TransactionCommand(
    command="non",
    label="Non essential",
    emoji="🍔",
    sense=TransactionSense.negative,
)
INCOME = TransactionCommand(
    command="inc",
    label="Income",
    emoji="💸",
    sense=TransactionSense.positive,
)
TRANSACTION_COMMANDS = {
    ESSENTIAL.command: ESSENTIAL,
    NON_ESSENTIAL.command: NON_ESSENTIAL,
    INCOME.command: INCOME,
}


def process_request(body: str) -> str:
    """Process a request coming from the Twilio WhatsApp Webhook and returns a
    message that should be displayed to the user."""

    # Check if the command (first string before a whitespace) is supported.
    command = body.split(" ")[0]
    if not re.compile(COMMANDS_REGEXP).match(command):
        logging.error("command not supported")
        return error(f'command "{command}" is not supported')

    # Display the help menu.
    if command == "help":
        logging.info("used the help command, displaying help menu")
        return help()

    # If the message just says "report", an expense report is requested.
    if command == "report":
        logging.info("used the report command, creating financial report")

        # Retrieves the expenses from the database and tallies them.
        transactions = retrieve_transactions(date=datetime.now())
        return report(transactions=transactions)

    # Process a new tramsaction.
    if re.compile(TRANSACTION_REGEXP).match(command):
        logging.info("used a transaction command, recording the transaction")
        request = body.split(" ")

        # Checks that there are at least 2 spaces defining the request.
        if len(request) < 3:
            logging.error("request has fewer than 3 elements")
            return error(
                f'command "{command}" should have at least 2 spaces to record a transaction'
            )

        # Checks that the request has the correct ordering.
        value = float(request[1])
        if value <= 0:
            logging.error("value from the request is invalid")
            return error(
                f"Second element of the command should be the transaction value (a number) and >= 0: {request[1]}"
            )

        # Gets request elements.
        description = " ".join(request[2:])
        transaction_command = TransactionCommand.from_command(command=command)

        # Converts the value in case a foreign currency is used.
        value_converted = deepcopy(value)
        if transaction_command.currency != DEFAULT_CURRENCY:
            logging.info(
                f"currency is {transaction_command.currency}, using conversion"
            )
            value_converted = convert(
                value=value,
                currency=transaction_command.currency,
            )

        # Record the transaction in the database.
        label = transaction_command.label
        val = value * transaction_command.sense.value
        currency = transaction_command.currency
        val_conv = value_converted * transaction_command.sense.value
        record_transaction(
            created_at=datetime.now(pytz.timezone(os.getenv("TIMEZONE"))),
            description=description,
            label=label,
            value=val,
            currency=currency,
            value_converted=val_conv,
        )

        # Create a compelling log that is returned to the user.
        message = "✅ Successfully recorded transaction! 🎉\n"
        message += f"\t❓ Type: {transaction_command.emoji} {label}\n"
        message += f"\t🤑 Value: {currency} {'${:,.2f}'.format(abs(val))}\n"
        if val != val_conv:
            message += f"\t🌎 Value (converted): {DEFAULT_CURRENCY} {'${:,.2f}'.format(abs(val_conv))}\n"
        message += f"\t🔍 Description: {description}\n"

        return message

    return error(f'The message "{body}" could not be processed')


def report(transactions: List[Transactions]) -> str:
    """Tally transactions by creating monthly totals and differentiating
    between credits and debits. Returns a single formatted string with all the
    information."""

    current_month = datetime.now(pytz.timezone(os.getenv("TIMEZONE"))).month

    # Tally transactions by type.
    totals = defaultdict(lambda: defaultdict(int))
    current = {}
    for transaction in transactions:
        # Tally by month.
        month_key = f"{transaction.created_at.month}. {calendar.month_name[transaction.created_at.month]}"
        totals[month_key][transaction.label] += transaction.value_converted

        # Gather the current month's expenses to later get the highest.
        if (
            transaction.created_at.month == current_month
            and transaction.value_converted < 0
        ):
            current[
                f"{transaction.label};{transaction.created_at.strftime('%d/%m/%Y')};{transaction.description}"
            ] = abs(transaction.value_converted)

    # Sort keys.
    totals = dict(sorted(totals.items(), reverse=True))

    # Build a single string as a message.
    message = f"*🤓 This is your financial 💵 report 📊 in {DEFAULT_CURRENCY}.*\n\n\n"
    message += "*_Monthly 📅 totals 💯:_*\n"

    # Describe monthly totals.
    for month, financials in totals.items():
        message += f"💰 {month}\n"

        # Get the actual financials.
        debits = financials.get(INCOME.label, 0)
        essential_credits = financials.get(ESSENTIAL.label, 0)
        non_essential_credits = financials.get(NON_ESSENTIAL.label, 0)
        financial_credits = essential_credits + non_essential_credits

        # Check if there are debits.
        if debits > 0:
            message += (
                f"🟢🟢 {INCOME.emoji} {INCOME.label} = {'${:,.2f}'.format(debits)}\n"
            )

            # Only report savings when there are credits.
            if financial_credits < 0:
                savings = debits + financial_credits
                savings_ratio = floor((savings / debits) * 100)
                message += (
                    f"\t🥂 Savings ({savings_ratio}%)\n"
                    f"\t🥂 {'${:,.2f}'.format(savings)}\n"
                )

        # Check if there are credits.
        if financial_credits < 0:
            emojis = f"🔴🔴 {ESSENTIAL.emoji} {NON_ESSENTIAL.emoji}"
            message += (
                f"{emojis} Expenses = {'${:,.2f}'.format(abs(financial_credits))}\n"
            )

            # Report essential credits, if they exist.
            if essential_credits < 0:
                essential_ratio = abs(
                    floor((essential_credits / financial_credits) * 100)
                )
                message += (
                    f"\t{ESSENTIAL.emoji} {ESSENTIAL.label} ({essential_ratio}%)\n"
                )
                message += (
                    f"\t{ESSENTIAL.emoji} {'${:,.2f}'.format(abs(essential_credits))}\n"
                )

            # Report non essential credits, if they exist.
            if non_essential_credits < 0:
                non_essential_ratio = abs(
                    floor((non_essential_credits / financial_credits) * 100)
                )
                message += f"\t{NON_ESSENTIAL.emoji} {NON_ESSENTIAL.label} ({non_essential_ratio}%)\n"
                message += f"\t{NON_ESSENTIAL.emoji} {'${:,.2f}'.format(abs(non_essential_credits))}\n"

        message += "----------- ⏳ -----------\n"

    message += "\n\n"

    # Get the top expenses for the current month.
    message += "*_🙀 These are the top 🔝 expenses this month 🚨:_*\n"
    current = dict(sorted(current.items(), key=lambda item: item[1], reverse=True))
    top = {k: current[k] for k in list(current.keys())[:10]}
    for ix, (k, v) in enumerate(top.items()):
        components = k.split(";")
        label, date, description = components[0], components[1], components[2]
        message += f"🔥 {ix + 1}. {'${:,.2f}'.format(v)} ({date})\n"
        emoji = ESSENTIAL.emoji if label == ESSENTIAL.label else NON_ESSENTIAL.label
        message += f"\t{emoji} {label}\n"
        message += f"\t{description}\n"

    logging.info("successfully created the financial report")

    return message


def error(message: str) -> str:
    """Format an error with cool emojis."""

    return f"🚫 {message}. Try again 🙏🏻 or use the ```help``` command for more info ℹ️."


def help() -> str:
    """Returns the help menu of the app."""

    # Intro
    message = "👻 You asked for help! Here is what you can type 🤔:\n\n\n"

    # Help
    message += "*📲 ```help```*\n"
    message += "Show this help menu 🥶.\n\n"

    # Report
    message += "*📲 ```report```*\n"
    message += "Type this to get a financial report of your transactions 📊.\n\n"

    # Essential expense
    message += "*📲 ```ess <value> <description>```*\n"
    message += "Record an Essential 🌽 expense (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```ess-usd``` 🇺🇸. "
    automatically = (
        f"The app will automatically 🪄 convert it to {DEFAULT_CURRENCY}.\n\n"
    )
    message += automatically

    # Non essential expense
    message += "*📲 ```non <value> <description>```*\n"
    message += "Record a Non essential 🍔 expense (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```non-usd``` 🇺🇸. "
    message += automatically

    # Income
    message += "*📲 ```inc <value> <description>``*`\n"
    message += "Record an Income 💸 (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```inc-usd``` 🇺🇸. "
    message += automatically

    return message


def convert(value: float, currency: str) -> float:
    """convert the value to the default currency used with an external API."""

    url = f"https://api.apilayer.com/fixer/latest?base={currency}&symbols={DEFAULT_CURRENCY}"
    headers = {"apikey": os.getenv("FIXER_API_KEY")}
    try:
        logging.info(f"trying to request url: {url}")
        response = get(url=url, headers=headers)
        data = response.json()
        rate = data.get("rates").get(DEFAULT_CURRENCY)
        logging.info("successfully obtained exchange rate")

    except Exception as ex:
        logging.exception(f"error trying to get currency conversion: {ex}")
        rate = 4700

    return value * rate
