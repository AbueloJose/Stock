from database.db_manager import DBManager

class CatalogoModel:
    def __init__(self):
        self.db = DBManager()

    def obtener_sugerencias(self, termino):
        """Busca coincidencias en el catálogo base para autocompletar."""
        query = """
            SELECT descripcion_base, familia, subfamilia, material 
            FROM catalogo_base 
            WHERE descripcion_base LIKE ?
        """
        # Se usa % para buscar coincidencias parciales en cualquier parte del texto
        return self.db.obtener_datos(query, (f"%{termino}%",))

    def cargar_catalogo_inicial(self, datos):
        """Inserta los datos limpios leídos del archivo Excel."""
        query = "INSERT INTO catalogo_base (familia, subfamilia, material, descripcion_base) VALUES (?, ?, ?, ?)"
        for dato in datos:
            self.db.ejecutar_consulta(query, dato)