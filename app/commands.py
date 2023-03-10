import logging
import os
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from math import floor
from typing import Any, Dict, List

import pytz
from dotenv import load_dotenv
from requests import get

from app.database import Organizations, record_transaction, retrieve_transactions
from app.messages import (
    HELP_INTRO_MSG,
    LENGTH_ERROR_MSG,
    MONTHS,
    NEGATIVE_ERROR_MSG,
    REPORT_HELP_MSG,
    REPORT_MSG,
    TRANSACTION_CURRENCY_MSG,
    TRANSACTION_HELP_MSG,
    TRANSACTION_MSG,
    VALUE_ERROR_MSG,
    ErrorMsg,
    Language,
)

# Load environment variables from a .env file.
load_dotenv()


@dataclass
class Command:
    """Command supported by the application. Any command should be an instance
    of this class."""

    regexp: str
    """Regular expression used for the command. If the message body provided by
    the user matches this regexp, then this command is used. Each command
    should have a regexp defined, that is why no default is provided."""

    def match(self, body: str) -> bool:
        """Returns true if the command's given regexp matches the input
        provided, false otherwise."""

        user_input = body.lower().split(" ")[0]
        return bool(re.compile(self.regexp).match(user_input))

    def execute(self, org: Organizations, **kwargs) -> Dict[str, Any] | ErrorMsg | None:
        """Execute the command. Any logic that the command implements should be
        hosted here. Depending on the logic the command executes, this function
        may return information needed for displaying the final user message.
        Should be implemented by children classes."""
        return

    def message(self, org: Organizations, **kwargs) -> str:
        """Final message that is displayed to the user. Varies based on the
        language provided. A single string is returned, containing the complete
        text for the user. Should be implemented by children classes."""
        return

    def help_message(self, org: Organizations) -> str | None:
        """Help text of the command. Varies based on the language provided.
        Should be implemented by children classes."""
        return


@dataclass
class Help(Command):
    """Display the help menu of the application."""

    regexp: str = "help"

    def execute(self, org: Organizations, **kwargs) -> Dict[str, Any] | ErrorMsg | None:
        # This command does not execute any logic, only passes the commands
        # through.
        return {"commands": kwargs.get("commands")}

    def message(self, org: Organizations, **kwargs) -> str:
        commands: List[Command] = kwargs.get("commands")

        # Intro of the text.
        message = HELP_INTRO_MSG.to_str(org.language)

        # Append the help of all commands.
        for command in commands:
            # Skip commands that do not have a help message.
            if command.help_message(org) is None:
                continue

            message += command.help_message(org)
            message += "\n\n"

        return message

    def help_message(self, org: Organizations) -> str | None:
        # This command is the help of the application, there is no help for the
        # help.
        return None


@dataclass
class Report(Command):
    """Get the financial report."""

    regexp: str = "report"

    def execute(self, org: Organizations, **kwargs) -> Dict[str, Any] | ErrorMsg | None:
        # Tally transactions by creating monthly totals and differentiating
        # between credits and debits. Returns all the transactions in the
        # current month.
        transactions = retrieve_transactions(date=datetime.now())
        current_month = datetime.now(pytz.timezone(os.getenv("TIMEZONE"))).month

        # Tally transactions by type.
        totals = defaultdict(lambda: defaultdict(int))
        current = {}
        for transaction in transactions:
            # Tally by month.
            month_key = f"{transaction.created_at.month}. {MONTHS[org.language][transaction.created_at.month]}"
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

        return {"totals": totals, "current": current}

    def message(self, org: Organizations, **kwargs) -> str:
        totals, current = kwargs.get("totals"), kwargs.get("current")

        # Describe monthly totals.
        monthly_totals_msg = ""
        for month, financials in totals.items():
            monthly_totals_msg += "----------- ⏳ -----------\n"
            monthly_totals_msg += f"💰 {month}\n"

            # Get the actual financials.
            debits = financials.get(COMMANDS["inc"].database_label, 0)
            essential_credits = financials.get(COMMANDS["ess"].database_label, 0)
            non_essential_credits = financials.get(COMMANDS["non"].database_label, 0)
            financial_credits = essential_credits + non_essential_credits

            # Check if there are debits.
            if debits > 0:
                symbols = (
                    f"🟢 {COMMANDS['inc'].emoji} {COMMANDS['inc'].label(org.language)}"
                )
                monthly_totals_msg += f"{symbols} = {'${:,.2f}'.format(debits)}\n"

                # Only report savings when there are credits.
                if financial_credits < 0:
                    savings = debits + financial_credits
                    savings_ratio = floor((savings / debits) * 100)
                    savings_text = (
                        "\t🥂 Savings" if org.language == Language.en else "\t🥂 Ahorros"
                    )
                    monthly_totals_msg += (
                        f"{savings_text} ({savings_ratio}%)\n"
                        f"\t   👉 {'${:,.2f}'.format(savings)}\n"
                    )

            # Check if there are credits.
            if financial_credits < 0:
                expenses_text = (
                    "🔴 Expenses" if org.language == Language.en else "🔴 Gastos"
                )
                monthly_totals_msg += (
                    f"{expenses_text} = {'${:,.2f}'.format(abs(financial_credits))}\n"
                )

                # Report essential credits, if they exist.
                if essential_credits < 0:
                    essential_ratio = abs(
                        floor((essential_credits / financial_credits) * 100)
                    )
                    symbols = f"\t{COMMANDS['ess'].emoji} {COMMANDS['ess'].label(org.language)}"
                    monthly_totals_msg += f"{symbols} ({essential_ratio}%)\n"
                    monthly_totals_msg += (
                        f"\t   👉 {'${:,.2f}'.format(abs(essential_credits))}\n"
                    )

                # Report non essential credits, if they exist.
                if non_essential_credits < 0:
                    non_essential_ratio = abs(
                        floor((non_essential_credits / financial_credits) * 100)
                    )
                    symbols = f"\t{COMMANDS['non'].emoji} {COMMANDS['non'].label(org.language)}"
                    monthly_totals_msg += f"{symbols} ({non_essential_ratio}%)\n"
                    monthly_totals_msg += (
                        f"\t   👉 {'${:,.2f}'.format(abs(non_essential_credits))}\n"
                    )

            monthly_totals_msg += "----------- ⏳ -----------\n"

        # Get the top expenses for the current month.
        current = dict(sorted(current.items(), key=lambda item: item[1], reverse=True))
        top = {k: current[k] for k in list(current.keys())[:10]}
        top_expenses_message = ""
        for ix, (k, v) in enumerate(top.items()):
            components = k.split(";")
            label, date, description = components[0], components[1], components[2]
            top_expenses_message += f"🔥 {ix + 1}. {'${:,.2f}'.format(v)} ({date})\n"
            emoji = (
                COMMANDS["ess"].emoji
                if label == COMMANDS["ess"].database_label
                else COMMANDS["non"].emoji
            )
            translated_label = (
                COMMANDS["ess"].label(org.language)
                if label == COMMANDS["ess"].database_label
                else COMMANDS["non"].label(org.language)
            )
            top_expenses_message += f"\t{emoji} {translated_label}\n"
            top_expenses_message += f"\t{description}\n"

        return REPORT_MSG.to_str(
            org.language,
            val_1=org.currency.value,
            val_2=monthly_totals_msg,
            val_3=top_expenses_message,
        )

    def help_message(self, org: Organizations) -> str | None:
        return REPORT_HELP_MSG.to_str(org.language)


class TransactionSense(IntEnum):
    """TransactionSense represents the sense, or symbol, of a transaction,
    which can be positive if it debits an account or negative if it credits
    it."""

    positive = 1
    """Increases monetary value."""
    negative = -1
    """Decreases monetary value."""


@dataclass
class Transaction(Command):
    """Register a transaction in the database."""

    database_label: str
    """String for the command to save in the database."""
    user_label: str
    """String for the user to execute the command."""
    sense: TransactionSense
    """Positive debits an account, negative credits it."""
    emoji: str
    """Graphical representation if the transaction."""

    def __init__(self):
        # The regular expression is based on the string that the user applies
        # to execute the command.
        self.regexp = (
            "(^(?={user_label}$)|(?:{user_label}-[a-zA-z][a-zA-z][a-zA-z])$)".format(
                user_label=self.user_label
            )
        )

    def execute(self, org: Organizations, **kwargs) -> Dict[str, Any] | ErrorMsg | None:
        # Record a new transaction in the database, based on the currency and
        # type: a debit or a credit.
        body = kwargs.get("body")
        request = body.lower().split(" ")

        # Checks that there are at least 2 spaces defining the request.
        if len(request) < 3:
            return ErrorMsg(error_str=LENGTH_ERROR_MSG.to_str(org.language, val_1=body))

        # Checks that the request has the correct ordering.
        value = 0
        try:
            value = float(request[1])
        except ValueError:
            return ErrorMsg(
                error_str=VALUE_ERROR_MSG.to_str(org.language, val_1=request[1])
            )

        if value <= 0:
            return ErrorMsg(error_str=NEGATIVE_ERROR_MSG.to_str(org.language))

        # Gets request elements.
        full_command = request[0].split("-")
        currency = org.currency.value
        if len(full_command) > 1:
            currency = full_command[1].upper()
        description = " ".join(request[2:])

        # Converts the value in case a foreign currency is used.
        value_converted = deepcopy(value)
        if currency != org.currency.value:
            value_converted = self.convert(
                value=value,
                base_currency=currency,
                target_currency=org.currency.value,
            )

        # Record the transaction in the database.
        val = value * self.sense.value
        val_conv = value_converted * self.sense.value
        record_transaction(
            created_at=datetime.now(pytz.timezone(os.getenv("TIMEZONE"))),
            description=description,
            label=self.database_label,
            value=val,
            currency=currency,
            value_converted=val_conv,
        )

        return {
            "currency": currency,
            "value": val,
            "value_converted": val_conv,
            "description": description,
        }

    def message(self, org: Organizations, **kwargs) -> str:
        currency, value, value_converted, description = (
            kwargs.get("currency"),
            kwargs.get("value"),
            kwargs.get("value_converted"),
            kwargs.get("description"),
        )

        message = TRANSACTION_MSG.to_str(
            org.language,
            val_1=self.emoji,
            val_2=self.label(org.language),
            val_3=currency,
            val_4="${:,.2f}".format(abs(value)),
            val_5=description,
        )

        if value != value_converted:
            message += TRANSACTION_CURRENCY_MSG.to_str(
                org.language,
                val_1=org.currency.value,
                val_2="${:,.2f}".format(abs(value_converted)),
            )

        return message

    def help_message(self, org: Organizations) -> str | None:
        return TRANSACTION_HELP_MSG.to_str(
            org.language,
            val_1=self.user_label,
            val_2=self.label(org.language),
            val_3=self.emoji,
            val_4=org.currency.value,
            val_5=org.currency.value,
            val_6=self.user_label,
            val_7=self.user_label,
        )

    def label(self, language: Language) -> str:
        """Label that is shown to the user for the transaction type. Should be
        implemented by children classes."""
        return

    @staticmethod
    def convert(value: float, base_currency: str, target_currency: str) -> float:
        """convert the value to the default currency used with an external API."""

        url = f"https://api.apilayer.com/fixer/latest?base={base_currency}&symbols={target_currency}"
        headers = {"apikey": os.getenv("FIXER_API_KEY")}
        try:
            response = get(url=url, headers=headers)
            data = response.json()
            rate = data.get("rates").get(target_currency)

        except Exception as ex:
            logging.exception(f"error trying to get currency conversion: {ex}")
            rate = 4700

        return value * rate


@dataclass
class Essential(Transaction):
    """An essential expense."""

    database_label: str = "Essential"
    user_label: str = "ess"
    sense: TransactionSense = TransactionSense.negative
    emoji: str = "🌽"

    def __init__(self):
        super().__init__()

    def label(self, language: Language) -> str:
        return self.database_label if language == Language.en else "Esencial"


@dataclass
class NonEssential(Transaction):
    """A non-essential expense."""

    database_label: str = "Non essential"
    user_label: str = "non"
    sense: TransactionSense = TransactionSense.negative
    emoji: str = "🍔"

    def __init__(self):
        super().__init__()

    def label(self, language: Language) -> str:
        return self.database_label if language == Language.en else "No esencial"


@dataclass
class Income(Transaction):
    """An income (increases monetary value)."""

    database_label: str = "Income"
    user_label: str = "inc"
    sense: TransactionSense = TransactionSense.positive
    emoji: str = "💸"

    def __init__(self):
        super().__init__()

    def label(self, language: Language) -> str:
        return self.database_label if language == Language.en else "Ingreso"


# Instantiate the supported commands once because they contain static
# information that does not need updating.
COMMANDS: Dict[str, Command | Transaction] = {
    "help": Help(),
    "report": Report(),
    "ess": Essential(),
    "non": NonEssential(),
    "inc": Income(),
}
