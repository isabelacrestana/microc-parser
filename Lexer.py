from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterator


class TokenKind(enum.Enum):
    """Interface publicada na etapa do lexer; nomes e números são fixos."""

    EOF = -1
    IDENTIFIER = 1
    INT_LITERAL = 2
    STRING_LITERAL = 3
    KW_INT = 10
    KW_BOOL = 11
    KW_VOID = 12
    KW_TRUE = 13
    KW_FALSE = 14
    KW_IF = 15
    KW_ELSE = 16
    KW_WHILE = 17
    KW_RETURN = 18
    KW_PRINT = 19
    PLUS = 20
    MINUS = 21
    STAR = 22
    SLASH = 23
    PERCENT = 24
    LESS = 25
    LESS_EQUAL = 26
    GREATER = 27
    GREATER_EQUAL = 28
    EQUAL_EQUAL = 29
    NOT_EQUAL = 30
    LOGICAL_AND = 31
    LOGICAL_OR = 32
    LOGICAL_NOT = 33
    ASSIGN = 34
    LEFT_PAREN = 40
    RIGHT_PAREN = 41
    LEFT_BRACE = 42
    RIGHT_BRACE = 43
    COMMA = 44
    SEMICOLON = 45


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | str | bool | None
    line: int
    column: int

    def __str__(self) -> str:
        return (
            f"<{self.kind.value}, {self.kind.name}, {self.lexeme!r}, "
            f"{self.value!r}, {self.line}, {self.column}>"
        )


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"erro léxico em {self.line}:{self.column}: {self.message}"


class Lexer:
    """Converte texto-fonte MicroC em uma sequência de tokens."""

    def __init__(self, source: str):
        self.source = source
        # TODO: inicialize aqui o estado exigido por sua estratégia.
        self.position = 0
        self.length = len(source)
        self.line = 1
        self.column = 1

        self.transition_table = {

            'start': {
                'alpha': self.state_identifier,
                'digit': self.state_number,
                '+': self.state_second,
                '-': self.state_second,
                '/': self.state_slash,
                '*': self.state_second,
                '%': self.state_second,
                '<': self.state_second,
                '>': self.state_second,
                '=': self.state_second,
                '!': self.state_second,
                '&': self.state_and_or,
                '|': self.state_and_or,
                '(': self.state_second,
                ')': self.state_second,
                '"': self.state_string,
                '{': self.state_second,
                '}': self.state_second,
                ',': self.state_second,
                ';': self.state_second,
                'whitespace': self.state_whitespace,
                },

            'slash':{
                '/': self.state_comment_line,
                '*': self.state_comment_block,
                'default': None,
            },

        }

        self.simple_tokens = {
            '+': TokenKind.PLUS,
            '-': TokenKind.MINUS,
            '*': TokenKind.STAR,
            '%': TokenKind.PERCENT,
            '(': TokenKind.LEFT_PAREN,
            ')': TokenKind.RIGHT_PAREN,
            '{': TokenKind.LEFT_BRACE,
            '}': TokenKind.RIGHT_BRACE,
            ',': TokenKind.COMMA,
            ';': TokenKind.SEMICOLON,
            ">": TokenKind.GREATER,
            "<": TokenKind.LESS,
            "!": TokenKind.LOGICAL_NOT,
            "=": TokenKind.ASSIGN,
            'default':None
        }

        self.keywords = {
            "int": TokenKind.KW_INT,
            "bool": TokenKind.KW_BOOL,
            "void": TokenKind.KW_VOID,
            "true": TokenKind.KW_TRUE,
            "false": TokenKind.KW_FALSE,
            "if": TokenKind.KW_IF,
            "else": TokenKind.KW_ELSE,
            "while": TokenKind.KW_WHILE,
            "return": TokenKind.KW_RETURN,
            "print": TokenKind.KW_PRINT
        }

        self.dualoperands = {
            ">=": TokenKind.GREATER_EQUAL,
            "<=": TokenKind.LESS_EQUAL,
            "!=": TokenKind.NOT_EQUAL,
            "==": TokenKind.EQUAL_EQUAL,
            "&&": TokenKind.LOGICAL_AND,
            "||": TokenKind.LOGICAL_OR,
            'default': None
        }

    def state_second(self) -> Token:
        initial_line = self.line
        initial_column = self.column

        lexeme = ""
        lexeme += self.source[self.position]

        self.position += 1
        self.column += 1

        next_char = self.source[self.position] if self.position < self.length else 'EOF'

        if next_char == "=":
            lexeme += next_char

            self.position += 1
            self.column += 1

            kind = self.dualoperands[lexeme]   
        else:
            kind = self.simple_tokens[lexeme]


        return Token(kind=kind, lexeme=lexeme, value=None, line=initial_line, column=initial_column)



    def state_and_or(self) -> Token:
        initial_line = self.line
        initial_column = self.column

        lexeme = ""
        lexeme += self.source[self.position]

        self.position += 1
        self.column += 1

        next_char = self.source[self.position] if self.position < self.length else 'EOF'

        if next_char == "&" or next_char== "|":
            lexeme += next_char

            self.position += 1
            self.column += 1

            kind = self.dualoperands[lexeme]

            return Token(kind=kind, lexeme=lexeme, value=None, line=initial_line, column=initial_column)

        raise LexerError("Operador invalido!", initial_line, initial_column)



    def state_comment_line(self) -> None:
        self.position += 1
        self.column += 1

        while self.position < self.length and self.source[self.position] != '\n':
            self.position += 1
            self.column += 1

        return None
    


    def state_comment_block(self, initial_line: int, initial_column: int) -> None:

        self.position += 1
        self.column += 1

        while self.position < self.length:

            char = self.source[self.position]
            next_char = self.source[self.position + 1] if self.position + 1 < self.length else 'EOF'

            if char == '*' and next_char == '/':
                self.position += 2
                self.column += 2
                return None

            if char == '\n':
                self.line += 1
                self.column = 1

            else:
                self.column += 1

            self.position += 1

        raise LexerError("Comentário de bloco não fechado", initial_line, initial_column)



    def state_slash(self) -> Token | None:
        initial_line = self.line
        initial_column = self.column

        self.position += 1
        self.column += 1

        next_char = self.source[self.position] if self.position < self.length else 'EOF'

        handler = self.transition_table['slash'].get(next_char, self.transition_table['slash']['default'])

        if handler == self.state_comment_line:
            return self.state_comment_line()
        elif handler == self.state_comment_block:
            return self.state_comment_block(initial_line=initial_line, initial_column=initial_column)
        
        return Token(kind=TokenKind.SLASH, lexeme='/', value= None, line= initial_line, column=initial_column )



    def state_whitespace(self) -> None:

        while self.position < self.length and self.source[self.position].isspace():

            char = self.source[self.position]

            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1

            self.position += 1 

        return None

    def state_string(self) -> Token:
        initial_line = self.line
        initial_column = self.column
        
        # Guardamos a posição inicial para recortar o lexema real direto do código
        start_pos = self.position
        
        # Usamos uma lista para montar o valor da string com os escapes decodificados
        value_chars = []

        # Pula a aspa dupla de abertura
        self.position += 1
        self.column += 1

        while self.position < self.length:
            char = self.source[self.position]

            # 1. Condição de parada: aspa dupla de fechamento
            if char == '"':
                self.position += 1
                self.column += 1
                
                # Lexema é o texto exato do código-fonte (ex: "\"abc\\n\"")
                lexeme = self.source[start_pos:self.position]
                
                # Value é a string decodificada na memória (ex: "abc" seguido de quebra de linha)
                value = "".join(value_chars)
                
                return Token(
                    kind=TokenKind.STRING_LITERAL,
                    lexeme=lexeme,
                    value=value,
                    line=initial_line,
                    column=initial_column
                )

            # 2. Quebra de linha não escapada no meio da string (erro léxico)
            if char == '\n':
                raise LexerError("String não fechada", self.line, self.column)

            # 3. Tratamento da barra de escape (\)
            if char == '\\':
                # Salva a linha e coluna exatas da barra invertida para caso o escape seja inválido
                esc_line = self.line
                esc_col = self.column
                
                self.position += 1
                self.column += 1

                # Se o arquivo acabar logo depois da barra
                if self.position >= self.length:
                    raise LexerError("String não fechada", initial_line, initial_column)

                # Decodifica o próximo caractere
                next_char = self.source[self.position]
                if next_char == 'n':
                    value_chars.append('\n')
                elif next_char == 't':
                    value_chars.append('\t')
                elif next_char == '"':
                    value_chars.append('"')
                elif next_char == '\\':
                    value_chars.append('\\')
                else:
                    # Lança o erro apontando EXATAMENTE para o local do `\`
                    raise LexerError("Sequência de escape inválida", esc_line, esc_col)

                self.position += 1
                self.column += 1
                
            # 4. Qualquer outro caractere comum
            else:
                value_chars.append(char)
                self.position += 1
                self.column += 1

        # 5. Se o while terminar e a string não tiver sido fechada, 
        # o erro deve apontar para onde a string COMEÇOU
        raise LexerError("String não fechada", initial_line, initial_column)


    def state_number(self) -> Token:
        initial_line = self.line
        initial_column = self.column
        digits = ""

        while self.position < self.length and self.source[self.position].isdigit():
            
            digits += self.source[self.position]

            self.position += 1
            self.column += 1

        return Token(kind=TokenKind.INT_LITERAL, lexeme=digits, value=int(digits), line=initial_line, column=initial_column)


    def state_identifier(self) -> Token:
        initial_line = self.line
        initial_column = self.column
        identifier = ""

        while self.position < self.length:
            char = self.source[self.position]
            if (char.isascii() and char.isalnum()) or char == '_':
                identifier += char
                self.position += 1
                self.column += 1
            else:
                break

        lexeme = identifier

        if identifier in self.keywords:
            kind = self.keywords[identifier]
            
            if kind == TokenKind.KW_TRUE:
                value = True
            elif kind == TokenKind.KW_FALSE:
                value = False
            else:
                value = None 
        else:
            kind = TokenKind.IDENTIFIER
            value = identifier

        return Token(kind=kind, lexeme=lexeme, value=value, line=initial_line, column=initial_column)
    
    def tokens(self) -> Iterator[Token]:
        """Produza todos os tokens significativos e um único EOF ao final."""

        while self.position < self.length:
            char = self.source[self.position]

            # 1. Classifica o caractere para consultar a tabela
            if (char.isascii() and char.isalpha()) or char == '_':
                key = 'alpha'
            elif char.isdigit():
                key = 'digit'
            elif char.isspace():
                key = 'whitespace'
            else:
                key = char

            # 2. Busca a função de transição mapeada no estado 'start'
            handler = self.transition_table['start'].get(key)

            if handler is None:
                raise LexerError(f"Caractere inválido: {char!r}", self.line, self.column)

            # 3. Executa a função do estado
            token = handler()

            # 4. Emite o token se ele existir (whitespace retorna None)
            if token is not None:
                yield token

        # 5. Emite o token obrigatório de fim de arquivo
        yield Token(TokenKind.EOF, "", None, self.line, self.column)
    

    def scan(self) -> list[Token]:

        return list(self.tokens())

