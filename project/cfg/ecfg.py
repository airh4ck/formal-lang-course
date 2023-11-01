from typing import Set, Dict
from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.regular_expression import Regex
import os


class ECFG:
    def __init__(
        self,
        variables: Set[Variable],
        terminals: Set[Terminal],
        start: Variable,
        productions: Dict[Variable, Regex],
    ):
        self.variables = variables
        self.terminals = terminals
        self.start = start
        self.productions = productions

    @staticmethod
    def from_cfg(cfg: CFG) -> "ECFG":
        ecfg_productions = dict()
        for production in cfg.productions:
            head, body = production.head, production.body
            rhs = Regex(".".join(symbol.value for symbol in body))
            if len(body) == 0:
                rhs = Regex("$")

            if head in ecfg_productions:
                ecfg_productions[head] = ecfg_productions[head].union(rhs)
            else:
                ecfg_productions[head] = rhs

        return ECFG(cfg.variables, cfg.terminals, cfg.start_symbol, ecfg_productions)

    @staticmethod
    def from_text(text: str) -> "ECFG":
        return ECFG.from_cfg(CFG.from_text(text))

    @staticmethod
    def from_file(path: str) -> "ECFG":
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        with open(path, "r") as file:
            cfg_text = file.read()

        return ECFG.from_text(cfg_text)
