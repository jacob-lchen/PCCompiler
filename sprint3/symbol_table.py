from dataclasses import dataclass
from AST import Type as A_Type
from C_AST import Type as C_Type
from typing import Union, List, Dict
from AST import ParameterLst, PrimitiveType
from copy import deepcopy
import random

class ParseError(Exception): pass

@dataclass
class Variable():
    type: Union[A_Type,C_Type]

@dataclass
class Function():
    param_names: List[str]
    param_types: List[Union[A_Type,C_Type]]
    return_type: Union[Union[A_Type,C_Type], None]

@dataclass
class C_Function():
    hashed_name: str
    param_types: List[Union[A_Type,C_Type]]
    return_type: Union[Union[A_Type,C_Type], None]

@dataclass
class Functions():
    functions: List[Union[Function, C_Function]]

def _one_function_helper(param_name: str, param_type: str, return_type: Union[str, None]):
    return Functions([Function(param_names=[param_name], param_types=[A_Type(PrimitiveType(param_type))], return_type=A_Type(PrimitiveType(return_type)))])
    # return Functions([Function(param_names=[param_name], param_types=[], return_type=A_Type(PrimitiveType(return_type)))])

def _one_function_helper2(name, param_name: str, param_type: str, return_type: Union[str, None]):
    return Functions([C_Function(hashed_name=name, param_types=[C_Type(param_type + "_t")], return_type=A_Type(PrimitiveType(return_type)))])
    # return Functions([C_Function(hashed_name=name, param_types=[], return_type=A_Type(PrimitiveType(return_type)))])

global_functions: Dict[str, Functions] = {
    'print_int': _one_function_helper('var', 'int', 'none'),
    # 'print_float': _one_function_helper('var', 'float', 'none'),
    # # 'print_char': _one_function_helper('var', 'char', 'none'),
    # 'print_str': _one_function_helper('var', 'str', 'none'),
    # 'print_bool': _one_function_helper('var', 'bool', 'none'),
    # 'println_int': _one_function_helper('var', 'int', 'none'),
    # 'println_float': _one_function_helper('var', 'float', 'none'),
    # # 'println_char': _one_function_helper('var', 'char', 'none'),
    # 'println_str': _one_function_helper('var', 'str', 'none'),
    # 'println_bool': _one_function_helper('var', 'bool', 'none'),
    # 'input_int': _one_function_helper('prompt', 'str', 'int'),
    'input_int': _one_function_helper('prompt', 'none', 'int'),
    # 'input_float': _one_function_helper('prompt', 'str', 'float'),
    # # 'input_char': _one_function_helper('prompt', 'str', 'char'),
    # 'input_bool': _one_function_helper('prompt', 'str', 'bool'),
}
global_functions2: Dict[str, Functions] = {
    'print_int': _one_function_helper2('print_int', 'var', 'int', 'none'),
    # 'print_float': _one_function_helper2('print_float', 'var', 'float', 'none'),
    # # 'print_char': _one_function_helper2(# , 'var', 'char', 'none'),
    # 'print_str': _one_function_helper2('print_str', 'var', 'str', 'none'),
    # 'print_bool': _one_function_helper2('print_bool', 'var', 'bool', 'none'),
    # 'println_int': _one_function_helper2('println_int', 'var', 'int', 'none'),
    # 'println_float': _one_function_helper2('println_float', 'var', 'float', 'none'),
    # # 'println_char': _one_function_helper2(# , 'var', 'char', 'none'),
    # 'println_str': _one_function_helper2('println_str', 'var', 'str', 'none'),
    # 'println_bool': _one_function_helper2('println_bool', 'var', 'bool', 'none'),
    # # 'input_int': _one_function_helper2('input_int', 'prompt', 'str', 'int'),
    'input_int': _one_function_helper2('input_int', 'prompt', 'none', 'int'),
    # 'input_float': _one_function_helper2('input_float', 'prompt', 'str', 'float'),
    # # 'input_char': _one_function_helper2(# , 'prompt', 'str', 'char'),
    # 'input_bool': _one_function_helper2('input_bool', 'prompt', 'str', 'bool'),
}

class SymbolTable(object):
    """
    Base symbol table class
    """

    def __init__(self):
        self.scope_stack = deepcopy([global_functions2, global_functions])
        self.func_call_stack = []
        random.seed(9)
        self.random = random.sample(range(1000,9999),1000)

    def __repr__(self):
        from pprint import pformat
        return pformat({ 'Scope': self.scope_stack, 'Function Call': self.func_call_stack })

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        assert len(self.scope_stack) > 1
        self.scope_stack.pop()

    def create_name(self,name):
        return name+str(self.random.pop())

    def declare_variable(self, name: str, type: Union[A_Type,C_Type], line_number=-1):
        """
        Add a new variable.
        Need to do duplicate variable declaration error checking.
        """
        if name in self.scope_stack[-1]:
            raise ParseError("Redeclaring variable named \"" + name + "\"", line_number)
        self.scope_stack[-1][name] = Variable(type=type)

    def lookup_variable(self, name: str, line_number=-1):
        """
        Return the type of the variable named 'name', or throw
        a ParseError if the variable is not declared in the scope.
        """
        # You should traverse through the entire scope stack
        for scope in reversed(self.scope_stack):
            if name in scope:
                found = scope[name]
                assert isinstance(found, Variable), f"When looking for {name}, found function when expecting variable"
                return found.type
        raise ParseError("Referencing undefined variable \"" + name + "\"", line_number)


    def declare_function(self, name: str, params: ParameterLst, return_type: Union[Union[A_Type,C_Type], None], line_number=-1):
        param_types = [param.paramType for param in params]
        param_names = [param.var for param in params]
        function_to_be_declared = Function(param_names,param_types, return_type)
        if name in self.scope_stack[-1]:
            if isinstance(self.scope_stack[-1][name], Functions):
                for scope in reversed(self.scope_stack):
                    if name in scope:
                        assert isinstance(scope[name], Functions), "Expect function, got probably Variable"
                        for f in scope[name].functions:
                            if repr(f.param_types) == repr(param_types) or f.param_names == param_names:
                                raise ParseError("Re-declaring function with same param types \""+name+"\"", line_number)
                self.scope_stack[-1][name].functions.append(function_to_be_declared)
                return
            else:
                raise ParseError("Function \"" + name + "\" is previously declared as variable", line_number)
        self.func_call_stack.append(function_to_be_declared.return_type)
        self.scope_stack[-1][name] = Functions([function_to_be_declared])


    def lookup_function(self, name: str, param_types: List[Union[A_Type,C_Type]], line_number=-1):
        for scope in reversed(self.scope_stack):
            if name in scope:
                assert isinstance(scope[name], Functions), "Expect function, got probably Variable"
                for f in scope[name].functions:
                    if repr(f.param_types) == repr(param_types):
                        return f.return_type

        raise ParseError("Referencing undefined function \"" + name + "\"", line_number)

    def get_func_by_name(self,name:str,param_names:List[str]):
        for scope in reversed(self.scope_stack):
            if name in scope:
                for f in scope[name].functions:
                    if f.param_names == param_names:
                        return [f.param_types,f.return_type]
        raise ParseError("C_Gen: Referencing undefined function \"" + name + "\"")

    def declare_C_function(self, name: str, param_types: List[Union[A_Type, C_Type]],
                         return_type: Union[Union[A_Type, C_Type], None], line_number=-1):
        hash_name = self.create_name(name)
        function_to_be_declared = C_Function(hash_name,param_types, return_type)
        if name in self.scope_stack[-1]:
            self.scope_stack[-1][name].functions.append(function_to_be_declared)
            return hash_name
        self.scope_stack[-1][name] = Functions([function_to_be_declared])
        return hash_name

    # return the modified name and return type
    def get_C_function(self, name: str, param_types: List[C_Type], line_number=-1):
        for scope in reversed(self.scope_stack):
            if name in scope:
                for f in scope[name].functions:
                    if repr(f.param_types) == repr(param_types):
                        return f.hashed_name, f.return_type
        raise ParseError("C_Gen: Referencing undefined function \"" + name + "\"", line_number)

    def update_variable(self, name: str, type: Union[A_Type, C_Type], line_number=-1):
        found = None
        for scope in reversed(self.scope_stack):
            if name in scope:
                found = scope[name]
                found.type = type
        if not found:
            self.scope_stack[-1][name] = Variable(type=type)
