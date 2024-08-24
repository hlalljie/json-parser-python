# keep track of the state of the programs
# functions for each character will validate based on the state
class JsonValidator:   

    def __init__(self) -> None:
        self.file = None
        self.token = ""
        self.line = 1
        self.character = 1

    def open_file(self, filename: str):
        self.file = open(filename, "r", encoding="UTF-8")
        self.line = 1
        self.character = 1
        self.get_char()

    def close_file(self):
        self.file.close()

    def get_char(self):
        self.token = self.file.read(1)
        self.character += 1
        return self.token

    def whitespace(self):
        """ Gets new whitespace, tracking characters and lines until there is no more whitespace """
        if self.token == " ":
            self.get_char()
            self.whitespace()
        if self.token == "\t":
            self.get_char()
            self.character += 3
            self.whitespace()
        elif self.token == "\r":
            self.get_char()
            self.character = 1
            self.whitespace()
        elif self.token == "\n":
            self.get_char()
            self.line += 1
            self.character = 1
            self.whitespace()

    def string_hex(self):
        if not self.get_char():
            return False
        hex_char = "1234567890abcdefABCDEF"
        for _ in range(4):
            if self.token not in hex_char:
                return False
            if not self.get_char():
                return False
        return True

    def string_backslash(self):
        if not self.get_char():
            return False
        if (
            self.token == '"' or
            self.token == '\\' or
            self.token == 'b' or
            self.token == 'f' or
            self.token == 'n' or
            self.token == 'r' or
            self.token == 't' or
            (self.token == 'u' and self.string_hex())
        ):
            return True
        return False
            
    def string_char(self):
        if self.token == '\\':
            if not self.string_backslash():
                return False
        elif self.token == '"':
            return True
        if not self.get_char():
            return False
        return self.string_char()

    def string(self) -> bool:
        # enter on quote so no need to check
        self.get_char()

        if not self.string_char():
            return False

        # string_char exits on endquote so no need to check
        self.get_char()
        return True

    def digit(self) -> None:
        """ Keeps looping until a non digit """
        self.get_char()
        if self.token.isdigit():
            self.digit()

    def decimal(self) -> bool:
        self.get_char()
        if not self.token or not self.token.isdigit():
            return False
        self.digit()
        return True

    def exponent(self):
        self.get_char()
        if self.token == '-' or self.token == '+':
            self.get_char()
        if self.token.isdigit():
            self.digit()
            return True
        return False

    def number(self):
        """ Parses a number moving through it while also checking the validity note 
        that note that some validity is checked by value function and other higher functions"""
        if self.token == '-':
            self.get_char()

        if self.token == '0':
            self.get_char()
            if self.token.isdigit():
                return False
        elif self.token.isdigit():
            self.digit()
        else:
            return False

        if self.token == ".":
            if not self.decimal():
                return False

        if self.token == "e" or self.token == "E":
            return self.exponent()

        return True

    def true_value(self) -> bool:
        self.get_char()
        for c in "rue":
            if c != self.token:
                return False
            self.get_char()
        return True

    def false_value(self) -> bool:
        self.get_char()
        for c in "alse":
            if c != self.token:
                return False
            self.get_char()
        return True

    def null_value(self) -> bool:
        self.get_char()
        for c in "ull":
            if c != self.token:
                return False
            self.get_char()
        return True
    def value(self) -> bool:
        self.whitespace()
        if self.token == '"':
            if not self.string():
                return False
        elif self.token == '-' or self.token.isdigit():
            if not self.number():
                return False
        elif self.token == '{':
            if not self.json_object():
                return False
        elif self.token == '[':
            if not self.array():
                return False
        elif self.token == 't':
            if not self.true_value():
                return False
        elif self.token == 'f':
            if not self.false_value():
                return False
        elif self.token == 'n':
            if not self.null_value():
                return False
        else:
            return False
        self.whitespace()
        return True

    def value_list(self) -> bool:
        if not self.value():
            return False
        if self.token == ',':
            self.get_char()
            if not self.value_list():
                return False
        return True

    def array(self) -> bool:
        self.get_char()
        self.whitespace()
        if self.token == "]":
            self.get_char()
            return True
        elif not self.value_list():
            return False
        if self.token == "]":
            self.get_char()
            return True
        return False

    def key_value_list(self) -> bool:
        if self.token != '"':
            print("no quote to denote string before key: ", self.token)
            return False
        if not self.string():
            print("not string for key")
            return False
        self.whitespace()

        if self.token != ':':
            print('need ":" folowing key')
            return False
        self.get_char()
        self.whitespace()

        if not self.value():
            print("not value in object")
            return False

        if self.token == ',':
            self.get_char()
            self.whitespace()
            if not self.key_value_list():
                print('not key_value_list after comma')
                return False

        return True

    def json_object(self) -> bool:
        self.get_char()
        self.whitespace()
        if self.token == '}':
            self.get_char()
            return True
        if not self.key_value_list():
            print("not key_value_list")
            return False
        if self.token == '}':
            self.get_char()
            return True
        return False

    def validate_json(self, filename: str) -> bool:
        """ Function checks if a json file is valid """
        self.open_file(filename)

        self.whitespace()
        if self.token == '{':
            if not self.json_object():
                return False

        elif self.token == '[':
            if not self.array():
                return False
            
        else:
            return False
        
        self.whitespace()

        if self.token:
            print("content after close: ", self.token)
            return False

        self.close_file()
        return True