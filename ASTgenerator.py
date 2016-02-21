### Builds on what I have from the parserInterpreter.py file
### Parses input and builds an AST representation for it

from scanner import Scanner
from tokenizer import Tokenizer, Token

### Supported Grammar
# program : expr (Token.SEPARATOR expr)* Token.SEPARATOR? Token.EOF
# expr : term ((Token.PLUS | Token.MINUS) term)*
# term : power ((Token.PRODUCT | Token.DIVISION) power)*
# power : base (Token.POWER base)*
# base : Token.MINUS base | Token.LGROUP expr Token.RGROUP |
#                           Token.INTEGER | Token.FLOAT

class Node(object):
    def __init__(self, token, parent=None,
                                children=None):
        self.token = token
        self.parent = parent
        if children:
            for child in children:
                child.parent = self
        
    def __str__(self):
        if self.left is None:
            l = "None"
        else:
            l = str(self.left.token)
            
        if self.right is None:
            r = "None"
        else:
            r = str(self.right.token)
            
        s = "{}[ {} ]: l = {} | r = {}".format(
                                self.__name__, str(self.token), l, r)
        return s
        
    def get_strings(self):
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
    def __init__(self, token, parent=None, child=None):
        children = [child] if child else []
        Node.__init__(self, token, parent, children)
        self.left = child
        self.right = None
        
class BinOp(Node):
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
        
class Literal(Node):
    def __init__(self, token, parent=None):
        Node.__init__(self, token, parent, [])
        self.left = self.right = None

class Parser(object):
    def __init__(self, expression):
        self.sc = Scanner(expression)
        self.tok = Tokenizer(self.sc)
        self.tokens = None
        self.tokens = self.get_token_sequence()
        self.root = None
        
    def get_token_sequence(self):
        if self.tokens is not None:
            return self.tokens[::]
            
        self.tokens = []
        
        self.tokens.append(self.tok.get_next_token())
        while self.tokens[-1].get_type() != Token.EOF:
            self.tokens.append(self.tok.get_next_token())
            
        return self.tokens[::]
        
    def generate_tree(self):
        # get the expression subtree
        subtree = self.get_expr()
        
        while self.tokens[0].get_type() is Token.SEPARATOR:
            tok = self.tokens[0]
            # the subtree we already have becomes the left node
            self.tokens = self.tokens[1:]
            # if we got to the end there is no right child
            if self.tokens[0].get_type() is Token.EOF:
                right = None
            # fetch the subtree to the right of the separator node
            else:
                right = self.get_expr()
                
            subtree = BinOp(tok, parent=None, left_child=subtree,
                                                right_child=right)
                                                
        # the subtree we got so far is the only child of the EOF node
        if self.tokens[0].get_type() is Token.EOF:
            self.root = UnOp(Token.EOF, parent=None, child=subtree)
        # something weird happened! :D
        else:
            self.error("Program did not terminate with expected EOF")
    
    def get_expr(self):
        subtree = self.get_term()
        
        while self.tokens[0].get_type() in (Token.PLUS,
                                            Token.MINUS):
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            # set the left subtree, get the right child
            subtree = BinOp(tok, parent=None,
                        left_child=subtree, right_child=self.get_term())
                
        return subtree
        
    def get_term(self):
        subtree = self.get_power()
        
        # do we have a * or / operator? if so, create its node
        while self.tokens[0].get_type() in (Token.PRODUCT,
                                            Token.DIVISION):
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            # set the left subtree, get the right child
            subtree = BinOp(tok, parent=None,
                    left_child=subtree, right_child=self.get_power())
            
        return subtree
        
    def get_power(self):
        subtree = self.get_base()
        
        # do we have a power operator here?
        while self.tokens[0].get_type() is Token.POWER:
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            # if so, create its node and set the left subtree
            # get the right child subtree
            subtree = BinOp(tok, parent=None,
                            left_child=subtree, right_child=self.get_base())
            
        return subtree
    
    def get_base(self):
        tok = self.tokens[0]
        self.tokens = self.tokens[1:]
        
        # if we find a ( we must get the corresponding subtree
        if tok.get_type() in (Token.INTEGER, Token.FLOAT):
            return Literal(tok)
        elif tok.get_type() is Token.LGROUP:
            # get the subtree
            subtree = self.get_expr()
            tok = self.tokens[0]
            self.tokens = self.tokens[1:]
            # right enclosing parenthesis was found, return subtree
            if tok.get_type() is not Token.RGROUP:
                self.error("Unmatched left parenthesis")
            return base
        elif tok.get_type() is Token.MINUS:
            return UnOp(tok, parent=None, child=self.get_base())
        else:
            self.error("Unexpected {} Token".format(tok.get_type()))
        
    def error(self, msg):
        raise Exception(msg)
        
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

if __name__ == "__main__":
    while True:
        expr = input(">> ")
        tree = Parser(expr)
        tree.generate_tree()
        tree.show()