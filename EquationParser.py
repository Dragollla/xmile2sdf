class EquationParser:

    TYPE_NUMBER = "NUMBER"
    TYPE_REFERENCE = "REFERENCE"
    TYPE_EQUATION = "EQUATION"
    TYPE_OPERATOR = "OPERATOR"

    def __init__(self):
        self.digits = "0123456789"
        self.operators = "+-*/"
        self.constants = ["pi", "e"]
        self.functions = ["sqrt", "pow", "sin", "cos", "tg"]
        self.quotes = "\"\'"

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
        if equationString[i] in self.quotes:
            # scan to next matching quote
            j = i + 1
            while j < len(equationString) and equationString[j] != equationString[i]:
                j += 1
            # include quotes in returning value
            return (equationString[i:j + 1], j + 1)
        # if token starts with digits then it is number
        if(equationString[i] in self.digits):
            # scan to last digit in number
            j = i + 1
            while j < len(equationString) and equationString[j] in self.digits:
                j += 1
            return (equationString[i:j], j + 1)
        if(equationString[i] in self.operators):
            return (equationString[i], i + 1)
        # if token is not a number, operator or var name wrapped in quotes
        # then it is a var name without quotes and possible math constant
        j = i + 1
        while j < len(equationString) and equationString[j] not in (self.digits + " " + self.operators):
            j += 1
        token = equationString[i:j+1]
        if token in self.constants:
            # replace constant with its value maybe? 
            return (token, j + 1)
        elif token in self.functions:    
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
    
    def getTokenType(self, tokenString):
        isNumber = True
        if tokenString[0] in self.quotes:
            return self.TYPE_REFERENCE
        if len(tokenString) == 1 and tokenString[0] in self.operators:
            return self.TYPE_OPERATOR
        for char in tokenString:
            if char not in self.digits:
                isNumber = False
        if isNumber:
            return self.TYPE_NUMBER
        return self.TYPE_EQUATION

    def parse(self, equationString):
        tokens = self.splitInTokens(equationString)
        for i, token in enumerate(tokens):
            tokenType = self.getTokenType(token)
            if tokenType == self.TYPE_EQUATION:
                tokens[i] = self.parse(token)
        return tokens
        
print(EquationParser().parse("(1 + 2) * 3 - (4 - (6 + 3)) / 10"))
