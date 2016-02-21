s = """Roj Interpreter [v1.0.1]
by Rodrigo Girao Serrao"""

from ASTParser import Parser, Interpreter

print(s)

inp = None

inp = input(">> ")
while inp != "quit":
    if inp.startswith("execute"):
        args = inp.split()
        filename = args[1]
        try:
            with open(filename, "r") as f:
                inp = f.read()
        except FileNotFoundError:
            print("File not found")
            inp = ""
            
    if inp:
        tree = Parser(inp)
        interpreter = Interpreter(tree)
        print(interpreter.evaluate())
    
    inp = input(">> ")