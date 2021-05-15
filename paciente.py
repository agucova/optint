from random import randint, seed

seed(32893892489)


class Paciente:
    def __init__(self):
        self.cov = None  # booleano
        self.cama_ideal = None  # entero
        self.unidad_ideal = None  # entero
        self.severidad = None  # float
        self.entrada = None  # entero entre 1 y 24
        self.salida = None  # entero entre 1 y 24, entrada < salida

    @property
    def v(self):
        return self.cov

    @property
    def g(self):
        return self.cama_ideal

    @property
    def i(self):
        return self.unidad_ideal

    @property
    def s(self):
        return self.severidad

    @property
    def e_start(self):
        return self.entrada

    @property
    def e_end(self):
        return self.salida
