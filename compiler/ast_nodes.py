class Node:
    """
    AST'deki temel düğüm (node) sınıfı. Tüm diğer düğümler bundan türetilir.
    
    Özellikler:
    -----------
    - lineno: Kaynak kod satırı numarası (hata mesajları için)
    """
    def __init__(self, lineno=0):
        self.lineno = lineno
        
    def __repr__(self):
        return f'<{self.__class__.__name__}>'
    
    def walk(self):
        raise NotImplementedError


class BinOp(Node):
    """İkili işlemleri (toplama, çıkarma, çarpma vb.) temsil eder."""
    def __init__(self, op, left, right, lineno=0):
        super().__init__(lineno)
        self.op = op          # Operatör: '+', '-', '*', '/' vb.
        self.left = left      # Sol operand (Node)
        self.right = right    # Sağ operand (Node)
        
    def __repr__(self):
        return f'<{self.__class__.__name__} op={self.op}>'


class UnaryOp(Node):
    """Tekli işlemleri (negasyon, mantıksal not vb.) temsil eder."""
    def __init__(self, op, expr, lineno=0):
        super().__init__(lineno)
        self.op = op
        self.expr = expr      # İşlem yapılacak ifade (Node)


class Literal(Node):
    """Sabit değerleri temsil eder (sayı, string, bool)."""
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value


class Identifier(Node):
    """Değişken veya fonksiyon adlarını temsil eder."""
    def __init__(self, name, lineno=0):
        super().__init__(lineno)
        self.name = name


class FunCall(Node):
    """Fonksiyon çağrılarını temsil eder."""
    def __init__(self, name, args, lineno=0):
        super().__init__(lineno)
        self.name = name      # Identifier düğümü
        self.args = args or []  # Argüman listesi (Node listesi)


class Program(Node):
    """Programın kök düğümü, tüm ifadeleri ve blokları içerir."""
    def __init__(self, statements, lineno=0):
        super().__init__(lineno)
        self.statements = statements or []  # Statement listesi


class Block(Node):
    """Kod bloklarını ({ ... }) temsil eder."""
    def __init__(self, statements, lineno=0):
        super().__init__(lineno)
        self.statements = statements or []


class Assignment(Node):
    """Atama işlemini temsil eder (x = expr)."""
    def __init__(self, target, value, lineno=0):
        super().__init__(lineno)
        self.target = target  # Identifier düğümü
        self.value = value    # Atanan ifade (Node)


class IfStatement(Node):
    """If / If-Else ifadelerini temsil eder."""
    def __init__(self, condition, then_body, else_body=None, lineno=0):
        super().__init__(lineno)
        self.condition = condition    # Koşul (Node)
        self.then_body = then_body    # Then bloğu (Node / Block)
        self.else_body = else_body    # Else bloğu (Node / Block, opsiyonel)


class WhileStatement(Node):
    """While döngüsünü temsil eder."""
    def __init__(self, condition, body, lineno=0):
        super().__init__(lineno)
        self.condition = condition  # Koşul (Node)
        self.body = body            # Döngü gövdesi (Node / Block)


class ForStatement(Node):
    """For döngüsünü temsil eder."""
    def __init__(self, init, condition, update, body, lineno=0):
        super().__init__(lineno)
        self.init = init            # Başlatma ifadesi (Node / Assignment)
        self.condition = condition  # Koşul (Node)
        self.update = update        # Güncelleme ifadesi (Node)
        self.body = body            # Döngü gövdesi (Node / Block)


class FunctionDef(Node):
    """Fonksiyon tanımını temsil eder."""
    def __init__(self, name, params, body, lineno=0):
        super().__init__(lineno)
        self.name = name            # Fonksiyon adı (string)
        self.params = params or []  # Parametre listesi (Identifier listesi)
        self.body = body            # Fonksiyon gövdesi (Block)


class ReturnStatement(Node):
    """Return ifadesini temsil eder."""
    def __init__(self, value=None, lineno=0):
        super().__init__(lineno)
        self.value = value          # Döndürülecek ifade (Node)


class ControlFlow(Node):
    """Break ve Continue ifadelerini temsil eder."""
    def __init__(self, keyword, lineno=0):
        super().__init__(lineno)
        self.keyword = keyword      # 'break' veya 'continue'


class ExprStatement(Node):
    """Sadece bir ifadeyi çalıştıran statement."""
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr            # Çalıştırılacak ifade (Node)
