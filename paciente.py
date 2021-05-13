from random import randint, seed

seed(32893892489)

class Paciente:

    def __init__(self, cov, cama_ideal, unidad_ideal, severidad, entrada, salida):
        self.cov = cov # booleano
        self.cama_ideal = cama_ideal # entero
        self.unidad_ideal = unidad_ideal # entero
        self.severidad = severidad # float
        self.entrada = entrada # entero entre 1 y 24
        self.salida = salida # entero entre 1 y 24, entrada < salida
        
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