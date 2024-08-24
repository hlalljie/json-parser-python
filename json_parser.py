# keep track of the state of the programs
# functions for each character will validate based on the state

file = None
token = ""
line = 1
character = 1

def open_file(filename: str):
    global file
    file = open(filename, "r", encoding="UTF-8")
    get_char()

def close_file():
    file.close()

def get_char():
    global token
    global character
    token = file.read(1)
    character += 1
    return token

def whitespace():
    """ Gets new whitespace, tracking characters and lines until there is no more whitespace """
    global line
    global character
    if token == " ":
        get_char()
        whitespace()
    if token == "\t":
        get_char()
        character += 3
        whitespace()
    elif token == "\r":
        get_char()
        character = 1
        whitespace()
    elif token == "\n":
        get_char()
        line += 1
        character = 1
        whitespace()

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

def string() -> bool:
    # enter on quote so no need to check
    get_char()

    if not string_char():
        return False

    # string_char exits on endquote so no need to check
    get_char()
    return True

def digit() -> None:
    """ Keeps looping until a non digit """
    get_char()
    if token.isdigit():
        digit()

def decimal() -> bool:
    get_char()
    if not token or not token.isdigit():
        return False
    digit()
    return True

def exponent():
    get_char()
    if token == '-' or token == '+':
        get_char()
    if token.isdigit():
        digit()
        return True
    return False

def number():
    """ Parses a number moving through it while also checking the validity note 
    that note that some validity is checked by value function and other higher functions"""
    if token == '-':
        get_char()

    if token == '0':
        get_char()
        if token.isdigit():
            return False
    elif token.isdigit():
        digit()
    else:
        return False

    if token == ".":
        if not decimal():
            return False

    if token == "e" or token == "E":
        return exponent()

    return True

def true_value() -> bool:
    get_char()
    for c in "rue":
        if c != token:
            return False
        get_char()
    return True

def false_value() -> bool:
    get_char()
    for c in "alse":
        if c != token:
            return False
        get_char()
    return True

def null_value() -> bool:
    get_char()
    for c in "ull":
        if c != token:
            return False
        get_char()
    return True
def value() -> bool:
    whitespace()
    if token == '"':
        if not string():
            return False
    elif token == '-' or token.isdigit():
        if not number():
            return False
    elif token == '{':
        if not json_object():
            return False
    elif token == '[':
        if not array():
            return False
    elif token == 't':
        if not true_value():
            return False
    elif token == 'f':
        if not false_value():
            return False
    elif token == 'n':
        if not null_value():
            return False
    else:
        return False
    whitespace()
    return True

def value_list() -> bool:
    if not value():
        return False
    if token == ',':
        get_char()
        if not value_list():
            return False
    return True

def array() -> bool:
    get_char()
    whitespace()
    if token == "]":
        get_char()
        return True
    elif not value_list():
        return False
    if token == "]":
        get_char()
        return True
    return False

def key_value_list() -> bool:
    if token != '"':
        print("no quote to denote string before key: ", token)
        return False
    if not string():
        print("not string for key")
        return False
    whitespace()

    if token != ':':
        print('need ":" folowing key')
        return False
    get_char()
    whitespace()

    if not value():
        print("not value in object")
        return False

    if token == ',':
        get_char()
        whitespace()
        if not key_value_list():
            print('not key_value_list after comma')
            return False

    return True

def json_object() -> bool:
    get_char()
    whitespace()
    if token == '}':
        return True
    if not key_value_list():
        print("not key_value_list")
        return False
    if token == '}':
        get_char()
        return True
    return False

def validate_json(filename: str) -> bool:
    """ Function checks if a json file is valid """
    open_file(filename)

    whitespace()
    if token == '{':
        if not json_object():
            return False

    elif token == '[':
        if not array():
            return False
        
    else:
        return False

    close_file()
    return True