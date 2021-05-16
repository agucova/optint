from random import randint, seed, uniform, choices

seed(32893892489)

class Paciente:
    def __init__(self):
        self.cov = choices(
            [True, False],
            weights=[0.4466019417, 1 - 0.4466019417]
        )[0] # booleano

        self.cama_ideal = choices(
            [1, 2, 3, 4],
            weights=[0.1941747573, 0.145631068, 0.145631068, 0.5145631068]
        )[0]   # entero

        self.unidad_ideal = choices(
            [1, 2, 3, 4, 5, 6, 7, 8],
            weights=[
                0.3312892185, 0.07615516258, 0.2114945807, 0.0463491158,
                0.1479091985, 0.1167475185, 0.02336289218, 0.04669231318
            ]
        )[0]  # entero
        
        # TODO: se dejo para probar
        self.severidad = uniform(0, 1) # float
        
        self.entrada = choices(
            range(1, 13),
            weights=[0.04464285714, 0.04464285714, 0.04464285714, 0.03571428571, 0.0625,
                    0.09821428571, 0.1160714286, 0.1830357143, 0.07589285714, 0.125,
                    0.08928571429, 0.08035714286]
        )[0] # entero entre 1 y 24
        
        x = choices(
            range(1,13),
            weights=[0, 0, 0.2, 0.2, 0.2, 0.2, 0.2, 0, 0, 0, 0, 0]

        )[0]  # entero entre 1 y 24, entrada < salida
        while(x < self.entrada):
            x = choices(
                range(1,13),
                weights=[0, 0, 0.2, 0.2, 0.2, 0.2, 0.2, 0, 0, 0, 0, 0]

            )[0]
        
        self.salida = x

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
