# Roj
Toy programming language

Based on the series "Let's build a simple interpreter" (https://ruslanspivak.com/lsbasi-part1/) I wrote an interpreter
for a toy language I called "Roj".

This directory has the following layout:

  - Grammar
    - grammar.txt
    - grammar.html
    - htmlGrammar.py
  - snippets
     - several .txt files
  - ASTgenerator.py
  - ASTParser.py
  - calculator.py
  - docTokenizer.py
  - errorSystem.py
  - parserInterpreter.py
  - RojInterpreter.py
  - scanner.py
  - tokenizer.py
  
scanner.py and tokenizer.py both implement two classes that are used throughout the rest of the code.

docTokenizer.py is a helper file that takes a file as argument and tokenizes it; for debugging purposes.

errorSystem.py is my first attempt to create better error messages for the parsing/evaluation. (only used in ASTParser.py)

parserInterpreter.py implements one first version of the parser that generates the token sequence of the program
  and evaluates it. The supported grammar is on top of the file.
  
calculator.py wraps around parserInterpreter.py; repeatedly asks for input to the user and evaluates math expressions.

ASTgenerator.py builds from parserInterpreter and creates an Abstract Syntax Tree for the program.


ASTParser.py is the real deal. Implements the whole business. Asks for user input; tokenizes the input, creates
  the AST and evaluates it.
  
RojInterpreter.py is the user entry-point. Starts a (very lame) python like interpreter session where you can either
  type expressions or evaluate text files
  
  
The 'snippets' directory contains several .txt files that contain Roj code

The 'grammar' directory has one file grammar.txt with the supported grammar by the language; htmlGrammar.py that builds
  an HTML file with the grammar, and grammar.html which is the generated file;
