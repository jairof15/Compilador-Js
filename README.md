# Compilador de JavaScript en Python

Este es un compilador simple de JavaScript implementado en Python que realiza análisis léxico, sintáctico y semántico del código fuente.

## Características

- Análisis léxico para identificar tokens
- Análisis sintáctico para construir el árbol de sintaxis abstracta (AST)
- Análisis semántico para verificar errores de declaración y uso de variables
- Interfaz gráfica moderna con:
  - Editor de código con resaltado
  - Pestañas para ver resultados de análisis
  - Visualización en tiempo real de errores
- Soporte para estructuras básicas de JavaScript:
  - Variables (var, let, const)
  - Funciones
  - Estructuras de control (if, while)
  - Operaciones aritméticas básicas

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
- Editor de código con fuente monoespaciada
- Botón de compilación
- Tres pestañas para visualizar resultados:
  - Análisis Léxico: Muestra los tokens identificados
  - Análisis Sintáctico: Muestra el árbol de sintaxis abstracta
  - Análisis Semántico: Muestra errores de variables y scope

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
}
```

## Estructura del Proyecto

- `main.py`: Punto de entrada del programa en modo terminal
- `gui.py`: Interfaz gráfica del compilador
- `lexer.py`: Analizador léxico
- `parser.py`: Analizador sintáctico
- `semantic_analyzer.py`: Analizador semántico
- `requirements.txt`: Dependencias del proyecto

## Limitaciones

- Soporte limitado para características avanzadas de JavaScript
- No genera código ejecutable
- No maneja todas las estructuras de control de JavaScript
- No soporta programación orientada a objetos

## Contribuir

Siéntete libre de contribuir al proyecto creando issues o pull requests. 