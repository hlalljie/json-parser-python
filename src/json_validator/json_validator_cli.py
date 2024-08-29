"""
    json_validator_cli.py

    A command line interface for validating a given json file.

    Example:
        python json_validator_cli.py valid.json

    Args:
        json_file (str): The path to the json file to be validated.

    Returns:
        error_code (int): 0 if the json file is valid, otherwise the error code of the first found error.
"""
import click

from .json_validator_errors import JSONValidatorError, ErrorCode
from .json_validator import JsonValidator

class CustomClickException(click.ClickException):
    """ A custom click exception for JSON validation errors. 
    
    Throws a command line available error code with an optional error message"""
    def __init__(self, error: JSONValidatorError):
        """ Initializes the custom click exception. 
        
        Args:
            error (JSONValidatorError): The error information including code message and line number
        """
        # set the error for use in other class methods
        self.error = error
        # set the exit code to be returned from the CLI
        self.exit_code= error.error_code.value
        super().__init__(self.error.message)

    def show(self, file=None):
        """ Prints the error message to the command line.
        
        Args:
            file (IO[Any]): The file to write the error message to
        """
        # print the error message in red
        click.echo(click.style(f"JSON is not valid - {self.error}", fg="red"))

# setup click command line interface
@click.command()
# setup click command line argument of json file
@click.argument("json_file")
def cli(json_file: str):
    """
    Command line interface for validating a given json file.

    Args:
        json_file (str): The path to the json file to be validated.

    Returns:
        error_code (int): 0 if the json file is valid, otherwise the error code of the first found error.
    """
    # create a json validator object
    validator = JsonValidator()

    # try to validate the json file
    try:
        # validate the json file
        validator.validate_json(json_file)
        # print success message
        click.echo(click.style("JSON is valid", fg="green"))
        # return 0 for success
        return 0

    # catch JSON validation errors, print them, and return the error code for other CLIs
    except JSONValidatorError as e:
        # raise a custom error code
        raise CustomClickException(e) from e

    # catch any unexpected errors
    except Exception as e: # pylint: disable=broad-except
        click.echo(click.style(f"Unexpected Error, please contact creator or tool: {e}",
            fg="purple"),err=True)
        return ErrorCode.UNRECOGNIZED_ERROR.value

if __name__ == '__main__':
    cli() #pylint: disable=no-value-for-parameter
