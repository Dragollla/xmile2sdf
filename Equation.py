class Equation:

    TYPE_NUMBER = "NUMBER"
    TYPE_REFERENCE = "REFERENCE"
    TYPE_EXPRESSION = "EXPRESSION"
    TYPE_OPERATOR = "OPERATOR"

    DIGITS = "0123456789"
    OPERATORS = "*/+-"
    CONSTANTS = ["pi", "e"]
    FUNCTIONS = ["sqrt", "pow", "sin", "cos", "tg"]
    QUOTES = "\"\'"

    @staticmethod
    def getType(token):
        if type(token) is Equation:
            return token.type
        if len(token) == 1 and token in Equation.OPERATORS:
            return Equation.TYPE_OPERATOR
        if token.isdigit():
            return Equation.TYPE_NUMBER
        for op in list(Equation.OPERATORS) + Equation.FUNCTIONS:
            if op in token:
                return Equation.TYPE_EXPRESSION
        return Equation.TYPE_REFERENCE

    def __init__(self, text):
        self.text = text
        self.type = Equation.getType(text)
        self.tokens = self.parse(text)

    def __str__(self):
        return str(self.tokens) + " -> " + self.type

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not type(other) is Equation or len(self.tokens) != len(other.tokens):
            return False
        for i, self_token in enumerate(self.tokens):
            if self_token != other.tokens[i]:
                    return False
        return True
        
    # returns token and next index
    def readToken(self, equationString, i):
        # skip whitespaces
        while i < len(equationString) and equationString[i] == ' ':
            i += 1
        # if token starts with brace ( then it is equationString wrapped in braces
        if equationString[i] == '(':
            # scan to closing brace
            j = i + 1
            openingBracesCount = 1
            while j < len(equationString) and openingBracesCount > 0:
                j += 1
                if equationString[j] == '(':
                    openingBracesCount += 1
                elif equationString[j] == ')':
                    openingBracesCount -= 1
            # exclude braces from returning value
            return (equationString[i + 1:j], j + 1)
        # if token starts with quote then it is var name
        if equationString[i] in Equation.QUOTES:
            # scan to next matching quote
            j = i + 1
            while j < len(equationString) and equationString[j] != equationString[i]:
                j += 1
            # exclude quotes in returning value
            token = equationString[i:j]
            token = token.replace("\"", "")
            return (token, j + 1)
        # if token starts with digits then it is number
        if(equationString[i] in Equation.DIGITS):
            # scan to last digit in number
            j = i + 1
            while j < len(equationString) and equationString[j] in Equation.DIGITS:
                j += 1
            return (equationString[i:j], j + 1)
        if(equationString[i] in Equation.OPERATORS):
            return (equationString[i], i + 1)
        # if token is not a number, operator or var name wrapped in quotes
        # then it is a var name without quotes and possible math constant
        j = i + 1
        while j < len(equationString) and equationString[j] not in (Equation.DIGITS + " " + Equation.OPERATORS):
            j += 1
        token = equationString[i:j+1]
        if token in Equation.CONSTANTS:
            # replace constant with its value maybe? 
            return (token, j + 1)
        elif token in Equation.FUNCTIONS:    
            # todo: consider function token format
            return (token, j + 1)
        else:
            return (token, j + 1)

    def splitInTokens(self, equationString):
        tokens = []
        i = 0
        while i < len(equationString):
            t = self.readToken(equationString, i)
            tokens.append(Equation(t[0]))
            i = t[1]
        return tokens

    def parse(self, equationString):
        tokens = []
        if self.type == Equation.TYPE_EXPRESSION:
            tokens = self.splitInTokens(equationString)
        elif self.type == Equation.TYPE_NUMBER:
            tokens = [int(self.text)]
        elif self.type == Equation.TYPE_OPERATOR:
            tokens = [self.text]
        elif self.type == Equation.TYPE_REFERENCE:
            tokens = [self.text.replace("\"", "").replace("'", "")]
        return tokens
        
#print(Equation('("Teacup Temperature"-"Room Temperature")/"Characteristic Time"'))
