"""
    json_parser_errors.py
    
    A module containing the ErrorCode and JSONValidatorError classes for custom
    error handling for JSON validation.
"""

from enum import Enum

class ErrorCode(Enum):
    """ List of error codes """

    SUCCESS = 0
    INVALID_JSON = 1
    # File errors
    FILE_NOT_FOUND = 2
    FILE_READ_ERROR = 3
    # String errors
    STRING_HEX_ERROR = 4
    STRING_ESCAPE_ERROR = 5
    STRING_EOF_ERROR = 6
    STRING_CHARACTER_ERROR = 7
    # Number errors
    NUMBER_EOF_ERROR = 8
    NUMBER_DIGIT_ERROR = 9
    NUMBER_EXPONENT_ERROR = 10
    NUMBER_LEADING_ZERO_ERROR = 11
    # Value errors
    VALUE_EOF_ERROR = 12
    VALUE_CHARACTER_ERROR = 13
    # Array errors
    ARRAY_EOF_ERROR = 14
    ARRAY_CHARACTER_ERROR = 15
    # Object errors
    OBJECT_EOF_ERROR = 16
    OBJECT_KEY_ERROR = 17
    OBJECT_SEPARATOR_ERROR = 18
    OBJECT_VALUE_ERROR = 19
    OBJECT_CLOSE_ERROR = 20
    # Outside of JSON error
    INVALID_START_ERROR = 21
    EOF_CHARACTER_ERROR = 22

    def __str__(self):
        return f"{self.name}({self.value})"
    def __repr__(self):
        return self.__str__()
class JSONValidatorError(Exception):
    """ Custom exception class providing and interface for JSON validation errors """
    def __init__(self, message: str, error_code: ErrorCode, line: int, column: int):
        """ Initialize the exception class.

        Which sets the exception with error message, error code, line number, and column number

        Args:
            message (str): The error message
            error_code (ErrorCode): The error code
            line (int): The line number
            column (int): The column number
        """
        self.message = message
        self.error_code = error_code
        self.line = line
        self.column = column

    def __str__(self):
        if not self.line and not self.column:
            return f"{self.error_code.name}: {self.message}"
        return f"{self.error_code.name}: {self.message} at line {self.line}, column {self.column}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return (self.error_code == other.error_code and
            self.line == other.line and 
            self.column == other.column)
