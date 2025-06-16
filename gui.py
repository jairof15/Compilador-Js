import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font
import subprocess
import sys
import os
import tempfile
from lexer import tokenize
from parser import parse
from ttkthemes import ThemedTk
from pygments import lex
from pygments.lexers import JavascriptLexer
from pygments.styles import get_style_by_name
import re

class LineNumberCanvas(tk.Canvas):
    def __init__(self, parent, text_widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = text_widget
        self.config(width=40)
        
        # Configuración de colores para los números de línea
        self.bg_color = "#1e1e1e"
        self.fg_color = "#6e7681"
        self.config(bg=self.bg_color, highlightthickness=0)
        
        self.text_widget.bind('<<Modified>>', self._on_change)
        self.text_widget.bind('<Configure>', self._on_change)
        self.text_widget.bind('<KeyRelease>', self._on_change)
        self.text_widget.bind('<MouseWheel>', self._on_change)
        
    def _on_change(self, event=None):
        self.redraw()
        
    def redraw(self):
        self.delete('all')
        
        # Obtener información sobre las líneas visibles
        first_line = self.text_widget.index("@0,0")
        last_line = self.text_widget.index("@0,%d" % self.text_widget.winfo_height())
        first_line_num = int(float(first_line))
        last_line_num = int(float(last_line))
        
        # Dibujar números de línea
        for line_num in range(first_line_num, last_line_num + 1):
            y_coord = self.text_widget.dlineinfo("%d.0" % line_num)
            if y_coord:
                self.create_text(
                    35,
                    y_coord[1] + y_coord[3]/2,
                    text=str(line_num),
                    anchor='e',
                    fill=self.fg_color,
                    font=self.text_widget['font']
                )

class CompiladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador JavaScript")
        self.root.geometry("1400x800")
        
        # Configurar tema oscuro
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()
        style.configure(".", background="#1e1e1e", foreground="#d4d4d4")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#d4d4d4")
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#d4d4d4")
        
        # Configurar estilo de botones
        style.configure("Blue.TButton",
            background="#0078d4",
            foreground="white",
            padding=(10, 5),
            relief="flat"
        )
        style.map("Blue.TButton",
            background=[("active", "#1e90ff"), ("pressed", "#005fb8")],
            relief=[("pressed", "sunken")]
        )
        
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
            'NORMAL': '#FFFFFF',    # Blanco para tokens y AST
            'ERROR': '#FF0000',     # Rojo para errores
            'SUCCESS': '#FFFFFF',   # Blanco para mensajes de éxito en consola
            'OUTPUT': '#FFFFFF',    # Blanco para salida en consola
            'INFO': '#FFFFFF',      # Blanco para información en consola
            'COMMENT': '#FFFFFF',   # Blanco
            'KEYWORD': '#FFFFFF',   # Blanco
            'STRING': '#FFFFFF',    # Blanco
            'NUMBER': '#FFFFFF',    # Blanco
            'OPERATOR': '#FFFFFF'   # Blanco
        }
        
        # Configurar colores de sintaxis
        self.syntax_colors = {
            'Token.Keyword': '#569cd6',
            'Token.String': '#ce9178',
            'Token.Number': '#b5cea8',
            'Token.Comment': '#6a9955',
            'Token.Operator': '#d4d4d4',
            'Token.Name.Function': '#dcdcaa',
            'Token.Name': '#9cdcfe'
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
        
        # Frame para el editor y números de línea
        editor_with_lines = ttk.Frame(editor_frame)
        editor_with_lines.pack(fill=tk.BOTH, expand=True)

        self.code_editor = scrolledtext.ScrolledText(
            editor_with_lines,
            wrap=tk.NONE,
            font=self.code_font,
            background="black",
            foreground="white",
            insertbackground="white",
            selectbackground="#264F78",
            selectforeground="white",
            height=20,
            padx=10,
            pady=5
        )
        
        # Crear y configurar el widget de números de línea
        self.line_numbers = LineNumberCanvas(editor_with_lines, self.code_editor)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar el resaltado de sintaxis
        self.code_editor.bind('<KeyRelease>', self._highlight_syntax)
        
        # Configurar la sangría automática
        self.code_editor.bind('<Return>', self._auto_indent)
        self.code_editor.bind('<Tab>', self._handle_tab)

        # Botones
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.compile_button = tk.Button(
            button_frame,
            text="Compilar",
            command=self.compile_code,
            bg="#0078d4",
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.compile_button.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(
            button_frame,
            text="Ejecutar (F5)",
            command=self.run_code,
            bg="#0078d4",
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="Limpiar Consola",
            command=self.clear_console,
            bg="#0078d4",
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Consola de salida
        console_frame = ttk.LabelFrame(left_panel, text="Consola")
        left_panel.add(console_frame)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=self.code_font,
            background="black",
            foreground="white",
            insertbackground="white",
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
            background="black",
            foreground="white",
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
            background="black",
            foreground="white",
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
            background="black",
            foreground="white",
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

        # Análisis sintáctico y semántico
        try:
            self.ast = parse(code)
            if isinstance(self.ast, str):
                self.write_to_errors(self.ast)
                self.write_to_console(self.ast, 'ERROR')
                return
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

    def _highlight_syntax(self, event=None):
        # Obtener todo el texto
        content = self.code_editor.get("1.0", tk.END)
        
        # Eliminar tags existentes
        for tag in self.code_editor.tag_names():
            if tag != "sel":  # Mantener la selección
                self.code_editor.tag_remove(tag, "1.0", tk.END)
        
        # Aplicar resaltado de sintaxis usando Pygments
        try:
            for token, text in lex(content, JavascriptLexer()):
                if str(token) in self.syntax_colors:
                    # Encontrar la posición del token
                    start = content.find(text)
                    if start != -1:
                        end = start + len(text)
                        start_pos = f"1.0+{start}c"
                        end_pos = f"1.0+{end}c"
                        
                        # Crear un tag único para este tipo de token
                        tag_name = str(token).replace(".", "_")
                        self.code_editor.tag_config(tag_name, foreground=self.syntax_colors[str(token)])
                        self.code_editor.tag_add(tag_name, start_pos, end_pos)
        except Exception as e:
            print(f"Error en el resaltado de sintaxis: {e}")

    def _auto_indent(self, event):
        # Obtener la línea actual
        current_line = self.code_editor.get("insert linestart", "insert")
        
        # Obtener la indentación actual
        match = re.match(r'^(\s*)', current_line)
        indent = match.group(1) if match else ""
        
        # Agregar indentación extra si la línea termina con {
        if current_line.rstrip().endswith("{"):
            indent += "    "
            
        # Insertar nueva línea con indentación
        self.code_editor.insert("insert", f"\n{indent}")
        return "break"  # Prevenir el comportamiento por defecto

    def _handle_tab(self, event):
        # Insertar 4 espacios en lugar de un tab
        self.code_editor.insert("insert", "    ")
        return "break"  # Prevenir el comportamiento por defecto

def main():
    root = tk.Tk()
    app = CompiladorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 