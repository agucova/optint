from typing import Tuple, List
from paciente import Paciente
from random import seed
from functools import lru_cache

def gen_patients(
    n_pacientes: int,
    deterministic=True
) -> Tuple[
    List[int], List[int], List[int], List[int], List[int], List[bool], List[int]
]:
    """Generate n patients using the probabilistic patient model.
    Returns as lists, P, G, I, E_start, E_end, V, S"""
    if deterministic:
        seed(93983298324)
    pacientes = [Paciente() for _ in range(n_pacientes)]
    return tuple(
        zip(
            *[
                (index, p.g, p.i, p.e_start, p.e_end, p.v, p.s)
                for index, p in enumerate(pacientes)
            ]
        )
    )
