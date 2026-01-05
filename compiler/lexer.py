import ply.lex as lex 
import os

class Lexer:
    """
    Kaynak kodu token (leksik birim) haline dönüştüren lexer sınıfı.

    Özellikler:
    -------------
    - PLY (Python Lex-Yacc) kullanır
    - C/Java tarzı bir dil için anahtar kelimeleri ve operatörleri tanımlar
    - Yorumlar (// veya /* */) ve boşlukları yok sayar
    - Sayı, string, identifier, operatör, blok sembollerini tanır
    - Tüm tokenları liste halinde döndürebilir
    """

    # Token türleri
    tokens = (
        'IF', 'ELSE', 'WHILE', 'FOR', 'FUNC', 'RETURN', 'BREAK', 'CONTINUE',
        'IDENTIFIER', 'NUMBER', 'STRING',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'EQ', 'NE', 'LE', 'GE', 'AND', 'OR',
        'EQUALS', 'LT', 'GT', 'NOT',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET', 'SEMI', 'COMMA',
    )
    
    # Anahtar kelimeler
    keywords = {
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'func': 'FUNC', 'return': 'RETURN', 'break': 'BREAK', 'continue': 'CONTINUE'
    }

    # Operatörler
    t_EQ         = r'=='
    t_NE         = r'!='
    t_LE         = r'<='
    t_GE         = r'>='
    t_AND        = r'&&'
    t_OR         = r'\|\|'
    
    t_EQUALS     = r'='
    t_NOT        = r'!'
    t_LT         = r'<'
    t_GT         = r'>'

    t_PLUS       = r'\+'
    t_MINUS      = r'-'
    t_TIMES      = r'\*'
    t_DIVIDE     = r'/'
    t_MOD        = r'%'

    # Parantez, blok, köşeli parantez, noktalı virgül, virgül
    t_LPAREN     = r'\('
    t_RPAREN     = r'\)'
    t_LBRACE     = r'\{'
    t_RBRACE     = r'\}'
    t_LBRACKET   = r'\['
    t_RBRACKET   = r'\]'
    t_SEMI       = r';'
    t_COMMA      = r','

    # Boşluk ve tab karakterlerini yok say
    t_ignore     = ' \t'
    
    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, debug=False, **kwargs)
        
    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)' 
        t.lexer.lineno += t.value.count('\n')
        pass  

    def t_STRING(self, t):
        r'"[^"\n]*"|\'[^\'\n]*\''
        return t

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?([eE][+-]?\d+)?'
        t.value = float(t.value) if ('.' in t.value or 'e' in t.value.lower()) else int(t.value)
        return t

    def t_IDENTIFIER(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.keywords.get(t.value, 'IDENTIFIER')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()
    
    def get_all_tokens(self, data):
        self.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens
