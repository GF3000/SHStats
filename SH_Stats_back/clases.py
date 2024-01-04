class equipo:
    def __init__(self, nombre, federacion=None, liga=None, grupo=None, temporada=None) -> None:
        self.nombre = nombre
        self.federacion = federacion
        self.liga = liga
        self.grupo = grupo
        self.temporada = temporada
        self.partidos = []
        self.gf = 0
        self.gc = 0
        self.victorias = 0
        self.derrotas = 0
        self.empates = 0

    def add_partido(self, partido):
        if (partido.gl == None or partido.gv == None):
            return
        # make a copy of the partido

        self.partidos.append(partido)

        if (self.es_local(partido)):
            self.gf += partido.gl
            self.gc += partido.gv
            if (partido.gl > partido.gv):
                self.victorias += 1
            elif (partido.gl < partido.gv):
                self.derrotas += 1
            else:
                self.empates += 1

        else:  # es visitante
            self.gf += partido.gv
            self.gc += partido.gl
            if (partido.gl > partido.gv):
                self.derrotas += 1
            elif (partido.gl < partido.gv):
                self.victorias += 1
            else:
                self.empates += 1

    def es_local(self, partido):
        return partido.local == self.nombre

    def __eq__(self, otro) -> bool:
        return isinstance(otro,
                          equipo) and self.nombre == otro.nombre  and self.temporada == otro.temporada

    def __str__(self) -> str:
        return self.nombre + "-> GF: " + str(self.gf) + " GC: " + str(self.gc)

    def _lt__(self, otro):
        return (self.gf - self.gc) < (otro.gf - otro.gc)

    def __gt__(self, otro):
        return (self.gf - self.gc) > (otro.gf - otro.gc)

    def __le__(self, otro):
        return (self.gf - self.gc) <= (otro.gf - otro.gc)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "federacion": self.federacion,
            "liga": self.liga,
            "grupo": self.grupo,
            "temporada": self.temporada,
            "partidos": len(self.partidos),
            "gf": self.gf,
            "gc": self.gc,
            "victorias": self.victorias,
            "derrotas": self.derrotas,
            "empates": self.empates
        }

class partido:

    def __init__(self, l=None, v=None, gl=0, gv=0, liga=None, grupo=None, temporada=None, federacion=None,
                 fecha=None) -> None:
        self.local = l
        self.visitante = v
        self.gl = int(gl)
        self.gv = int(gv)
        self.liga = liga
        self.grupo = grupo
        self.temporada = temporada
        self.federacion = federacion
        self.fecha = fecha

    def __str__(self) -> str:
        return self.local + " " + str(self.gl) + " - " + str(self.gv) + " " + self.visitante

    def copy(self):
        return partido(self.local, self.visitante, self.gl, self.gv, self.liga, self.grupo, self.temporada,
                       self.federacion, self.fecha)

    def to_dict(self):
        return {
            "local": self.local,
            "visitante": self.visitante,
            "gl": self.gl,
            "gv": self.gv,
            "liga": self.liga,
            "grupo": self.grupo,
            "temporada": self.temporada,
            "federacion": self.federacion,
            "fecha": self.fecha
        }


class listado_equipos:
    def __init__(self, elementos=None) -> None:
        if elementos is None:
            self.elementos = []
        else:
            self.elementos = elementos
        self.indice = 0
        print(f"Número de elementos: {len(self.elementos)}")

    def __contains__(self, item):
        for elemento in self.elementos:
            if elemento == item:
                return True
        return False

    def __iter__(self):
        return self

    def __next__(self):
        if (self.indice < len(self.elementos)):
            elemento = self.elementos[self.indice]
            self.indice += 1
            return elemento
        else:
            raise StopIteration()

    def __getitem__(self, index):
        return self.elementos[index]

    def __setitem__(self, index, value):
        self.elementos[index] = value

    def __len__(self):
        return len(self.elementos)

    def __str__(self) -> str:
        print("Elementos: ", end="")
        for elemento in self.elementos:
            print(elemento, end=", ")
        return str(self.elementos)

    def add(self, item):
        self.elementos.append(item)

    def index(self, item):
        for i, elemento in enumerate(self.elementos):
            if elemento == item:
                return i
        return -1

    def buscar(self, item):
        for elemento in self.elementos:
            if elemento == item:
                # print("Encontrado: " + str(elemento) + " es " + str(item))
                return elemento
        return None

    def buscar_por_nombre(self, nombre):
        for elemento in self.elementos:
            if elemento.nombre == nombre:
                return elemento
        return None

    def to_dict(self):
        diccionario = {}
        for elemento in self.elementos:
            nombre = elemento.nombre
            diccionario[nombre] = elemento.to_dict()
        return diccionario

    def get_nombre_equipos(self):
        nombres = []
        for elemento in self.elementos:
            nombres.append(elemento.nombre)
        return nombres



