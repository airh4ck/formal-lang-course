import os
from pyformlang.cfg import CFG


def cfg_to_wcnf(cfg: CFG) -> CFG:
    wcnf = cfg.eliminate_unit_productions().remove_useless_symbols()
    wcnf_productions = wcnf._get_productions_with_only_single_terminals()
    wcnf_productions = wcnf._decompose_productions(wcnf_productions)

    return CFG(start_symbol=wcnf.start_symbol, productions=wcnf_productions)


def cfg_from_file(path: str) -> CFG:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, "r") as file:
        cfg = file.read()

    return CFG.from_text(cfg)
