"""
    json_validator_cli.py

    A command line interface for validating a given json file.

    Example:
        python json_validator_cli.py valid.json

    Args:
        json_file: The path to the json file to be validated.

    Returns:
        0 if the json file is valid, otherwise the error code of the first
        found error.
"""

import click

from src.json_validator import JsonValidator
from src.json_validator_errors import JSONValidatorError, ErrorCode

# setup click command line interface
@click.command()
# setup click command line argument of json file
@click.argument("json_file")
def main(json_file):
    """
    Command line interface for validating a given json file.

    Args:
        json_file: The path to the json file to be validated.

    Returns:
        0 if the json file is valid, otherwise the error code of the first
        found error.
    """
    # create a json validator object
    validator = JsonValidator()
    try:
        # validate the json file
        validator.validate_json(json_file)
        # print success message
        click.echo("JSON is valid")
        # return 0 for sucess
        return 0
    # catch JSON validation errors, print them, and return the error code for other CLIs
    except JSONValidatorError as e:
        click.echo(f"JSON is invalid with error: {e}", err=True)
        return e.error_code
    # catch any unexcepted errors
    except Exception as e: # pylint: disable=broad-except
        click.echo(f"Unexpected Error, please contact creator or tool: {e}", err=True)
        return ErrorCode.UNRECOGNIZED_ERROR

if __name__ == '__main__':
    main() #pylint: disable=no-value-for-parameter
