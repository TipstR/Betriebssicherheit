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
        for i in range(len(self.blocks)-1):
            self.blocks[i+1].make_graph(graph, self.blocks[i])

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


e = Block("eingang 0.99", 0.99)
r1 = Block("r1 0.99", 0.99)
r2 = Block("r2 0.99", 0.99)
r3 = Block("r3 0.99", 0.99)
r4 = Block("r4 0.99", 0.99)
a = Block("ausgang 0.99", 0.99)

seq = SeqBlock("Alle")
par = ParBlock("Alle_Rechner")

par.append(r1)
par.append(r2)
par.append(r3)
par.append(r4)

seq.append(e)
seq.append(par)
seq.append(a)

g = graphviz.Graph("rel_diagram", graph_attr={"rankdir": "LR"}, node_attr={"shape": "rectangle"})

g = seq.make_graph(g)
g.view()

print(seq.rel())
