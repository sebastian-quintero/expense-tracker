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

from dotenv import load_dotenv
from requests import get

from app.database import (
    DEFAULT_CURRENCY,
    Transactions,
    record_transaction,
    retrieve_transactions,
)

# Load environment variables from a .env file.
load_dotenv()

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
TRANSACTION_COMMANDS = {
    "ess": TransactionCommand(
        command="ess",
        label="Essential",
        emoji="🌽",
        sense=TransactionSense.negative,
    ),
    "non": TransactionCommand(
        command="non",
        label="Non essential",
        emoji="🍔",
        sense=TransactionSense.negative,
    ),
    "inc": TransactionCommand(
        command="inc",
        label="Income",
        emoji="💸",
        sense=TransactionSense.positive,
    ),
}


def process_request(body: str, timezone: datetime.tzinfo) -> str:
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
        return report(transactions=transactions, timezone=timezone)

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
            created_at=datetime.now(timezone),
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


def report(transactions: List[Transactions], timezone: datetime.tzinfo) -> str:
    """Tally transactions by creating monthly totals and differentiating
    between credits and debits. Returns a single formatted string with all the
    information."""

    current_month = datetime.now(timezone).month

    # Tally transactions by type.
    total = defaultdict(int)
    ess = defaultdict(int)
    non = defaultdict(int)
    current = {}
    for transaction in transactions:
        # Tally by month.
        key = f"{transaction.created_at.month}. {calendar.month_name[transaction.created_at.month]}"
        total[key] += transaction.value

        # Tally by type (also by month).
        expense_type = str.from_str(transaction.label)
        if expense_type == str.essential:
            ess[key] += transaction.value
        else:
            non[key] += transaction.value

        # Gather the current month's expenses to later get the highest.
        if transaction.created_at.month == current_month:
            current[
                f"{expense_type.value};{transaction.created_at.strftime('%d/%m/%Y')};{transaction.description}"
            ] = transaction.value

    # Sort keys.
    total = dict(sorted(total.items()))
    ess = dict(sorted(ess.items()))
    non = dict(sorted(non.items()))

    # Build a single string as a message.
    message = "*🤓 This is your financial 💵 report 📊.*\n\n\n"
    message += "*_Monthly 📅 totals 💯:_*\n"

    # Describe monthly totals.
    for month, value in total.items():
        # Format to monetary units.
        message += f"💰 {month} = {'${:,.2f}'.format(value)}\n"

        # Only report essential and non-essential if they exist.
        if ess.get(month) is not None:
            ess_value = ess[month]
            ess_ratio = floor((ess_value / value) * 100)
            message += f"🌽 Essential ({ess_ratio}%)\n"
            message += f"\t{'${:,.2f}'.format(ess_value)}\n"

        if non.get(month) is not None:
            non_value = non[month]
            non_ratio = floor((non_value / value) * 100)
            message += f"🍔 Non essential ({non_ratio}%)\n"
            message += f"\t{'${:,.2f}'.format(non_value)}\n"

        message += "----------- ⏳ -----------\n"

    message += "\n\n"

    # Get the top expenses for the current month.
    message += "*_🙀 These are the top 🔝 expenses this month 🚨:_*\n"
    current = dict(sorted(current.items(), key=lambda item: item[1], reverse=True))
    top = {k: current[k] for k in list(current.keys())[:10]}
    for ix, (k, v) in enumerate(top.items()):
        components = k.split(";")
        type, date, description = components[0], components[1], components[2]
        message += f"🔥 {ix + 1}. {'${:,.2f}'.format(v)} ({date})\n"
        emoji = "🍔" if type == str.non_essential else "🌽"
        message += f"\t{emoji} {type}\n"
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

    # Report
    message += "📲 ```report```\n"
    message += "Type this to get a financial report of your transactions 📊.\n\n"

    # Help
    message += "📲 ```help```\n"
    message += "Show this help menu 🥶.\n\n"

    # Essential expense
    message += "📲 ```ess <value> <description>```\n"
    message += "Record an Essential 🌽 expense (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```ess-usd``` 🇺🇸. "
    automatically = (
        f"The app will automatically 🪄 convert it to {DEFAULT_CURRENCY}.\n\n"
    )
    message += automatically

    # Non essential expense
    message += "📲 ```non <value> <description>```\n"
    message += "Record a Non essential 🍔 expense (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```non-usd``` 🇺🇸. "
    message += automatically

    # Income
    message += "📲 ```inc <value> <description>```\n"
    message += "Record an Income 💸 (transaction). "
    message += f"Add ```-CURRENCY``` if the transaction's currency is not {DEFAULT_CURRENCY}, e. g.: ```inc-usd``` 🇺🇸. "
    message += automatically

    return message


def convert(value: float, currency: str) -> float:
    """convert the value to the default currency used."""

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
