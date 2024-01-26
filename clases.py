class competicion:
    def __init__(self, index = 0, nombre = "", enlaces = None):
        self.index = index
        self.nombre = nombre
        self.enlaces = enlaces if enlaces else []

    def __str__(self):
        return f"{self.nombre} - index = {self.index} - {self.enlaces}"

    def __repr__(self):
        return f"{self.nombre} - index = {self.index} - {self.enlaces}"
