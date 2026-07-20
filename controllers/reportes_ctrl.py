from models.inventario_model import InventarioModel
from models.movimientos_model import MovimientosModel

class ReportesController:
    def __init__(self):
        self.inv_model = InventarioModel()
        self.mov_model = MovimientosModel()

    def preparar_datos_excel_inventario(self):
        """Extrae el inventario completo para exportarlo."""
        datos = self.inv_model.obtener_todos()
        # Aquí se podrían formatear columnas antes de enviarlas al Excel
        return datos

    def preparar_datos_pdf_salidas(self, periodo=None):
        """Filtra los movimientos y se queda solo con las salidas (Ventas y Traslados)."""
        historial_completo = self.mov_model.obtener_historial()
        
        salidas = []
        for movimiento in historial_completo:
            # movimiento = (fecha_hora, descripcion, tipo_movimiento, cantidad, detalles)
            tipo = movimiento[2]
            if tipo in ['Venta', 'Traslado Salida']:
                salidas.append(movimiento)
                
        # (Futuro) Aquí se implementaría el filtro por fechas ('periodo' = días, semanas, meses)
        return salidas