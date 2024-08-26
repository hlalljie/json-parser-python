"""
    test_json_parser.py
    
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
import pytest
from json_parser_errors import ErrorCode, JSONValidatorError
from json_parser import JsonValidator

# Globals
TEST_DATA_PATH = "./test_data/"

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
        folder = f"{TEST_DATA_PATH}/{component_name}/"
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
            except JSONValidatorError:
                pytest.fail(message)
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

    class TestString(_TestComponent):
        """ Unit tests for the _string functional component """

        component_name = "string"

        @pytest.mark.parametrize("setup_validator, message", [
            ("valid.json", "regular string is valid"),
            ("valid2.json", "string with double backslash is a valid string"),
            ("valid3.json", "string with backslash u followed by 4 hex is valid"),
            ("valid4.json", "empty string is valid"),
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
# class TestJSONChallenges:

#     @pytest.fixture
#     def setup_validator(self, request):
#         validator = JsonValidator()
#         return validator

#     @pytest.mark.parametrize("filename,expected,message", [
#         ("step1/invalid.json", False, "empty file is not valid json"),
#         ("step1/valid.json", True, "file with only matching curly braces is valid json"),
#         ("step1/my_invalid.json", False, "unclosed curly brace is not valid json"),
#         ("step1/my_invalid2.json", False, "closing curly brace without open brace is not valid json"),
#         ("step1/my_invalid3.json", False, "bracket closed before more recent open curly brace is invalid json"),
#         ("step1/my_valid.json", True, "matching square brackets with whitespace is valid json"),
#         ]
#     )
#     def test_step1(self, setup_validator, filename, expected, message):
#         assert setup_validator.validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

#     @pytest.mark.parametrize("filename,expected,message", [
#         ("step2/valid.json", True, "object with one key value pair is valid"),
#         ("step2/valid2.json", True, "object with two key value pairs is valid"),
#         ("step2/invalid.json", False, "object with one key value pair followed by comma is invalid"),
#         ("step2/invalid2.json", False, "object non-string key is not valid")
#         ]
#     )
#     def test_step2(self, setup_validator, filename, expected, message):
#         assert setup_validator.validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

#     @pytest.mark.parametrize("filename,expected,message", [
#         ("step3/valid.json", True, "object with bool, null, number, and string values is valid"),
#         ("step3/invalid.json", False, "object with False as a value is not valid")
#         ]
#     )
#     def test_step3(self, setup_validator, filename, expected, message):
#         assert setup_validator.validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

#     @pytest.mark.parametrize("filename,expected,message", [
#         ("step4/valid.json", True, "object with string, number, array, and object values is valid"),
#         ("step4/valid2.json", True, "object with nested object and array is valid"),
#         ("step4/invalid.json", False, "single quotes for string delimiter is not valid")
#         ]
#     )
#     def test_step4(self, setup_validator, filename, expected, message):
#         assert setup_validator.validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

# class TestOfficialJSONTests:

    # @pytest.fixture
    # def setup_validator(self, request):
    #     validator = JsonValidator()
    #     return validator

    # @pytest.mark.parametrize("filename,expected,message", [
    #     ("fail1.json", False, "A JSON payload should be an object or array, not a string."),
    #     ("fail2.json", False, "Unclosed array is not valid"),
    #     ("fail3.json", False, "unquoted key is not valid"),
    #     ("fail4.json", False, "Extra comma after value in array is not valid"),
    #     ("fail5.json", False, "double extra comma after value in array is not valid"),
    #     ("fail6.json", False, "missing value before array is not valid"),
    #     ("fail7.json", False, "comma after closing array is not valid"),
    #     ("fail8.json", False, "extra closing bracket is not valid"),
    #     ("fail9.json", False, "comma after bool value with following key value pair is valid"),
    #     ("fail10.json", False, "quoted value after close is not valid"),
    #     ("fail11.json", False, "expression as value is not valid"),
    #     ("fail12.json", False, "function as value is not valid"),
    #     ("fail13.json", False, "number with leading zero is not valid"),
    #     ("fail14.json", False, "hex number value is not valid"),
    #     ("fail15.json", False, "backslash x in string is not valid"),
    #     ("fail16.json", False, "backslash naked value is not valid"),
    #     ("fail17.json", False, "backslash 0 is not valid"),
    #     ("fail19.json", False, 'missing ":" in key value pair is not valid'),
    #     ("fail20.json", False, "double colon is not valid"),
    #     ("fail21.json", False, "comma instead of colon not valid"),
    #     ("fail22.json", False, "colon instead of comma not valid"),
    #     ("fail23.json", False, "truth is not valid value"),
    #     ("fail24.json", False, "single quote for array is not valid"),
    #     ("fail26.json", False, "backslash tab character in string is not valid"),
    #     ("fail28.json", False, "backslash linebreak in string is not valid"),
    #     ("fail29.json", False, "number with empty exponent value is not valid"),
    #     ("fail30.json", False, "number with empty positive exponent is not valid"),
    #     ("fail31.json", False, "number with positive and negative exponent is not valid"),
    #     ("fail32.json", False, "comma instead of closing brace is not valid"),
    #     ("fail33.json", False, "mismatched bracket with brace is not valid"),
    #     ("pass2.json", True, "heavily nested array is valid"),
    #     ("pass3.json", True, "standard nested json is valid"),
    # ])
    # def test_official_json_tests(self, setup_validator, filename, expected, message):
    #     assert setup_validator.validate_json(f"{TEST_DATA_PATH}official_tests/{filename}") == expected, message

    # # TODO: Implement these tests when ready
    # @pytest.mark.skip(reason="No official documentation supporting this test")
    # def test_fail18(self):
    #     # Test for array depth of 20 not valid
    #     pass

    # @pytest.mark.skip(reason="Need to implement tab handling in strings")
    # def test_fail25(self):
    #     # Test for tab character in string is not valid
    #     pass

    # @pytest.mark.skip(reason="Need to handle line break handling in strings")
    # def test_fail27(self):
    #     # Test for line break character in string is not valid
    #     pass

    # @pytest.mark.skip(reason="Not yet implemented, need to find issues with this large test")
    # def test_pass1(self):
    #     # Test for complex json is valid (pass1)
    #     pass