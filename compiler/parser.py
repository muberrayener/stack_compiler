import ply.yacc as yacc
from .lexer import Lexer
from .ast_nodes import * 

class Parser:
    """
    Kaynak kodu AST (Abstract Syntax Tree) haline dönüştüren parser sınıfı.
    
    Özellikler:
    -------------
    - PLY (Python Lex-Yacc) kullanır
    - C/Java benzeri bir dil için kurallar tanımlar
    - Operator precedence ve blok/if/while/for/fonksiyon yapılarını destekler
    - AST düğümlerini (ast_nodes.py) üretir
    """
    
    def __init__(self):
        self.lexer_obj = Lexer()  # Lexer objesi oluşturulur
        self.tokens = self.lexer_obj.tokens  # Lexer tarafından tanımlı tokenlar
        self.parser = yacc.yacc(module=self, debug=False, write_tables=1)  # Yacc parser oluşturulur
        self.error_flag = False

    def parse(self, text):
        """Verilen kaynak kod metnini parse eder ve AST döndürür."""
        return self.parser.parse(text, lexer=self.lexer_obj.lexer)

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'GT', 'LE', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('right', 'NOT', 'UMINUS'),
    )

    def p_program(self, p):
        '''program : statement_list'''
        p[0] = Program(p[1], p.lineno(1))
    
    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | statement'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]
    
    def p_statement(self, p):
        '''statement : expression_statement
                     | assignment_statement
                     | if_statement
                     | while_statement
                     | for_statement
                     | function_declaration
                     | return_statement
                     | break_statement
                     | continue_statement
                     | block'''
        p[0] = p[1]
    
    def p_expression_statement(self, p):
        '''expression_statement : expression SEMI'''
        p[0] = ExprStatement(p[1], p.lineno(2))
    
    def p_assignment_statement(self, p):
        '''assignment_statement : IDENTIFIER EQUALS expression SEMI'''
        target_node = Identifier(p[1], p.lineno(1))
        p[0] = Assignment(target_node, p[3], p.lineno(2))
    
    def p_block(self, p):
        '''block : LBRACE statement_list RBRACE
                 | LBRACE RBRACE'''
        if len(p) == 4:
            p[0] = Block(p[2], p.lineno(1))
        else:
            p[0] = Block([], p.lineno(1))
    
    def p_if_statement(self, p):
        '''if_statement : IF LPAREN expression RPAREN statement
                        | IF LPAREN expression RPAREN statement ELSE statement'''
        if len(p) == 6:
            p[0] = IfStatement(p[3], p[5], None, p.lineno(1))
        else:
            p[0] = IfStatement(p[3], p[5], p[7], p.lineno(1))
    
    def p_while_statement(self, p):
        '''while_statement : WHILE LPAREN expression RPAREN statement'''
        p[0] = WhileStatement(p[3], p[5], p.lineno(1))
    
    def p_for_statement(self, p):
        '''for_statement : FOR LPAREN assignment_or_empty SEMI expression_or_empty SEMI expression_or_empty RPAREN statement'''
        p[0] = ForStatement(p[3], p[5], p[7], p[9], p.lineno(1))
    
    def p_assignment_or_empty(self, p):
        '''assignment_or_empty : IDENTIFIER EQUALS expression
                               | empty'''
        if len(p) == 4:
            target_node = Identifier(p[1], p.lineno(1))
            p[0] = Assignment(target_node, p[3], p.lineno(2))
        else:
            p[0] = None
    
    def p_expression_or_empty(self, p):
        '''expression_or_empty : expression
                               | empty'''
        p[0] = p[1]
    
    def p_function_declaration(self, p):
        '''function_declaration : FUNC IDENTIFIER LPAREN parameter_list RPAREN block
                                | FUNC IDENTIFIER LPAREN RPAREN block'''
        if len(p) == 7:
            p[0] = FunctionDef(p[2], p[4], p[6], p.lineno(1))
        else:
            p[0] = FunctionDef(p[2], [], p[5], p.lineno(1))
    
    def p_parameter_list(self, p):
        '''parameter_list : parameter_list COMMA IDENTIFIER
                          | IDENTIFIER'''
        if len(p) == 4:
            p[0] = p[1] + [Identifier(p[3], p.lineno(3))]
        else:
            p[0] = [Identifier(p[1], p.lineno(1))]
    
    def p_return_statement(self, p):
        '''return_statement : RETURN expression SEMI
                            | RETURN SEMI'''
        if len(p) == 4:
            p[0] = ReturnStatement(p[2], p.lineno(1))
        else:
            p[0] = ReturnStatement(None, p.lineno(1))
    
    def p_break_statement(self, p):
        '''break_statement : BREAK SEMI'''
        p[0] = ControlFlow('BREAK', p.lineno(1))
    
    def p_continue_statement(self, p):
        '''continue_statement : CONTINUE SEMI'''
        p[0] = ControlFlow('CONTINUE', p.lineno(1))
    
    def p_expression_binop(self, p):
        '''expression : expression OR expression
                      | expression AND expression
                      | expression EQ expression
                      | expression NE expression
                      | expression LT expression
                      | expression GT expression
                      | expression LE expression
                      | expression GE expression
                      | expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression MOD expression'''
        p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))
    
    
    def p_expression_unary(self, p):
        '''expression : NOT expression
                      | MINUS expression %prec UMINUS'''
        p[0] = UnaryOp(p[1], p[2], p.lineno(1))
    
    def p_expression_group(self, p):
        '''expression : LPAREN expression RPAREN'''
        p[0] = p[2]
    
    
    def p_expression_number(self, p):
        '''expression : NUMBER'''
        p[0] = Literal(p[1], p.lineno(1))
    
    def p_expression_string(self, p):
        '''expression : STRING'''
        p[0] = Literal(p[1], p.lineno(1))
    
    def p_expression_identifier(self, p):
        '''expression : IDENTIFIER'''
        p[0] = Identifier(p[1], p.lineno(1))
    
    def p_expression_function_call(self, p):
        '''expression : IDENTIFIER LPAREN argument_list RPAREN
                      | IDENTIFIER LPAREN RPAREN'''
        name_node = Identifier(p[1], p.lineno(1))
        
        if len(p) == 5:
            p[0] = FunCall(name_node, p[3], p.lineno(2))
        else:
            p[0] = FunCall(name_node, [], p.lineno(2))
    
    def p_argument_list(self, p):
        '''argument_list : argument_list COMMA expression
                         | expression'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def p_empty(self, p):
        '''empty :'''
        p[0] = None
    
    def p_error(self, p):
        """Hata yakalama"""
        if p:
            print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
        else:
            print("Syntax error at EOF")
        self.error_flag = True