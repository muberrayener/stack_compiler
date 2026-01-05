from .ast_nodes import *

class SemanticError(Exception):
    """Semantik analiz sırasında oluşan hatalar için özel exception sınıfı."""
    pass


class Symbol:
    """
    Sembol tablosunda yer alan bir değişken veya fonksiyon kaydı.
    
    Attributes:
        name (str): Sembolün adı
        type (str): Sembolün tipi (int, float, string, bool, function, vb.)
        lineno (int): Tanımlandığı satır
        params (list): Fonksiyon parametreleri (varsa)
    """
    def __init__(self, name, value_type=None, lineno=0, params=None):
        self.name = name
        self.type = value_type
        self.lineno = lineno
        self.params = params or []


class SymbolTable:
    """
    Sembolleri saklayan ve çözümleyen tablo. Scope yönetimi içerir.
    
    Özellikler:
    - push_scope/pop_scope: bloklar için yeni scope açıp kapama
    - declare: sembol ekleme
    - resolve: isim çözümleme
    """
    def __init__(self):
        self.scopes = [{}]  # global scope

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare(self, name, symbol):
        self.scopes[-1][name] = symbol

    def resolve(self, name, lineno=None):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        if lineno is not None:
            raise SemanticError(f"Use of undefined variable '{name}' at line {lineno}")
        else:
            raise SemanticError(f"Use of undefined variable '{name}'")

    def define(self, name, typ):
        self.scopes[-1][name] = typ


class SemanticAnalyzer:
    """
    AST üzerinde semantik analiz yapan sınıf.
    
    Özellikler:
    -------------
    - Tür kontrolü (type checking)
    - Fonksiyon ve değişken tanımları
    - Döngü ve kontrol akışı kontrolü (break/continue)
    - Implicit typing (atama ile tip belirleme)
    """
    def __init__(self):
        self.symbols = SymbolTable()
        self.current_function = None
        self.loop_depth = 0

    def analyze(self, node):
        """Verilen AST düğümünü analiz eder ve uygun visitor metodunu çağırır."""
        method = "visit_" + node.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(node)
        raise Exception(f"No visitor for {node.__class__.__name__}")

    # Program / Block
    def visit_Program(self, node):
        for stmt in node.statements:
            self.analyze(stmt)

    def visit_Block(self, node):
        self.symbols.push_scope()
        for stmt in node.statements:
            self.analyze(stmt)
        self.symbols.pop_scope()

    # Literals
    def visit_Literal(self, node):
        v = node.value
        if v is None: return "null"
        if isinstance(v, bool): return "bool"
        if isinstance(v, int): return "int"
        if isinstance(v, float): return "float"
        if isinstance(v, str): return "string"
        return "unknown"

    # Identifier
    def visit_Identifier(self, node):
        sym = self.symbols.resolve(node.name, node.lineno)
        if sym.type is None:
            return "unknown"  # parametre veya implicit değişken
        return sym.type

    # Assignment (implicit typing)
    def visit_Assignment(self, node):
        value_type = self.analyze(node.value)
        try:
            sym = self.symbols.resolve(node.target.name, node.lineno)
        except SemanticError:
            # Tanımlı değilse otomatik declare
            sym = Symbol(node.target.name, value_type, node.lineno)
            self.symbols.declare(node.target.name, sym)
            return value_type

        # null atamaları
        if value_type == "null":
            sym.type = sym.type or "null"
            return value_type

        if sym.type == "null" or sym.type is None:
            sym.type = value_type
            return value_type

        # Dinamik tipleme
        sym.type = value_type
        return value_type

    # Binary operators
    def visit_BinOp(self, node):
        lt = self.analyze(node.left)
        rt = self.analyze(node.right)
        op = node.op

        # Unknown olan tiplere diğer tarafa uyum sağla
        if lt == "unknown" and rt != "unknown":
            lt = rt
            if isinstance(node.left, Identifier):
                sym = self.symbols.resolve(node.left.name, node.left.lineno)
                sym.type = lt
        if rt == "unknown" and lt != "unknown":
            rt = lt
            if isinstance(node.right, Identifier):
                sym = self.symbols.resolve(node.right.name, node.right.lineno)
                sym.type = rt

        # Eğer her ikisi de unknown ise, + / - / * / / / % için int varsay
        if lt == "unknown" and rt == "unknown" and op in ["+", "-", "*", "/", "%"]:
            lt = rt = "int"
            if isinstance(node.left, Identifier):
                sym = self.symbols.resolve(node.left.name, node.left.lineno)
                sym.type = "int"
            if isinstance(node.right, Identifier):
                sym = self.symbols.resolve(node.right.name, node.right.lineno)
                sym.type = "int"

        # ---------- String concatenation ----------
        if op == "+" and ("string" in (lt, rt)):
            return "string"

        # ---------- Modulus ----------
        if op == "%" and (lt != "int" or rt != "int"):
            raise SemanticError(
                f"Modulo '%' requires integer operands, got {lt} and {rt} at line {node.lineno}"
            )

        # ---------- Arithmetic ----------
        if lt in ("int", "float") and rt in ("int", "float"):
            return "float" if "float" in (lt, rt) else "int"

        # ---------- Equality ----------
        if op in ["==", "!="]:
            if lt == "null" or rt == "null":
                return "bool"
            if lt != rt:
                raise SemanticError(
                    f"Cannot compare '{lt}' with '{rt}' using '{op}' at line {node.lineno}"
                )
            return "bool"

        # ---------- Relational ----------
        if op in ["<", "<=", ">", ">="]:
            if lt in ("int", "float") and rt in ("int", "float"):
                return "bool"
            if lt == rt == "string":
                return "bool"
            raise SemanticError(
                f"Operator '{op}' not supported between '{lt}' and '{rt}' at line {node.lineno}"
            )

        # ---------- Logical ----------
        if op in ["and", "or"]:
            if lt == "bool" and rt == "bool":
                return "bool"
            raise SemanticError(
                f"Logical operator '{op}' requires bool operands, got {lt} and {rt} at line {node.lineno}"
            )

        return lt


    # Unary operators
    def visit_UnaryOp(self, node):
        return self.analyze(node.expr)

    # If / While / For
    def visit_IfStatement(self, node):
        self.analyze(node.condition)
        self.visit_Block(node.then_body)
        if node.else_body:
            self.visit_Block(node.else_body)

    def visit_WhileStatement(self, node):
        self.analyze(node.condition)
        self.loop_depth += 1
        self.visit_Block(node.body)
        self.loop_depth -= 1

    def visit_ForStatement(self, node):
        self.symbols.push_scope()
        if node.init: self.analyze(node.init)
        if node.condition: self.analyze(node.condition)
        if node.update: self.analyze(node.update)

        self.loop_depth += 1
        self.visit_Block(node.body)
        self.loop_depth -= 1
        self.symbols.pop_scope()

    # Function Definition
    def visit_FunctionDef(self, node):
        sym = Symbol(node.name, "function", node.lineno, params=node.params)
        self.symbols.declare(node.name, sym)
        self.symbols.push_scope()
        self.current_function = node.name

        for p in node.params:
            pname = getattr(p, "name", p)
            self.symbols.declare(pname, Symbol(pname, None, node.lineno))

        self.visit_Block(node.body)
        self.symbols.pop_scope()
        self.current_function = None

    # Function Call
    def visit_FunCall(self, node):
        sym = self.symbols.resolve(node.name.name, node.lineno)
        if sym.type != "function":
            raise SemanticError(f"'{node.name}' is not a function (line {node.lineno})")
        if len(node.args) != len(sym.params):
            raise SemanticError(f"Argument count mismatch calling {node.name} at line {node.lineno}")
        for arg in node.args:
            self.analyze(arg)
        return None  # implicit return type

    # Return
    def visit_ReturnStatement(self, node):
        if not self.current_function:
            raise SemanticError(f"'return' outside function at line {node.lineno}")
        if node.value:
            self.analyze(node.value)

    # Loop control (break / continue)
    def visit_ControlFlow(self, node):
        keyword_upper = node.keyword.upper()   # Lexer büyük harf kullanıyorsa
        if self.loop_depth == 0:
            raise SemanticError(f"'{keyword_upper}' used outside loop at line {node.lineno}")
        if keyword_upper not in ("BREAK", "CONTINUE"):
            raise SemanticError(f"Unknown control flow '{keyword_upper}' at line {node.lineno}")