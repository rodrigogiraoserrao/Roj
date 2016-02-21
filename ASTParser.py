### Builds on what I have from the ASTgenerator.py
### Parses input and builds an AST representation for it

#### Parsing follows the grammar structure
## Every grammar production rule has a get_<rule name> method
# the method's only argument is the tokens to be parsed
## The method attempts to build the components of the RHS of the grammar
# rule i.e. the sequence of terminals and non-terminals
## Upon success, returns the subtree with the components and the rest of
# the input; upon failure, returns None and the input unchanged
## Because of the return "mechanics", the methods start by trying to
# parse the rules which are easier to rule out i.e. the ones with more
# distinct keywords in them;

### Evaluates the tree by recursively evaluating the nodes

from scanner import Scanner, Char
from tokenizer import Tokenizer, Token
from errorSystem import *
from sys import exit

### Grammar
## check the grammar.txt file

class Node(object):
    """Implements the base of our Abstract Syntax Tree (AST).
    The structure of the program will be parse by building a tree whose
        nodes all inherit from this class.
    Provides functionality for pretty printing"""
    def __init__(self, token, parent=None,
                                children=None):
        """Initializes the parent of all the children to itself"""
        self.token = token
        self.parent = parent
        if children:
            for child in children:
                child.parent = self
        
    def __str__(self):
        """Override __str__ method for a more detailed representation"""
        if self.left is None:
            l = "None"
        else:
            l = str(self.left.token)
            
        if self.right is None:
            r = "None"
        else:
            r = str(self.right.token)
            
        s = "{}[ {} ]: l = {} | r = {}".format(
                                type(self).__name__,
                                str(self.token), l, r)
        return s
        
    def get_strings(self):
        """Returns a list with the string representations of itself
    and the lists of the same call on each child"""
        if self.left is None:
            l = []
        else:
            l = self.left.get_strings()
        if self.right is None:
            r = []
        else:
            r = self.right.get_strings()
        s = " > " + str(self.token)
        
        return [s, l, r]
        
class UnOp(Node):
    """Node implemented for Unary Operators like 'not'"""
    def __init__(self, token, parent=None, child=None):
        children = [child] if child else []
        Node.__init__(self, token, parent, children)
        self.left = child
        self.right = None
        
class IOOp(UnOp):
    """Node implemented for I/O operators like 'read' and 'out'"""
    def __init__(self, token, parent=None, child=None):
        UnOp.__init__(self, token, parent, child)
        
class Control(UnOp):
    """Node implemented for control statements like 'halt'"""
    def __init__(self, token, parent=None, child=None):
        UnOp.__init__(self, token, parent, child)
        
class BinOp(Node):
    """Node implemented for ordinary binary operators like ;"""
    def __init__(self, token, parent=None,
                                left_child=None, right_child=None):
        children = []
        if left_child:
            children.append(left_child)
        if right_child:
            children.append(right_child)
        Node.__init__(self, token, parent, children)
        self.left = left_child
        self.right = right_child
        
class BoolBinOp(BinOp):
    """Node implemented for boolean binary operators like 'and'"""
    def __init__(self, token, parent=None,
                                left_child=None, right_child=None):
        BinOp.__init__(self, token, parent, left_child, right_child)
        
class CompBinOp(BoolBinOp):
    """Node implemented for binary comparison operators like '=='"""
    def __init__(self, token, parent=None,
                                left_child=None, right_child=None):
        BoolBinOp.__init__(self, token, parent, left_child, right_child)
        
class ArithBinOp(BinOp):
    """Node implemented for arithmetic binary operators like +"""
    def __init__(self, token, parent=None,
                                left_child=None, right_child=None):
        BinOp.__init__(self, token, parent, left_child, right_child)
        
class Literal(Node):
    """Node implemented to hold any literal, like strings or integers"""
    def __init__(self, token, parent=None):
        Node.__init__(self, token, parent, [])
        self.left = self.right = None
       
class Variable(Node):
    """Node implemented to represent any user-defined variable"""
    def __init__(self, token, parent=None):
        Node.__init__(self, token, parent, [])
        self.left = self.right = None
        
class CompStmt(Node):
    """Node implemented to represent any compound statement"""
    def __init__(self, token, parent=None,
                                left_child=None, right_child=None):
        children = []
        if left_child:
            children.append(left_child)
        if right_child:
            children.append(right_child)
        Node.__init__(self, token, parent, children)
        self.left = left_child
        self.right = right_child

class Parser(object):
    """Implement a recursive-descent parser;
    The parser will attempt to build an AST of the program;
    Its only argument is the string to be parsed; Upon success, it will
        store the AST's root (the EOF Node) in self.root.
    The show() method provides pretty tree-like printing for debugging"""
    def __init__(self, expression):
        """Initialize the parser by generating the token sequence"""
        self.sc = Scanner(expression)
        self.tok = Tokenizer(self.sc)
        self.tokens = None
        self.tokens = self.get_token_sequence()
        self.root = None
        
    def get_token_sequence(self):
        """Generate the whole token sequence for the given program"""
        # prevent redundant calls
        if self.tokens is not None:
            return self.tokens[::]
            
        self.tokens = []
        
        self.tokens.append(self.tok.get_next_token())
        while self.tokens[-1].get_type() != Token.EOF:
            self.tokens.append(self.tok.get_next_token())
            
        return self.tokens[::]
    
    def get_program(self):
        """Entry point to the parser; The method will raise an error
            if it is not able to build an AST Tree for the program"""
        token_list = self.tokens[::]
        subtree, token_list = self.get_suite(token_list)
        if subtree is None:
            raise ParserException("Could not parse the program correctly")
        
        if token_list[0].get_type() != Token.EOF:
            raise ParserException("Could not parse the program")
        else:
            eof = token_list[0]
            self.root = UnOp(eof, parent=None, child=subtree)
            
    def get_suite(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_stmt(token_list)
        
        while token_list and token_list[0].get_type() is Token.SEPARATOR:
            tok = token_list[0]
            token_list = token_list[1:]
            if token_list[0].get_type() is Token.EOF:
                right = Literal(Token(Token.NULL, "Null"), parent=None)
            else:
                right, token_list = self.get_stmt(token_list)
                
            if right is None:
                break
            subtree = BinOp(tok, parent=None, left_child=subtree,
                                                right_child=right)

        if subtree is None:
            return None, tokens
        return subtree, token_list
        
    def get_stmt(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_io_stmt(token_list)
        
        if subtree is None:
            # could not get an IO statement, try a control
            subtree, token_list = self.get_control(token_list)
        if subtree is None:
            # could not get a control statement, try an assignment
            subtree, token_list = self.get_assignment(token_list)
        if subtree is None:
            # could not get an assignment, try a compound stmt
            subtree, token_list = self.get_compound(token_list)
        if subtree is None:
            # could not get a compound stmt, try an expression
            subtree, token_list = self.get_expression(token_list)
        if subtree is None:
            return None, tokens
        
        return subtree, token_list
        
    def get_io_stmt(self, token_list):
        tokens = token_list[::]
        
        subtree, token_list = self.get_in_stmt(token_list)
        if subtree is None:
            subtree, token_list = self.get_out_stmt(token_list)
        if subtree is None:
            return None, tokens
            
        return subtree, token_list
        
    def get_control(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() not in [Token.STOP, Token.RETURN,
                                    Token.JUMPOVER, Token.HALT]:
            return None, tokens
        tok = token_list[0]
        token_list = token_list[1:]
        if tok.get_type() in [Token.STOP, Token.JUMPOVER]:
            sub = Literal(Token(Token.NULL, "Null"))
        else:
            sub, token_list = self.get_expression(token_list)
            if sub is None:
                sub = Literal(Token(Token.NULL, "Null"))
                
        return Control(tok, parent=None, child=sub), token_list
        
    def get_in_stmt(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() in [Token.READ, Token.READINT,
                                    Token.READFLOAT, Token.READBOOL]:
            in_tok = token_list[0]
            token_list = token_list[1:]
        else:
            return None, tokens
            
        if token_list[0].get_type() == Token.USER_VAR:
            var_tok = token_list[0]
            var_node = Variable(var_tok)
            token_list = token_list[1:]
        else:
            self.error("After READ a user variable is expected")
            
        subtree = IOOp(in_tok, parent=None, child=var_node)
        return subtree, token_list
        
    def get_out_stmt(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() == Token.OUT:
            out_tok = token_list[0]
            token_list = token_list[1:]
            subtree, token_list = self.get_expression(token_list)
            if subtree is None:
                self.error("Could not parse an 'out' statement")
        else:
            return None, tokens
            
        subtree = IOOp(out_tok, parent=None, child=subtree)
        return subtree, token_list
    
    def get_assignment(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() != Token.USER_VAR:
            return None, tokens
        # create the variable node
        var_node = Variable(token_list[0], parent=None)
        # found a user_var, check for a Token.ASSIGNMENT
        token_list = token_list[1:]
        if token_list[0].get_type() != Token.ASSIGNMENT:
            return None, tokens
        tok = token_list[0]
        token_list = token_list[1:]
        
        # get the right node; is it another assignment?
        right, token_list = self.get_assignment(token_list)
        if right is None:
            right, token_list = self.get_expression(token_list)
        if right is None:
            return None, tokens
        return BinOp(tok, parent=None, left_child=var_node,
                                    right_child=right), token_list
                                    
    def get_compound(self, token_list):
        tokens = token_list[::]
        
        # try to get a while compound
        subtree, token_list = self.get_while(token_list)
        if subtree is None:
            subtree, token_list = self.get_if(token_list)
        if subtree is None:
            return None, tokens
        return subtree, token_list
            
    def get_while(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() != Token.WHILE:
            return None, tokens
            
        tok = token_list[0]
        token_list = token_list[1:]
        expression, token_list = self.get_expression(token_list)
        if expression is None:
            return None, tokens
            
        if token_list[0].get_type() != Token.DO:
            return None, tokens
        token_list = token_list[1:]
        suite, token_list = self.get_suite(token_list)
        if suite is None:
            return None, tokens
            
        if token_list[0].get_type() != Token.END:
            return None, tokens
        token_list = token_list[1:]
        
        return CompStmt(tok, parent=None, left_child=expression,
                                        right_child=suite), token_list
                                        
    def get_if(self, token_list):
        tokens = token_list[::]
        
        if token_list[0].get_type() != Token.IF:
            return None, tokens
            
        if_tok = token_list[0]
        token_list = token_list[1:]
        expression, token_list = self.get_expression(token_list)
        if expression is None:
            return None, tokens
            
        if token_list[0].get_type() != Token.DO:
            return None, tokens
        token_list = token_list[1:]
        if_suite, token_list = self.get_suite(token_list)
        if if_suite is None:
            return None, tokens
            
        if token_list[0].get_type() != Token.END:
            return None, tokens
        token_list = token_list[1:]
        
        if token_list[0].get_type() != Token.ELSE:
            else_tok = None
        else:
            else_tok = token_list[0]
            token_list = token_list[1:]
            if token_list[0].get_type() != Token.DO:
                return None, tokens
            token_list = token_list[1:]
            
            else_suite, token_list = self.get_suite(token_list)
            if else_suite is None:
                return None, tokens
            
            if token_list[0].get_type() != Token.END:
                return None, tokens
            token_list = token_list[1:]
            
        if else_tok is None:
            else_tok = Token(Token.ELSE, "else")
            else_node = CompStmt(else_tok, parent=None,
                                left_child=if_suite, right_child=None)
        else:
            else_node = CompStmt(else_tok, parent=None,
                            left_child=if_suite, right_child=else_suite)
                            
        if_node = CompStmt(if_tok, parent=None,
                        left_child=expression, right_child=else_node)
        return if_node, token_list

    def get_expression(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_or_test(token_list)
        
        if subtree is None:
            return None, tokens
        return subtree, token_list
        
    def get_or_test(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_and_test(token_list)
        
        if subtree is None:
            return None, tokens
        
        while token_list[0].get_type() == Token.OR:
            tok = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_and_test(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = BoolBinOp(tok, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
        
    def get_and_test(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_not_test(token_list)
        
        if subtree is None:
            return None, tokens
        
        while token_list[0].get_type() == Token.AND:
            tok = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_not_test(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = BoolBinOp(tok, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
    
    def get_not_test(self, token_list):
        if token_list[0].get_type() != Token.NEGATION:
            return self.get_comparison(token_list)
        
        tokens = token_list[::]
        tok = token_list[0]
        token_list = token_list[1:]
        subtree, token_list = self.get_not_test(token_list)
        if subtree is None:
            return None, tokens
        else:
            return UnOp(tok, parent=None, child=subtree), token_list
            
    def get_comparison(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_arith(token_list)
        
        if subtree is None:
            return None, tokens
            
        comp_ops = [Token.EQUALITY, Token.INEQUALITY, Token.GREATER,
                    Token.LESSER, Token.GREATEREQUAL, Token.LESSEREQUAL]
        while token_list[0].get_type() in comp_ops:
            op = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_arith(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = CompBinOp(op, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
        
    def get_arith(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_term(token_list)
        
        if subtree is None:
            return None, tokens
            
        while token_list[0].get_type() in [Token.PLUS, Token.MINUS]:
            op = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_term(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = ArithBinOp(op, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
        
    def get_term(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_factor(token_list)
        
        if subtree is None:
            return None, tokens
            
        while token_list[0].get_type() in [Token.PRODUCT, Token.DIVISION]:
            op = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_factor(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = ArithBinOp(op, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
        
    def get_factor(self, token_list):
        tokens = token_list[::]
        subtree, token_list = self.get_atom(token_list)
        
        if subtree is None:
            return None, tokens
            
        while token_list[0].get_type() == Token.POWER:
            op = token_list[0]
            token_list = token_list[1:]
            right, token_list = self.get_atom(token_list)
            if right is None:
                return None, tokens
            else:
                subtree = ArithBinOp(op, parent=None, left_child=subtree,
                                                    right_child=right)
                                                    
        return subtree, token_list
        
    def get_atom(self, token_list): 
        tokens = token_list[::]
        
        literals = [Token.BOOL, Token.INTEGER, Token.FLOAT,
                    Token.NULL, Token.STRING, Token.BOOL]
        
        if token_list[0].get_type() in [Token.PLUS, Token.MINUS]:
            op = token_list[0]
            token_list = token_list[1:]
            subtree, token_list = self.get_atom(token_list)
            if subtree is None:
                return None, tokens
            else:
                return UnOp(op, parent=None, child=subtree), token_list
                
        elif token_list[0].get_type() in literals:
            return Literal(token_list[0]), token_list[1:]
            
        elif token_list[0].get_type() == Token.USER_VAR:
            return Variable(token_list[0]), token_list[1:]
            
        elif token_list[0].get_type() == Token.LGROUP:
            subtree, token_list = self.get_expression(token_list[1:])
            if subtree is None or token_list[0].get_type() != Token.RGROUP:
                return None, tokens
            else:
                return subtree, token_list[1:]
                
        else:
            return None, token_list
        
    def error(self, msg):
        print(msg)
        exit()
        
    def show(self):
        strings = self.root.get_strings()
        
        def simplify(l, depth):
            s = l[0]
            indent = "  " * depth
            for ele in l[1:]:
                if ele:
                    s += "\n  " + indent + " |:" + simplify(ele, depth+1)
            
            return s
            
        print(simplify(strings, 0))
        
class NodeVisitor(object):
    """Implement the Visitor pattern for the interpreter"""
    def __init__(self):
        pass
        
    def visit(self, node):
        """Dispatch the evaluation to the correct visit_ method;
            By using the Visitor pattern we need not to use
            if-statements to tell the Interpret to call the
            correct visit_ methods"""
        # get the name of the method we want
        method_name = "visit_" + type(node).__name__
        visit_method = getattr(self, method_name, self.no_visit)
        
        return visit_method(node)
        
    def no_visit(self, node):
        """Generic error-signaling visit_ method"""
        print("There is no visit_ method for " + str(node))
        exit()
        
class Interpreter(NodeVisitor):
    """Implement the Interpreter;
    Its only argument is a parser. Interprets the program by recursively
        traversing the tree the parser provides."""
    def __init__(self, parser):
        NodeVisitor.__init__(self)
        self.parser = parser
        self.variables = {}
        
    def evaluate(self):
        """Entry point to the recursive evaluation of the program"""
        # ensure we have generated a tree
        if self.parser.root is None:
            self.parser.get_program()
            
        return self.visit(self.parser.root)
        
    def visit_Variable(self, node):
        """Handle evaluation of a variable"""
        # This only gets called if we need the variable in an expression
        # Assignment is directly taken care by the BinOp assignment
        name = node.token.value
        if name not in self.variables.keys():
            self.error("Undefined variable '{}'".format(name))
        else:
            return self.variables[name]
        
    def visit_Literal(self, node):
        """Handle the evaluation of a literal"""
        return node.token.value
        
    def visit_CompStmt(self, node):
        """Handle evaluation of compound statements"""
        tok = node.token
        
        if tok.get_type() is Token.WHILE:
            expr = node.left
            suite = node.right
            while self.visit(expr):
                # we may execute a stop or halt statement, check for that
                r = self.visit(suite)
                if isinstance(r, Token):
                    if r.get_type() == Token.STOP:
                        break
                    elif r.get_type() == Token.HALT:
                        return r
                
        elif tok.get_type() is Token.IF:
            condition = node.left
            if self.visit(condition):
                return self.visit(node.right.left)
            else:
                if node.right.right is not None:
                    return self.visit(node.right.right)
                else:
                    return None
            
    def visit_UnOp(self, node):
        """Handle evaluation of generic unary operators"""
        tok = node.token
        left = self.visit(node.left)
        if tok.get_type() is Token.EOF:
            ### we may have returned a halt/stop/return/jumpover
            # all the way here; act accordingly
            if isinstance(left, Token):
                if left.get_type() == Token.HALT:
                    self.error("program halted: {}".format(left.value))
                # if one of these control stmts got here it was misused
                elif left.get_type() in [Token.JUMPOVER, Token.STOP,
                                        Token.RETURN]:
                    self.error("{} used out of scope".format(left.value))
            print("program terminated; return value <{}>".format(left))
        elif tok.get_type() is Token.MINUS:
            if type(left) not in [int, float]:
                self.error("- did not expect value of type {}".format(
                                                type(left).__name__))
            return -1 * (left)
        elif tok.get_type() is Token.PLUS:
            if type(left) not in [int, float]:
                self.error("+ did not expect value of type {}".format(
                                                type(left).__name__))
            return left
        elif tok.get_type() is Token.NEGATION:
            if type(left) != bool:
                self.error("'not' expected a boolean, not a {}".format(
                                                type(left).__name__))
            return not left
        else:
            self.error("Could not evaluate {}".format(node))
            
    def visit_IOOp(self, node):
        """Handle I/O evaluation"""
        tok = node.token
        if tok.get_type() in [Token.READINT, Token.READFLOAT,
                            Token.READBOOL, Token.READ]:
            inp = input("[in]: ")
            # readint, readfloat and readbool require type conversion
            if tok.get_type() is Token.READINT:
                try:
                    inp = int(inp)
                except Exception:
                    self.error("Could not read an integer")
            elif tok.get_type() is Token.READFLOAT:
                try:
                    inp = float(inp)
                except Exception:
                    self.error("Could not read a float")
            elif tok.get_type() is Token.READBOOL:
                if inp in ["True", "False"]:
                    inp = eval(inp)
                else:
                    self.error("Could not read a boolean")
            var_name = node.left.token.value
            self.variables[var_name] = inp
            return inp
            
        elif tok.get_type() == Token.OUT:
            val = self.visit(node.left)
            print("[out]:", val)
            return val
            
        else:
            self.error("Unknown IO operator{}".format(tok))
    
    def visit_Control(self, node):
        """Handle the evaluation of control operators"""
        tok = node.token
        if tok.get_type() in [Token.STOP, Token.JUMPOVER]:
            return tok
        elif tok.get_type() in [Token.HALT, Token.RETURN]:
            # they may be returning a result; save it
            tok.value = self.visit(node.left)
            return tok
        else:
            self.error("Unknown control operator{}".format(tok))
            
    def visit_BinOp(self, node):
        """Handle the evaluation of generic binary operators"""
        tok = node.token
        if tok.get_type() is Token.SEPARATOR:
            # we may get a control token; these must be passed up
            # on the recursive calls to stop the program/alter the
            # flow of a loop construct
            r = self.visit(node.left)
            if isinstance(r, Token):
                if r.get_type() in [Token.JUMPOVER, Token.STOP,
                                    Token.HALT]:
                    return r
                    
            return self.visit(node.right)
        elif tok.get_type() is Token.ASSIGNMENT:
            var_name = node.left.token.value
            self.variables[var_name] = self.visit(node.right)
            return self.variables[var_name]
        else:
            raise InterpreterException(
                    "Unknown binary operator{}".format(tok))
            
    def visit_BoolBinOp(self, node):
        """Handle the evaluation of boolean binary operators"""
        tok = node.token
        
        left = self.visit(node.left)
        if type(left) != type(True):
            raise TypeException("LHS of {} should be a boolean".format(tok))
        right = self.visit(node.right)
        if type(right) != type(True):
            raise TypeException("RHS of {} should be a boolean".format(tok))
            
        if tok.get_type() is Token.AND:
            return left and right
        elif tok.get_type() is Token.OR:
            return left or right
        else:
            raise InterpreterException(
                    "Unknown boolean binary operator{}".format(tok))
            
    def visit_CompBinOp(self, node):
        """Handle the evaluation of comparison operators"""
        tok = node.token
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # does not need type checking
        if tok.get_type() is Token.EQUALITY:
            return left == right
        elif tok.get_type() is Token.INEQUALITY:
            return left != right
        
        # cannot compare strings or booleans with these operators
        if type(left) not in [int, float]:
            raise TypeException("LHS of {} operator cannot be of type {}".format(
                        tok.value, type(left).__name__))
        if type(right) not in [int, float]:
            raise TypeException("RHS of {} operator cannot be of type {}".format(
                        tok.value, type(right).__name__))
        if tok.get_type() is Token.GREATER:
            return left > right
        elif tok.get_type() is Token.LESSER:
            return left < right
        elif tok.get_type() is Token.GREATEREQUAL:
            return left >= right
        elif tok.get_type() is Token.LESSEREQUAL:
            return left <= right
        else:
            self.error("Unknown comparison binary operator{}".format(tok))
            
    def visit_ArithBinOp(self, node):
        """Handle the evaluation of arithmetic binary operators"""
        tok = node.token
        # do some type checking to enforce correct expressions
        left = self.visit(node.left)
        if type(left) not in [int, float, str]:
            raise TypeException("LHS of {} operator cannot be of type {}".format(
                        tok.value, type(left).__name__))
        right = self.visit(node.right)
        if type(right) not in [int, float, str]:
            raise TypeException("RHS of {} operator cannot be of type {}".format(
                        tok.value, type(right).__name__))
        if tok.get_type() is Token.PLUS:
            return left + right
            
        # Token.PLUS is the only one to handle anything beyond numbers
        if type(left) not in [int, float]:
            raise TypeException("LHS of {} operator cannot be of type {}".format(
                        tok.value, type(left).__name__))
        if type(right) not in [int, float]:
            raise TypeException("RHS of {} operator cannot be of type {}".format(
                        tok.value, type(right).__name__))
        if tok.get_type() is Token.MINUS:
            return left - right
        elif tok.get_type() is Token.PRODUCT:
            return left * right
        elif tok.get_type() is Token.DIVISION:
            return left / right
        elif tok.get_type() is Token.POWER:
            return pow(left, right)
        else:
            self.error("Unknown arithmetic binary operator{}".format(tok))
            
    def error(self, msg):
        print(msg)
        exit()

if __name__ == "__main__":
    while True:
        expr = input(">> ")
        try:
            tree = Parser(expr)
        except RojException as e:
            print("{}: {}".format(e.name, "; ".join(e.args)))
            continue
        #print(tree.tokens)
        try:
            tree.get_program()
        except RojException as e:
            print("{}: {}".format(e.name, "; ".join(e.args)))
            continue
        try:
            interpreter = Interpreter(tree)
        except RojException as e:
            print("{}: {}".format(e.name, "; ".join(e.args)))
            continue
        #tree.show()
        try:
            interpreter.evaluate()
        except RojException as e:
            print("{}: {}".format(e.name, "; ".join(e.args)))
            continue