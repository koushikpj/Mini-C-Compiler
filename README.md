# Mini-C Compiler 🚀

A complete multi-stage compiler for a subset of the C programming language, built as a group project at **Ramaiah University of Applied Sciences**.

## 👨‍💻 Team Members
- Koushik PJ  – 23ETCS002062  
- Mohammed Saad – 23ETCS002073  
- Pathikrit Datta – 23ETCS002084  
- Pranay Parekh – 23ETCS002091  

---

## 📖 Introduction
This project implements a **Mini-C Compiler** – a teaching-oriented compiler that covers the essential phases of compilation without the full complexity of C.  

It supports:
- Lexical Analysis  
- Syntax Analysis  
- Semantic Analysis  
- Intermediate Code Generation (Three-Address Code)  
- Bonus: Tree-Walking Interpreter  
- Web-based frontend for interactive use  

The goal was to **learn compiler construction hands-on** while keeping the design modular, clear, and easy to extend.

---

## ⚡ Mini-C Language Features
Mini-C is a simplified subset of C with just enough constructs to demonstrate compiler concepts:

- `int` and `float` variables  
- Arithmetic & relational expressions (`+ - * / < > == !=`)  
- Single-dimensional integer arrays  
- `if-else` branching  
- `while` loops  
- Built-in `print()` function  
- Single-line comments (`// ...`)  
- Block scoping with `{ }`  

Example:
```c
int x = 5;
while (x < 10) {
    print(x);
    x = x + 1;
}
