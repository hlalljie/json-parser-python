"""
    test_json_validator.py
    
    This module contains unit tests for the json_parser.py module.
    Included in this testing module are:
        - TestJSONComponents - unit tests for individual JSON components
        - TestJSONChallenges - unit tests for based on the 
          codingchallenges.fyi/challenge-json-parser challenge
        - TestOfficialJsonTests - unit tests for the official json tests from json.org

    These tests are intended to be run with pytest.
"""
# Imports
import warnings
from typing import Generator, Callable
from abc import ABC, abstractmethod
from functools import partial
import pytest
from src.json_validator.json_validator_errors import ErrorCode, JSONValidatorError
from src.json_validator.json_validator import JsonValidator

# Globals
TEST_DATA_PATH = "test/test_data/"

class _TestComponent(ABC):
    """ Abstract base class for JSON components """

    component_name = None # set in child class to the name of the component being tested

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.component_name:
            raise TypeError(f"{cls.__name__} must define a class variable `component_name`.")

    @abstractmethod
    def test_valid(self, setup_validator: Callable[[], None], message: str) -> None:
        """
        Test that valid components are accepted
        
        Parameterized to run all of the valid tests in the test_data/{component_name} directory

        Args:
            setup_validator: a JsonValidator component function passed from the fixture
            message: the message to display on test failure
            
        """
        # Test that valid components throw no errors
        try:
            setup_validator()
        except JSONValidatorError as error_received:
            pytest.fail(f'"{message}" marked invalid with Error: {error_received}')
    @abstractmethod
    def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
    error_spec: JSONValidatorError, check_messages: str) -> None:
        """
        Test that invalid components throw the correct errors
        
        Parameterized to run all of the invalid tests in the 
        test_data/{component_name} directory

        Args:
            setup_validator: a JsonValidator component function passed from the fixture
            fail_message: the message to display if no error is thrown 
            (if the invalid component is marked valid)
            error_spec: the specified JSONValidatorError that should be thrown
            check_messages: whether or not to check the message part of the error, 
            defaults to False. Two modes normal which warns if the spec message is empty, 
            and strict which fails if the spec message is empty

        """
        # check that invalid components do throw errors
        try:
            setup_validator()
            pytest.fail(fail_message + " (was marked valid)")
        # checks all parts of the error code received
        except JSONValidatorError as error_received:
            # Checks error code match
            assert error_received.error_code == error_spec.error_code, (
                f'Specified error {error_spec.error_code}' \
                f' does not match received error code {error_received.error_code}'
            )
            # Checks line number match
            assert error_received.line == error_spec.line, \
                f'Specified line {error_spec.line}' \
                f' does not match received line {error_received.line}'
            # Checks column number match
            assert error_received.column == error_spec.column, \
                f'Specified column {error_spec.column}' \
                f' does not match received column {error_received.column}'
            # Checks message match, if message option is turned on
            if check_messages:
                # If message spec is empty, warn or on 'strict' fail
                if error_spec.message == "":
                    warning = 'Message specification is empty for test'
                    warning += f', received message: "{error_received.message}"'
                    if check_messages == 'strict':
                        pytest.fail(warning)
                    else:
                        warnings.warn(warning)
                else:
                    assert error_received.message == error_spec.message, (
                        f'Specified message "{error_spec.message}" '
                        f' does not match received message "{error_received.message}"'
                    )

class TestJSONComponents:
    """ Unit tests for individual JSON parsing components 
    
    Tests for String, Number, Boolean, Null, Array, and Object

    """
    @pytest.fixture
    def setup_validator(self, request: pytest.FixtureRequest) \
        -> Generator[Callable[[], None], None, None]:
        """
        Create a JsonValidator instance, open the test file, and setup the method for testing. 
        Passes the method to the test function. 
        Close the file after the test is complete.
        
        Args:
            request: the request object passed to the test function
        
        Yields:
            The callable method based on the given test function
        """

        # get component name
        component_name = request.cls.component_name

        # instantiate validator and open given file
        folder = f"{TEST_DATA_PATH}{component_name}/"
        filename = request.param
        filepath = folder + filename
        validator = JsonValidator()
        validator.open_file(filepath)

        # get method for testing given component
        method_name = f"_{component_name}"
        method = getattr(validator, method_name)

        # pass method to tests
        yield method

        # close file
        validator.close_file()

    class TestString(_TestComponent):
        """ Unit tests for the _string functional component """

        component_name = "string"

        @pytest.mark.parametrize("setup_validator, message", [
            ("valid.json", "regular string is valid"),
            ("valid2.json", "string with double backslash is a valid string"),
            ("valid3.json", "string with backslash u followed by 4 hex is valid"),
            ("valid4.json", "empty string is valid"),
            ("valid5.json", "string with multiple hex escapes is valid"),
            ("valid5.json", "characters after full hex is valid"),
        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator: Callable[[], None], message: str) -> None:
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec",[

            ("invalid.json", "no closing quote is invalid",
                JSONValidatorError("file ended in middle of string",
                    ErrorCode.STRING_EOF_ERROR, line=1, column=11)),

            ("invalid2.json", "string with only backslash is invalid",
                JSONValidatorError("file ended in middle of string",
                    ErrorCode.STRING_EOF_ERROR, line=1, column=4)),

            ("invalid3.json", "backslash followed by number is not valid",
                JSONValidatorError("invalid escape character in string",
                    ErrorCode.STRING_ESCAPE_ERROR, line=1, column=3)),

            ("invalid4.json",
                "backslash u with less than 4 hex is not valid",
                JSONValidatorError("invalid hex digit after \\u in string",
                    ErrorCode.STRING_HEX_ERROR, line=1, column=13)),

            ("invalid5.json", "string with single quotes is invalid",
                JSONValidatorError("file ended in middle of string",
                    ErrorCode.STRING_EOF_ERROR, line=1, column=9)),

        ], indirect=["setup_validator"])

        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
        error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestNumber(_TestComponent):

        component_name = "number"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "regular number is valid"),
            ("valid2.json", "standard negative number is valid"),
            ("valid3.json", "standard decimal is valid"),
            ("valid4.json", "0 start decimal is valid"),
            ("valid5.json", "negative decimal is valid"),
            ("valid6.json", "standard exponent with no signs or decimals is valid"),
            ("valid7.json", "0.0e-1 is a valid zero negative decimal exponent"),
            ("valid8.json", "number followed by a comma is valid as validation for " \
                "characters after number is covered elsewhere"),

        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "lone minus sign is not valid",
                JSONValidatorError("file ended in middle of number",
                    ErrorCode.NUMBER_EOF_ERROR, line=1, column=2)),

            ("invalid2.json", "lone period is not valid",
                JSONValidatorError("",
                    ErrorCode.NUMBER_DIGIT_ERROR, line=1, column=1)),

            ("invalid3.json", "0 followed by digit is not valid",
                JSONValidatorError("",
                    ErrorCode.NUMBER_LEADING_ZERO_ERROR, line=1, column=2)),

            ("invalid4.json", "decimal with no trailing digits is invalid",
                JSONValidatorError("",
                    ErrorCode.NUMBER_DIGIT_ERROR, line=1, column=5)),

            ("invalid5.json", "decimal with no leading digits is invalid",
                JSONValidatorError("",
                    ErrorCode.NUMBER_DIGIT_ERROR, line=1, column=1)),

            ("invalid6.json", "exponent by itself is not valid",
                JSONValidatorError("file ended in middle of number",
                    ErrorCode.NUMBER_DIGIT_ERROR, line=1, column=1)),

            ("invalid7.json", "exponent sign with no trailing decimals is invalid",
                JSONValidatorError("file ended in middle of number",
                    ErrorCode.NUMBER_EXPONENT_ERROR, line=1, column=11)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator, fail_message, error_spec, check_messages) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestValue(_TestComponent):

        component_name = "value"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "true is valid value"),
            ("valid2.json", "false is valid value"),
            ("valid3.json", "null is valid value"),
            ("valid4.json", "whitespace with value is a valid value"),
            ("valid5.json", "object is valid value"),
            ("valid6.json", "array is valid value"),
            ("valid7.json", "value followed by non value is valid as the non value is checked later"),
            ("valid8.json", "string is valid value"),
            ("valid9.json", "number is valid value"),
        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "word is not a valid value",
                JSONValidatorError("",
                    ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=1)),

            ("invalid2.json", "tru is not a valid value",
                JSONValidatorError("",
                    ErrorCode.VALUE_EOF_ERROR, line=1, column=4)),

            ("invalid3.json", "flase is not a valid value",
                JSONValidatorError("",
                    ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=2)),

            ("invalid4.json", "empty is not a valid value",
                JSONValidatorError("",
                    ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=1)),

            ("invalid5.json", "string with single quotes is not a valid value",
                JSONValidatorError("",
                    ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=1)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
        error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestArray(_TestComponent):

        component_name = "array"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "empty array is a valid array"),
            ("valid2.json", "array of 4 numbers with no spaces is a valid array"),
            ("valid3.json", "single value is a valid array"),
            ("valid4.json", "empty array full of whitespace is a valid array"),
            ("valid5.json", "array in an array is a valid array"),
        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "open bracket with values is not a valid array",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=9)),

            ("invalid2.json", "mismatched brackets do not make a valid array",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=4)),

            ("invalid3.json", "two commas make a non valid array",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=5)),

            ("invalid4.json", "two values next to each other make a non valid array",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=4)),

            ("invalid5.json", "array with single quote delimited string is not a valid array",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=2)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
        error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestObject(_TestComponent):

        component_name = "json_object"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "empty object is a valid object"),
            ("valid2.json", "standard object with one key value pair is valid"),
            ("valid3.json", "standard object with many spaces is valid"),
            ("valid4.json", "Nested object with many types is valid"),
            ("valid5.json", "object with empty string key and empty list value is valid"),
        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "open curly with no closing curly is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_CLOSE_ERROR, line=1, column=14)),

            ("invalid2.json", "key value pair followed by comma and no other pairs is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=18)),

            ("invalid3.json", 'key value pair with no ":" is not valid',
                JSONValidatorError("", ErrorCode.OBJECT_SEPARATOR_ERROR, line=1, column=10)),

            ("invalid4.json", "multiple keys for key value pair not valid",
                JSONValidatorError("", ErrorCode.OBJECT_SEPARATOR_ERROR, line=1, column=9)),

            ("invalid5.json", "multiple values for key value pair not valid",
                JSONValidatorError("", ErrorCode.OBJECT_CLOSE_ERROR, line=1, column=16)),

            ("invalid6.json", "no key in key value pair is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_SEPARATOR_ERROR, line=1, column=25)),

            ("invalid7.json", "number as key not valid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=3)),

            ("invalid8.json", "single quote string in array as value is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=10)),

            ("invalid9.json", "single quote string in nested array as value is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=5, column=15)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
        error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

class TestOfficialCases:
    @pytest.fixture
    def setup_validator(self, request: pytest.FixtureRequest) \
        -> Generator[Callable[[], None], None, None]:
        """
        Create a JsonValidator instance.
        Create a partial function with the validate_json method and the filename. 
        Passes the method to the test function.
        
        Args:
            request: the request object passed to the test function
        
        Returns:
            Generator[Callable[[], None], None, None]: The callable method 
            based on the given test function
        """
        # get component name
        folder_name = request.cls.component_name

        # instantiate validator and open given file
        folder = f"{TEST_DATA_PATH}{folder_name}/"
        filename = request.param
        filepath = folder + filename
        validator = JsonValidator()

        # get method for testing given component
        method = partial(validator.validate_json, filepath)

        # pass method to tests
        return method
    class TestStep1(_TestComponent):

        component_name = "step1"
        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "file with only matching curly braces is valid json"),
            ("my_valid.json", "matching square brackets with whitespace is valid json"),
            ], indirect=["setup_validator"]
        )
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [
            ("invalid.json", "empty file is not valid json",
                JSONValidatorError("", ErrorCode.INVALID_START_ERROR, line=1, column=1)),

            ("my_invalid.json", "unclosed curly brace is not valid json",
                JSONValidatorError("", ErrorCode.OBJECT_EOF_ERROR, line=1, column=2)),

            ("my_invalid2.json", "closing curly brace without open brace is not valid json",
                JSONValidatorError("", ErrorCode.INVALID_START_ERROR, line=1, column=1)), 

            ("my_invalid3.json", "bracket closed before more recent open curly brace is invalid json",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=3))

            ],indirect=["setup_validator"]
        )
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
        error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestStep2(_TestComponent):
        component_name = "step2"
        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "object with one key value pair is valid"),
            ("valid2.json", "object with two key value pairs is valid"),
            ], indirect=["setup_validator"]
        )
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)
        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [
            ("invalid.json", "object with one key value pair followed by comma is invalid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=17)),

            ("invalid2.json", "object non-string key is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=3, column=3))

            ], indirect=["setup_validator"]
        )
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
            error_spec: JSONValidatorError, check_messages: str) -> None:
                super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestStep3(_TestComponent):
        component_name = "step3"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "object with bool, null, number, and string values is valid"),
            ], indirect=["setup_validator"]
        )
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)
        
        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "object with False as a value is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=3, column=11)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
            error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestStep4(_TestComponent):
        component_name = "step4"

        @pytest.mark.parametrize("setup_validator,message", [
            ("valid.json", "object with string, number, array, and object values is valid"),
            ("valid2.json", "object with nested object and array is valid"),
            ], indirect=["setup_validator"]
        )
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)
        
        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [

            ("invalid.json", "single quotes for string delimiter is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=7, column=13)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
            error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)

    class TestOfficialJSONTests(_TestComponent):

        component_name = "official_tests"

        @pytest.mark.parametrize("setup_validator,message", [
            ("pass1.json", "complex json is valid"),
            ("pass2.json", "heavily nested array is valid"),
            ("pass3.json", "standard nested json is valid"),
        ], indirect=["setup_validator"])
        def test_valid(self, setup_validator, message):
            super().test_valid(setup_validator, message)

        @pytest.mark.parametrize("setup_validator,fail_message,error_spec", [
            
            ("fail1.json", "A JSON payload should be an object or array, not a string.",
                JSONValidatorError("", ErrorCode.INVALID_START_ERROR, line=1, column=1)),

            ("fail2.json", "Unclosed array is not valid",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=18)),

            ("fail3.json", "unquoted key is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=2)),

            ("fail4.json", "Extra comma after value in array is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=16)),

            ("fail5.json", "double extra comma after value in array is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=23)),

            ("fail6.json", "missing value before array is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=5)),

            ("fail7.json", "comma after closing array is not valid",
                JSONValidatorError("", ErrorCode.EOF_CHARACTER_ERROR, line=1, column=26)),

            ("fail8.json", "extra closing bracket is not valid",
                JSONValidatorError("", ErrorCode.EOF_CHARACTER_ERROR, line=1, column=16)),

            ("fail9.json", "comma after bool value with following key value pair is valid",
                JSONValidatorError("", ErrorCode.OBJECT_KEY_ERROR, line=1, column=22)),

            ("fail10.json", "quoted value after close is not valid",
                JSONValidatorError("", ErrorCode.EOF_CHARACTER_ERROR, line=1, column=35)),

            ("fail11.json", "expression as value is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_CLOSE_ERROR, line=1, column=26)),

            ("fail12.json", "function as value is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=24)),

            ("fail13.json", "number with leading zero is not valid",
                JSONValidatorError("", ErrorCode.NUMBER_LEADING_ZERO_ERROR, line=1, column=41)),

            ("fail14.json", "hex number value is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_CLOSE_ERROR, line=1, column=28)),

            ("fail15.json", "backslash x in string is not valid",
                JSONValidatorError("", ErrorCode.STRING_ESCAPE_ERROR, line=1, column=30)),

            ("fail16.json", "backslash naked value is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=2)),

            ("fail17.json", "backslash 0 is not valid",
                JSONValidatorError("", ErrorCode.STRING_ESCAPE_ERROR, line=1, column=30)),

            # fail18.json skipped, no supporting documentation for max nested of arrays

            ("fail19.json", 'missing ":" in key value pair is not valid',
                JSONValidatorError("", ErrorCode.OBJECT_SEPARATOR_ERROR, line=1, column=18)),

            ("fail20.json", "double colon is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=17)),

            ("fail21.json", "comma instead of colon not valid",
                JSONValidatorError("", ErrorCode.OBJECT_SEPARATOR_ERROR, line=1, column=26)),

            ("fail22.json", "colon instead of comma not valid",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=26)),

            ("fail23.json", "truth is not valid value",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=18)),

            ("fail24.json", "single quote for array is not valid",
                JSONValidatorError("", ErrorCode.VALUE_CHARACTER_ERROR, line=1, column=2)),

            ("fail25.json", "tab character in string is not valid",
                JSONValidatorError("", ErrorCode.STRING_CHARACTER_ERROR, line=1, column=3)),

            ("fail26.json", "backslash tab character in string is not valid",
                JSONValidatorError("", ErrorCode.STRING_ESCAPE_ERROR, line=1, column=7)),

            ("fail27.json", "newline character in string is not valid",
                JSONValidatorError("", ErrorCode.STRING_CHARACTER_ERROR, line=1, column=7)),

            ("fail28.json", "backslash line break in string is not valid",
                JSONValidatorError("", ErrorCode.STRING_ESCAPE_ERROR, line=1, column=8)),

            ("fail29.json", "number with empty exponent value is not valid",
                JSONValidatorError("", ErrorCode.NUMBER_EXPONENT_ERROR, line=1, column=4)),

            ("fail30.json", "number with empty positive exponent is not valid",
                JSONValidatorError("", ErrorCode.NUMBER_EXPONENT_ERROR, line=1, column=5)),

            ("fail31.json", "number with positive and negative exponent is not valid",
                JSONValidatorError("", ErrorCode.NUMBER_EXPONENT_ERROR, line=1, column=5)),

            ("fail32.json", "comma instead of closing brace is not valid",
                JSONValidatorError("", ErrorCode.OBJECT_EOF_ERROR, line=1, column=41)),

            ("fail33.json", "mismatched bracket with brace is not valid",
                JSONValidatorError("", ErrorCode.ARRAY_CHARACTER_ERROR, line=1, column=12)),

        ], indirect=["setup_validator"])
        def test_invalid(self, setup_validator: Callable[[], None], fail_message: str,
            error_spec: JSONValidatorError, check_messages: str) -> None:
            super().test_invalid(setup_validator, fail_message, error_spec, check_messages)