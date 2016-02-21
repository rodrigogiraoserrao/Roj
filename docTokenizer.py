# ask for a file name
# read it
# tokenize it

from tokenizer import Tokenizer, Token
from scanner import Scanner

n = input(">> ")
with open(n, "r") as f:
    text = f.read()
    
sc = Scanner(text)
tok = Tokenizer(sc)

t = tok.get_next_token()
while t.get_type() != Token.EOF:
    print(t)
    t = tok.get_next_token()