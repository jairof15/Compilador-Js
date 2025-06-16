import ply.yacc as yacc
from lexer import tokens
from semantic_analyzer import SemanticAnalyzer
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
    '''program : statements
               | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = Node('Program', [p[1]])
    else:
        p[0] = Node('Program', [])

def p_statements(p):
    '''statements : statement
                 | statements statement
                 | empty'''
    if len(p) == 2 and p[1] is not None:
        if isinstance(p[1], list):
            p[0] = Node('Statements', p[1])
        else:
            p[0] = Node('Statements', [p[1]])
    elif len(p) == 3:
        p[1].children.append(p[2])
        p[0] = p[1]
    else:
        p[0] = Node('Statements', [])

def p_statement_missing_semicolon(p):
    '''statement : expression
                 | declaration
                 | assignment
                 | method_call'''
    raise SyntaxError(f"Error: Falta punto y coma al final de la instrucción en la línea {p.lineno(1)}.")

def p_statement(p):
    '''statement : expression SEMICOLON
                | declaration SEMICOLON
                | assignment SEMICOLON
                | method_call SEMICOLON
                | function_declaration
                | if_statement
                | while_statement
                | for_statement
                | break_statement
                | switch_statement
                | try_catch_statement
                | throw_statement'''
    p[0] = Node('Statement', [p[1]])

def p_function_declaration(p):
    '''function_declaration : FUNCTION ID LPAREN parameter_list RPAREN block'''
    p[0] = Node('FunctionDeclaration', [
        Node('Identifier', value=p[2]),
        p[4],  # parameter_list
        p[6]   # block (statements)
    ])

def p_parameter_list(p):
    '''parameter_list : 
                     | ID
                     | parameter_list COMMA ID'''
    if len(p) == 1:
        p[0] = Node('Parameters', [])
    elif len(p) == 2:
        p[0] = Node('Parameters', [Node('Parameter', value=p[1])])
    else:
        p[1].children.append(Node('Parameter', value=p[3]))
        p[0] = p[1]

def p_statement_return(p):
    '''statement : RETURN expression SEMICOLON'''
    p[0] = Node('Return', [p[2]])

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
    '''expression : expression QUESTION expression COLON expression
                 | term
                 | expression PLUS term
                 | expression MINUS term
                 | expression GT term
                 | expression LT term
                 | expression GE term
                 | expression LE term
                 | expression EQUALS term
                 | expression NOTEQUALS term
                 | expression AND term
                 | expression OR term
                 | array_literal
                 | array_access'''
    if len(p) == 6:
        p[0] = Node('TernaryOp', [p[1], p[3], p[5]])
    elif len(p) == 2:
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
              | method_call
              | function_call
              | array_access
              | property_access
              | NOT factor
              | object_literal
              | arrow_function
              | anonymous_function
              | TRUE
              | FALSE'''
    if len(p) == 2:
        if isinstance(p[1], Node):
            p[0] = p[1]
        else:
            if isinstance(p[1], (int, float)):
                p[0] = Node('Number', value=p[1])
            elif p.slice[1].type == 'STRING':
                p[0] = Node('String', value=p[1])
            elif p[1] == 'true':
                p[0] = Node('Boolean', value=True)
            elif p[1] == 'false':
                p[0] = Node('Boolean', value=False)
            elif p.slice[1].type == 'TRUE':
                p[0] = Node('Boolean', value=True)
            elif p.slice[1].type == 'FALSE':
                p[0] = Node('Boolean', value=False)
            else:
                p[0] = Node('Identifier', value=p[1])
    else:
        p[0] = Node('UnaryOp', [p[2]], value=p[1])

def p_function_call(p):
    '''function_call : ID LPAREN arguments RPAREN'''
    p[0] = Node('FunctionCall', [Node('Identifier', value=p[1]), p[3]])

def p_method_call(p):
    '''method_call : console_log
                  | ID DOT ID LPAREN arguments RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        object_node = Node('Identifier', value=p[1])
        method_node = Node('Identifier', value=p[3])
        p[0] = Node('MethodCall', [object_node, method_node, p[5]])

def p_console_log(p):
    '''console_log : CONSOLE DOT LOG LPAREN arguments RPAREN'''
    p[0] = Node('ConsoleLog', [p[5]])

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

def p_if_statement(p):
    '''if_statement : IF LPAREN condition RPAREN block
                   | IF LPAREN condition RPAREN block ELSE block'''
    if len(p) == 6:  # if sin else
        p[0] = Node('IfStatement', [p[3], p[5]])
    else:  # if con else
        p[0] = Node('IfStatement', [p[3], p[5], p[7]])

def p_condition(p):
    '''condition : expression
                | expression GT expression
                | expression LT expression
                | expression GE expression
                | expression LE expression
                | expression EQUALS expression
                | expression NOTEQUALS expression'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node('Condition', [p[1], p[3]], value=p[2])

def p_array_literal(p):
    '''array_literal : LBRACKET array_elements RBRACKET'''
    p[0] = Node('ArrayLiteral', [p[2]])

def p_array_elements(p):
    '''array_elements : 
                     | expression
                     | array_elements COMMA expression'''
    if len(p) == 1:
        p[0] = Node('ArrayElements', [])
    elif len(p) == 2:
        p[0] = Node('ArrayElements', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

def p_array_access(p):
    '''array_access : ID LBRACKET expression RBRACKET'''
    p[0] = Node('ArrayAccess', [Node('Identifier', value=p[1]), p[3]])

def p_while_statement(p):
    'while_statement : WHILE LPAREN condition RPAREN block'
    p[0] = Node('WhileStatement', [p[3], p[5]])

def p_block(p):
    'block : LBRACE statements RBRACE'
    p[0] = p[2]

def p_empty(p):
    'empty :'
    p[0] = None

def p_property_access(p):
    'property_access : ID DOT ID'
    p[0] = Node('PropertyAccess', [Node('Identifier', value=p[1]), Node('Identifier', value=p[3])])

def p_break_statement(p):
    'break_statement : BREAK SEMICOLON'
    p[0] = Node('Break')

def p_for_statement(p):
    'for_statement : FOR LPAREN for_init SEMICOLON for_condition SEMICOLON for_update RPAREN block'
    p[0] = Node('ForStatement', [p[3], p[5], p[7], p[9]])

def p_for_init(p):
    '''for_init : declaration
               | assignment
               | empty'''
    p[0] = p[1]

def p_for_condition(p):
    '''for_condition : expression
                    | empty'''
    p[0] = p[1]

def p_for_update(p):
    '''for_update : assignment
                 | expression
                 | empty'''
    p[0] = p[1]

def get_token_position(p, index):
    try:
        token = p.slice[index]
        return f"línea {token.lineno}, columna {token.lexpos}"
    except:
        return "posición desconocida"

def p_error(p):
    if p:
        code_lines = p.lexer.lexdata.splitlines()
        lineno = p.lineno
        context_line = code_lines[lineno-1] if 1 <= lineno <= len(code_lines) else ''
        # Si el error ocurre al inicio de una línea, sugiere revisar la línea anterior
        if lineno > 1 and (p.lexpos - p.lexer.linestart) == 0:
            prev_line = code_lines[lineno-2]
            error_msg = (
                f"Error sintáctico cerca de la línea {lineno}:\n"
                f"       {prev_line}\n"
                f"Sugerencia: Revisa si falta un punto y coma al final de la línea anterior.\n"
                f"       {context_line}\n"
                f"       ^"
            )
        else:
            error_msg = f"Error sintáctico: Error de sintaxis en '{p.value}' en la línea {p.lineno}:\n"
            error_msg += f"       {context_line}\n"
            error_msg += f"       {' ' * (p.lexpos - p.lexer.linestart)}^\n"
        raise SyntaxError(error_msg)
    else:
        raise SyntaxError("Error sintáctico: Fin de archivo inesperado")

def p_object_literal(p):
    'object_literal : LBRACE object_properties RBRACE'
    p[0] = Node('ObjectLiteral', [p[2]])

def p_object_properties(p):
    '''object_properties : object_property
                        | object_properties COMMA object_property
                        | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = []

def p_object_property(p):
    'object_property : ID COLON expression'
    p[0] = (p[1], p[3])

def p_arrow_function(p):
    'arrow_function : LPAREN parameter_list RPAREN ARROW expression'
    p[0] = Node('ArrowFunction', [p[2], p[5]])

def p_switch_statement(p):
    'switch_statement : SWITCH LPAREN expression RPAREN LBRACE case_blocks default_block RBRACE'
    p[0] = Node('SwitchStatement', [p[3], p[6], p[7]])

def p_case_blocks(p):
    '''case_blocks : case_blocks case_block
                  | case_block'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_case_block_error(p):
    '''case_block : CASE error COLON'''
    error_msg = f"Error sintáctico: Se esperaba una expresión después de 'case' en la línea {p.lineno(1)}"
    raise SyntaxError(error_msg)

def p_case_block(p):
    'case_block : CASE expression COLON statements'
    p[0] = (p[2], p[4])

def p_default_block(p):
    '''default_block : DEFAULT COLON statements
                    | empty'''
    if len(p) == 4:
        p[0] = p[3]
    else:
        p[0] = None

def p_anonymous_function(p):
    'anonymous_function : FUNCTION LPAREN parameter_list RPAREN block'
    p[0] = Node('AnonymousFunction', [p[3], p[5]])

def p_try_catch_statement(p):
    'try_catch_statement : TRY block CATCH LPAREN ID RPAREN block'
    p[0] = Node('TryCatch', [p[2], p[5], p[7]])

def p_throw_statement(p):
    'throw_statement : THROW expression SEMICOLON'
    p[0] = Node('Throw', [p[2]])

# --- Reglas de manejo de errores sintácticos específicas ---

def p_if_statement_error(p):
    '''if_statement : IF error block'''
    error_msg = f"Error sintáctico: Se esperaba una condición válida después de 'if' en la línea {p.lineno(1)}"
    raise SyntaxError(error_msg)

def p_declaration_error_id(p):
    '''declaration : VAR error
                   | LET error
                   | CONST error'''
    error_msg = f"Error sintáctico: Se esperaba un identificador después de la palabra clave en la línea {p.lineno(1)}."
    raise SyntaxError(error_msg)

def p_switch_statement_error(p):
    '''switch_statement : SWITCH error block'''
    error_msg = f"Error sintáctico: Se esperaba una expresión válida después de 'switch' en la línea {p.lineno(1)}"
    raise SyntaxError(error_msg)

def p_for_statement_error(p):
    '''for_statement : FOR error block'''
    error_msg = f"Error sintáctico: Se esperaba una declaración válida después de 'for' en la línea {p.lineno(1)}"
    raise SyntaxError(error_msg)

# --- Reglas de error sintáctico personalizadas ---

def p_if_statement_error_paren(p):
    '''if_statement : IF LPAREN error block'''
    raise SyntaxError(f"Error: Paréntesis sin cerrar en la condición del if en la línea {p.lineno(1)}.")

def p_block_missing_rbrace(p):
    '''block : LBRACE statements error'''
    raise SyntaxError(f"Error: Falta llave de cierre '}}' en el bloque iniciado en la línea {p.lineno(1)}.")

def p_function_declaration_error_params(p):
    '''function_declaration : FUNCTION ID LPAREN error RPAREN block'''
    raise SyntaxError(f"Error: Error en la lista de parámetros de la función en la línea {p.lineno(1)}.")

def p_case_block_error_colon(p):
    '''case_block : CASE error COLON statements'''
    raise SyntaxError(f"Error: Se esperaba una expresión después de 'case' en la línea {p.lineno(1)}.")

def p_switch_statement_error_paren(p):
    '''switch_statement : SWITCH LPAREN error RPAREN LBRACE case_blocks default_block RBRACE'''
    raise SyntaxError(f"Error: Paréntesis sin cerrar en la condición del switch en la línea {p.lineno(1)}.")

# Construir el parser
parser = yacc.yacc()

def parse(data):
    try:
        result = parser.parse(data)
        if result is None:
            return None  # No hacer análisis semántico si el AST no se pudo construir
        # Realizar análisis semántico
        analyzer = SemanticAnalyzer()
        analyzer.analyze(result)
        errors = analyzer.get_errors()
        if errors:
            return "\n".join(errors)  # Devuelve los errores como string
        return result
    except SyntaxError as e:
        return str(e)
    except Exception as e:
        return f"Error inesperado: {str(e)}" 