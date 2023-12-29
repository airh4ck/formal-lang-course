from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNode

from project.language.langListener import langListener

from pydot import Dot, Edge, Node


class DotListener(langListener):
    def __init__(self, tree: Dot, rules):
        self.tree = tree
        self.num_nodes = 0
        self.nodes = {}
        self.rules = rules
        super(DotListener, self).__init__()

    def enterEveryRule(self, ctx: ParserRuleContext):
        if ctx not in self.nodes:
            self.num_nodes += 1
            self.nodes[ctx] = self.num_nodes

        if ctx.parentCtx:
            self.tree.add_edge(Edge(self.nodes[ctx.parentCtx], self.nodes[ctx]))

        self.tree.add_node(Node(self.nodes[ctx], label=self.rules[ctx.getRuleIndex()]))

    def visitTerminal(self, node: TerminalNode):
        self.num_nodes += 1
        self.tree.add_edge(Edge(self.nodes[node.parentCtx], self.num_nodes))
        self.tree.add_node(Node(self.num_nodes, label=f"{node}"))
