import re
import xml.etree.ElementTree

class Model:
    def __init__(self, flows, stocks, auxies, start, stop, dt):
        self.flows = flows
        self.stocks = stocks
        self.auxies = auxies
        self.start = start
        self.stop = stop
        self.dt = dt

class Flow:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = eqn

class Stock:
    def __init__(self, name, amount, inflows, outflows):
        self.name = name
        self.amount = amount
        self.inflows = inflows
        self.outflows = outflows

class Aux:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = eqn

def transform_equation(equation, auxies, stocks):
    aliases = re.findall(r"\"(.+?)\"", equation)
    for alias in aliases:
        aux = next((a for a in auxies if a.name == alias), None)
        if aux != None:
            equation = equation.replace('"' + alias + '"', aux.eqn)
        else:
            equation = equation.replace('"' + alias + '"', "amount (find (\\st -> name st == \"%s\") stocks)" % alias)
    return equation

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
        amount = stock.find("xmile:eqn", ns).text
        inflows = []
        for inflow in stock.findall("xmile:inflow", ns):
            inflows.append(inflow.text)
        outflows = []
        for outflow in stock.findall("xmile:outflow", ns):
            outflows.append(outflow.text)
        stocks.append(Stock(name, amount, inflows, outflows))

    flows = []
    for flow in variables.findall("xmile:flow", ns):
        name = flow.get("name")
        eqnStr = flow.find("xmile:eqn", ns).text
        eqn = transform_equation(eqnStr, auxies, stocks)
        flows.append(Flow(name, eqn))

    return Model(flows, stocks, auxies, start, stop, dt)

def gen_haskell_model(model):
    header = """module Model(
    stocks,
    flows,
    dt,
    start,
    stop
) where

import           Xmile
"""
    flowsType = "flows :: [Flow]"
    stocksType = "stocks :: [Stock]"
    startType = "start :: Num"
    stopType = "stop :: Num"
    dtType = "dt :: Num"

    stocksDeclaration = "stocks = "
    for stock in model.stocks:
        stocksDeclaration += "(Stock \"%s\" %s [%s] [%s]):" % \
        (stock.name, stock.amount, ", ".join(stock.inflows), ", ".join(stock.outflows))
    stocksDeclaration += "[]"

    flowsDeclaration = "flows = "
    for flow in model.flows:
        flowsDeclaration += "(Flow \"%s\" (\\s dt stocks -> changeStockAmount s (amount s + dt * (%s)))):" % (flow.name, flow.eqn)
    flowsDeclaration += "[]"

    source = header + '\n' + \
    startType + '\n' + \
    "start = " + model.start + "\n\n" + \
    stopType + '\n' + \
    "stop = " + model.stop + "\n\n" + \
    dtType + '\n' + \
    "dt = " + model.dt + "\n\n" + \
    flowsType + '\n' + \
    flowsDeclaration + "\n\n" + \
    stocksType + '\n' + \
    stocksDeclaration + "\n\n"

    file = open("generated.hs", "w")
    file.write(source)
    file.close()

model = parse_xmile("teacup.xml")
gen_haskell_model(model)
