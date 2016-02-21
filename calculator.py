from parserInterpreter import ParserInterpreter
from tokenizer import Token

class Calculator(ParserInterpreter):
    MATH_OPS = Token.get_math_operators()
    
    def __init__(self, text):
        ParserInterpreter.__init__(self, text)
        
    def evaluate(self):
        return self.get_program()
    
if __name__ == "__main__":
    while True:
        text = input(">> ")
        calc = Calculator(text)
        l = calc.get_token_sequence()
        print(l)
        print(calc.evaluate())