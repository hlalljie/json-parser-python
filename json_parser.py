# keep track of the state of the programs
# functions for each character will validate based on the state

file = None
token = ""

def open_file(filename: str):
    global file
    file = open(filename, "r", encoding="UTF-8")
    get_char()

def close_file():
    file.close()

def get_char():
    global token
    token = file.read(1)
    return token

def string_hex():
    if not get_char():
        return False
    hex_char = "1234567890abcdefABCDEF"
    for _ in range(4):
        if token not in hex_char:
            return False
        if not get_char():
            return False
    return True
def string_backslash():
    if not get_char():
        return False
    if (
        token == '"' or
        token == '\\' or
        token == 'b' or
        token == 'f' or
        token == 'n' or
        token == 'r' or
        token == 't' or
        (token == 'u' and string_hex())
    ):
        return True
    return False
        
def string_char():
    if token == '\\':
        if not string_backslash():
            return False
    elif token == '"':
        return True
    if not get_char():
        return False
    return string_char()

def string():
    # enter on quote so no need to check
    get_char()

    if not string_char():
        return False

    # string_char exits on endquote so no need to check
    get_char()
    return True

def validate_json(filename: str) -> bool:
    """ Function checks if a json file is valid """
    return True