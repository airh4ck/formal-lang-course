from project.language.langParser import langParser
from project.language.langVisitor import langVisitor
from project.graphs.graph_info import get_graph

from project.language.typing import MyAutomaton, MyCFG, MySet


class Visitor(langVisitor):
    def __init__(self):
        self.__env = dict()

    def visitString(self, ctx: langParser.StringContext):
        return ctx.STRING().getText()[1:-1]

    def visitInt(self, ctx: langParser.IntContext):
        num = ctx.DIGIT() or ctx.INT()
        return int(num.getText())

    def visitBool(self, ctx: langParser.BoolContext):
        return ctx.BOOL().getText() == "true"

    def visitRegex(self, ctx: langParser.RegexContext):
        return MyAutomaton.from_regex(ctx.REGEX().getText()[1:-1])

    def visitCfg(self, ctx: langParser.CfgContext):
        return MyCFG.from_text(ctx.CFG().getText()[2:-1])

    def visitVal(self, ctx: langParser.ValContext):
        return self.visitChildren(ctx)

    def visitVar(self, ctx: langParser.VarContext):
        id = ctx.CHAR() or ctx.ID()
        if id.getText() not in self.__env:
            raise RuntimeError(f"Unbound variable: {id.getText()}")
        return self.__env[id.getText()]

    def visitLambda(self, ctx: langParser.LambdaContext):
        if lam := ctx.lambda_():
            return self.visit(lam)

        return self.visitChildren(ctx)

    def _get_lam_args(self, ctx: langParser.LambdaContext):
        if lam := ctx.lambda_():
            return self._get_lam_args(lam)

        return ctx.var()

    def visitMap(self, ctx: langParser.MapContext):
        st = self.visit(ctx.set_())
        if not isinstance(st, MySet):
            raise TypeError("Map expects a set as its operand")
        lambda_args = self._get_lam_args(ctx.lambda_())
        result = set()
        for elem in st.data:
            old_env = self.__env.copy()
            self.__env[lambda_args[0].getText()] = elem
            result.add(self.visit(ctx.lambda_()))
            self.__env = old_env.copy()
        return MySet(result)

    def visitFilter(self, ctx: langParser.FilterContext):
        st = self.visit(ctx.set_())
        if not isinstance(st, MySet):
            raise TypeError("Filter expects a set as its operand")
        lambda_args = self._get_lam_args(ctx.lambda_())
        result = set()
        for elem in st.data:
            old_env = self.__env.copy()
            self.__env[lambda_args[0].getText()] = elem
            if not isinstance(filter_result := self.visit(ctx.lambda_()), bool):
                raise TypeError(
                    f"Filter expected a function that returns a bool. Received {type(filter_result)} instead"
                )

            if filter_result:
                result.add(elem)
            self.__env = old_env.copy()
        return MySet(result)

    def visitSet_start(self, ctx: langParser.Set_startContext):
        automaton = self.visit(ctx.graph())
        if not isinstance(automaton, MyAutomaton):
            raise TypeError(
                "Expected a regular expression or a graph when setting start vertices"
            )
        return automaton.set_start(self.visit(ctx.set_()))

    def visitSet_final(self, ctx: langParser.Set_finalContext):
        automaton = self.visit(ctx.graph())
        if not isinstance(automaton, MyAutomaton):
            raise TypeError(
                "Expected a regular expression or a graph when setting final vertices"
            )
        return automaton.set_final(self.visit(ctx.set_()))

    def visitAdd_start(self, ctx: langParser.Add_startContext):
        automaton = self.visit(ctx.graph())
        if not isinstance(automaton, MyAutomaton):
            raise TypeError(
                "Expected a regular expression or a graph when adding start vertices"
            )
        return automaton.add_start(self.visit(ctx.set_()))

    def visitAdd_final(self, ctx: langParser.Add_finalContext):
        automaton = self.visit(ctx.graph())
        if not isinstance(automaton, MyAutomaton):
            raise TypeError(
                "Expected a regular expression or a graph when adding final vertices"
            )
        return automaton.add_final(self.visit(ctx.set_()))

    def visitLoad(self, ctx: langParser.LoadContext):
        path = self.visit(ctx.string())
        if path.endswith(".dot"):
            return MyAutomaton.from_dot(path)
        return MyAutomaton.from_graph(get_graph(path))

    def visitGet_start(self, ctx: langParser.Get_startContext):
        return self.visit(ctx.graph()).get_start()

    def visitGet_final(self, ctx: langParser.Get_finalContext):
        return self.visit(ctx.graph()).get_final()

    def visitGet_edges(self, ctx: langParser.Get_edgesContext):
        return self.visit(ctx.graph()).get_edges()

    def visitGet_labels(self, ctx: langParser.Get_labelsContext):
        return self.visit(ctx.graph()).get_labels()

    def visitGet_vertices(self, ctx: langParser.Get_verticesContext):
        return self.visit(ctx.graph()).get_vertices()

    def visitEmpty_list(self, ctx: langParser.Empty_listContext):
        return MySet(set())

    def visitGet_reachable(self, ctx: langParser.Get_reachableContext):
        return self.visit(ctx.graph()).get_reachable()

    def visitList(self, ctx: langParser.ListContext):
        if ctx.empty_list():
            return self.visitChildren(ctx)

        lst = [self.visit(expr) for expr in ctx.expr()]
        return MySet(set(lst))

    def visitRange(self, ctx: langParser.RangeContext):
        left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("Expected both boundaries of a range to be integers")
        return MySet(set(range(left, right + 1)))

    def visitExpr(self, ctx: langParser.ExprContext):
        if ctx.LANG_AND():
            left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
            if not (
                isinstance(left, MyAutomaton) and isinstance(right, MyAutomaton)
            ) and not (isinstance(left, MyCFG) and isinstance(right, MyAutomaton)):
                raise TypeError(
                    "Intersection expects both operands to be regexes/graphs or left operand to be a CFG and right operand to be regex/graph"
                )
            return left.intersect(right)
        if ctx.LANG_OR():
            left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
            if not (
                isinstance(left, MyAutomaton) and isinstance(right, MyAutomaton)
            ) and not (isinstance(left, MyCFG) and isinstance(right, MyCFG)):
                raise TypeError(
                    "Union expects both operands to have the same type: either regex/graph or CFG"
                )
            return left.union(right)
        if ctx.LANG_DOT():
            left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
            if not (
                isinstance(left, MyAutomaton) and isinstance(right, MyAutomaton)
            ) and not (isinstance(left, MyCFG) and isinstance(right, MyCFG)):
                raise TypeError(
                    "Concatenation expects both operands to have the same type: either regex/graph or CFG"
                )
            return left.concat(right)
        if ctx.AND():
            left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
            if not isinstance(left, bool) or not isinstance(right, bool):
                raise TypeError(
                    "Operands of logical AND are expected to have type bool"
                )
            return left and right
        if ctx.OR():
            left, right = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
            if not isinstance(left, bool) or not isinstance(right, bool):
                raise TypeError("Operands of logical OR are expected to have type bool")
            return left or right
        if ctx.KLEENE():
            expr = self.visit(ctx.expr(0))
            if not isinstance(expr, MyAutomaton):
                raise TypeError("Kleene star expects a regex/graph")
            return expr.kleene()
        if ctx.NOT():
            expr = self.visit(ctx.expr(0))
            if not isinstance(expr, bool):
                raise TypeError(
                    "Logical negation expects its argument to have type bool"
                )
            return not expr
        if ctx.NEG():
            expr = self.visit(ctx.expr(0))
            if not isinstance(expr, int):
                raise TypeError(
                    "Integer negation expects its argument to have type int (duh!)"
                )
            return (-1) * expr

        return self.visitChildren(ctx)

    def visitStmt(self, ctx: langParser.StmtContext):
        return self.visitChildren(ctx)

    def visitBind(self, ctx: langParser.BindContext):
        var_name = ctx.var().getText()
        expr = self.visit(ctx.expr())
        self.__env[var_name] = expr

    def visitPrint(self, ctx: langParser.PrintContext):
        val = self.visit(ctx.expr())
        print(val)
