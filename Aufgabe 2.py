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


class ParBlock:
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
            reliability = (1 - reliability) * (1 - self.blocks[i].rel())

        reliability = 1 - reliability

        return reliability


e = Block("Eingang", 0.99)
r1 = Block("Rechner1", 0.99)
r2 = Block("Rechner2", 0.99)
a = Block("Ausgang", 0.99)

seq = SeqBlock("Alle")
par = ParBlock("Alle_Rechner")

par.append(r1)
par.append(r2)

seq.append(e)
seq.append(par)
seq.append(a)

g = graphviz.Graph("rel_diagram", graph_attr={"rankdir": "LR"}, node_attr={"shape":"rectangle"})

print(seq.rel())