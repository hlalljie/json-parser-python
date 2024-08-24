# test_json_parser.py
import pytest

from json_parser import open_file, close_file, string, number, value, array, json_object, validate_json

TEST_DATA_PATH = "./test_data/"

class TestJSONComponents:
    @pytest.fixture
    def json_file(self, request):
        filename = request.param
        open_file(filename)
        yield filename
        close_file()

    class TestString:
        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}string/valid.json", "regular string is valid"),
            (f"{TEST_DATA_PATH}string/valid2.json", "string with double backslash is a valid string"),
            (f"{TEST_DATA_PATH}string/valid3.json", "string with backslash u followed by 4 hex is valid"),
            (f"{TEST_DATA_PATH}string/valid4.json", "empty string is valid"),
        ], indirect=["json_file"])
        def test_valid_strings(self, json_file, message):
            assert string(), message

        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}string/invalid.json", "no closing quote is invalid"),
            (f"{TEST_DATA_PATH}string/invalid2.json", "string with only backslash is invalid"),
            (f"{TEST_DATA_PATH}string/invalid3.json", "backslash followed by number is not valid"),
            (f"{TEST_DATA_PATH}string/invalid4.json", "backslash u with less than 4 hex is not valid"),
            (f"{TEST_DATA_PATH}string/invalid5.json", "string with single quotes is invalid"),
        ], indirect=["json_file"])
        def test_invalid_strings(self, json_file, message):
            assert not string(), message
            
    class TestNumber: 
        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}number/valid.json", "regular number is valid"),
            (f"{TEST_DATA_PATH}number/valid2.json", "standard negative number is valid"),
            (f"{TEST_DATA_PATH}number/valid3.json", "standard decimal is valid"),
            (f"{TEST_DATA_PATH}number/valid4.json", "0 start decimal is valid"),
            (f"{TEST_DATA_PATH}number/valid5.json", "negative decimal is valid"),
            (f"{TEST_DATA_PATH}number/valid6.json", "standard exponent with no signs or decimals is valid"),
            (f"{TEST_DATA_PATH}number/valid7.json", "0.0e-1 is a valid zero negative decimal exponent"),
            (f"{TEST_DATA_PATH}number/valid8.json", "number followed by a comma is valid as validation for characters after number is covered elsewhere"),
        ], indirect=["json_file"])
        def test_valid_numbers(self, json_file, message):
            assert number(), message

        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}number/invalid.json", "lone minus sign is not valid"),
            (f"{TEST_DATA_PATH}number/invalid2.json", "lone period is not valid"),
            (f"{TEST_DATA_PATH}number/invalid3.json", "0 followed by digit is not valid"),
            (f"{TEST_DATA_PATH}number/invalid4.json", "decimal with no trailing digits is invalid"),
            (f"{TEST_DATA_PATH}number/invalid5.json", "decimal with no leading digits is invalid"),
            (f"{TEST_DATA_PATH}number/invalid6.json", "exponent by itself is not valid"),
            (f"{TEST_DATA_PATH}number/invalid7.json", "exponent sign with no trailing decimals is invalid"),
        ], indirect=["json_file"])
        def test_invalid_numbers(self, json_file, message):
            assert not number(), message

    class TestValue:
        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}value/valid.json", "true is valid value"),
            (f"{TEST_DATA_PATH}value/valid.json", "false is valid value"),
            (f"{TEST_DATA_PATH}value/valid.json", "null is valid value"),
            (f"{TEST_DATA_PATH}number/valid.json", "number is valid value"),
            (f"{TEST_DATA_PATH}string/valid.json", "string is valid value"),
            (f"{TEST_DATA_PATH}value/valid4.json", "whitespace with value is a valid value"),
            (f"{TEST_DATA_PATH}value/valid5.json", "object is valid value"),
            (f"{TEST_DATA_PATH}value/valid6.json", "array is valid value"),
            (f"{TEST_DATA_PATH}value/valid7.json", "value followed by non value is valid as the non value is checked later"),
        ], indirect=["json_file"])
        def test_valid_values(self, json_file, message):
            assert value(), message

        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}value/invalid.json", "word is not a valid value"),
            (f"{TEST_DATA_PATH}value/invalid2.json", "tru is not a valid value"),
            (f"{TEST_DATA_PATH}value/invalid3.json", "flase is not a valid value"),
            (f"{TEST_DATA_PATH}value/invalid4.json", "empty is not a valid value"),
            (f"{TEST_DATA_PATH}value/invalid4.json", "string with single quotes is not a valid value"),
        ], indirect=["json_file"])
        def test_invalid_values(self, json_file, message):
            assert not value(), message

    class TestArray:
        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}array/valid.json", "empty array is a valid array"),
            (f"{TEST_DATA_PATH}array/valid2.json", "array of 4 numbers with no spaces is a valid array"),
            (f"{TEST_DATA_PATH}array/valid3.json", "single value is a valid array"),
            (f"{TEST_DATA_PATH}array/valid4.json", "empty array full of whitespace is a valid array"),
            (f"{TEST_DATA_PATH}array/valid5.json", "array in an array is a valid array"),
        ], indirect=["json_file"])
        def test_valid_arrays(self, json_file, message):
            assert array(), message

        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}array/invalid.json", "open bracket with values is not a valid array"),
            (f"{TEST_DATA_PATH}array/invalid2.json", "mismatched brackets do not make a valid array"),
            (f"{TEST_DATA_PATH}array/invalid3.json", "two commas make a non valid array"),
            (f"{TEST_DATA_PATH}array/invalid4.json", "two values next to each other make a non valid array"),
            (f"{TEST_DATA_PATH}array/invalid5.json", "array with single quote delimited string is not a valid array"),
        ], indirect=["json_file"])
        def test_invalid_arrays(self, json_file, message):
            assert not array(), message

    class TestObject:
        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}object/valid.json", "empty object is a valid object"),
            (f"{TEST_DATA_PATH}object/valid2.json", "standard object with one key value pair is valid"),
            (f"{TEST_DATA_PATH}object/valid3.json", "standard object with many spaces is valid"),
            (f"{TEST_DATA_PATH}object/valid4.json", "Nested object with many types is valid"),
            (f"{TEST_DATA_PATH}object/valid5.json", "object with empty string key and empty list value is valid"),
        ], indirect=["json_file"])
        def test_valid_objects(self, json_file, message):
            assert json_object(), message

        @pytest.mark.parametrize("json_file,message", [
            (f"{TEST_DATA_PATH}object/invalid.json", "open curly with no closing curly is not valid"),
            (f"{TEST_DATA_PATH}object/invalid2.json", "key value pair followed by comma and no other pairs is not valid"),
            (f"{TEST_DATA_PATH}object/invalid3.json", 'key value pair with no ":" is not valid'),
            (f"{TEST_DATA_PATH}object/invalid4.json", "multiple keys for key value pair not valid"),
            (f"{TEST_DATA_PATH}object/invalid5.json", "multiple values for key value pair not valid"),
            (f"{TEST_DATA_PATH}object/invalid6.json", "no key in key value pair is not valid"),
            (f"{TEST_DATA_PATH}object/invalid7.json", "number as key not valid"),
            (f"{TEST_DATA_PATH}object/invalid8.json", "single quote string in array as value is not valid"),
            (f"{TEST_DATA_PATH}object/invalid9.json", "single quote string in nested array as value is not valid"),
        ], indirect=["json_file"])
        def test_invalid_objects(self, json_file, message):
            assert not json_object(), message

class TestJSONChallenges:
    @pytest.mark.parametrize("filename,expected,message", [
        ("step1/invalid.json", False, "empty file is not valid json"),
        ("step1/valid.json", True, "file with only matching curly braces is valid json"),
        ("step1/my_invalid.json", False, "unclosed curly brace is not valid json"),
        ("step1/my_invalid2.json", False, "closing curly brace without open brace is not valid json"),
        ("step1/my_invalid3.json", False, "bracket closed before more recent open curly brace is invalid json"),
        ("step1/my_valid.json", True, "matching square brackets with whitespace is valid json"),
    ])
    def test_step1(self, filename, expected, message):
        assert validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

    @pytest.mark.parametrize("filename,expected,message", [
        ("step2/valid.json", True, "object with one key value pair is valid"),
        ("step2/valid2.json", True, "object with two key value pairs is valid"),
        ("step2/invalid.json", False, "object with one key value pair followed by comma is invalid"),
        ("step2/invalid2.json", False, "object non-string key is not valid"),
    ])
    def test_step2(self, filename, expected, message):
        assert validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

    @pytest.mark.parametrize("filename,expected,message", [
        ("step3/valid.json", True, "object with bool, null, number, and string values is valid"),
        ("step3/invalid.json", False, "object with False as a value is not valid"),
    ])
    def test_step3(self, filename, expected, message):
        assert validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

    @pytest.mark.parametrize("filename,expected,message", [
        ("step4/valid.json", True, "object with string, number, array, and object values is valid"),
        ("step4/valid2.json", True, "object with nested object and array is valid"),
        ("step4/invalid.json", False, "single quotes for string delimiter is not valid"),
    ])
    def test_step4(self, filename, expected, message):
        assert validate_json(f"{TEST_DATA_PATH}{filename}") == expected, message

class TestOfficialJSONTests:
    @pytest.mark.parametrize("filename,expected,message", [
        ("fail1.json", False, "A JSON payload should be an object or array, not a string."),
        ("fail2.json", False, "Unclosed array is not valid"),
        ("fail3.json", False, "unquoted key is not valid"),
        ("fail4.json", False, "Extra comma after value in array is not valid"),
        ("fail5.json", False, "double extra comma after value in array is not valid"),
        ("fail6.json", False, "missing value before array is not valid"),
        ("fail7.json", False, "comma after closing array is not valid"),
        ("fail8.json", False, "extra closing bracket is not valid"),
        ("fail9.json", False, "comma after bool value with following key value pair is valid"),
        ("fail10.json", False, "quoted value after close is not valid"),
        ("fail11.json", False, "expression as value is not valid"),
        ("fail12.json", False, "function as value is not valid"),
        ("fail13.json", False, "number with leading zero is not valid"),
        ("fail14.json", False, "hex number value is not valid"),
        ("fail15.json", False, "backslash x in string is not valid"),
        ("fail16.json", False, "backslash naked value is not valid"),
        ("fail17.json", False, "backslash 0 is not valid"),
        ("fail19.json", False, 'missing ":" in key value pair is not valid'),
        ("fail20.json", False, "double colon is not valid"),
        ("fail21.json", False, "comma instead of colon not valid"),
        ("fail22.json", False, "colon instead of comma not valid"),
        ("fail23.json", False, "truth is not valid value"),
        ("fail24.json", False, "single quote for array is not valid"),
        ("fail26.json", False, "backslash tab character in string is not valid"),
        ("fail28.json", False, "backslash linebreak in string is not valid"),
        ("fail29.json", False, "number with empty exponent value is not valid"),
        ("fail30.json", False, "number with empty positive exponent is not valid"),
        ("fail31.json", False, "number with positive and negative exponent is not valid"),
        ("fail32.json", False, "comma instead of closing brace is not valid"),
        ("fail33.json", False, "mismatched bracket with brace is not valid"),
        ("pass2.json", True, "heavily nested array is valid"),
        ("pass3.json", True, "standard nested json is valid"),
    ])
    def test_official_json_tests(self, filename, expected, message):
        assert validate_json(f"{TEST_DATA_PATH}official_tests/{filename}") == expected, message

    # TODO: Implement these tests when ready
    @pytest.mark.skip(reason="No official documentation supporting this test")
    def test_fail18(self):
        # Test for array depth of 20 not valid
        pass

    @pytest.mark.skip(reason="Need to implement tab handling in strings")
    def test_fail25(self):
        # Test for tab character in string is not valid
        pass

    @pytest.mark.skip(reason="Need to handle line break handling in strings")
    def test_fail27(self):
        # Test for line break character in string is not valid
        pass

    @pytest.mark.skip(reason="Not yet implemented, need to find issues with this large test")
    def test_pass1(self):
        # Test for complex json is valid (pass1)
        pass