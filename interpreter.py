class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.current_scope = self.variables

    def interpret(self, node):
        if node is None:
            return None

        method_name = f'interpret_{node.type}'
        method = getattr(self, method_name, self.generic_interpret)
        return method(node)

    def generic_interpret(self, node):
        if hasattr(node, 'children'):
            for child in node.children:
                self.interpret(child)
        return None

    def interpret_Program(self, node):
        for child in node.children:
            self.interpret(child)

    def interpret_Statements(self, node):
        for child in node.children:
            self.interpret(child)

    def interpret_Declaration(self, node):
        var_name = node.children[0].value
        if len(node.children) > 1:
            value = self.interpret(node.children[1])
            self.current_scope[var_name] = value
        else:
            self.current_scope[var_name] = None

    def interpret_Assignment(self, node):
        var_name = node.children[0].value
        value = self.interpret(node.children[1])
        self.current_scope[var_name] = value
        return value

    def interpret_BinaryOp(self, node):
        left = self.interpret(node.children[0])
        right = self.interpret(node.children[1])
        op = node.value

        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '&&':
            return left and right
        elif op == '||':
            return left or right

    def interpret_Number(self, node):
        return node.value

    def interpret_String(self, node):
        return node.value

    def interpret_Identifier(self, node):
        var_name = node.value
        if var_name in self.current_scope:
            value = self.current_scope[var_name]
            # Si es un array, agregar la propiedad length
            if isinstance(value, list):
                return {
                    'value': value,
                    'length': len(value)
                }
            return value
        raise Exception(f"Variable '{var_name}' no definida")

    def interpret_FunctionDeclaration(self, node):
        func_name = node.children[0].value
        params = node.children[1]
        body = node.children[2]
        self.functions[func_name] = {
            'params': params,
            'body': body
        }

    def interpret_FunctionCall(self, node):
        func_name = node.children[0].value
        args = node.children[1]

        if func_name not in self.functions:
            raise Exception(f"Función '{func_name}' no definida")

        func = self.functions[func_name]
        params = func['params']
        body = func['body']

        # Crear nuevo scope para la función
        old_scope = self.current_scope
        self.current_scope = {}
        
        # Asignar argumentos a parámetros
        for i, param in enumerate(params.children):
            param_name = param.value
            if i < len(args.children):
                self.current_scope[param_name] = self.interpret(args.children[i])
            else:
                self.current_scope[param_name] = None

        # Ejecutar cuerpo de la función
        result = self.interpret(body)
        
        # Restaurar scope anterior
        self.current_scope = old_scope
        
        return result

    def interpret_IfStatement(self, node):
        condition = self.interpret(node.children[0])
        if condition:
            return self.interpret(node.children[1])
        elif len(node.children) > 2:
            return self.interpret(node.children[2])
        return None

    def interpret_ArrayLiteral(self, node):
        return [self.interpret(child) for child in node.children[0].children]

    def interpret_ArrayAccess(self, node):
        array_name = node.children[0].value
        index = self.interpret(node.children[1])
        
        if array_name not in self.current_scope:
            raise Exception(f"Array '{array_name}' no definido")
            
        array = self.current_scope[array_name]
        if isinstance(array, dict) and 'value' in array:
            array = array['value']
            
        if not isinstance(array, list):
            raise Exception(f"'{array_name}' no es un array")
            
        if not isinstance(index, int):
            raise Exception("Índice debe ser un número entero")
            
        if index < 0 or index >= len(array):
            raise Exception("Índice fuera de rango")
            
        return array[index]

    def interpret_ConsoleLog(self, node):
        args = [self.interpret(arg) for arg in node.children[0].children]
        print(*args)
        return None

    def interpret_Break(self, node):
        raise BreakException()

    def interpret_WhileStatement(self, node):
        condition = node.children[0]
        body = node.children[1]
        while self.interpret(condition):
            try:
                self.interpret(body)
            except BreakException:
                break

    def interpret_PropertyAccess(self, node):
        obj = self.interpret(node.children[0])
        prop = node.children[1].value
        if isinstance(obj, dict) and prop in obj:
            return obj[prop]
        elif prop == 'length' and isinstance(obj, list):
            return len(obj)
        elif isinstance(obj, dict) and 'value' in obj and prop == 'length' and isinstance(obj['value'], list):
            return len(obj['value'])
        else:
            raise Exception(f"Propiedad '{prop}' no encontrada en el objeto")

    def interpret_UnaryOp(self, node):
        op = node.value
        value = self.interpret(node.children[0])
        if op == '!':
            return not value

    def interpret_ForStatement(self, node):
        init = node.children[0]
        condition = node.children[1]
        update = node.children[2]
        body = node.children[3]
        self.interpret(init)
        while True:
            if condition is not None and not self.interpret(condition):
                break
            try:
                self.interpret(body)
            except BreakException:
                break
            self.interpret(update)

    def interpret_ObjectLiteral(self, node):
        obj = {}
        for key, value_node in node.children[0]:
            obj[key] = self.interpret(value_node)
        return obj

    def interpret_MethodCall(self, node):
        obj_node = node.children[0]
        method_node = node.children[1]
        args_node = node.children[2]

        obj = self.interpret(obj_node)
        method = method_node.value
        args = [self.interpret(arg) for arg in args_node.children]

        if method == 'push':
            if isinstance(obj, list):
                obj.append(args[0])
                return None
            else:
                raise Exception("El método 'push' solo se puede usar en arrays")
        elif method == 'pop':
            if isinstance(obj, list):
                return obj.pop()
            else:
                raise Exception("El método 'pop' solo se puede usar en arrays")
        else:
            raise Exception(f"Método '{method}' no soportado")

    def interpret_TernaryOp(self, node):
        condition = self.interpret(node.children[0])
        if condition:
            return self.interpret(node.children[1])
        else:
            return self.interpret(node.children[2])

    def interpret_ArrowFunction(self, node):
        params = node.children[0]
        expr = node.children[1]
        def func(*args):
            old_scope = self.current_scope
            self.current_scope = {}
            for i, param in enumerate(params.children):
                self.current_scope[param.value] = args[i] if i < len(args) else None
            result = self.interpret(expr)
            self.current_scope = old_scope
            return result
        return func

    def interpret_SwitchStatement(self, node):
        expr = self.interpret(node.children[0])
        cases = node.children[1]
        default = node.children[2]
        for case_expr, case_stmts in cases:
            if self.interpret(case_expr) == expr:
                self.interpret(case_stmts)
                return
        if default is not None:
            self.interpret(default)

    def interpret_AnonymousFunction(self, node):
        params = node.children[0]
        body = node.children[1]
        def func(*args):
            old_scope = self.current_scope
            self.current_scope = {}
            for i, param in enumerate(params.children):
                self.current_scope[param.value] = args[i] if i < len(args) else None
            result = self.interpret(body)
            self.current_scope = old_scope
            return result
        return func

    def interpret_TryCatch(self, node):
        try_block = node.children[0]
        error_var = node.children[1]
        catch_block = node.children[2]
        try:
            self.interpret(try_block)
        except Exception as e:
            old_scope = self.current_scope
            self.current_scope = dict(old_scope)  # Copia el scope actual
            self.current_scope[error_var] = str(e)
            self.interpret(catch_block)
            self.current_scope = old_scope

    def interpret_Throw(self, node):
        value = self.interpret(node.children[0])
        raise Exception(value)

class BreakException(Exception):
    pass 