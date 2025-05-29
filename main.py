from lexer import tokenize
from parser import parser
from semantic_analyzer import SemanticAnalyzer
from colorama import init, Fore, Style

def main():
    init()  # Inicializar colorama para colores en la terminal
    print(Fore.CYAN + "Compilador de JavaScript en Python" + Style.RESET_ALL)
    print(Fore.YELLOW + "Escribe 'exit' para salir" + Style.RESET_ALL)
    
    while True:
        try:
            code = input(Fore.GREEN + "\nIngresa código JavaScript > " + Style.RESET_ALL)
            
            if code.lower() == 'exit':
                break
            
            # Análisis léxico
            print(Fore.CYAN + "\n=== Análisis Léxico ===" + Style.RESET_ALL)
            tokens = tokenize(code)
            for token in tokens:
                print(f"Token: {token.type}, Valor: {token.value}, Línea: {token.lineno}")
            
            # Análisis sintáctico
            print(Fore.CYAN + "\n=== Análisis Sintáctico ===" + Style.RESET_ALL)
            try:
                ast = parser.parse(code)
                if ast:
                    print(ast)
                
                # Análisis semántico
                print(Fore.CYAN + "\n=== Análisis Semántico ===" + Style.RESET_ALL)
                semantic_analyzer = SemanticAnalyzer()
                semantic_analyzer.analyze(ast)
                
                errors = semantic_analyzer.get_errors()
                if errors:
                    print(Fore.RED + "Errores semánticos encontrados:" + Style.RESET_ALL)
                    for error in errors:
                        print(Fore.RED + f"- {error}" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + "No se encontraron errores semánticos" + Style.RESET_ALL)
                    
            except Exception as e:
                print(Fore.RED + f"Error en el análisis: {str(e)}" + Style.RESET_ALL)
                
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    main() 