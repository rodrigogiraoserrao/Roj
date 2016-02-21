from scanner import Scanner
from tokenizer import Tokenizer, Token

"""This file contains one class ParserInterpreter that
gets a string as argument; it does both token sequence generation
and token sequence evaluation"""

### Supported Grammar
# program : expr (Token.SEPARATOR expr)* Token.SEPARATOR? Token.EOF
# expr : term ((Token.PLUS | Token.MINUS) term)*
# term : power ((Token.PRODUCT | Token.DIVISION) power)*
# power : base (Token.POWER base)*
# base : Token.LGROUP expr Token.RGROUP | Token.INTEGER | Token.FLOAT

class ParserInterpreter(object):
    def __init__(self, expression):
        self.sc = Scanner(expression)
        self.tok = Tokenizer(self.sc)
        self.tokens = None
        
    def get_token_sequence(self):
        if self.tokens is not None:
            return self.tokens[::]
            
        self.tokens = []
        
        self.tokens.append(self.tok.get_next_token())
        while self.tokens[-1].get_type() != Token.EOF:
            self.tokens.append(self.tok.get_next_token())
            
        return self.tokens[::]
        
    def get_program(self):
        result = self.get_expr()
        print("pre-result: {}".format(result))
        
        while self.tokens[0].get_type() is Token.SEPARATOR:
            self.tokens = self.tokens[1:]
            if self.tokens[0].get_type() is Token.EOF:
                break
            else:
                result = self.get_expr()
                print("pre-result: {}".format(result))
                
        if self.tokens[0].get_type() is Token.EOF:
            return result
        else:
            self.error("Program did not terminate with expected EOF")
    
    def get_expr(self):
        result = self.get_term()
        
        while self.tokens[0].get_type() in (Token.PLUS,
                                            Token.MINUS):
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            other = self.get_term()
            
            if tok.get_type() == Token.PLUS:
                result += other
            elif tok.get_type() == Token.MINUS:
                result -= other
                
        return result
        
    def get_term(self):
        result = self.get_power()
        
        while self.tokens[0].get_type() in (Token.PRODUCT,
                                            Token.DIVISION):
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            other = self.get_power()
            
            if tok.get_type() == Token.PRODUCT:
                result *= other
            elif tok.get_type() == Token.DIVISION:
                result /= other
                
        return result
        
    def get_power(self):
        result = self.get_base()
        
        while self.tokens[0].get_type() is Token.POWER:
            self.tokens = self.tokens[1:]
            other = self.get_base()
            
            result = pow(result, other)
            
        return result
    
    def get_base(self):
        tok = self.tokens[0]
        self.tokens = self.tokens[1:]
        
        if tok.get_type() not in (Token.INTEGER, Token.FLOAT):
            if tok.get_type() is not Token.LGROUP:
                self.error("Could not get a valid base")
            else:
                base = self.get_expr()
                tok = self.tokens[0]
                self.tokens = self.tokens[1:]
                if tok.get_type() is not Token.RGROUP:
                    self.error("Unmatched left parenthesis")
                return base
        else:
            return tok.get_value()
        
    def error(self, msg):
        raise Exception(msg)