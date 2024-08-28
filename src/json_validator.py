"""
    json_validator.py

    A recursive descent parser for JSON files.

    Example:
        validator = JsonValidator()
        validator.validate_json("valid.json") # True"
"""

from src.json_validator_errors import ErrorCode, JSONValidatorError

class JsonValidator:
    """ A validator for JSON files.

    This class provides a set of methods for recursive descent parsing of JSON files.

    Example:
        validator = JsonValidator()
        validator.validate_json("valid.json") # True
    """

    def __init__(self):
        """ Initializes a new instance of the JSONValidator class.

        Opens a file for JSON validation, sets the initial line number and _column
        number then gets the first _column.
        """
        self._file = None # file that must be opened
        self._token = "" # current character token
        self._line = 0 # current line number
        self._column = 0 # current column number

    def _raise_error(self, message: str, error_code: ErrorCode):
        """ Raises a JSONValidatorError.

        Uses the provided message, error code, and the current line and column number

        Args:
            message (str): The error message
            error_code (ErrorCode): The error code

        Raises:
            JSONValidatorError: An exception with error message, error code,
            line number, and column number
        """
        raise JSONValidatorError(message, error_code, self._line, self._column)

    def open_file(self, filename: str):
        """ Opens a file for JSON validation.

        Sets the initial _line number and column number then gets the first column.

        Args:
            filename (str): The name of the file to be opened.

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # check for no file provided
        if not filename or "." not in filename:
            self._raise_error("no file specified", ErrorCode.FILE_MISSING_ERROR)
        # check for invalid file type
        if not filename.endswith(".json"):
            self._raise_error("invalid file type", ErrorCode.FILE_TYPE_ERROR)
        # open file and throw error if not found
        try:
            self._file = open(filename, "r", encoding="UTF-8")
        except FileNotFoundError as e:
            self._raise_error(str(e), ErrorCode.FILE_NOT_FOUND)
        # set initial line to 1 and column to 0 so getting hte first char sets column index to 1
        self._line = 1
        self._column = 0
        # get first character
        self._get_char()

    def close_file(self):
        """ Closes the file """
        self._file.close()

    def _get_char(self, error_if_eof: tuple[str, ErrorCode]=None):
        """ Gets the next character from the file

        If at the end of the file, sets the token to empty string

        Args:
            error_if_eof (tuple[str, ErrorCode], optional): Optional error code and message to raise
            if at the end of the file, if there is no error specified, no error will be raised

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # increment column before reading so errors are on correct column
        self._column += 1
        try:
            self._token = self._file.read(1)
        # checks if there is a problem reading the next character
        except UnicodeDecodeError as e:
            self._raise_error(str(e), ErrorCode.FILE_READ_ERROR)

        # Raises an error if at the end of the file
        # if there is an error specified
        if not self._token and error_if_eof:
            self._raise_error(*error_if_eof)

    def _whitespace(self) -> None:
        """ Recursively skips through whitespace """
        if self._token == " ":
            self._get_char()
            self._whitespace()
        # tabs take 3 spaces
        if self._token == "\t":
            self._get_char()
            self._column += 3
            self._whitespace()
        # carriage returns go to beginning of line
        elif self._token == "\r":
            self._get_char()
            self._column = 1
            self._whitespace()
        # line feeds go to next line
        elif self._token == "\n":
            self._get_char()
            self._line += 1
            self._column = 1
            self._whitespace()

    def _string_hex(self) -> None:
        """ Checks if the 4 characters following backslash u are hex digits

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # All hex digits
        hex_char = "1234567890abcdefABCDEF"
        # Check for 4 hex digits
        for _ in range(4):
            # check if end of file
            self._get_char(("end of file reached in string hex, must have 4 hex digits after \\u",
                ErrorCode.STRING_HEX_ERROR))
            # Check if character is valid hex
            if self._token not in hex_char:
                self._raise_error(
                    "invalid hex digit after \\u in string", ErrorCode.STRING_HEX_ERROR)

    def _string_backslash(self) -> None:
        """ Validates escape characters.

        Checks if the next character is a valid escape character and
        validates the sequence if necessary

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # get the escape character, cannot be eof
        self._get_char(("end of file instead of escape character in string",
            ErrorCode.STRING_ESCAPE_ERROR))

        # check if valid escape character and checks sequence for hex (backlash u)
        if (
            self._token == '"' or
            self._token == '\\' or
            self._token == '/' or
            self._token == 'b' or
            self._token == 'f' or
            self._token == 'n' or
            self._token == 'r' or
            self._token == 't'
        ):
            return
        if (self._token == 'u'):
            self._string_hex()
            return
        self._raise_error("invalid escape character in string", ErrorCode.STRING_ESCAPE_ERROR)

    def _string_char(self) -> None:
        """ Recursively checks if the next character is a valid string character

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("file ended in middle of string", ErrorCode.STRING_EOF_ERROR))

        # checks for escape characters
        if self._token == '\\':
            self._string_backslash()
        elif self._token == '\t':
            self._raise_error("invalid tab character in string", ErrorCode.STRING_CHARACTER_ERROR)
        elif self._token == '\n':
            self._raise_error("invalid newline character in string", ErrorCode.STRING_CHARACTER_ERROR)
        # check for end of string
        elif self._token == '"':
            return

        # recursively checks next character
        self._string_char()

    def _string(self) -> None:
        """ Parses a string to check if it is valid

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """

        # recursively check if string is valid
        self._string_char()

        # _string_char exits on endquote so no need to check for endquote
        # value checks for eof so no check here
        self._get_char()

    def _digit(self) -> None:
        """ Recursively loops until the next character is not a digit """
        # eof is checked in number, so no need to check here
        self._get_char()
        if self._token.isdigit():
            self._digit()

    def _decimal(self) -> None:
        """ Parses a decimal number after the decimal point

        Decimal number must have at least one digit after the decimal point

        """
        self._get_char(("end of file reached in decimal", ErrorCode.NUMBER_EOF_ERROR))
        if not self._token.isdigit():
            self._raise_error("non digit in decimal", ErrorCode.NUMBER_DIGIT_ERROR)
        self._digit()

    def _exponent(self) -> None:
        """ Parses an exponent after e or E

        Exponent must have at least one digit after e or E

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("end of file reached in exponent", ErrorCode.NUMBER_EXPONENT_ERROR))
        if self._token == '-' or self._token == '+':
            self._get_char(("end of file reached in exponent", ErrorCode.NUMBER_EXPONENT_ERROR))
        if self._token.isdigit():
            self._digit()
            return
        self._raise_error("invalid exponent", ErrorCode.NUMBER_EXPONENT_ERROR)

    def _number(self) -> None:
        """ Parses a number to check if it is valid

        Checks all valid number sequences, does not check validity of
        exit character as that is checked by number

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # negative number
        if self._token == '-':
            self._get_char(("end of file reached in number", ErrorCode.NUMBER_EOF_ERROR))
        # leading 0
        if self._token == '0':
            self._get_char()
            if self._token.isdigit():
                self._raise_error("leading 0 in number", ErrorCode.NUMBER_LEADING_ZERO_ERROR)
        # non leading 0 number
        elif self._token.isdigit():
            self._digit()
        # if there's no digit after negative is invalid
        # - is the only enter character that could trigger this
        else:
            self._raise_error('"-" followed by non digit in number', ErrorCode.NUMBER_DIGIT_ERROR)

        # decimal
        if self._token == ".":
            self._decimal()

        # exponent
        if self._token == "e" or self._token == "E":
            self._exponent()

    def _true_value(self) -> None:
        """ Checks if value starting with "t" is "true"

        true is the only valid value starting with t (strings start with a quote)

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # get character after t
        self._get_char(("end of file reached in true value", ErrorCode.VALUE_EOF_ERROR))
        # check rue since it is the only valid value after t
        for c in "rue":
            if c != self._token:
                self._raise_error("invalid character in true value",
                    ErrorCode.VALUE_CHARACTER_ERROR)
            self._get_char(("end of file reached in true value", ErrorCode.VALUE_EOF_ERROR))

    def _false_value(self) -> None:
        """ Checks if value starting with "f" is "false"

        false is the only valid value starting with f (strings start with a quote)

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("end of file reached in false value", ErrorCode.VALUE_EOF_ERROR))
        # check alse since it is the only valid string after f # cSpell: disable-line
        for c in "alse": # cSpell: disable-line
            if c != self._token:
                self._raise_error("invalid character in false value",
                    ErrorCode.VALUE_CHARACTER_ERROR)
            self._get_char(("end of file reached in false value", ErrorCode.VALUE_EOF_ERROR))

    def _null_value(self) -> None:
        """ Checks if value starting with "n" is "null"

        null is the only valid value starting with n (strings start with a quote)

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("end of file reached in null value", ErrorCode.VALUE_EOF_ERROR))
        for c in "ull":
            if c != self._token:
                self._raise_error("invalid character in null value",
                    ErrorCode.VALUE_CHARACTER_ERROR)
            self._get_char(("end of file reached in null value", ErrorCode.VALUE_EOF_ERROR))
    
    def _value(self) -> None:
        """ Parses a value to check if it is valid

        Checks all valid value sequences including strings, numbers, bools, null,
        arrays, and objects

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._whitespace()

        # string
        if self._token == '"':
            self._string()
        # number
        elif self._token == '-' or self._token.isdigit():
            self._number()
        # object
        elif self._token == '{':
            self._json_object()
        # array
        elif self._token == '[':
            self._array()
        # true
        elif self._token == 't':
            self._true_value()
        # false
        elif self._token == 'f':
            self._false_value()
        # null
        elif self._token == 'n':
            self._null_value()
        else:
            self._raise_error("invalid character in value", ErrorCode.VALUE_CHARACTER_ERROR)

        self._whitespace()

    def _value_list(self) -> None:
        """ Recursively parses the inner part of an array to check if it is valid
        
        Value lists consist of values separated by commas

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # must contain a value array already validated empty array
        self._value()

        # check for another value
        if self._token == ',':
            # eof after comma is not valid
            self._get_char(("end of file reached in array", ErrorCode.ARRAY_EOF_ERROR))
            self._value_list()

    def _array(self) -> None:
        """ Parses an array to check if it is valid

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # eof after [ is not valid, array must close ]
        self._get_char(("end of file reached in array", ErrorCode.ARRAY_EOF_ERROR))
        self._whitespace()

        # close empty array
        if self._token == "]":
            # can end file after ]
            self._get_char()
            return
        # non empty array must contain value(s)
        self._value_list()
        # close non empty array
        if self._token == "]":
            # can end file after ]
            self._get_char()
            return
        self._raise_error("invalid character in array", ErrorCode.ARRAY_CHARACTER_ERROR)

    def _key_value_list(self) -> None:
        """ Parses the inner part of an object to check if it is valid

        Key value lists consist of key value pairs separated by commas

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # string key
        if self._token != '"':
            self._raise_error("no quote to denote string before key", ErrorCode.OBJECT_KEY_ERROR)
        self._string()
        self._whitespace()

        # colon separator between key and value
        if self._token != ':':
            self._raise_error("need colon between key and value", ErrorCode.OBJECT_SEPARATOR_ERROR)
        self._get_char(("end of file reached in object", ErrorCode.OBJECT_EOF_ERROR))
        self._whitespace()

        # value
        self._value()

        # check for another value
        if self._token == ',':
            self._get_char(("end of file not valid after comma in object",
                ErrorCode.OBJECT_EOF_ERROR))
            self._whitespace()
            self._key_value_list()

    def _json_object(self) -> None:
        """ Parses an object to check if it is valid

        Object consists of key value pairs separated by commas

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # eof after { is not valid
        self._get_char(("end of file reached in object", ErrorCode.OBJECT_EOF_ERROR))
        self._whitespace()
        # close empty object
        if self._token == '}':
            # can end file after }
            self._get_char()
            return
        # non empty object must contain key value(s)
        self._key_value_list()
        # close non empty object
        if self._token == '}':
            # can end file after }
            self._get_char()
            return

        self._raise_error("no closing bracket in object", ErrorCode.OBJECT_CLOSE_ERROR)

    def validate_json(self, filename: str) -> None:
        """ Function checks if a json file is valid
        
        Opens file and checks if it is a valid json, returns True
        if valid and gives and error if false

        Args:
            filename (str): name of json file

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # open file with given filename
        self.open_file(filename)
        #clear whitespace
        self._whitespace()
        # object enter character
        if self._token == '{':
            self._json_object()
        # array enter character
        elif self._token == '[':
            self._array()
        # other values are an invalid start to a json
        else:
            self._raise_error("not object or array", ErrorCode.INVALID_START_ERROR)

        # whitespace allowed after final object or array
        self._whitespace()

        # characters after final object or array are not valid
        if self._token:
            self._raise_error("invalid character after end of final object or array",
                ErrorCode.EOF_CHARACTER_ERROR)

        # close file
        self.close_file()
