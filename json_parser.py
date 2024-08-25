"""
    json_parser.py

    A recursive descent parser for JSON files.

    Example:
        validator = JsonValidator()
        validator.validate_json("valid.json") # True"
"""

from json_parser_errors import ErrorCode, JSONValidatorError

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

    def _whitespace(self):
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

    def _string_hex(self) -> bool:
        """ Checks if the 4 characters following backslash u are hex digits

        Returns:
            bool: True if the 4 characters following backslash u are hex digits

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        # Get next character after u, cannot be eof
        self._get_char(("cannot end file after \\u", ErrorCode.STRING_HEX_ERROR))
        # All hex digits
        hex_char = "1234567890abcdefABCDEF"
        # Check for 4 hex digits
        for _ in range(4):
            # Check if character is valid hex
            if self._token not in hex_char:
                self._raise_error(
                    "invalid hex digit after \\u in string", ErrorCode.STRING_HEX_ERROR)
            # check if end of file
            self._get_char(("end of file reached in string hex, must have 4 hex digits after \\u",
                ErrorCode.STRING_HEX_ERROR))
        return True

    def _string_backslash(self) -> bool:
        """ Validates escape characters.

        Checks if the next character is a valid escape character and
        validates the sequence if necessary

        Returns:
            bool: True if the following sequence is a valid escape sequence

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
            self._token == 'b' or
            self._token == 'f' or
            self._token == 'n' or
            self._token == 'r' or
            self._token == 't' or
            (self._token == 'u' and self._string_hex())
        ):
            return True
        self._raise_error("invalid escape character in string", ErrorCode.STRING_ESCAPE_ERROR)
        return False

    def _string_char(self) -> bool:
        """ Recursively checks if the next character is a valid string character

        Returns:
            bool: True if the next sequence is a valid string sequence

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("file ended in middle of string", ErrorCode.STRING_EOF_ERROR))

        # checks for escape characters
        if self._token == '\\':
            self._string_backslash()
        # check for end of string
        elif self._token == '"':
            return True

        # recursively checks next character
        return self._string_char()

    def _string(self) -> bool:
        """ Parses a string to check if it is valid

        Returns:
            bool: True if the string is valid

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """

        # recursively check if string is valid
        self._string_char()

        # _string_char exits on endquote so no need to check for endquote
        # value checks for eof so no check here
        self._get_char()
        return True

    def _digit(self) -> None:
        """ Recursively loops until the next character is not a digit """
        # eof is checked in number, so no need to check here
        self._get_char()
        if self._token.isdigit():
            self._digit()

    def _decimal(self) -> bool:
        """ Parses a decimal number after the decimal point

        Decimal number must have at least one digit after the decimal point

        Returns:
            bool: True if the decimal number is valid

        """
        self._get_char(("end of file reached in decimal", ErrorCode.NUMBER_EOF_ERROR))
        if not self._token.isdigit():
            self._raise_error("non digit in decimal", ErrorCode.NUMBER_DIGIT_ERROR)
        self._digit()
        return True

    def _exponent(self) -> bool:
        """ Parses an exponent after e or E

        Exponent must have at least one digit after e or E

        Returns:
            bool: True if the exponent is valid

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("end of file reached in exponent", ErrorCode.NUMBER_EXPONENT_ERROR))
        if self._token == '-' or self._token == '+':
            self._get_char(("end of file reached in exponent", ErrorCode.NUMBER_EXPONENT_ERROR))
        if self._token.isdigit():
            self._digit()
            return True
        return self._raise_error("invalid exponent", ErrorCode.NUMBER_EXPONENT_ERROR)

    def _number(self) -> bool:
        """ Parses a number to check if it is valid

        Checks all valid number sequences, does not check validity of
        exit character as that is checked by number

        Returns:
            bool: True if the number is valid

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

        return True

    def _true_value(self) -> bool:
        """ Checks if value starting with "t" is "true"

        true is the only valid value starting with t (strings start with a quote)

        Returns:
            bool: True if value starting with "t" is "true"

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
        return True

    def _false_value(self) -> bool:
        """ Checks if value starting with "f" is "false"

        false is the only valid value starting with f (strings start with a quote)

        Returns:
            bool: True if value starting with "f" is "false"

        Raises:
            JSONValidatorError: An exception with error message, error code, line number,
            and column number
        """
        self._get_char(("end of file reached in false value", ErrorCode.VALUE_EOF_ERROR))
        # check alse since it is the only valid string after f
        for c in "alse": 
            if c != self._token:
                self._raise_error("invalid character in false value",
                    ErrorCode.VALUE_CHARACTER_ERROR)
            self._get_char(("end of file reached in false value", ErrorCode.VALUE_EOF_ERROR))
        return True

    def _null_value(self) -> bool:
        """ Checks if value starting with "n" is "null"

        null is the only valid value starting with n (strings start with a quote)

        Returns:
            bool: True if value starting with "n" is "null"

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
        return True
    def _value(self) -> bool:
        """ Parses a value to check if it is valid

        Checks all valid value sequences including strings, numbers, bools, null,
        arrays, and objects

        Returns:
            bool: True if the value is valid

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
        return True

    def _value_list(self) -> bool:
        """ Recursively parses the inner part of an array to check if it is valid
        
        Value lists consist of values separated by commas

        Returns:
            bool: True if the value list is valid

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
        return True

    def _array(self) -> bool:
        """ Parses an array to check if it is valid

        Returns:
            bool: True if the array is valid

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
            return True
        # non empty array must contain value(s)
        self._value_list()
        # close non empty array
        if self._token == "]":
            # can end file after ]
            self._get_char()
            return True
        self._raise_error("invalid character in array", ErrorCode.ARRAY_CHARACTER_ERROR)
        return False

    def _key_value_list(self) -> bool:
        """ Parses the inner part of an object to check if it is valid

        Key value lists consist of key value pairs separated by commas

        Returns:
            bool: True if the key value list is valid

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

        return True

    def _json_object(self) -> bool:
        """ Parses an object to check if it is valid

        Object consists of key value pairs separated by commas

        Returns:
            bool: True if the object is valid

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
            return True
        # non empty object must contain key value(s)
        self._key_value_list()
        # close non empty object
        if self._token == '}':
            # can end file after }
            self._get_char()
            return True

        self._raise_error("invalid character in object", ErrorCode.OBJECT_KEY_ERROR)
        return False

    def validate_json(self, filename: str) -> bool:
        """ Function checks if a json file is valid
        
        Opens file and checks if it is a valid json, returns True
        if valid and gives and error if false

        Args:
            filename (str): name of json file

        Returns:
            bool: True if json is valid

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
        return True
