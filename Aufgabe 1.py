import graphviz


class AndNode:
    def __init__(self, name):
        self.name = name
        self.nodes = []

    def __repr__(self):
        return self.name

    def add(self, node):
        self.nodes.append(node)
        return

    def topdown(self, mat):
        for i in range(len(mat)):
            for j in range(len(mat[i])):
                if mat[i][j].name == self.name:
                    del mat[i][j]
                    for k in self.nodes:
                        mat[i].append(k)

        for l in self.nodes:
            mat = l.topdown(mat)
        return mat

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

    def __repr__(self):
        return self.name

    def add(self, node):
        self.nodes.append(node)
        return

    def topdown(self, mat):
        for i in range(len(mat)):
            for j in range(len(mat[i])):
                if mat[i][j].name == self.name:
                    del mat[i][j]
                    mat[i].append(self.nodes[0])
                    if len(self.nodes) > 1:
                        for k in self.nodes[1:]:
                            mat.append(mat[i][:-1] + [k])

        for l in self.nodes:
            mat = l.topdown(mat)
        return mat

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




class Event:
    name = ""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def topdown(self, mat):
        return mat


# top = AndNode("TOP")
# a = OrNode("A")
# b = OrNode("B")
# d = AndNode("C")
# e1 = Event("1")
# e2 = Event("2")
# e3 = Event("3")
# e4 = Event("4")
# e5 = Event("5")
#
# top.add(a)
# top.add(b)
# b.add(d)
# b.add(e5)
# a.add(e1)
# a.add(e2)
# d.add(e3)
# d.add(e4)

k1 = AndNode("K1")
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

g = graphviz.Graph("error_tree")

g = k1.make_graph(g)

g.view()

mat = [[k1]]
mat = k1.topdown(mat)

print(mat)