import ply.lex as lex

# Lista de tokens
tokens = [
    'NUMBER',
    'STRING',
    'ID',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ASSIGN',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',  # Para arrays [
    'RBRACKET',  # Para arrays ]
    'SEMICOLON',
    'COMMA',
    'COLON',  # Para objetos :
    'QUESTION', # Para operador ternario ?
    'ARROW',    # Para funciones flecha =>
    'EQUALS',
    'NOTEQUALS',
    'GT',  # Mayor que
    'LT',  # Menor que
    'GE',  # Mayor o igual que
    'LE',  # Menor o igual que
    'DOT',  # Punto para acceso a métodos
    'AND',  # Operador &&
    'OR',   # Operador ||
    'NOT',   # Operador !
    'TRUE',
    'FALSE'
]

# Palabras reservadas
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'var': 'VAR',
    'let': 'LET',
    'const': 'CONST',
    'console': 'CONSOLE',
    'log': 'LOG',
    'break': 'BREAK',
    'for': 'FOR',
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',
    'try': 'TRY',
    'catch': 'CATCH',
    'throw': 'THROW',
    'true': 'TRUE',
    'false': 'FALSE'
}

tokens = tokens + list(reserved.values())

# Reglas para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_COLON = r':'
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_GE = r'>='
t_LE = r'<='
t_GT = r'>'
t_LT = r'<'
t_DOT = r'\.'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_QUESTION = r'\?'
t_ARROW = r'=>'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

def t_STRING(t):
    r'\"([^\"\\]|\\.)*\"'
    t.value = t.value[1:-1]  # Remover las comillas
    return t

def t_NUMBER(t):
    r'\d*\.?\d+'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_\u00C0-\u00FF][a-zA-Z0-9_\u00C0-\u00FF]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Manejo de nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.linestart = t.lexer.lexpos

# Manejo de comentarios
def t_COMMENT(t):
    r'//.*'
    pass  # Ignorar comentarios, no devolver token

def t_error(t):
    error_msg = f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}, columna {t.lexpos - t.lexer.linestart}"
    t.lexer.skip(1)
    raise SyntaxError(error_msg)

# Construir el lexer
lexer = lex.lex()

def tokenize(data):
    lexer.input(data)
    lexer.lineno = 1
    lexer.linestart = 0
    tokens = []
    
    try:
        while True:
            tok = lexer.token()
            if not tok:
                break
            # Calcular la columna
            tok.column = tok.lexpos - lexer.linestart + 1
            tokens.append(tok)
        return tokens
    except SyntaxError as e:
        raise e
    except Exception as e:
        raise SyntaxError(f"Error durante el análisis léxico: {str(e)}") 