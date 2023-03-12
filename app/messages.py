from typing import Dict

from app.database import Language

# Months as text format, based on language.
MONTHS = {
    Language.en: {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    },
    Language.es: {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    },
}


class Message:
    """Any user-facing message should implement this class to properly display
    information based on the language and given formats."""

    base_text: str
    """The base for the message with the main body of the text. Add format
    placeholders {text_n} to signal where different text components should go,
    like {text_1}, {text_2}, etc... For value components, such as variables
    that do not have a fixed value, add format placeholders with the format
    {val_n}"""

    translations: Dict[Language, Dict[str, str]]
    """The actual text components that are missing from the base text. The
    components should be written for each supported language and the dict for
    each language should fulfill the missing text keys, such as: {'text_1':
    'the first text', 'text_2': 'the next text'}."""

    def to_str(self, language: Language, **kwargs) -> str:
        """Render the string of the message using a target language and all the
        components that are needed to format the text, as kwargs."""

        text_components = self.translations[language]
        return self.base_text.format(**text_components | kwargs)


class HelpIntroMsg(Message):
    base_text: str = (
        "👋 {text_1} {val_1}!\n"
        "{text_2} {val_2} 🧙‍♀️:\n"
        "\t 🇬🇧🇪🇸 {text_3}: {val_3}"
        "\t 🌎 {text_4}: {val_4}"
        "\n\n"
        "👻 {text_5} 🤔:\n\n"
        "📲 ```help```\n"
        "{text_6} 🥶."
        "\n\n"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Hello",
            "text_2": "This is the info of",
            "text_3": "Language",
            "text_4": "Currency",
            "text_5": "You asked for help! Here is what you can type",
            "text_6": "Show this help menu",
        },
        Language.es: {
            "text_1": "¡Hola",
            "text_2": "Ésta es la información de",
            "text_3": "Idioma",
            "text_4": "Moneda",
            "text_5": "¡Pediste ayuda! Esto es lo que puedes escribir",
            "text_6": "Muestra este menú de ayuda",
        },
    }


class TransactionMsg(Message):
    base_text: str = (
        "✅ {text_1} 🎉\n"
        "\t❓ {text_2}: {val_1} {val_2}\n"
        "\t🤑 {text_3}: {val_3} {val_4}\n"
        "\t🔍 {text_4}: {val_5}\n"
        "{val_6}"
        "\n"
        "👋 {text_5} {val_7}!"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Successfully recorded transaction!",
            "text_2": "Type",
            "text_3": "Value",
            "text_4": "Description",
            "text_5": "Have a nice day",
        },
        Language.es: {
            "text_1": "¡Transacción registrada exitosamente!",
            "text_2": "Tipo",
            "text_3": "Valor",
            "text_4": "Descripción",
            "text_5": "¡Que tengas un lindo día",
        },
    }


class TransactionCurrencyMsg(Message):
    base_text: str = "\t🌎 {text_1}: {val_1} {val_2}\n"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {"text_1": "Value (converted)"},
        Language.es: {"text_1": "Valor (convertido)"},
    }


class TransactionHelpMsg(Message):
    base_text: str = (
        "📲 ```{val_1} <{text_1}> <{text_2}>```\n"
        "{text_3} {val_2} {val_3}. "
        "{text_4} {val_4}, {text_5} ```ess-usd``` 🇺🇸. "
        "{text_6} 🪄 {text_7} {val_5}.\n"
        "💡 {text_8}:\n"
        "```{val_6} 3600 {text_9}```\n"
        "```{val_7}-usd 87 {text_10} USD```"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "value",
            "text_2": "description",
            "text_3": "Record a transaction of type",
            "text_4": "Add ```-CURRENCY``` if the transaction's currency is not",
            "text_5": "for example",
            "text_6": "The app will automatically",
            "text_7": "convert it to",
            "text_8": "Here are some examples when using this command (you can use upper or lower case)",
            "text_9": "a sample transaction",
            "text_10": "a transaction in the currency",
        },
        Language.es: {
            "text_1": "valor",
            "text_2": "descripción",
            "text_3": "Registra una transacción de tipo",
            "text_4": "Agrega ```-MONEDA``` si la moneda de la transacción no es",
            "text_5": "por ejemplo",
            "text_6": "La aplicación automaticamente",
            "text_7": "la va a convertir a",
            "text_8": "Aquí hay algunos ejemplos para usar este comando (puedes usar mayúsculas o minúsculas)",
            "text_9": "una transacción de prueba",
            "text_10": "transacción en la moneda",
        },
    }


class ReportMsg(Message):
    base_text: str = (
        "{text_1} {val_1}!\n"
        "*🤓 {text_2} {val_2} {text_3} {val_3} 💵📊.*\n\n\n"
        "*_{text_4} 📅💯:_*\n"
        "{val_4}\n\n"
        "*_🙀 {text_5} 🔝 {text_6} 🚨:_*\n"
        "{val_5}"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Hello",
            "text_2": "This is the financial report of",
            "text_3": "in the currency",
            "text_4": "Monthly totals",
            "text_5": "These are the top",
            "text_6": "expenses this month",
        },
        Language.es: {
            "text_1": "¡Hola",
            "text_2": "Éste es el reporte financiero de",
            "text_3": "en la moneda",
            "text_4": "Totales mensuales",
            "text_5": "Éstos son el top",
            "text_6": "de gastos este mes",
        },
    }


class ReportHelpMsg(Message):
    base_text: str = "📲 ```report```\n{text_1} 📊."
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Type this to get a financial report of your transactions",
        },
        Language.es: {
            "text_1": "Usa este comando para obtener el reporte financiero de tus transacciones"
        },
    }


class ErrorMsg(Message):
    """This is a special class because it holds an error that must be
    propagated all the way up the request for the user to see. It must be
    instantiated when the error presents itself."""

    error_str: str
    base_text: str = "🚫 {error_str}. {text_1} 🙏🏻 {text_2} ```help``` {text_3} ℹ️."
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Try again",
            "text_2": "or use the",
            "text_3": "command for more info",
        },
        Language.es: {
            "text_1": "Intenta otra vez",
            "text_2": "o usa el comando",
            "text_3": "para obtener más información",
        },
    }

    def __init__(self, error_str: str) -> None:
        self.error_str = error_str
        super().__init__()

    def to_str(self, language: Language, **kwargs) -> str:
        """This method is redefined for this class to explicitly define that
        the error_str must come from an attribute in the class."""

        text_components = self.translations[language]
        return self.base_text.format(error_str=self.error_str, **text_components)


class ValueErrorMsg(Message):
    base_text: str = "{text_1}: {val_1}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Second element of the command should be a numerical transaction value"
        },
        Language.es: {
            "text_1": "El segundo elemento del comando debe ser un valor transaccional numérico"
        },
    }


class LengthErrorMsg(Message):
    base_text: str = '{text_1} "{val_1}" {text_2}'
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Command",
            "text_2": "should have at least 2 spaces to record a transaction",
        },
        Language.es: {
            "text_1": "El comando",
            "text_2": "debe tener al menos 2 espacios para registrar una transacción",
        },
    }


class NegativeErrorMsg(Message):
    base_text: str = "{text_1}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Value should be greater than 0",
        },
        Language.es: {
            "text_1": "El valor debe ser mayor a 0",
        },
    }


class CommandUnsupportedErrorMsg(Message):
    base_text: str = '{text_1} "{val_1}" {text_2}'
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "The command (message body)",
            "text_2": "is not valid",
        },
        Language.es: {
            "text_1": "El comando (cuerpo del mensaje)",
            "text_2": "no es válido",
        },
    }


USER_ORG_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 Your WhatsApp phone number 📞 {phone} is not part of an authorized organization.\n"
    "🙏🏻 Please ask an an admin to add you."
    "\n\n"
    "🇪🇸\n"
    "🚫 Tu número de teléfono de WhatsApp 📞 {phone} no es parte de una organización autorizada.\n"
    "🙏🏻 Por favor pide a un administrador que te agregue."
)

UNEXPECTED_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 Unexpected error. 🙏🏻 Please contact the app owner."
    "\n\n"
    "🇪🇸\n"
    "🚫 Error inesperado. 🙏🏻 Favor contactar al dueño de la app."
)

# The classes are instantiated once because they hold static information.
HELP_INTRO_MSG = HelpIntroMsg()
TRANSACTION_MSG = TransactionMsg()
TRANSACTION_CURRENCY_MSG = TransactionCurrencyMsg()
TRANSACTION_HELP_MSG = TransactionHelpMsg()
REPORT_MSG = ReportMsg()
REPORT_HELP_MSG = ReportHelpMsg()
VALUE_ERROR_MSG = ValueErrorMsg()
LENGTH_ERROR_MSG = LengthErrorMsg()
NEGATIVE_ERROR_MSG = NegativeErrorMsg()
COMMAND_UNSUPPORTED_ERROR_MSG = CommandUnsupportedErrorMsg()
