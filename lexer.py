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
    'LBRACKET',
    'RBRACKET',
    'SEMICOLON',
    'COMMA',
    'EQUALS',
    'NOTEQUALS',
    'GT',  # Mayor que
    'LT',  # Menor que
    'DOT',  # Punto para acceso a métodos
    'ARROW',
    'COMMENT',
    'TERNARY',
    'COLON'
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
    'console': 'CONSOLE',  # Agregar console como palabra reservada
    'log': 'LOG',
    'async': 'ASYNC',
    'await': 'AWAIT',
    'new': 'NEW',
    'Promise': 'PROMISE'
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
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_GT = r'>'
t_LT = r'<'
t_DOT = r'\.'  # Agregar regla para el punto
t_ARROW = r'=>'
t_TERNARY = r'\?'
t_COLON = r':'

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
    r'[a-zA-Z_][a-zA-Z0-9_]*'
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
    t.value = t.value[2:].strip()  # Remover // y espacios en blanco
    return t

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