from scanner import Char, Scanner

class Token(object):
    """Implement a class to wrap the tokens and provide some useful
    methods regarding them"""
    
    # List token types
    ## variable types
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOL = "BOOL"
    ## operator types
    READ = "READ"
    READINT = "READINT"
    READFLOAT = "READFLOAT"
    READBOOL = "READBOOL"
    OUT = "OUT"
    ### math ops
    PLUS = "PLUS"
    MINUS = "MINUS"
    PRODUCT = "PRODUCT"
    DIVISION = "DIVISION"
    POWER = "POWER"
    ### logic ops
    AND = "AND"
    OR = "OR"
    NEGATION = "NEGATION"
    EQUALITY = "EQUALITY"
    INEQUALITY = "INEQUALITY"
    GREATER = "GREATER"
    LESSER = "LESSER"
    GREATEREQUAL = "GREATEREQUAL"
    LESSEREQUAL = "LESSEREQUAL"
    ## misc
    SEPARATOR = "SEPARATOR"
    LGROUP = "LGROUP"
    RGROUP = "RGROUP"
    ASSIGNMENT = "ASSIGNMENT"
    COMMENT = "COMMENT"
    NULL = "NULL"
    EOF = "EOF"
    USER_VAR = "USER_VAR"
    ## keywords
    WHILE = "WHILE"
    DO = "DO"
    END = "END"
    IF = "IF"
    ELSE = "ELSE"
    HALT = "HALT"
    STOP = "STOP"
    JUMPOVER = "JUMPOVER"
    RETURN = "RETURN"
    KEYWORD = "KEYWORD"
    
    KEYWORDS = ["Null", "True", "False", "or", "and", "not", "do",
                "end", "while", "if", "else", "out", "read", "readint",
                "readfloat", "readbool", "stop", "halt", "jumpover",
                "return"]
    
    def get_types():
        """Returns a list with all the known Token types"""
        values = []
        for attr in dir(Token):
            if attr.upper() == attr:
                if not attr.startswith("__"):
                    if not hasattr(getattr(Token, attr), "__call__"):
                        values.append(attr)
        return values

    def get_operators():
        """Returns a list with the string representations of the
        known operator types"""
        OPERATORS = [
            "+",  #Token.PLUS
            "-",  #Token.MINUS
            "*",  #Token.PRODUCT
            "/",  #Token.DIVISION
            "^",  #Token.POWER
            "=",  #Token.ASSIGNMENT
            "==",  #Token.EQUALITY
            "!=",  #Token.INEQUALITY
            ">",  #Token.GREATER
            "<",  #Token.LESSER
            ">=",  #Token.GREATEREQUAL
            "<="  #Token.LESSEREQUAL
        ]
        return OPERATORS
        
    def get_math_operator_types():
        """Returns a list with mathematical operators' types"""
        TYPES = [
            Token.PLUS,
            Token.MINUS,
            Token.PRODUCT,
            Token.DIVISION,
            Token.POWER
        ]
        return TYPES
       
    def get_math_operators():
        """Returns a list with the mathematical operators' strings"""
        MOPERATORS = [
            "+",  #Token.PLUS
            "-",  #Token.MINUS
            "*",  #Token.PRODUCT
            "/",  #Token.DIVISION
            "^"  #Token.POWER
        ]
        return MOPERATORS

    def __init__(self, typ, value):
        """Initialize the token; store its type and value"""
        if typ not in Token.get_types():
            raise Exception("Unknown token type {}".format(typ))
        self.typ = typ
        self.value = value

    def get_type(self):
        """Returns the type of the Token"""
        return self.typ
        
    def get_value(self):
        """Returns the value of the Token"""
        return self.value

    def __str__(self):
        """Returns a string representation of the Token object"""
        return "Token({}, {})".format(self.typ, self.value)

    def __repr__(self):
        return self.__str__()

class Tokenizer(object):
    """Implements an object to build Tokens from the given input.
    Needs a Scanner object as input and reads characters from there"""
    
    def __init__(self, scanner):
        """Store the scanner and initalize two auxiliary variables"""
        self.scanner = scanner
        self.current_char = None
        self.current_char_consumed = True

    def get_next_token(self):
        """Builds the next Token with characters given by the Scanner;
        Uses the first character to make a guess at the Token
        and dispatches execution to one of the get_Type methods"""
        
        if self.current_char_consumed:
            c = self.scanner.get_next_char()
        # some of the get_ methods may find the end of the Token by
        # encountering the beginning of the next one
        # we set self.current_char_consumed to indicate that we must
        # still use that character
        else:
            c = self.current_char

        # consume whitespace as it doesn't matter when between Tokens
        while c.is_whitespace():
            c = self.scanner.get_next_char()
           
        # reached EOF
        if c.is_eof():
            self.current_char_consumed = True
            return Token(Token.EOF, c.char)
        elif c.is_separator():
            self.current_char_consumed = True
            return Token(Token.SEPARATOR, c.char)
        # the char is consumed by default
        # if, for some reason, it isn't, the appropriate method
        # that is called will flag that
        self.current_char_consumed = True
        # integer or a float
        if c.char.isdigit() or c.char == ".":
            return self.get_num(c)
        # string
        if c.char == "\"":
            return self.get_string(c)
        # comment
        if c.char == "$":
            self.get_comment(c)
            return self.get_next_token()
        # grouping character
        if c.char == "(":
            return Token(Token.LGROUP, c.char)
        if c.char == ")":
            return Token(Token.RGROUP, c.char)
        # operator
        if c.char in "".join(Token.get_operators()):
            return self.get_operator(c)
        # variable name or keyword
        if c.char.isalpha():
            return self.get_word(c)
        
        self.error("Unknown Token starting with '{}'".format(c.char))
    
    def get_num(self, c):
        """Build a number, either a float or an integer;
        consume characters while they are either a digit or . """
        numS = ""
        while c.char.isdigit() or c.char == ".":
            numS = numS + c.char
            c = self.scanner.get_next_char()
        # the next char may be something tasty; store it
        self.current_char = c
        self.current_char_consumed = False
        # if we found a dot, we want to build a floating point number
        if "." in numS:
            try:
                f = float(numS)
            except Exception:
                self.error("Unrecognized float {}".format(numS))
            return Token(Token.FLOAT, f)
        # no dot, integer number
        else:
            try:
                i = int(numS)
            except Exception:
                self.error("Unrecognized integer {}".format(numS))
            return Token(Token.INTEGER, i)
            
    def get_word(self, c):
        s = ""
        while c.is_word_char():
            s += c.char
            c = self.scanner.get_next_char()
        self.current_char = c
        self.current_char_consumed = False
            
        if s in Token.KEYWORDS:
            return self.get_keyword(s)
        else:
            return Token(Token.USER_VAR, s)
            
    def get_keyword(self, s):
        if s not in Token.KEYWORDS:
            self.error("Unrecognized keyword '{}'".format(s))
        
        if s == "True":
            return Token(Token.BOOL, True)
        elif s == "False":
            return Token(Token.BOOL, False)
        else:
            tok_name = s.upper()
            flag = getattr(Token, tok_name, Token.KEYWORD)
            return Token(flag, s)
            
    def get_comment(self, c):
        """Ignore a comment token"""
        flag = c.char
        next_char = self.scanner.get_next_char()
        while next_char.char != flag:
            next_char = self.scanner.get_next_char()
        
    def get_string(self, c):
        """Build a string Token"""
        s = ""
        next_char = self.scanner.get_next_char()
        while next_char.char != "\"":
            s += next_char.char
            next_char = self.scanner.get_next_char()
        return Token(Token.STRING, s)
        
    def get_operator(self, c):
        """Build an operator Token; check if it is a one-char or
        two-char operator"""
        char = c.char
        # list all operator strings and its name
        d = {"+": Token.PLUS,
            "-": Token.MINUS,
            "*": Token.PRODUCT,
            "/": Token.DIVISION,
            "^": Token.POWER,
            "=": Token.ASSIGNMENT,
            "==": Token.EQUALITY,
            "!=": Token.INEQUALITY,
            ">": Token.GREATER,
            "<": Token.LESSER,
            ">=": Token.GREATEREQUAL,
            "<=": Token.LESSEREQUAL}
            
        if char not in "".join(Token.get_operators()):
            self.error("Unknown operator starting with '{}'".format(char))
            
        next_char = self.scanner.get_next_char()
        possible_op = char + next_char.char
        # try to create a two-char operator; does it exist?
        if (possible_op) in d.keys():
            return Token(d[possible_op], possible_op)
        # it is a one-char operator; store the 2nd char
        else:
            self.current_char = next_char
            self.current_char_consumed = False
            return Token(d[char], char)

    def error(self, msg):
        """Raise an error with a custom message"""
        raise Exception(msg)

if __name__ == "__main__":
    while True:
        text = input(">> ")
        scan = Scanner(text)
        Tok = Tokenizer(scan)
        token = Tok.get_next_token()
        print(token)
        while token.get_type() is not Token.EOF:
            token = Tok.get_next_token()
            print(token)