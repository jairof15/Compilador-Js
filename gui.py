import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font
import subprocess
import sys
import os
import tempfile
from lexer import tokenize
from parser import parser

class CompiladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador JavaScript")
        self.root.geometry("1400x800")
        
        # Crear fuente monoespaciada
        self.code_font = Font(family="Consolas", size=11)
        
        # Lista de tokens almacenados
        self.current_tokens = []
        
        # Estado de los filtros
        self.filter_states = {
            "KEYWORD": tk.BooleanVar(value=True),
            "IDENTIFIER": tk.BooleanVar(value=True),
            "PUNCTUATION": tk.BooleanVar(value=True),
            "COMMENT": tk.BooleanVar(value=True),
            "EOF": tk.BooleanVar(value=True)
        }
        
        # Configurar colores
        self.colors = {
            'NORMAL': '#000000',    # Negro para tokens y AST
            'ERROR': '#FF0000',     # Rojo para errores
            'SUCCESS': '#FFFFFF',   # Blanco para mensajes de éxito en consola
            'OUTPUT': '#FFFFFF',    # Blanco para salida en consola
            'INFO': '#FFFFFF',      # Blanco para información en consola
            'COMMENT': '#000000',   # Negro
            'KEYWORD': '#000000',   # Negro
            'STRING': '#000000',    # Negro
            'NUMBER': '#000000',    # Negro
            'OPERATOR': '#000000'   # Negro
        }
        
        # Crear el layout principal
        self.create_layout()

    def create_layout(self):
        # Panel principal horizontal
        main_panel = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Panel izquierdo (editor y consola)
        left_panel = ttk.PanedWindow(main_panel, orient=tk.VERTICAL)
        main_panel.add(left_panel)

        # Editor de código
        editor_frame = ttk.LabelFrame(left_panel, text="Editor JavaScript")
        left_panel.add(editor_frame)

        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=self.code_font,
            background="#1e1e1e",
            foreground="#d4d4d4",
            insertbackground="#d4d4d4",
            selectbackground="#264F78",
            selectforeground="#d4d4d4",
            height=20,
            padx=5,
            pady=5
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        # Botones
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.compile_button = ttk.Button(
            button_frame,
            text="Compilar",
            command=self.compile_code
        )
        self.compile_button.pack(side=tk.LEFT, padx=5)

        self.run_button = ttk.Button(
            button_frame,
            text="Ejecutar (F5)",
            command=self.run_code
        )
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(
            button_frame,
            text="Limpiar Consola",
            command=self.clear_console
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Consola de salida
        console_frame = ttk.LabelFrame(left_panel, text="Consola")
        left_panel.add(console_frame)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=self.code_font,
            background="#1e1e1e",
            foreground="#FFFFFF",
            insertbackground="#FFFFFF",
            height=10,
            padx=5,
            pady=5
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        # Panel derecho (análisis)
        right_panel = ttk.PanedWindow(main_panel, orient=tk.VERTICAL)
        main_panel.add(right_panel)

        # Sección de Tokens
        tokens_frame = ttk.LabelFrame(right_panel, text="Tokens")
        right_panel.add(tokens_frame)

        # Filtros de tokens
        filter_frame = ttk.Frame(tokens_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Filtrar por tipo:").pack(side=tk.LEFT)
        
        for filter_type in self.filter_states.keys():
            btn = ttk.Checkbutton(
                filter_frame,
                text=filter_type,
                variable=self.filter_states[filter_type],
                command=self.apply_token_filters
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.tokens_list = scrolledtext.ScrolledText(
            tokens_frame,
            wrap=tk.NONE,
            font=self.code_font,
            background="white",
            foreground="black",
            height=8
        )
        self.tokens_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sección de AST
        ast_frame = ttk.LabelFrame(right_panel, text="AST")
        right_panel.add(ast_frame)

        self.ast_view = scrolledtext.ScrolledText(
            ast_frame,
            wrap=tk.NONE,
            font=self.code_font,
            background="white",
            foreground="black",
            height=8
        )
        self.ast_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sección de Errores
        errors_frame = ttk.LabelFrame(right_panel, text="Errores")
        right_panel.add(errors_frame)

        self.error_list = scrolledtext.ScrolledText(
            errors_frame,
            wrap=tk.NONE,
            font=self.code_font,
            background="white",
            foreground="black",
            height=6
        )
        self.error_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurar atajo de teclado F5 para ejecutar
        self.root.bind('<F5>', lambda e: self.run_code())

        # Configurar colores para todos los widgets de texto
        for widget in [self.console, self.tokens_list, self.ast_view, self.error_list]:
            for color_name, color_value in self.colors.items():
                widget.tag_config(color_name, foreground=color_value)

    def write_to_console(self, text, color='OUTPUT'):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text + '\n', color)
        self.console.config(state=tk.DISABLED)
        self.console.see(tk.END)

    def write_to_tokens(self, text, color='NORMAL'):
        self.tokens_list.config(state=tk.NORMAL)
        self.tokens_list.insert(tk.END, text + '\n', color)
        self.tokens_list.config(state=tk.DISABLED)
        self.tokens_list.see(tk.END)

    def write_to_ast(self, text, color='NORMAL'):
        self.ast_view.config(state=tk.NORMAL)
        self.ast_view.insert(tk.END, text + '\n', color)
        self.ast_view.config(state=tk.DISABLED)
        self.ast_view.see(tk.END)

    def write_to_errors(self, text, color='ERROR'):
        self.error_list.config(state=tk.NORMAL)
        self.error_list.insert(tk.END, text + '\n', color)
        self.error_list.config(state=tk.DISABLED)
        self.error_list.see(tk.END)

    def clear_outputs(self):
        for widget in [self.tokens_list, self.ast_view, self.error_list]:
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.config(state=tk.DISABLED)

    def clear_console(self):
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)

    def apply_token_filters(self):
        self.tokens_list.config(state=tk.NORMAL)
        self.tokens_list.delete(1.0, tk.END)
        
        token_categories = {
            "KEYWORD": ['IF', 'ELSE', 'WHILE', 'FUNCTION', 'RETURN', 'VAR', 'LET', 'CONST'],
            "IDENTIFIER": ['ID'],
            "PUNCTUATION": ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'GT', 'LT'],
            "COMMENT": ['COMMENT'],
            "EOF": ['EOF']
        }
        
        for token in self.current_tokens:
            token_category = None
            for category, types in token_categories.items():
                if token.type in types:
                    token_category = category
                    break
            
            if token_category and self.filter_states[token_category].get():
                self.write_to_tokens(
                    f"{token.type:<15} {str(token.value):<20} Línea {token.lineno}, Columna {token.column}",
                    'NORMAL'
                )
        
        self.tokens_list.config(state=tk.DISABLED)

    def compile_code(self):
        self.clear_outputs()
        code = self.code_editor.get(1.0, tk.END).strip()
        
        if not code:
            self.write_to_errors("Error: No hay código para compilar")
            return

        # Análisis léxico
        try:
            self.current_tokens = tokenize(code)
            # Mostrar cada token con su tipo y valor
            for token in self.current_tokens:
                token_value = str(token.value)
                if token.type == 'STRING':
                    token_value = f'"{token_value}"'
                elif token.type == 'COMMENT':
                    token_value = f'// {token_value}'
                
                self.write_to_tokens(
                    f"{token.type:<15} {token_value:<30} Línea {token.lineno}, Columna {token.column}",
                    'NORMAL'
                )
            self.write_to_console("Análisis léxico completado", 'NORMAL')
        except Exception as e:
            error_msg = f"Error léxico: {str(e)}"
            self.write_to_errors(error_msg)
            self.write_to_console(error_msg, 'ERROR')
            return

        # Análisis sintáctico
        try:
            self.ast = parser.parse(code)
            if self.ast:
                self.write_to_ast("Árbol de Sintaxis Abstracta (AST):\n", 'INFO')
                self.write_to_ast(str(self.ast), 'NORMAL')
                self.write_to_console("Análisis sintáctico completado", 'SUCCESS')
            else:
                error_msg = "No se pudo generar el AST"
                self.write_to_errors(error_msg)
                self.write_to_console(error_msg, 'ERROR')
                return
        except Exception as e:
            error_msg = f"Error sintáctico: {str(e)}"
            self.write_to_errors(error_msg)
            self.write_to_console(error_msg, 'ERROR')
            return

    def run_code(self):
        code = self.code_editor.get(1.0, tk.END).strip()
        
        if not code:
            self.write_to_console("Error: No hay código para ejecutar", 'ERROR')
            return

        try:
            # Crear un archivo temporal con el código
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Ejecutar el código con Node.js
            try:
                result = subprocess.run(
                    ['node', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=5  # 5 segundos de timeout
                )
                
                # Mostrar la salida
                if result.stdout:
                    self.write_to_console(result.stdout.strip(), 'OUTPUT')
                
                # Mostrar errores si los hay
                if result.stderr:
                    self.write_to_console(result.stderr.strip(), 'ERROR')
                elif result.returncode == 0 and not result.stdout:
                    self.write_to_console("Código ejecutado correctamente", 'SUCCESS')
                    
            except subprocess.TimeoutExpired:
                self.write_to_console("Error: La ejecución del código tardó demasiado tiempo", 'ERROR')
            except FileNotFoundError:
                self.write_to_console("Error: Node.js no está instalado. Por favor, instala Node.js para ejecutar código JavaScript.", 'ERROR')
            
        except Exception as e:
            self.write_to_console(f"Error inesperado: {str(e)}", 'ERROR')
        finally:
            # Limpiar el archivo temporal
            try:
                os.unlink(temp_file_path)
            except:
                pass

def main():
    root = tk.Tk()
    app = CompiladorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 