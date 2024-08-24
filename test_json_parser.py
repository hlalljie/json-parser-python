# test_json_parser.py
import pytest

from json_parser import open_file, close_file, string, number, value, array, json_object, validate_json

TEST_DATA_PATH = "./test_data/"

def test_string():

    folder = "string/"
    path = TEST_DATA_PATH + folder

    open_file(path + "valid.json")
    assert string(), "regular string is valid"
    close_file()

    open_file(path + "valid2.json")
    assert string(), "string with double backslash is a valid string"
    close_file()

    open_file(path + "valid3.json")
    assert string(), "string with backslash u followed by 4 hex is valid"
    close_file()

    open_file(path + "valid4.json")
    assert string(), "empty string is valid"
    close_file()

    open_file(path + "invalid.json")
    assert not string(), "no closing quote is invalid"
    close_file()

    open_file(path + "invalid2.json")
    assert not string(), "string with only backslash is invalid"
    close_file()

    open_file(path + "invalid3.json")
    assert not string(), "backslash followed by number is not valid"
    close_file()

    open_file(path + "invalid3.json")
    assert not string(), "backslash followed by number is not valid"
    close_file()

    open_file(path + "invalid4.json")
    assert not string(), "backslash u with less than 4 hex is not valid"
    close_file()

    open_file(path + "invalid5.json")
    assert not string(), "string with single quotes is invalid"
    close_file()
  
def test_number():
    folder = "number/"
    path = TEST_DATA_PATH + folder

    open_file(path + "valid.json")
    assert number(), "regular number is valid"
    close_file()

    open_file(path + "valid2.json")
    assert number(), "standard negative number is valid"
    close_file()

    open_file(path + "valid3.json")
    assert number(), "standard decimal is valid"
    close_file()

    open_file(path + "valid4.json")
    assert number(), "0 start decimal is valid"
    close_file()

    open_file(path + "valid5.json")
    assert number(), "negative decimal is valid"
    close_file()

    open_file(path + "valid6.json")
    assert number(), "standard exponent with no signs or decimals is valid"
    close_file()

    open_file(path + "valid7.json")
    assert number(), "0.0e-1 is a valid zero negative decimal exponent"
    close_file()

    open_file(path + "invalid.json")
    assert not number(), "lone minus sign is not valid"
    close_file()

    open_file(path + "invalid2.json")
    assert not number(), "lone period is not valid"
    close_file()

    open_file(path + "invalid2.json")
    assert not number(), "lone period is not valid"
    close_file()

    open_file(path + "invalid3.json")
    assert not number(), "0 followed by digit is not valid"
    close_file()

    open_file(path + "invalid4.json")
    assert not number(), "decimal with no trailing digits is invalid"
    close_file()

    open_file(path + "invalid5.json")
    assert not number(), "decimal with no leading digits is invalid"
    close_file()

    open_file(path + "invalid6.json")
    assert not number(), "exponent by itself is not valid"
    close_file()

    open_file(path + "invalid7.json")
    assert not number(), "exponent sign with no trailing decimals is invalid"
    close_file()

    open_file(path + "valid8.json")
    assert number(), "number followed by a comma is valid as validation for characters after number is covered elsewhere"
    close_file()

def test_value():
    folder = "value/"
    path = TEST_DATA_PATH + folder

    open_file(path + "valid.json")
    assert value(), "true is valid value"
    close_file()

    open_file(path + "valid.json")
    assert value(), "false is valid value"
    close_file()

    open_file(path + "valid.json")
    assert value(), "null is valid value"
    close_file()

    open_file(TEST_DATA_PATH + "number/valid.json")
    assert value(), "number is valid value"
    close_file()

    open_file(TEST_DATA_PATH + "string/valid.json")
    assert value(), "string is valid value"
    close_file()

    open_file(path + "valid4.json")
    assert value(), "whitespace with value is a valid value"
    close_file()

    open_file(path + "valid5.json")
    assert value(), "object is valid value"
    close_file()

    open_file(path + "valid6.json")
    assert value(), "array is valid value"
    close_file()

    open_file(path + "valid7.json")
    assert value(), "value followed by non value is valid as the non value is checked later"
    close_file()

    open_file(path + "invalid.json")
    assert not value(), "word is not a valid value"
    close_file()

    open_file(path + "invalid2.json")
    assert not value(), "tru is not a valid value"
    close_file()

    open_file(path + "invalid3.json")
    assert not value(), "flase is not a valid value"
    close_file()

    open_file(path + "invalid4.json")
    assert not value(), "empty is not a valid value"
    close_file()

    open_file(path + "invalid4.json")
    assert not value(), "string with single quotes is not a valid value"
    close_file()

def test_array():
    folder = "array/"
    path = TEST_DATA_PATH + folder

    open_file(path + "valid.json")
    assert array(), "empty array is a valid array"
    close_file()

    open_file(path + "valid2.json")
    assert array(), "array of 4 numbers with no spaces is a valid array"
    close_file()

    open_file(path + "valid3.json")
    assert array(), "single value is a valid array"
    close_file()

    open_file(path + "valid4.json")
    assert array(), "empty array full of whitespace is a valid array"
    close_file()

    open_file(path + "valid5.json")
    assert array(), "array in an array is a valid array"
    close_file()

    open_file(path + "invalid.json")
    assert not array(), "open bracket with values is not a valid array"
    close_file()

    open_file(path + "invalid2.json")
    assert not array(), "mismatched brackets do not make a valid array"
    close_file()

    open_file(path + "invalid3.json")
    assert not array(), "two commas make a non valid array"
    close_file()

    open_file(path + "invalid4.json")
    assert not array(), "two values next to each other make a non valid array"
    close_file()

    open_file(path + "invalid5.json")
    assert not array(), "array with single quote delimited string is not a valid array"
    close_file()

def test_object():
    folder = "object/"
    path = TEST_DATA_PATH + folder

    open_file(path + "valid.json")
    assert json_object(), "empty object is a valid array"
    close_file()

    open_file(path + "valid2.json")
    assert json_object(), "standard object with one key value pair is valid"
    close_file()

    open_file(path + "valid3.json")
    assert json_object(), "standard object with many spaces is valid"
    close_file()

    open_file(path + "valid4.json")
    assert json_object(), "Nested object with many types is valid"
    close_file()

    open_file(path + "valid5.json")
    assert json_object(), "object with empty string key and empty list value is valid"
    close_file()

    open_file(path + "invalid.json")
    assert not json_object(), "open curly with no closing curly is not valid"
    close_file()

    open_file(path + "invalid2.json")
    assert not json_object(), 'key value pair followed by comma and no other pairs is not value'
    close_file()
    
    open_file(path + "invalid3.json")
    assert not json_object(), 'key value pair with no ":" is not valid'
    close_file()

    open_file(path + "invalid4.json")
    assert not json_object(), 'multiple keys for key value pair not valid'
    close_file()

    open_file(path + "invalid5.json")
    assert not json_object(), 'multiple values for key value pair not valid'
    close_file()

    open_file(path + "invalid6.json")
    assert not json_object(), 'no key in key value pair is not valid'
    close_file()

    open_file(path + "invalid7.json")
    assert not json_object(), 'number as key not valid'
    close_file()

    open_file(path + "invalid8.json")
    assert not json_object(), 'single quote string in array as value is not valid'
    close_file()

    open_file(path + "invalid9.json")
    assert not json_object(), 'single quote string in nested array as value is not valid'
    close_file()


def test_step_1() -> None:
    """ Tests Step 1"""
    
    folder = "step1/"
    path = TEST_DATA_PATH + folder

    filename = path + "invalid.json"
    assert not validate_json(filename), "empty file is not valid json"

    filename = path + "valid.json"
    assert validate_json(filename), "file with only matching curly braces is valid json"

    filename = path + "my_invalid.json"
    assert not validate_json(filename), "unclosed curly brace is not valid json"

    filename = path + "my_invalid2.json"
    assert not validate_json(filename), "closing curly brace without open brace is not valid json"

    filename = path + "my_invalid3.json"
    assert not validate_json(filename), "bracket closed before more recent open curly brace is invalid json"

    filename = path + "my_valid.json"
    assert validate_json(filename), "matching square brackets with whitespace is valid json"

def test_step2() -> None:
    """ Tests Step 2"""
    
    folder = "step2/"
    path = TEST_DATA_PATH + folder

    filename = path + "valid.json"
    assert validate_json(filename), "object with one key value pair is valid"

    filename = path + "valid2.json"
    assert validate_json(filename), "object with two key value pairs is valid"

    filename = path + "invalid.json"
    assert not validate_json(filename), "object with one key value pair followed by comma is invalid"

    filename = path + "invalid2.json"
    assert not validate_json(filename), "object non-string key is not valid"

def test_step3() -> None:
    """ Tests Step 3"""
    folder = "step3/"
    path = TEST_DATA_PATH + folder

    filename = path + "valid.json"
    assert validate_json(filename), "object with bool, null, number, and string values is valid"

    filename = path + "invalid.json"
    assert not validate_json(filename), "object with False as a value is not valid"

def test_step4() -> None:
    """ Tests Step 4"""
    folder = "step4/"
    path = TEST_DATA_PATH + folder

    filename = path + "valid.json"
    assert validate_json(filename), "object with string, number, array, and object values is valid"

    filename = path + "valid2.json"
    assert validate_json(filename), "object with nested object and array is valid"

    filename = path + "invalid.json"
    assert not validate_json(filename), "single quotes for string delimiter is not valid"

