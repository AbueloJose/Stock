from database.db_manager import DBManager

class MovimientosModel:
    def __init__(self):
        self.db = DBManager()

    def registrar_movimiento(self, id_producto, tipo_movimiento, cantidad, detalles):
        """Guarda un registro histórico inmutable de la operación."""
        query = """
            INSERT INTO movimientos (id_producto, tipo_movimiento, cantidad, detalles)
            VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_consulta(query, (id_producto, tipo_movimiento, cantidad, detalles))

    def obtener_historial(self):
        """Cruza datos con el inventario para obtener un reporte completo de movimientos."""
        query = """
            SELECT m.fecha_hora, i.descripcion, m.tipo_movimiento, m.cantidad, m.detalles 
            FROM movimientos m
            JOIN inventario i ON m.id_producto = i.id
            ORDER BY m.fecha_hora DESC
        """
        return self.db.obtener_datos(query)