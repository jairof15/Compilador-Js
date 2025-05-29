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
        self.current_scope = SymbolTable()
        self.errors = []

    def analyze(self, node):
        if not node:
            return

        if node.type == 'Program':
            self._analyze_program(node)
        elif node.type == 'VarDeclaration':
            self._analyze_var_declaration(node)
        elif node.type == 'Assignment':
            self._analyze_assignment(node)
        elif node.type == 'FunctionDeclaration':
            self._analyze_function_declaration(node)
        
        # Analizar recursivamente los hijos del nodo
        for child in node.children:
            self.analyze(child)

    def _analyze_program(self, node):
        pass  # El nodo programa no requiere análisis específico

    def _analyze_var_declaration(self, node):
        if not node.leaf:
            return
        
        var_name = node.leaf.get('id')
        var_type = node.leaf.get('type')
        
        # Verificar si la variable ya está declarada en el scope actual
        if self.current_scope.lookup(var_name):
            self.errors.append(f"Error semántico: Variable '{var_name}' ya declarada")
        else:
            self.current_scope.insert(var_name, var_type)

    def _analyze_assignment(self, node):
        if not node.leaf:
            return
        
        var_name = node.leaf.get('id')
        
        # Verificar si la variable está declarada
        if not self.current_scope.lookup(var_name):
            self.errors.append(f"Error semántico: Variable '{var_name}' no declarada")

    def _analyze_function_declaration(self, node):
        if not node.leaf:
            return
        
        func_name = node.leaf.get('id')
        
        # Crear un nuevo scope para la función
        new_scope = SymbolTable()
        new_scope.parent = self.current_scope
        old_scope = self.current_scope
        self.current_scope = new_scope
        
        # Analizar el cuerpo de la función
        for child in node.children:
            self.analyze(child)
        
        # Restaurar el scope anterior
        self.current_scope = old_scope

    def get_errors(self):
        return self.errors 