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

    for i in range(len(top_node.nodes)):
        if type(top_node.nodes[i]) == Event:
            allEvents.append(top_node.nodes[i])
            temporary = top_node.zero.connection
            while True:
                if type(temporary) == Event:
                    top_node.nodes[i].zero = temporary
                    break
                elif temporary is None:
                    break
                else:
                    temporary = temporary.nodes[0]

            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].one = top_node.one.connection
            else:
                top_node.nodes[i].one = top_node.nodes[i + 1]

        elif type(top_node.nodes[i]) == AndNode:
            top_node.nodes[i].zero.connection = top_node
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].one.connection = top_node
            else:
                top_node.nodes[i].one.connection = top_node.nodes[i + 1]

            createAnd(top_node.nodes[i], top_node.nodes[i - 1])

        elif type(top_node.nodes[i]) == OrNode:
            top_node.nodes[i].one.connection = top_node
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero.connection = top_node
            else:
                top_node.nodes[i].zero.connection = top_node.nodes[i + 1]

            createOr(top_node.nodes[i], top_node.nodes[i - 1])


def createOr(top_node, origin=None):
    global allEvents

    for i in range(len(top_node.nodes)):
        if type(top_node.nodes[i]) == Event:
            allEvents.append(top_node.nodes[i])
            temporary = top_node.one.connection
            while True:
                if type(temporary) == Event:
                    top_node.nodes[i].one = temporary
                    break
                elif temporary is None:
                    break
                else:
                    temporary = temporary.nodes[0]

            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero = top_node.zero.connection
            else:
                top_node.nodes[i].zero = top_node.nodes[i + 1]

        elif type(top_node.nodes[i]) == AndNode:
            if origin is None:
                top_node.nodes[i].one.connection = None
            else:
                top_node.nodes[i].one.connection = top_node.next_connection
            if i == len(top_node.nodes) - 1:
                if origin is None:
                    top_node.nodes[i].zero.connection = top_node.zero.connection
                else:
                    top_node.nodes[i].zero.connection = top_node.zero.connection
            else:
                top_node.nodes[i].zero.connection = top_node.nodes[i + 1]

            createAnd(top_node.nodes[i], top_node.nodes[i - 1])

        elif type(top_node.nodes[i]) == OrNode:
            top_node.nodes[i].one.connection = top_node
            if i == len(top_node.nodes) - 1:
                top_node.nodes[i].zero.connection = top_node
            else:
                top_node.nodes[i].zero.connection = top_node.nodes[i + 1]

            createOr(top_node.nodes[i], top_node.nodes[i - 1])


k1 = OrNode("K1")
k2 = AndNode("K2")
k3 = AndNode("K3")
k4 = AndNode("K4")
k5 = OrNode("K5")
a = Event("a")
b = Event("b")
c = Event("c")
d = Event("d")
e = Event("e")
f = Event("f")
g = Event("g")

k1.add(k2)
k1.add(k3)
k2.add(d)
k2.add(e)
k2.add(k4)
k3.add(f)
k3.add(g)
k4.add(k5)
k4.add(c)
k5.add(a)
k5.add(b)

fault_tree_graph = graphviz.Graph("fault_tree")
fault_tree_graph = k1.make_graph(fault_tree_graph)
fault_tree_graph.view()

bdd_graph = graphviz.Graph("BDD")
bdd_graph = fault_tree_2_bdd(k1, bdd_graph)
print("DEBUG")
bdd_graph.view()

print("K1: ", k1.zero)
print("K1: ", k1.one)
print("K2: ", k2.zero)
print("K2: ", k2.one)
print("K3: ", k3.zero)
print("K3: ", k3.one)
print("K4: ", k4.zero)
print("K4: ", k4.one)
print("K5: ", k5.zero)
print("K5: ", k5.one)

print("a: ", a.one)
print("a: ", a.zero)
