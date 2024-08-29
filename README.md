# JSON Validator

A command line integration written in Python that checks if a json file is valid. If invalid it will return an error code and print an error message. <br>
Built for the coding challenge on: https://codingchallenges.fyi/challenges/challenge-json-parser/.

## Installation

### For Users

To install the package and run the tool, run the following command via the command line (pip must be installed):

`pip install https://github.com/hlalljie/json-validator-python/releases/download/v1.0.0.0/validate_json-1.0.0-py3-none-any.whl`

### For Developers

1. Clone the repo

   ```bash
   git clone https://github.com/hlalljie/json-validator-python.git
   cd json_validator

   ```

2. Start a venv
   ```bash
   python -m venv venv
   ```
3. Activate venv
   ```
   source venv/bin/activate
   ```
4. Insure that your python interpreter is set to the venv interpreter
5. Build the package by running:
   ```bash
   python -m build
   ```
6. Install the program in edit mode:
   ```bash
   pip install -e .
   ```

## Usage

This `validate_json` command is used to check is a json file is valid. Call the command after installing and give it a json file as the first argument. If invalid it will return an error code and will print the error, line and column number.

Example with valid json file:

```json title="valid.json"
{ "valid json": 10 }
```

```bash
validate_json valid.json
```

Would return `0` and print:

```
JSON is valid
```

Example with invalid json:

```json title="invalid.json"
{"invalid": JSON}
```

```bash
validate_json invalid.json
```

Would return `15` and print:

```console
JSON is not valid - VALUE_CHARACTER_ERROR(15) line 1, column 13: invalid character in value
```

For a list of the error code names go to:
https://github.com/hlalljie/json-validator-python/blob/main/src/json_validator/json_validator_errors.py

## Testing

1. Insure that you are configured to tess from the test folder.
2. From the root directory run `pytest`
3. To add tests add to the list of parameters for a given test.
