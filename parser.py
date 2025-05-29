import ply.yacc as yacc
from lexer import tokens
import sys

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

    def __str__(self, level=0):
        ret = "  " * level + f"Type: {self.type}"
        if self.value is not None:
            ret += f", Value: {self.value}"
        ret += "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

def p_program(p):
    '''program : statements'''
    p[0] = Node('Program', [p[1]])

def p_statements(p):
    '''statements : statement
                 | statements statement'''
    if len(p) == 2:
        p[0] = Node('Statements', [p[1]])
    else:
        p[1].children.append(p[2])
        p[0] = p[1]

def p_statement(p):
    '''statement : expression SEMICOLON
                | declaration SEMICOLON
                | assignment SEMICOLON
                | method_call SEMICOLON'''
    p[0] = Node('Statement', [p[1]])

def p_declaration(p):
    '''declaration : VAR ID
                  | LET ID
                  | CONST ID
                  | VAR ID ASSIGN expression
                  | LET ID ASSIGN expression
                  | CONST ID ASSIGN expression'''
    if len(p) == 3:
        p[0] = Node('Declaration', [Node('Identifier', value=p[2])], value=p[1])
    else:
        p[0] = Node('Declaration', [Node('Identifier', value=p[2]), p[4]], value=p[1])

def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    p[0] = Node('Assignment', [Node('Identifier', value=p[1]), p[3]])

def p_expression(p):
    '''expression : term
                 | expression PLUS term
                 | expression MINUS term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node('BinaryOp', [p[1], p[3]], value=p[2])

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node('BinaryOp', [p[1], p[3]], value=p[2])

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | ID
              | LPAREN expression RPAREN
              | method_call'''
    if len(p) == 2:
        if isinstance(p[1], Node):
            p[0] = p[1]
        else:
            if isinstance(p[1], (int, float)):
                p[0] = Node('Number', value=p[1])
            elif isinstance(p[1], str):
                if p[1].startswith('"'):
                    p[0] = Node('String', value=p[1][1:-1])
                else:
                    p[0] = Node('Identifier', value=p[1])
    else:
        p[0] = p[2]

def p_method_call(p):
    '''method_call : CONSOLE DOT LOG LPAREN arguments RPAREN
                  | ID DOT ID LPAREN arguments RPAREN'''
    if p[1] == 'console' and p[3] == 'log':
        p[0] = Node('ConsoleLog', [p[5]])
    else:
        object_node = Node('Identifier', value=p[1])
        method_node = Node('Identifier', value=p[3])
        p[0] = Node('MethodCall', [object_node, method_node, p[5]])

def p_arguments(p):
    '''arguments : 
                | expression
                | arguments COMMA expression'''
    if len(p) == 1:
        p[0] = Node('Arguments', [])
    elif len(p) == 2:
        p[0] = Node('Arguments', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

def get_token_position(p, index):
    try:
        token = p.slice[index]
        return f"línea {token.lineno}, columna {token.lexpos}"
    except:
        return "posición desconocida"

def p_error(p):
    if p:
        error_msg = f"Error de sintaxis en '{p.value}' en la línea {p.lineno}, columna {getattr(p, 'column', '?')}"
    else:
        error_msg = "Error de sintaxis en EOF"
    raise SyntaxError(error_msg)

# Construir el parser
parser = yacc.yacc() 