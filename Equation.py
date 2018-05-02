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

    def __init__(self, text):
        self.text = text
        self.type = self.getTokenType(text)
        self.tokens = self.parse(text)

    def __str__(self):
        return self.text + '\n' + str(self.tokens)

    def __repr__(self):
        return (
    "-= Source =-" + self.text + " -> " + self.type + 
    "\n-= Tokens =-\n" + str(self.tokens) + 
    "\n-= Types =-\n" + str(list(map(lambda a: str(self.getTokenType(a)), self.tokens))))

    def __eq__(self, other):
        if len(self.tokens) != len(other.tokens):
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
            # include quotes in returning value
            return (equationString[i:j + 1], j + 1)
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
            tokens.append(t[0])
            i = t[1]
        return tokens
    
    def getTokenType(self, token):
        if type(token) is Equation:
            return Equation.TYPE_EXPRESSION
        
        # token is str

        isNumber = True
        isRef = True

        startsWithQuote = token[0] in Equation.QUOTES

        if len(token) == 1 and token[0] in Equation.OPERATORS:
            return self.TYPE_OPERATOR

        for i, char in enumerate(token):
            if char not in Equation.DIGITS:
                isNumber = False
            # if meet matching quote before the end of token 
            # than it is not valid reference
            if i > 0 and i < len(token) - 1 and startsWithQuote and char == token[0]:
                isRef = False
        if isRef and token[0] == token[len(token) - 1]:
            return Equation.TYPE_REFERENCE
        if isNumber:
            return Equation.TYPE_NUMBER
        return Equation.TYPE_EXPRESSION

    def parse(self, equationString):
        tokens = []
        if self.type == Equation.TYPE_EXPRESSION:
            tokens = self.splitInTokens(equationString)
            for i, token in enumerate(tokens):
                if self.getTokenType(token) == Equation.TYPE_EXPRESSION:
                    tokens[i] = Equation(token)
        elif self.type == Equation.TYPE_NUMBER:
            tokens = [int(self.text)]
        elif self.type == Equation.TYPE_OPERATOR or self.type == Equation.TYPE_REFERENCE:
            tokens = [self.text]
        return tokens
        
#print(Equation('("Teacup Temperature"-"Room Temperature")/"Characteristic Time"'))
