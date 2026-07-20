from database.db_manager import DBManager

class InventarioModel:
    def __init__(self):
        self.db = DBManager()

    def agregar_producto(self, descripcion, medida, familia, subfamilia, material, tipo_producto, largo, alto, galeria, local, stock, es_retazo=0, id_padre=None):
        query = """
            INSERT INTO inventario 
            (descripcion, medida, familia, subfamilia, material, tipo_producto, largo, alto, galeria, local, stock, es_retazo, id_producto_padre) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parametros = (descripcion, medida, familia, subfamilia, material, tipo_producto, largo, alto, galeria, local, stock, es_retazo, id_padre)
        cursor = self.db.ejecutar_consulta(query, parametros)
        return cursor.lastrowid

    def obtener_todos(self):
        # Agregamos "alto" (Espesor) a la consulta. 
        # Nota: subfamilia funciona como Material, y material funciona como Color según nuestro formulario.
        query = "SELECT id, descripcion, alto, medida, familia, subfamilia, material, galeria, local, stock FROM inventario"
        return self.db.obtener_datos(query)

    def buscar_productos(self, termino, galeria, local):
        query = "SELECT id, descripcion, alto, medida, familia, subfamilia, material, galeria, local, stock FROM inventario WHERE 1=1"
        parametros = []
        
        if galeria != "Todo":
            query += " AND galeria = ?"
            parametros.append(galeria)
            
        if local != "-" and local != "Todos":
            query += " AND local = ?"
            parametros.append(local)
            
        if termino and termino.strip():
            palabras = termino.strip().split()
            for palabra in palabras:
                # Búsqueda súper ampliada: Busca en nombre, medida, color y material
                query += " AND (descripcion LIKE ? OR medida LIKE ? OR material LIKE ? OR subfamilia LIKE ?)"
                param = f"%{palabra}%"
                parametros.extend([param, param, param, param])
                
        return self.db.obtener_datos(query, tuple(parametros))

    def actualizar_stock(self, id_producto, cantidad_cambio):
        query = "UPDATE inventario SET stock = stock + ? WHERE id = ?"
        self.db.ejecutar_consulta(query, (cantidad_cambio, id_producto))
        
    def obtener_por_id(self, id_producto):
        query = "SELECT * FROM inventario WHERE id = ?"
        resultado = self.db.obtener_datos(query, (id_producto,))
        return resultado[0] if resultado else None

    def actualizar_dimension_retazo(self, id_producto, nueva_medida, nuevo_largo):
        """
        Transforma un retazo existente a su nueva medida tras un corte,
        en vez de crear una fila nueva. Mantiene el mismo ID/identidad.
        """
        query = "UPDATE inventario SET medida = ?, largo = ? WHERE id = ?"
        self.db.ejecutar_consulta(query, (nueva_medida, nuevo_largo, id_producto))

    def eliminar_producto(self, id_producto):
        """Elimina físicamente una fila (usado cuando un retazo se consume por completo)."""
        query = "DELETE FROM inventario WHERE id = ?"
        self.db.ejecutar_consulta(query, (id_producto,))

    def buscar_retazos_disponibles(self, familia, subfamilia, material, tipo_producto, medida_minima, excluir_id=None):
        """
        Busca retazos existentes (es_retazo=1) del mismo material/familia/tipo
        que tengan una medida suficiente para cubrir lo que se necesita cortar.
        Sirve para avisar antes de sacrificar una pieza nueva innecesariamente.
        """
        query = """
            SELECT id, descripcion, largo, galeria, local, stock
            FROM inventario
            WHERE es_retazo = 1
            AND familia = ? AND subfamilia = ? AND material = ? AND tipo_producto = ?
            AND stock > 0
            AND largo >= ?
        """
        parametros = [familia, subfamilia, material, tipo_producto, medida_minima]

        if excluir_id is not None:
            query += " AND id != ?"
            parametros.append(excluir_id)

        query += " ORDER BY largo ASC"
        return self.db.obtener_datos(query, tuple(parametros))