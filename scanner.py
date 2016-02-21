class Char(object):
    """Character class to hold the information;
    Provides some methods to check if a given character is of a given
    type such as EOF or whitespace"""
    cEOF = "ENDOFFILE"
    cSEPARATOR = ";"
    WHITESPACE = ["\n", " ", "\t", "\r"]

    # a list of characters to be printed differently
    ESCAPE_CHARACTERS = {cEOF: "END OF FILE",
                                "\n": "NEWLINE",
                                "\t": "TAB",
                                " ": "SPACE"} 
                                
    def __init__(self, char, line, col):
        """Initializes the Character with the important information"""
        self.char = char
        self.line = line
        self.col = col
    
    def is_whitespace(self):
        """Flags if the character is whitespace"""
        return self.char in self.WHITESPACE

    def is_eof(self):
        """Flags if the character is the end of the file"""
        return self.char == self.cEOF
        
    def is_separator(self):
        """Flags if the character is a separator"""
        return self.char == self.cSEPARATOR
        
    def is_word_char(self):
        return self.char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLM" \
                            "NOPQRSTUVWXYZ_1234567890"

    def __str__(self):
        """Returns a string representation of the character"""
        if self.char in self.ESCAPE_CHARACTERS.keys():
            c = self.ESCAPE_CHARACTERS[self.char]
        else:
            c = self.char
        return "Char {} @ line {} col {}".format(
                c, self.line, self.col)

class Scanner(object):
    """Implement a Scanner object that traverses through an input
    string and returns a character at a time, keeping track of our
    position in the file with regard to line and column"""
    def __init__(self, text):
        """Initialize the position of the scanner"""
        self.index = -1
        self.line = 1
        self.col = -1
        self.text = text
        # placeholder
        self.current = Char("", 1, -1)

    def get_next_char(self):
        """Returns the next character in the string, if there is any"""
        self.index += 1
        if self.index >= len(self.text):
            self.current = Char(Char.cEOF, self.line, self.col)
            return self.current

        char = self.text[self.index]
        # was the previous one a new line? if so, change line!
        if self.current.char == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        self.current = Char(char, self.line, self.col)
        return self.current

    def has_chars(self):
        """Returns True if there are still more characters
        to be returned OR the EndOfFile character is yet to be returned"""
        return self.current is None or self.current.char != Char.cEOF

    def __str__(self):
        """String representation of the Scanner, for printing"""
        return "Scanner object @ line {} col {}".format(self.line, self.col)

if __name__ == "__main__":
    text = """Hello there darling.
My name is Rojer.
    Rojer Serrao :P"""

    sc = Scanner(text)
    print(sc)
    while sc.has_chars():
        c = sc.get_next_char()
        print(c)
