from compiler import Parser, AstPrinter, SemanticAnalyzer, SemanticError, StackMachine, CodeGenerator

def run_pipeline(code, parser):
    """
    Verilen kaynak kodu işleyen tam bir pipeline:
    1. Parsing -> AST üretir
    2. AST görselleştirme
    3. Semantik analiz
    4. (Opsiyonel) Kod üretimi ve çalıştırma
    
    Parametreler:
    ------------
    - code : str : Kaynak kod
    - parser : Parser : Parser nesnesi
    """
    print("-" * 60)
    print("SOURCE CODE:")
    print(code.strip())
    print("-" * 60)

    # -------- PARSING --------
    ast_root = parser.parse(code)

    if not ast_root or parser.error_flag:
        print("❌ Parsing FAILED")
        return

    # -------- AST GÖRSELLEŞTİRME --------
    print("\n🌳 AST Visualization")
    printer = AstPrinter()
    printer.print_ast(ast_root)

    # -------- SEMANTIC ANALYSIS --------
    print("\n🧠 Semantic Analysis")
    analyzer = SemanticAnalyzer()

    try:
        analyzer.analyze(ast_root)
        print("✅ No semantic errors. Program is semantically correct.")
    
    except SemanticError as e:
        print("❌ Semantic error:", e)
    
    # -------- CODE GENERATION & EXECUTION --------
    print("\n⚙ Code Generation (Stack Machine)")
    gen = CodeGenerator()
    bytecode = gen.generate(ast_root)
    # bytecode'u ekrana yazdır
    for instr in bytecode:
        print(instr)
    
    # stack machine ile çalıştır
    vm = StackMachine(bytecode)
    vars_out = vm.run()
    print("\n=== EXECUTION RESULT ===")
    for var, val in vars_out.items():
        print(f"{var} = {val}")
   

    print("-" * 60)


def test_file(filename, parser):
    """
    Verilen dosya adını okuyup pipeline ile işler.
    Hata ve eksiklikleri yakalar.
    
    Parametreler:
    ------------
    - filename : str : Kaynak kod dosyası
    - parser : Parser : Parser nesnesi
    """
    print("=" * 60)
    print(f"RUNNING: {filename}")
    print("=" * 60)

    # Dosyayı oku
    try:
        with open(filename, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return

    # Pipeline çalıştır
    try:
        run_pipeline(code, parser)
    except Exception as e:
        print("\n💥 Crash during processing:")
        print(e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Parser nesnesi oluştur
    parser = Parser()

    # Test dosyaları sırayla çalıştır
    test_file("tests/test1.txt", parser)
    test_file("tests/test2.txt", parser)
    test_file("tests/test3.txt", parser)
    test_file("tests/test4.txt", parser)
