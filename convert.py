import sys
import re
import xml.etree.ElementTree
import math
from Equation import Equation

class FunctionalBlock:
    def __init__(self, name, function, args):
        self.name = name
        self.function = function
        self.args = args
        self.outputs = []
        self.inputs = []

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        argsStr = ", ".join(map(lambda a: str(a), self.args))
        inputs = ", ".join(self.inputs)
        outputs = ", ".join(self.outputs)
        return self.name + ": " + self.function + "(" + argsStr + ")\n\tInputs: [" + inputs + "]\n\tOutputs: [" + outputs + "]\n"

    def __repr__(self): return str(self)

    def addInput(self, inpt):
        self.inputs.append(inpt)

    def output(self):
        index = len(self.outputs)
        output = self.name + str(index)
        self.outputs.append(output)
        return output

class Model:
    def __init__(self, flows, stocks, auxies, start, stop, dt):
        self.flows = flows
        self.stocks = stocks
        self.auxies = auxies
        self.start = start
        self.stop = stop
        self.dt = dt        
        # raise NameError(alias + " not found in flows, stocks and auxies")

class Flow:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = Equation(eqn)

class Stock:
    def __init__(self, name, eqn, inflows, outflows):
        self.name = name
        self.eqn = Equation(eqn)
        # references to incoming flows
        self.inflows = inflows
        # references to outgoing flows
        self.outflows = outflows

class Aux:
    def __init__(self, name, eqn):
        self.name = name
        self.eqn = Equation(eqn)

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

def symbolToFBName(symbol):
    symbols = "+-*/"
    names = ["add", "sub", "mul", "div"]
    return names[symbols.index(symbol)]

def listExpressions(expression, lst, name = ""):
    if len(name) == 0:
        name = expression.text.replace("\"", "")
    args = []
    if expression.tokens[0].type == Equation.TYPE_EXPRESSION:
        args.append(expression.tokens[0].text.replace("\"", ""))
        listExpressions(expression.tokens[0], lst)
    else:
        args.append(expression.tokens[0].tokens[0])
    if expression.tokens[2].type == Equation.TYPE_EXPRESSION:
        args.append(expression.tokens[2].text)
        listExpressions(expression.tokens[2], lst)
    else:
        args.append(expression.tokens[2].tokens[0])
    operator = symbolToFBName(expression.tokens[1].tokens[0])
    lst.append(FunctionalBlock(name, operator, args))

def resolveToNubmer(eqn, model):
    if eqn.type == Equation.TYPE_NUMBER:
        return eqn.tokens[0]
    if eqn.type == Equation.TYPE_EXPRESSION:
        raise NotImplementedError("Expressions not supported")
    for namedEqn in model.auxies:
        if namedEqn.name == eqn.text:
            return resolveToNubmer(namedEqn.eqn, model)

def build_sdf_model(model):
    constants = []
    fbs = []
    stocks = []
    for namedEqn in model.flows + model.auxies:
        if namedEqn.eqn.type == Equation.TYPE_EXPRESSION:
            listExpressions(namedEqn.eqn, fbs, namedEqn.name )
    for stock in model.stocks:
        val = resolveToNubmer(stock.eqn, model)
        stocks.append(FunctionalBlock(stock.name, "loop", [val, stock.name + "'"]))
    for aux in model.auxies:
        if aux.eqn.type == Equation.TYPE_NUMBER:
            constants.append(FunctionalBlock(aux.name, "constant", [aux.eqn.tokens[0]]))

    constants.append(FunctionalBlock("t_step", "constant", [str(model.dt)]))
    zero = FunctionalBlock("zero", "constant", "0")
    constants.append(zero)

    fbs.append(FunctionalBlock("t'", "add", ["t", "t_step"]))
    stocks.append(FunctionalBlock("t", "loop", [0, "t'"]))

    for stock in model.stocks:
        for inflow in stock.inflows:
            fbs.append(FunctionalBlock(stock.name + "_delta_in", "mul", [inflow.replace("\"", ""), "t_step"]))
        for outflow in stock.outflows:
            fbs.append(FunctionalBlock(stock.name + "_delta_out", "mul", [outflow.replace("\"", ""), "t_step"]))
        fbs.append(FunctionalBlock(stock.name + "_delta", "sub", [stock.name + "_delta_in", stock.name + "_delta_out"]))
        fbs.append(FunctionalBlock(stock.name + "'", "add", [stock.name, stock.name + "_delta"]))

    for fb in fbs + stocks:
        for arg in fb.args:
            connected = False
            for fb_in in (fbs + constants + stocks):
                if arg == fb_in.name:
                    fb.addInput(fb_in.output())
                    connected = True
                    break
            if not (connected or type(arg) is int):
                fb.addInput(zero.output())

    print(fbs, constants, stocks, sep='\n--------------------------------\n')
    return (fbs, constants, stocks)

def generate_haskell_fb_code(fbs, constants, stocks):
    fbSrc = "[ "
    nodes = []
    for constant in constants:
        node = "FB." + constant.function + " " + str(int(float(constant.args[0]) * 1000)) + " [" + ", ".join(map(lambda x: '"' + x + '"', constant.outputs)) + "]"
        nodes.append(node)
    for stock in stocks:
        node = "FB." + stock.function + " " + str(int(float(stock.args[0]) * 1000)) + " [" + ", ".join(map(lambda x: '"' + x + '"', stock.outputs)) + "] " + "\"" + stock.inputs[0] + "\""
        nodes.append(node)
    for fb in fbs:
        node = "FB." + fb.function + " " + " ".join(map(lambda x: "\"" + x + "\"", fb.inputs)) + " [" + ", ".join(map(lambda x: '"' + x + '"', fb.outputs)) + "]"
        nodes.append(node)
    fbSrc += "\n, ".join(nodes)
    fbSrc += " :: FB (Parcel String Int)\n]"
    return fbSrc

if len(sys.argv) != 2:
    print("Usage:\nxmile2sdf.py <input_file.xml>")
    exit(0)
print("\n================================\nSTARTED\n================================\n")
print("Opening", sys.argv[1])
model = parse_xmile(sys.argv[1])
print("\n================================\nXMILE -> DONE\n================================\n")
sdf = build_sdf_model(model)
print("\n================================\nSDF -> DONE\n================================\n")
print(generate_haskell_fb_code(sdf[0], sdf[1], sdf[2]), 
end="\n================================\nFB -> DONE\n================================\n")

