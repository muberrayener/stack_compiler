# 🔧 Stack-Based Compiler

Bu proje, **stack tabanlı mini bir programlama dili** için bir derleyici ve yorumlayıcı pipeline'ı sunar.  
Kaynak kod, sırasıyla **parsing, AST oluşturma, semantik analiz, kod üretimi ve yürütme** aşamalarından geçirilir.

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| Lexer & Parser | PLY kullanılarak token'lar ayrılır ve AST (Abstract Syntax Tree) oluşturulur. |
| AST Görselleştirme | AST hiyerarşik olarak görselleştirilir; düğümlerin türleri, değerleri ve operatörleri gösterilir. |
| Semantik Analiz | Değişkenler ve fonksiyonlar kontrol edilir, tip uyumsuzlukları ve hatalı kontrol akışları tespit edilir. |
| Stack Machine | AST'den üretilen bytecode, stack tabanlı sanal makinede çalıştırılır. |
| Opsiyonel Kod Üretimi | Bytecode üretimi ve yürütme desteği sağlanır. |

---

## 📋 Desteklenen Yapılar

- Değişken atamaları ve ifadeler  
- Karar yapıları: `if-else`  
- Döngüler: `while`, `for`  
- Fonksiyon tanımları ve çağrıları  
- Mantıksal ve aritmetik operatörler: `+`, `-`, `*`, `/`, `%`, `&&`, `||`, `==`, `!=`, `<`, `>`, `<=`, `>=`  
- `break` ve `continue` kontrol ifadeleri  
- `return` ifadeleri  

---

## 📁 Proje Yapısı

```
stack_compiler/           # Proje kök dizini
│
├─ compiler/               # Paket klasörü
│   ├─ __init__.py
│   ├─ lexer.py
│   ├─ parser.py
│   ├─ ast_nodes.py
│   ├─ ast_printer.py
│   ├─ semantic_analyzer.py
│   ├─ stack_interpreter.py
│   └─ stack_codegen.py
│
├─ tests/                  # Test dosyaları
│   ├─ test1.txt
│   ├─ test2.txt
│   └─ ...
│
├─ examples/               # Örnek kaynak kodlar
│
├─ main.py                 # Pipeline'ı çalıştıran script
└─ README.md
```

---

## 🚀 Kurulum

Python 3.8 veya üzeri sürüm gereklidir.

```bash
pip install ply
```

---

## 💻 Kullanım ve Test

```bash
python main.py
```

---

## 🧩 Modüller

### Lexer

Kaynak kod, token'lara ayrılır. Yorumlar ve boşluklar göz ardı edilir. Satır numarası takibi yapılır.

```python
from lexer import Lexer

lexer = Lexer()
lexer.input('x = 10 + 5;')

while True:
    tok = lexer.token()
    if not tok:
        break
    print(f"{tok.type} -> {tok.value} (line {tok.lineno})")
```

**Çıktı Örneği:**

```
IDENTIFIER -> x (line 1)
EQUALS -> = (line 1)
NUMBER -> 10 (line 1)
PLUS -> + (line 1)
NUMBER -> 5 (line 1)
SEMI -> ; (line 1)
```

### Parser

Token'lar kullanılarak AST oluşturulur. Tüm ifadeler ve blok yapıları AST düğümleriyle temsil edilir.

```python
from parser import Parser

parser = Parser()
ast = parser.parse('x = 10 + 5;')
print(ast)
```

### AST Görselleştirme

AST, hiyerarşik şekilde görselleştirilir. Düğüm türü, değer ve operatörler ekrana yazdırılır.

```python
from ast_printer import AstPrinter
printer = AstPrinter()
printer.print_ast(ast)
```

**Örnek Görselleştirme:**

```
<Program>
|   Stmt: <Assignment>
|   |   Target: <Identifier>
|   |   |   Name: x
|   |   Expr: <BinOp>
|   |   |   Left: <Literal>
|   |   |   |   Value: 10
|   |   |   Right: <Literal>
|   |   |   |   Value: 5
|   |   |   Op: +
```

### Semantik Analiz

Değişken ve fonksiyon türleri kontrol edilir. Döngü dışı break/continue ve return ifadeleri tespit edilir.

```python
from semantic_analyzer import SemanticAnalyzer, SemanticError

analyzer = SemanticAnalyzer()

try:
    analyzer.analyze(ast)
    print("Program semantik olarak doğru.")
except SemanticError as e:
    print("Semantik hata:", e)
```

### Stack Machine

AST'den üretilen bytecode, stack tabanlı sanal makinede çalıştırılır.

```python
from stack_interpreter import StackMachine
bytecode = ["PUSH 10", "PUSH 5", "ADD", "STORE x"]
vm = StackMachine(bytecode)
vars_out = vm.run()
print(vars_out)
```

**Çıktı:**

```python
{'x': 15}
```

### Opsiyonel Kod Üretimi

AST'den bytecode üretilir ve stack tabanlı sanal makinede yürütülür.

```python
from stack_codegen import CodeGenerator

gen = CodeGenerator()
bytecode = gen.generate(ast)
print(bytecode)
```

---

## 🔄 Tam Pipeline Örneği

Kod örnekleri, AST oluşturma, semantik analiz ve bytecode yürütme aşamalarından geçirilir.

```python
from parser import Parser
from ast_printer import AstPrinter
from semantic_analyzer import SemanticAnalyzer
from stack_interpreter import StackMachine

parser = Parser()
code = "x = 10 + 5;"

# Parsing
ast_root = parser.parse(code)

# AST Görselleştirme
printer = AstPrinter()
printer.print_ast(ast_root)

# Semantik Analiz
analyzer = SemanticAnalyzer()
analyzer.analyze(ast_root)

# Bytecode üretimi ve yürütme (opsiyonel)
try:
    from stack_codegen import CodeGenerator
    gen = CodeGenerator()
    bytecode = gen.generate(ast_root)
    print("Bytecode:", bytecode)

    vm = StackMachine(bytecode)
    vars_out = vm.run()
    print("Değişkenler:", vars_out)
except ImportError:
    print("Kod üretimi modülü bulunamadı. Atlandı.")
```

---

## ⚠️ Hatalar ve Uyarılar

- Söz dizimi hataları parsing sırasında raporlanır.
- Tanımsız değişken veya tip uyumsuzluğu semantik analizde tespit edilir.

---

## 📂 Örnek Dosyalar

Test dosyaları `test1.txt`, `test2.txt`, `test3.txt`, `test4.txt` şeklinde isimlendirilmiştir ve pipeline üzerinden çalıştırılabilir.

```bash
python main.py
```
