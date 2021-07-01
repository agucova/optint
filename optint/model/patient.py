from random import choices

class Contador:
    def __init__(self):
        self.value = 0

class Paciente:
    pacientes_covid = Contador()
    
    def __init__(self):
        self.cov = choices([True, False], weights=[0.4466019417, 1 - 0.4466019417])[
            0
        ]  # booleano


        self.cama_ideal = choices(
            range(4), weights=[0.1941747573, 0.145631068, 0.145631068, 0.5145631068]
        )[
            0
        ]  # entero

        self.unidad_ideal = choices(
            range(8),
            weights=[
                0.3312892185,
                0.07615516258,
                0.2114945807,
                0.0463491158,
                0.1479091985,
                0.1167475185,
                0.02336289218,
                0.04669231318,
            ],
        )[
            0
        ]  # entero

        self.severidad = choices(
            range(1, 11),
            weights=[
                3,
                5,
                6,
                4,
                3,
                2,
                3,
                1,
                2,
                1
            ],
        )[
            0
        ] 

        self.entrada = choices(
            range(12),
            weights=[
                83.6,
                0.8,
                0.8,
                0.6,
                1.1,
                1.7,
                2.0,
                3.1,
                1.3,
                2.2,
                1.5,
                1.4
            ],
        )[
            0
        ]

        self.salida = choices(
            range(12), 
            weights=[
                0.00,
                0.00,
                0.00,
                0.00,
                5.16,
                5.16,
                1.72,
                1.03,
                1.03,
                1.03,
                1.03,
                83.83
            ], 
        )[
            0
        ]  # entero entre 1 y 13, entrada < salida
        while self.salida < self.entrada:
            self.entrada = choices(
                range(12),
                weights=[
                    83.6,
                    0.8,
                    0.8,
                    0.6,
                    1.1,
                    1.7,
                    2.0,
                    3.1,
                    1.3,
                    2.2,
                    1.5,
                    1.4
                ],
            )[
                0
            ]

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
