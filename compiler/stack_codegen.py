class CodeGenerator:
    """
    CodeGenerator: AST (Abstract Syntax Tree) üzerinden stack tabanlı bytecode üreten sınıf.
    
    Özellikler:
    -------------
    - Literaller, değişkenler ve atama işlemleri
    - Aritmetik ve mantıksal ifadeler
    - Unary işlemler (negatif sayılar vb.)
    - Kontrol akışı: if-else, while, for
    - Fonksiyon tanımları ve çağrıları
    - Return ifadeleri ve loop control (break / continue)
    
    Kullanım:
    -------------
    generator = CodeGenerator()
    bytecode = generator.generate(program_node)  # AST'den bytecode üretir
    """

    def __init__(self):
        self.code = []            # Üretilen bytecode
        self.label_count = 0      # Yeni label için sayaç
        self.function_env = {}    # Fonksiyon ortamı (isteğe bağlı)
        self.loop_stack = []      # Döngü context'i (break / continue)
        self.function_code = []   

    # Label oluşturma
    def new_label(self, prefix="L"):
        """Yeni benzersiz label üretir."""
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def emit(self, instr):
        """Bytecode'a bir talimat ekler."""
        self.code.append(instr)

    def emit_label(self, label):
        """Bytecode'a bir label ekler."""
        self.code.append(f"{label}:")

    # Genel generate metodu
    def generate(self, node):
        """
        AST düğümünü inceleyip ilgili gen_<NodeType> metodunu çağırır.
        """
        method = "gen_" + node.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(node)
        else:
            raise Exception(f"No codegen for node type {node.__class__.__name__}")

    # Literals ve Identifier
    def gen_Literal(self, node):
        self.emit(f"PUSH {node.value}")

    def gen_Identifier(self, node):
        self.emit(f"LOAD {node.name}")

    # Atama işlemleri
    def gen_Assignment(self, node):
        self.generate(node.value)
        self.emit(f"STORE {node.target.name}")

    # Binary işlemler
    def gen_BinOp(self, node):
        self.generate(node.left)
        self.generate(node.right)

        opmap = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "%": "MOD",
            "<": "LT",
            ">": "GT",
            "<=": "LE",
            ">=": "GE",
            "==": "EQ",
            "!=": "NEQ",
            "&&": "AND",
            "||": "OR",
        }

        self.emit(opmap[node.op])

    # Unary işlemler
    def gen_UnaryOp(self, node):
        self.generate(node.expr)
        if node.op == "-":
            self.emit("NEG")

    # İfade olarak statement
    def gen_ExprStatement(self, node):
        self.generate(node.expr)
        self.emit("POP")  # değeri at

    # Program / Block
    def gen_Program(self, node):
        # Önce ana program kodunu üret
        for stmt in node.statements:
            if stmt.__class__.__name__ != 'FunctionDef':
                self.generate(stmt)
        
        # Program sonunu işaretle
        self.emit("HALT")
        
        # Sonra fonksiyonları ekle
        for stmt in node.statements:
            if stmt.__class__.__name__ == 'FunctionDef':
                self.generate(stmt)
        
        # Fonksiyon kodlarını ana koda ekle
        self.code.extend(self.function_code)
        
        return self.code

    def gen_Block(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    # If / Else
    def gen_IfStatement(self, node):
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")

        self.generate(node.condition)
        self.emit(f"JZ {else_label}")

        self.generate(node.then_body)
        self.emit(f"JMP {end_label}")

        self.emit(f"{else_label}:")
        if node.else_body:
            self.generate(node.else_body)

        self.emit(f"{end_label}:")

    # While loop
    def gen_WhileStatement(self, node):
        start_label = self.new_label("WHILE_START")
        end_label = self.new_label("WHILE_END")
    
        self.loop_stack.append((end_label, start_label))  # break/continue

        self.emit_label(start_label)
        self.generate(node.condition)
        self.emit(f"JMP_IF_FALSE {end_label}")

        self.generate(node.body)
        self.emit(f"JMP {start_label}")
    
        self.emit_label(end_label)
        self.loop_stack.pop()

    # For loop
    def gen_ForStatement(self, node):
        if node.init:
            self.generate(node.init)

        start_label = self.new_label("FOR_START")
        end_label = self.new_label("FOR_END")
        update_label = self.new_label("FOR_UPDATE")

        self.loop_stack.append((end_label, update_label))  # break/continue

        self.emit_label(start_label)
        if node.condition:
            self.generate(node.condition)
            self.emit(f"JMP_IF_FALSE {end_label}")

        self.generate(node.body)
        self.emit_label(update_label)
        if node.update:
            self.generate(node.update)

        self.emit(f"JMP {start_label}")
        self.emit_label(end_label)

        self.loop_stack.pop()

    # Fonksiyon tanımı
    def gen_FunctionDef(self, node):
        # Fonksiyon kodunu ayrı yere yaz
        old_code = self.code
        self.code = []
        
        self.emit(f"FUNC_{node.name}:")
        
        # Parametreleri stack'ten al (varsa)
        if hasattr(node, 'params') and node.params:
            for param in reversed(node.params):
                self.emit(f"STORE {param.name}")
        
        # Fonksiyon gövdesi
        for stmt in node.body.statements:
            self.generate(stmt)
        
        # Varsayılan return
        self.emit("PUSH 0")
        self.emit("RET")
        
        # Fonksiyon kodunu kaydet ve eski kodu geri yükle
        self.function_code.extend(self.code)
        self.code = old_code

    # Fonksiyon çağrısı
    def gen_FunCall(self, node):
        # Argümanları sırayla stack'e push et
        for arg in node.args:
            self.generate(arg)
        
        # Fonksiyonu çağır (argüman sayısı ile)
        arg_count = len(node.args)
        self.emit(f"CALL FUNC_{node.name.name} {arg_count}")

    # Return
    def gen_ReturnStatement(self, node):
        if node.value:
            self.generate(node.value)
        else:
            self.emit("PUSH 0")
        self.emit("RET")

    # Döngü Kontrol (break / continue)
    def gen_ControlFlow(self, node):
        if not self.loop_stack:
            raise Exception(f"{node.keyword} used outside loop at line {node.lineno}")

        break_label, continue_label = self.loop_stack[-1]
        if node.keyword == "break":
            self.emit(f"JMP {break_label}")
        else:  # continue
            self.emit(f"JMP {continue_label}")
