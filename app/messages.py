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
        "\t 🇬🇧🇪🇸 {text_3}: {val_3}\n"
        "\t 🌎 {text_4}: {val_4}"
        "\n\n"
        "👻 {text_5} 🤔:\n\n"
        "📲 *{text_6}*\n"
        "{text_7} 🥶."
        "\n\n"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Hello",
            "text_2": "This is the info of",
            "text_3": "Language",
            "text_4": "Currency",
            "text_5": "You asked for help! Here is what you can type",
            "text_6": "help",
            "text_7": "Show this help menu",
        },
        Language.es: {
            "text_1": "¡Hola",
            "text_2": "Ésta es la información de",
            "text_3": "Idioma",
            "text_4": "Moneda",
            "text_5": "¡Pediste ayuda! Esto es lo que puedes escribir",
            "text_6": "ayuda",
            "text_7": "Muestra este menú de ayuda",
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
        "📲 *{val_1} {text_1} {text_2}*\n"
        "{text_3} {val_2} {val_3}. "
        "{text_4} {val_4}, {text_5} *{val_1}-usd* 🇺🇸. "
        "{text_6} 🪄 {text_7} {val_5}."
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "VALUE",
            "text_2": "DESCRIPTION",
            "text_3": "Record a transaction of type",
            "text_4": "Add *-CURRENCY* if the transaction's currency is not",
            "text_5": "for example",
            "text_6": "The app will automatically",
            "text_7": "convert it to",
        },
        Language.es: {
            "text_1": "VALOR",
            "text_2": "DESCRIPCIÓN",
            "text_3": "Registra una transacción de tipo",
            "text_4": "Agrega *-MONEDA* si la moneda de la transacción no es",
            "text_5": "por ejemplo",
            "text_6": "La aplicación automaticamente",
            "text_7": "la va a convertir a",
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
    base_text: str = "📲 *{text_1}*\n{text_2} 📊."
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "report",
            "text_2": "Type this to get a financial report of your transactions",
        },
        Language.es: {
            "text_1": "reporte",
            "text_2": "Usa este comando para obtener el reporte financiero de tus transacciones",
        },
    }


class ErrorMsg(Message):
    """This is a special class because it holds an error that must be
    propagated all the way up the request for the user to see. It must be
    instantiated when the error presents itself."""

    error_str: str
    base_text: str = "🚫 {error_str}. {text_1} 🙏🏻 {text_2} *{text_3}* {text_4} ℹ️."
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Try again",
            "text_2": "or use the",
            "text_3": "help",
            "text_4": "command for more info",
        },
        Language.es: {
            "text_1": "Intenta otra vez",
            "text_2": "o usa el comando",
            "text_3": "ayuda",
            "text_4": "para obtener más información",
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
    base_text: str = "{text_1}: *{val_1}*"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Second element of the command should be a numerical transaction value"
        },
        Language.es: {
            "text_1": "El segundo elemento del comando debe ser un valor transaccional numérico"
        },
    }


class LengthErrorMsg(Message):
    base_text: str = "{text_1} *{val_1}* {text_2}"
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


COMMAND_UNSUPPORTED_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 The command (message body) *{val_1}* is not valid. 🙏🏻 Please use the *help* command for more info ℹ️."
    "\n\n"
    "🇪🇸\n"
    "🚫 El comando (cuerpo del mensaje) *{val_1}* no es válido. 🙏🏻 Por favor usa el comando *ayuda* para más info ℹ️."
)


class CommandUnsupportedErrorMsg(Message):
    base_text: str = "{text_1} *{val_1}* {text_2}"
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
    "🚫 Your WhatsApp phone number 📞 {phone} is not part of an authorized organization "
    "and cannot execute this command.\n"
    "🙏🏻 Please ask an an admin to add you."
    "\n\n"
    "🇪🇸\n"
    "🚫 Tu número de teléfono de WhatsApp 📞 {phone} no es parte de una organización autorizada "
    "y no puede ejecutar este comando.\n"
    "🙏🏻 Por favor pide a un administrador que te agregue."
)

UNEXPECTED_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 Unexpected error. 🙏🏻 Please contact the app owner."
    "\n\n"
    "🇪🇸\n"
    "🚫 Error inesperado. 🙏🏻 Favor contactar al dueño de la app."
)

CONF_LENGTH_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 Command *{val_1}* should have at least 3 spaces to configure an organization."
    "\n\n"
    "🇪🇸\n"
    "🚫 El comando *{val_1}* debe tener al menos 3 espacios para configurar una organización."
)

CONF_LANGUAGE_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 The second element of the command: *{val_1}*; should be one of the following supported languages: {val_2}. "
    "You may use upper or lower case."
    "\n\n"
    "🇪🇸\n"
    "🚫 El segundo elemento del comando: *{val_1}*; debe ser alguno de los siguientes idiomas soportados: {val_2}. "
    "Puedes usar mayúsculas o minúsculas."
)

CONF_CURRENCY_ERROR_MSG: str = (
    "🇬🇧\n"
    "🚫 The third element of the command: *{val_1}*; should be one of the following supported currencies: {val_2}. "
    "You may use upper or lower case."
    "\n\n"
    "🇪🇸\n"
    "🚫 El tercer elemento del comando: *{val_1}*; debe ser alguna de las siguientes monedas soportadas: {val_2}. "
    "Puedes usar mayúsculas o minúsculas."
)


class NewOrganizationMessage(Message):
    base_text: str = (
        "✅ {text_1} 🎉\n"
        "\t📝 {text_2}: {val_1}\n"
        "\t🇬🇧🇪🇸 {text_3}: {val_2}\n"
        "\t🌎 {text_4}: {val_3}\n"
        "\t📞 {text_5}: {val_4}\n\n"
        "{text_6}\n"
        "\t1. 📲 *{text_7} {text_8}*: {text_9}.\n"
        "\t2. 📲 *{text_10} {text_11}*: {text_12}."
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Successfully created a new organization!",
            "text_2": "Name",
            "text_3": "Language",
            "text_4": "Currency",
            "text_5": "Admin Phone Number",
            "text_6": "As a next step, you can use the following commands:",
            "text_7": "name",
            "text_8": "YOUR NAME",
            "text_9": "set you user's name in the app",
            "text_10": "add",
            "text_11": "PHONE NUMBER",
            "text_12": "invite another user to your organization, use the country code, e. g.: +12134567890",
        },
        Language.es: {
            "text_1": "¡Se creó exitosamente una nueva organización!",
            "text_2": "Nombre",
            "text_3": "Idioma",
            "text_4": "Moneda",
            "text_5": "Teléfono del administrador",
            "text_6": "Como siguiente paso, puedes utilizar los siguientes comandos:",
            "text_7": "nombre",
            "text_8": "TU NOMBRE",
            "text_9": "configura el nombre de tu usuario en la app",
            "text_10": "agregar",
            "text_11": "NÚMERO TELEFÓNICO",
            "text_12": "invita a otro usuario a tu organización, usa el código del país, por ejemplo: +573124567890",
        },
    }


class UserNotAdminErrorMsg(Message):
    base_text: str = "{text_1}: *{val_1}*"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "You are not the admin of the organization and cannot execute the command",
        },
        Language.es: {
            "text_1": "No eres el administrador de la organización y por lo tanto no puedes ejecutar el comando",
        },
    }


class UserExistsErrorMsg(Message):
    base_text: str = "{text_1}: *{val_1}*"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "You are already part of the organization",
        },
        Language.es: {
            "text_1": "Ya eres parte de la organización",
        },
    }


class NameLengthErrorMsg(Message):
    base_text: str = "{text_1} *{val_1}* {text_2}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Command",
            "text_2": "should have at least 1 space to change your user's name",
        },
        Language.es: {
            "text_1": "El comando",
            "text_2": "debe tener al menos 1 espacio para cambiar el nombre de tu usuario",
        },
    }


class UpdatedUserMsg(Message):
    base_text: str = (
        "✅ {text_1} 🎉\n"
        "\t📝 {text_2}: {val_1}\n"
        "\t📞 {text_3}: {val_2}\n"
        "\t💻 {text_4}?: {val_3}"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Successfully updated your user! Here is your info",
            "text_2": "Name",
            "text_3": "Phone Number",
            "text_4": "Organization Admin",
        },
        Language.es: {
            "text_1": "¡Se actualizó exitosamente tu usuario! Aquí está tu info",
            "text_2": "Nombre",
            "text_3": "Teléfono",
            "text_4": "¿Administrador de la organización",
        },
    }


class NameHelpMsg(Message):
    base_text: str = (
        "📲 *{text_1} {text_2}*\n" "{text_3} 📝.\n" "💡 {text_4}:\n" "*{text_1} {text_5}*"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "name",
            "text_2": "YOUR NAME",
            "text_3": "Change your user's name in the app",
            "text_4": "Here is an example of using this command (you can use upper or lower case)",
            "text_5": "John Doe",
        },
        Language.es: {
            "text_1": "nombre",
            "text_2": "TU NOMBRE",
            "text_3": "Cambia el nombre de tu usuario en la app",
            "text_4": "Aquí hay un ejemplo de este comando (puedes usar mayúsculas o minúsculas)",
            "text_5": "Pepito Pérez",
        },
    }


class AddLengthErrorMsg(Message):
    base_text: str = "{text_1} *{val_1}* {text_2}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Command",
            "text_2": "should have at least 1 space to add a new user to the organization",
        },
        Language.es: {
            "text_1": "El comando",
            "text_2": "debe tener al menos 1 espacio para agregar un usuario a la organización",
        },
    }


class InvalidPhoneErrorMsg(Message):
    base_text: str = "{text_1} *{val_1}* {text_2}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "The phone number",
            "text_2": (
                "is not valid, as it should have the symbol *+*, "
                "the country code and the number, for example: +15234567890"
            ),
        },
        Language.es: {
            "text_1": "El número",
            "text_2": (
                "no es válido, pues debe tener el símbolo *+*, "
                "el código del país y el número, por ejemplo: +573161234567"
            ),
        },
    }


class AddedUserMsg(Message):
    base_text: str = "✅ {text_1}: {val_1} 🎉\n" "\t📞 {text_2}: {val_2}\n"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Successfully added a new user to your organization",
            "text_2": "Phone Number",
        },
        Language.es: {
            "text_1": "Se agregó exitosamente un usuario nuevo a tu organización",
            "text_2": "Teléfono",
        },
    }


class AddedUserExistsErrorMsg(Message):
    base_text: str = "{text_1} 📞 *{val_1}* {text_2}"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "The user with phone number",
            "text_2": "is already part of an organization and cannot be added again",
        },
        Language.es: {
            "text_1": "El usuario con número de teléfono",
            "text_2": "ya es parte de una organización y no puede ser agregado nuevamente",
        },
    }


class AddHelpMsg(Message):
    base_text: str = (
        "📲 *{text_1} {text_2}*\n" "👋 {text_3}.\n" "💡 {text_4}:\n" "*{text_1} {text_5}*"
    )
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "add",
            "text_2": "PHONE NUMBER",
            "text_3": (
                "Add a new user to your organization. "
                "Only an Admin can execute this command. "
                "The phone number should begin with the symbol *+*, "
                "followed by the country's code and the complete phone number"
            ),
            "text_4": "Here is an example of using this command",
            "text_5": "+12345678090",
        },
        Language.es: {
            "text_1": "agregar",
            "text_2": "NÚMERO TELEFÓNICO",
            "text_3": (
                "Agrega un nuevo usuario a tu organización. "
                "Sólo un administrador puede ejecutar este comando. "
                "El número telefónico debe empezar con el símbolo *+*, "
                "seguido por el código del país y el número completo"
            ),
            "text_4": "Aquí hay un ejemplo de este comando",
            "text_5": "+573152843265",
        },
    }


class UserWelcomeMsg(Message):
    base_text: str = (
        "👋 {text_1} 📊💸{text_2}\n\n"
        "{text_3}:\n"
        "📝 {text_4} {val_1}\n"
        "🇬🇧🇪🇸 {text_5} {val_2}\n"
        "🌎 {text_6} {val_3}\n"
        "🧙‍♀️📞 {text_7} {val_4}\n\n"
        "{text_8}:\n"
        "📲 *{text_9}*\n\n"
        "💡 {text_10}:\n"
        "- *{text_11}* 👉 {text_12}.\n\n"
        "{text_13}.\n\n"
        "{text_14} 🥂"
    )

    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "Hello there! You have been added to a WhatsApp Expense Tracker",
            "text_2": " organization.",
            "text_3": "Here are the details of the organization",
            "text_4": "Name:",
            "text_5": "Language:",
            "text_6": "Currency:",
            "text_7": "Admin Phone Number :",
            "text_8": "You can get started by using the *name* command to set your name in the app",
            "text_9": "name YOUR NAME",
            "text_10": "Here is an example of using the command",
            "text_11": "name John Doe",
            "text_12": 'Set your name to be "John Doe"',
            "text_13": "You can use the *help* command at anytime to explore what is possible",
            "text_14": "Have fun!",
        },
        Language.es: {
            "text_1": "¡Hola! Has sido agregado/a a una organización para seguir gastos en WhatsApp",
            "text_2": ".",
            "text_3": "Éstos son los detalles de la organización",
            "text_4": "Nombre:",
            "text_5": "Idioma:",
            "text_6": "Moneda:",
            "text_7": "Teléfono del Administrador:",
            "text_8": "Puedes empezar usando el comando *nombre* para establecer tu nombre en la app",
            "text_9": "nombre TU NOMBRE",
            "text_10": "Aquí hay un ejemplo de cómo usar el comando",
            "text_11": "nombre Pepito Pérez",
            "text_12": 'Configura tu nombre para que sea "Pepito Pérez"',
            "text_13": "Puedes usar el comando *ayuda* en cualquier momento para explorar qué es posible",
            "text_14": "¡Diviértete!",
        },
    }


class SendMessageErrorMsg(Message):
    base_text: str = "{text_1}: 📞 *{val_1}*"
    translations: Dict[Language, Dict[str, str]] = {
        Language.en: {
            "text_1": "There was an error while trying to send the invitation message to this number",
        },
        Language.es: {
            "text_1": "Hubo un error al intentar enviar el mensaje de invitación a este número",
        },
    }


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
NEW_ORGANIZATION_MSG = NewOrganizationMessage()
USER_NOT_ADMIN_ERROR_MSG = UserNotAdminErrorMsg()
USER_EXISTS_ERROR_MSG = UserExistsErrorMsg()
NAME_LENGTH_ERROR_MSG = NameLengthErrorMsg()
UPDATED_USER_MSG = UpdatedUserMsg()
NAME_HELP_MSG = NameHelpMsg()
ADD_LENGTH_ERROR_MSG = AddLengthErrorMsg()
INVALID_PHONE_ERROR_MSG = InvalidPhoneErrorMsg()
ADDED_USER_MSG = AddedUserMsg()
ADDED_USER_EXISTS_ERROR_MSG = AddedUserExistsErrorMsg()
ADD_HELP_MSG = AddHelpMsg()
USER_WELCOME_MSG = UserWelcomeMsg()
SEND_MESSAGE_ERROR_MSG = SendMessageErrorMsg()
