import re
import xml.etree.ElementTree
import math

class FunctionalBlock:
    def __init__(self, inputs, outputs, function):
        self.inputs = inputs
        self.outputs = outputs
        self.function = function

class Equation:
    def __init__(self, text):
        self.text = text
        self.aliases = re.findall(r"\"(.+?)\"", text)
        # If there are no aliases in equation then it is constant.
        # Provided aliases are wrapped in quotes.
        self.isConstant = len(self.aliases) == 0

class Model:
    def __init__(self, flows, stocks, auxies, start, stop, dt):
        self.flows = flows
        self.stocks = stocks
        self.auxies = auxies
        self.start = start
        self.stop = stop
        self.dt = dt
        aliasesExtractor = lambda obj: obj.aliases
        allAliases = map(aliasesExtractor, flows) + map(aliasesExtractor, stocks) + map(aliasesExtractor, auxies)
        for equatable in (flows + stocks + auxies):
            for alias in equatable.eqn.aliases:
                # check for invalid aliases
                if(alias not in allAliases):
                    raise NameError(alias + " not found in flows, stocks and auxies")       
    
    def transformEquationToBlock(self, equation):
        inputs = []
        if equation[0] == '\"':
            inputs.append(getFirstAliasWithinQuotes(equation))
        else:
            pass
        

    def nextToken(self, equationString):
        pass

class Flow:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = Equation(eqn)
        self.isConstant = eqn.isConstant

class Stock:
    def __init__(self, name, eqn, inflows, outflows):
        self.name = name
        self.eqn = Equation(eqn)
        # references to incoming flows
        self.inflows = inflows
        # references to outgoing flows
        self.outflows = outflows
        self.isConstant = eqn.isConstant

class Aux:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = Equation(eqn)
        self.isConstant = eqn.isConstant

def parse_xmile(filename):
    ns = { "xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0" }
    tree = xml.etree.ElementTree.parse(filename)
    root = tree.getroot()

    simSpecs = root.find("xmile:sim_specs", ns)
    start = simSpecs.find("xmile:start", ns).text
    stop = simSpecs.find("xmile:stop", ns).text
    dt = simSpecs.find("xmile:dt", ns).text

    variables = root.find("xmile:model", ns).find("xmile:variables", ns)

    auxies = []
    for aux in variables.findall("xmile:aux", ns):
        name = aux.get("name")
        eqn = aux.find("xmile:eqn", ns).text
        auxies.append(Aux(name, eqn))

    stocks = []
    for stock in variables.findall("xmile:stock", ns):
        name = stock.get("name")
        eqn = stock.find("xmile:eqn", ns).text
        inflows = []
        for inflow in stock.findall("xmile:inflow", ns):
            inflows.append(inflow.text)
        outflows = []
        for outflow in stock.findall("xmile:outflow", ns):
            outflows.append(outflow.text)
        stocks.append(Stock(name, eqn, inflows, outflows))

    flows = []
    for flow in variables.findall("xmile:flow", ns):
        name = flow.get("name")
        eqn = flow.find("xmile:eqn", ns).text
        flows.append(Flow(name, eqn))

    return Model(flows, stocks, auxies, start, stop, dt)

model = parse_xmile("teacup.xml")