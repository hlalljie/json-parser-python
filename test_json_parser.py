# test_json_parser.py
import pytest

from json_parser import open_file, close_file, string

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
    


# def test_step_1() -> None:
#     """ Tests step 1 of validating json checking that no output
#       is not valid and matched curly braces are valid"""
#     folder = "step1/"
#     path = TEST_DATA_PATH + folder
#     filename = path + "invalid.json"
#     assert not validate_json(filename), "empty file is not valid json"
#     filename = path + "valid.json"
#     assert validate_json(filename), "file with only matching parentheses is valid json"
#     filename = path + "my_invalid.json"
#     assert not validate_json(filename), "unclosed curly brace is not valid json"
#     filename = path + "my_invalid2.json"
#     assert not validate_json(filename), "closing curly brace without open brace is not valid json"
#     filename = path + "my_invalid3.json"
#     assert not validate_json(filename), "bracket closed before more recent open curly brace is invalid json"
#     filename = path + "my_valid.json"
#     assert validate_json(filename), "matching square brackets with whitespace is valid json"
    
    
