import graphviz


class Block:
    def __init__(self, name, reliability):
        self.name = name
        self.reliability = reliability

    def print_name(self):
        print(self.name)

    def get_name(self):
        return self.name

    def rel(self):
        return self.reliability

    def make_graph(self, graph, origin=None):
        if type(origin) == ParBlock:
            for i in range(len(origin.blocks)):
                graph.edge(origin.blocks[i].name, self.name)
            return graph

        if origin is not None:
            graph.edge(origin.name, self.name)

        return graph


class SeqBlock:
    def __init__(self, name):
        self.blocks = []
        self.name = name

    def append(self, node):
        self.blocks.append(node)
        return

    def print_name(self):
        print(self.name)

    def get_name(self):
        return self.name

    def rel(self):
        reliability = 1.0

        for i in range(len(self.blocks)):
            reliability *= self.blocks[i].rel()

        return reliability

    def make_graph(self, graph, origin=None):
        self.blocks[0].make_graph(graph, origin)
        for i in range(len(self.blocks) - 1):
            self.blocks[i + 1].make_graph(graph, self.blocks[i])

        return graph


class ParBlock:
    def __init__(self, name):
        self.blocks = []
        self.name = name

    def __repr__(self):
        return self.name

    def append(self, node):
        self.blocks.append(node)
        return

    def print_name(self):
        print(self.name)

    def get_name(self):
        return self.name

    def rel(self):
        probability = 1.0

        for i in range(len(self.blocks)):
            probability *= 1 - self.blocks[i].rel()

        return 1 - probability

    def make_graph(self, graph, origin):
        if origin is not None:
            for i in range(len(self.blocks)):
                self.blocks[i].make_graph(graph, origin)
        else:
            pass

        return graph


# new Classes
class AndNode:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.zero = Connector("Failure")
        self.one = Connector("Success")
        self.next_connection = None

    def __repr__(self):
        return self.name

    def add(self, node):
        self.nodes.append(node)
        return

    def make_graph(self, graph):
        for i in self.nodes:
            if type(self) == AndNode:
                top_ext = " &"
            elif type(self) == OrNode:
                top_ext = " >=1"
            else:
                top_ext = ""

            if type(i) == AndNode:
                i_ext = " &"
            elif type(i) == OrNode:
                i_ext = " >=1"
            else:
                i_ext = ""

            graph.edge(self.name + top_ext, i.name + i_ext)
            if type(i) == Event:
                pass
            else:
                i.make_graph(graph)
        return graph


class OrNode:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.zero = Connector("Failure")
        self.one = Connector("Success")
        self.next_connection = None

    def __repr__(self):
        return self.name

    def add(self, node):
        self.nodes.append(node)
        return

    def make_graph(self, graph):
        for i in self.nodes:
            if type(self) == AndNode:
                top_ext = " &"
            elif type(self) == OrNode:
                top_ext = " >=1"
            else:
                top_ext = ""

            if type(i) == AndNode:
                i_ext = " &"
            elif type(i) == OrNode:
                i_ext = " >=1"
            else:
                i_ext = ""

            graph.edge(self.name + top_ext, i.name + i_ext)
            if type(i) == Event:
                pass
            else:
                i.make_graph(graph)
        return graph


class Connector:
    def __init__(self, name):
        self.name = name
        self.connection = None

    def __repr__(self):
        if self.connection is None:
            return self.name + ": None"
        else:
            return self.name + ": " + self.connection.name


class Event:
    def __init__(self, name):
        self.name = name
        self.zero = None
        self.one = None

    def __repr__(self):
        return self.name


allEvents = []


def fault_tree_2_bdd(top_node, graph):
    if type(top_node) == AndNode:
        createAnd(top_node)

    elif type(top_node) == OrNode:
        createOr(top_node)

    else:
        raise Exception("params wrong types: Make sure you use AndNode or OrNode")

    print(allEvents)

    for event in allEvents:
        if event.zero is None:
            graph.edge(event.name, "failure", label="fail", color="red:red")
        else:
            graph.edge(event.name, event.zero.name, label="fail", color="red:red")
        if event.one is None:
            graph.edge(event.name, "success", label="success", color="green:green")
        else:
            graph.edge(event.name, event.one.name, label="success", color="green:green")

    return graph


def createAnd(top_node, origin=None):
    global allEvents

    if origin is None:
        pass
    else:
        origin.one = top_node.nodes[0]

    for i in range(len(top_node.nodes)):
        if type(top_node.nodes[i]) == Event:
            allEvents.append(top_node.nodes[i])
            top_node.nodes[i].zero = None

            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].one = top_node.one.connection
            else:
                top_node.nodes[i].one = top_node.nodes[i + 1]

        elif type(top_node.nodes[i]) == AndNode:
            top_node.nodes[i].zero.connection = top_node.zero.connection
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].one.connection = top_node.one.connection
            else:
                top_node.nodes[i].one.connection = top_node.nodes[i + 1].nodes[0]

            createAnd(top_node.nodes[i], top_node.nodes[i - 1])

        elif type(top_node.nodes[i]) == OrNode:
            top_node.nodes[i].one.connection = top_node.one.connection
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero.connection = top_node.zero.connection
            else:
                top_node.nodes[i].zero.connection = top_node.nodes[i + 1].nodes[0]

            createOr(top_node.nodes[i], top_node.nodes[i - 1])


def createOr(top_node, origin=None):
    global allEvents

    for i in range(len(top_node.nodes)):
        if type(top_node.nodes[i]) == Event:
            allEvents.append(top_node.nodes[i])
            top_node.nodes[i].one = top_node.one.connection

            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero = top_node.zero.connection
            else:
                top_node.nodes[i].zero = top_node.nodes[i + 1]

        elif type(top_node.nodes[i]) == AndNode:
            top_node.nodes[i].zero.connection = top_node.zero.connection
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].one.connection = top_node.one.connection
            else:
                top_node.nodes[i].one.connection = top_node.nodes[i + 1].nodes[0]

            createAnd(top_node.nodes[i], top_node.nodes[i - 1])

        elif type(top_node.nodes[i]) == OrNode:
            top_node.nodes[i].one.connection = top_node.one.connection
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero.connection = top_node.zero.connection
            else:
                top_node.nodes[i].zero.connection = top_node.nodes[i+1].nodes[0]

            createOr(top_node.nodes[i], top_node.nodes[i - 1])


top = OrNode('TOP')
a = OrNode('A')
b = OrNode('B')

e1 = Event('E1')
e2 = Event('E2')
e3 = Event('E3')
e4 = Event('E4')

a.add(e3)
a.add(e4)

b.add(e1)
b.add(e2)

top.add(b)
top.add(a)

fault_tree_graph = graphviz.Graph("fault_tree")
fault_tree_graph = top.make_graph(fault_tree_graph)
fault_tree_graph.view()

bdd_graph = graphviz.Graph("BDD")
bdd_graph = fault_tree_2_bdd(top, bdd_graph)
print("DEBUG")
bdd_graph.view()

