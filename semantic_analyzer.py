class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def insert(self, name, type, scope='global'):
        self.symbols[name] = {'type': type, 'scope': scope}

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]  # Lista de diccionarios para manejar scopes
        self.current_scope = 0
        self.errors = []

    def enter_scope(self):
        self.scopes.append({})
        self.current_scope += 1

    def exit_scope(self):
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1

    def declare_variable(self, name, node):
        if name in self.scopes[self.current_scope]:
            self.errors.append(f"Error semántico: La variable '{name}' ya fue declarada en este scope.")
            return False
        self.scopes[self.current_scope][name] = node
        return True

    def check_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        self.errors.append(f"Error semántico: La variable '{name}' no está declarada.")
        return False

    def analyze(self, ast):
        if ast is None:
            return
        
        if ast.type == 'Program':
            for child in ast.children:
                self.analyze(child)
            return
        
        elif ast.type == 'Statements':
            for child in ast.children:
                self.analyze(child)
            return
        
        elif ast.type == 'Declaration':
            if len(ast.children) > 0:
                var_name = ast.children[0].value
                self.declare_variable(var_name, ast)
            return
        
        elif ast.type == 'Assignment':
            if len(ast.children) > 0:
                var_name = ast.children[0].value
                if not self.check_variable(var_name):
                    self.errors.append(f"Error semántico: No se puede asignar a '{var_name}' porque no está declarada.")
            return
        
        elif ast.type == 'Identifier':
            if hasattr(ast, 'value') and ast.value is not None:
                if not self.check_variable(ast.value):
                    self.errors.append(f"Error semántico: La variable '{ast.value}' no está declarada.")
            return
        
        elif ast.type == 'FunctionDeclaration':
            # Registrar el nombre de la función en el scope actual
            func_name = ast.children[0].value
            self.declare_variable(func_name, ast)
            self.enter_scope()
            if len(ast.children) > 2:
                for param in ast.children[1].children:
                    self.declare_variable(param.value, param)
                self.analyze(ast.children[2])
            self.exit_scope()
            return
        
        elif ast.type == 'IfStatement':
            if len(ast.children) > 1:
                self.analyze(ast.children[0])
                self.enter_scope()
                self.analyze(ast.children[1])
                self.exit_scope()
                if len(ast.children) > 2:
                    self.enter_scope()
                    self.analyze(ast.children[2])
                    self.exit_scope()
            return
        
        elif ast.type == 'WhileStatement':
            if len(ast.children) > 1:
                self.analyze(ast.children[0])
                self.enter_scope()
                self.analyze(ast.children[1])
                self.exit_scope()
            return
        
        elif ast.type == 'ForStatement':
            if len(ast.children) > 3:
                self.enter_scope()
                self.analyze(ast.children[0])
                self.analyze(ast.children[1])
                self.analyze(ast.children[2])
                self.analyze(ast.children[3])
                self.exit_scope()
            return
        
        elif ast.type == 'SwitchStatement':
            if len(ast.children) > 1:
                self.analyze(ast.children[0])
                self.enter_scope()
                for case in ast.children[1].children:
                    self.analyze(case)
                self.exit_scope()
            return
        
        elif ast.type in ['String', 'Number', 'Boolean']:
            return
        
        # Analizar hijos recursivamente
        for child in ast.children:
            self.analyze(child)

    def get_errors(self):
        return self.errors 