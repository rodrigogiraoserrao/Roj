### Implement the different exceptions thrown by the parser and interpreter

class RojException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.name = type(self).__name__
    
class TypeException(RojException):
    def __init__(self, *args):
        RojException.__init__(self, *args)
        
class SyntaticException(RojException):
    def __init__(self, *args):
        RojException.__init__(self, *args)
        
class ParserException(RojException):
    def __init__(self, *args):
        RojException.__init__(self, *args)
        
class InterpreterException(RojException):
    def __init__(self, *args):
        RojException.__init__(self, *args)