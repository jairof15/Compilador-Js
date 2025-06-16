# Compilador de JavaScript en Python

Este es un compilador simple de JavaScript implementado en Python que realiza análisis léxico, sintáctico y semántico del código fuente, con una interfaz gráfica moderna y soporte para la mayoría de las construcciones básicas del lenguaje.

## Características

- **Análisis léxico:**
  - Identificación y clasificación de tokens: palabras clave, identificadores, operadores, literales numéricos, de texto y booleanos, símbolos de puntuación, etc.
  - Muestra los tokens con su tipo, valor, línea y columna.

- **Análisis sintáctico:**
  - Construcción del Árbol de Sintaxis Abstracta (AST) para:
    - Declaraciones de variables (`let`, `var`, `const`)
    - Asignaciones
    - Expresiones aritméticas, lógicas y booleanas
    - Estructuras de control: `if`, `else`, `while`, `for`, `switch`, `case`, `default`
    - Funciones y llamadas a funciones (incluyendo funciones flecha y anónimas)
    - Arrays y objetos literales
    - Acceso a propiedades y métodos (`console.log`, `push`, `pop`, etc.)
    - Operador ternario
    - Sentencias `break`, `return`, `try/catch`, `throw`

- **Análisis semántico:**
  - **Variables:**
    - Detecta uso de variables no declaradas.
    - Detecta redeclaración de variables en el mismo scope.
    - Detecta asignación a variables no declaradas.
    - Maneja correctamente el scope de variables en bloques, funciones, ciclos, etc.
  - **Funciones:**
    - Detecta uso de parámetros no declarados dentro de funciones.
    - Maneja el scope de parámetros y variables locales.
  - **Bloques y control de flujo:**
    - Detecta uso de variables fuera de su scope (por ejemplo, variables declaradas dentro de un `if` o `while` y usadas fuera).
  - **Literales:**
    - Reconoce correctamente literales `true`, `false`, strings y números, sin tratarlos como variables.
  - **Errores sintácticos personalizados:**
    - Señala errores como `case:` sin expresión, `if` sin condición, declaración de variable sin identificador, etc., con mensajes claros y precisos.

- **Visualización:**
  - Muestra tokens, AST, errores léxicos, sintácticos y semánticos en la interfaz gráfica.
  - Colores y fondos configurables para mejor legibilidad.

## Requisitos

```bash
pip install -r requirements.txt
```

## Uso

El compilador ofrece dos modos de uso:

### Modo Terminal

Para ejecutar el compilador en modo terminal:

```bash
python main.py
```

### Modo Interfaz Gráfica

Para ejecutar el compilador con interfaz gráfica:

```bash
python gui.py
```

La interfaz gráfica incluye:
- Editor de código con fuente monoespaciada y tema oscuro
- Botón de compilación y ejecución
- Pestañas para visualizar resultados:
  - **Tokens:** Muestra los tokens identificados
  - **AST:** Muestra el árbol de sintaxis abstracta
  - **Errores:** Muestra errores léxicos, sintácticos y semánticos
  - **Consola:** Muestra mensajes de compilación y ejecución

### Ejemplo de uso:

```javascript
// Declarar una variable
let x = 10;

// Definir una función
function suma(a, b) {
    return a + b;
}

// Estructura de control
if (x > 5) {
    let y = 20;
    console.log(y);
}

// Uso de booleanos
if (true) {
    console.log("Esto siempre se imprime");
}
```

## Estructura del Proyecto

- `main.py`: Punto de entrada del programa en modo terminal
- `gui.py`: Interfaz gráfica del compilador
- `lexer.py`: Analizador léxico
- `parser.py`: Analizador sintáctico
- `semantic_analyzer.py`: Analizador semántico
- `interpreter.py`: Intérprete para ejecución de código
- `requirements.txt`: Dependencias del proyecto

## Limitaciones

- No detecta errores de tipo (por ejemplo, operaciones entre tipos incompatibles).
- El acceso fuera de rango en arrays y propiedades no existentes en objetos se detecta en tiempo de ejecución (intérprete), no en análisis semántico.
- No soporta todas las características avanzadas de JavaScript.

---

¡Listo para compilar y aprender JavaScript en Python! 