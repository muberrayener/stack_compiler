class AstPrinter:
    """
    AST (Abstract Syntax Tree) ağacını görsel olarak ekrana yazdıran sınıf.

    Özellikler:
    -------------
    - Her düğümü (node) sınıf adı, değeri, adı veya işlemi ile gösterir
    - İç içe bloklar için girinti (indent) kullanır
    - Program, blok, if/else, while/for, fonksiyon çağrısı gibi yapıları görselleştirir
    - Hem tek düğüm hem de liste halinde düğümleri (statements) işler
    """

    def __init__(self):
        """İç içe yazdırma için indent seviyesini başlatır."""
        self.indent = 0
        
    def _print(self, node, prefix=""):
        """
        AST ağacının bir düğümünü ve alt düğümlerini ekrana yazdırır.
        
        Parametreler:
        -------------
        - node: Yazdırılacak AST düğümü
        - prefix: Ön ek, düğüm tipini veya rolünü belirtmek için
        """
        # Mevcut düğümün türünü yazdır
        print(f"{'|   ' * self.indent}{prefix}<{node.__class__.__name__}>")

        self.indent += 1  # alt düğümlerde girinti artır

        # Düğümün değer, isim veya işlem bilgisi varsa yazdır
        if hasattr(node, 'value'): 
            print(f"{'|   ' * self.indent}Value: {repr(node.value)}")
        if hasattr(node, 'name'): 
            print(f"{'|   ' * self.indent}Name: {node.name}")
        if hasattr(node, 'op'): 
            print(f"{'|   ' * self.indent}Op: {node.op}")

        # Statements varsa sırayla yazdır
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self._print(stmt, prefix="Stmt: ")
        
        # AST ilişkili diğer düğümleri yazdır
        if hasattr(node, 'left'): self._print(node.left, prefix="Left: ")
        if hasattr(node, 'right'): self._print(node.right, prefix="Right: ")
        if hasattr(node, 'expr'): self._print(node.expr, prefix="Expr: ")
        if hasattr(node, 'target'): self._print(node.target, prefix="Target: ")
        if hasattr(node, 'condition'): self._print(node.condition, prefix="Condition: ")
        if hasattr(node, 'then_body'): self._print(node.then_body, prefix="Then: ")
        if hasattr(node, 'else_body') and node.else_body: 
            self._print(node.else_body, prefix="Else: ")
        if hasattr(node, 'body'): 
            if isinstance(node.body, list):
                # Body listesi varsa her bir öğeyi yazdır
                for b in node.body: self._print(b, prefix="Body Stmt: ")
            else:
                self._print(node.body, prefix="Body: ")

        self.indent -= 1  # üst seviyeye geri dön

    def print_ast(self, root_node):
        """
        AST ağacını kök düğümden başlatarak ekrana yazdırır.

        Parametreler:
        -------------
        - root_node: AST ağacının kök düğümü
        """
        self._print(root_node)
