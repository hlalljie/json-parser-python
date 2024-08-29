"""
    test_cli.py
    
    This module contains unit tests for the json_validator_cli.py module.
    Included in this testing module are:
        - TestCli - unit tests for the json_validator_cli.py module

    These tests are intended to be run with pytest.

"""

# Imports
import pytest
from click.testing import CliRunner
from src.json_validator.json_validator_cli import cli
from src.json_validator.json_validator_errors import ErrorCode

class TestCli:

    """
        TestCli - unit tests for the json_validator_cli.py module

        Included in this testing module are:
            - TestFileErrors - unit tests for the json_validator_cli.py module

        These tests are intended to be run with pytest.

    """

    # File path of test files
    test_path = "test/test_data/file/"

    # Sets up the CliRunner to test the cli click module
    @pytest.fixture
    def runner(self):
        """ Sets up the CliRunner to test the cli click module
        
        Returns:
            CliRunner: Runs the python module as if it were a cli tool
        """
        return CliRunner()

    # Parameters for file test cases
    @pytest.mark.parametrize("filename, error_code, fail_message", [
        ("valid.json", ErrorCode.SUCCESS, "valid json marked as invalid with error"),
        ("invalid.json", ErrorCode.OBJECT_KEY_ERROR, "invalid json returned incorrect result"),
        ("no_file.json", ErrorCode.FILE_NOT_FOUND, "file not found returned incorrect result"),
        ("non_json.txt", ErrorCode.FILE_TYPE_ERROR, "non json file returned incorrect result"),
        ("", ErrorCode.FILE_MISSING_ERROR, "missing file returned incorrect result"),
    ])

    # Unit test for file errors
    def test_file_errors(self, runner: CliRunner, filename: str,
    error_code: ErrorCode, fail_message: str) -> None:
        """ Unit test for file errors 
        
        Args:
            runner (CliRunner): Runs the python module as if it were a cli tool 
            filename (str): The name of the file to test
            error_code (ErrorCode): The expected error code
            fail_message (str): The message to display if the test fails  
        """
        # create a file path from the filename and the path to the file
        file_path = str(self.test_path) + filename
        # run the cli with the file path
        result = runner.invoke(cli, [file_path])
        # check that the error code matches th expected error code
        assert result.exit_code == error_code.value, \
        f'{fail_message}: {ErrorCode(result.exit_code)}'
