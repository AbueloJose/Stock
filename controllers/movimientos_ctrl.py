from models.movimientos_model import MovimientosModel
from models.inventario_model import InventarioModel

class MovimientosController:
    def __init__(self):
        self.mov_model = MovimientosModel()
        self.inv_model = InventarioModel()

    def registrar_operacion_basica(self, id_producto, tipo_movimiento, cantidad, notas):
        """Para Ventas, Traslados y Reposiciones."""
        # Si es Venta o Traslado (salida), la cantidad debe ser negativa para el stock
        multiplicador = -1 if tipo_movimiento in ['Venta', 'Traslado Salida'] else 1
        
        self.inv_model.actualizar_stock(id_producto, cantidad * multiplicador)
        self.mov_model.registrar_movimiento(id_producto, tipo_movimiento, cantidad, notas)
        return True

    def procesar_corte(self, id_producto, corte_largo, corte_alto=None):
        """Lógica matemática para reducir barras y planchas y generar retazos."""
        producto = self.inv_model.obtener_por_id(id_producto)
        if not producto:
            return False, "Producto original no encontrado."

        # Desempaquetado basado en el SELECT de inventario_model.py
        # id(0), desc(1), medida(2), fam(3), subfam(4), mat(5), tipo(6), largo(7), alto(8), galeria(9), local(10)...
        tipo_producto = producto[6]
        largo_original = float(producto[7]) if producto[7] else 0

        # Validaciones físicas mínimas
        if corte_largo > largo_original:
            return False, "Error: El corte lineal es mayor al largo original del producto."

        # 1. Descontar una (1) unidad del stock principal
        self.inv_model.actualizar_stock(id_producto, -1)
        self.mov_model.registrar_movimiento(id_producto, "Corte", 1, f"Pieza cortada a {corte_largo}x{corte_alto if corte_alto else 'N/A'}")

        # 2. Generar el Retazo reutilizable
        if tipo_producto == 'barra':
            largo_sobrante = largo_original - corte_largo
            if largo_sobrante > 0:
                medida_retazo = f"{largo_sobrante}mm"
                desc_retazo = f"Retazo de {producto[1]}"
                
                self.inv_model.agregar_producto(
                    descripcion=desc_retazo, medida=medida_retazo, familia=producto[3],
                    subfamilia="Retazos", material=producto[5], tipo_producto='barra',
                    largo=largo_sobrante, alto=None, galeria=producto[9], local=producto[10],
                    stock=1, es_retazo=1, id_padre=id_producto
                )

        elif tipo_producto == 'plancha':
            alto_original = float(producto[8]) if producto[8] else 0
            if corte_alto and corte_alto > alto_original:
                return False, "Error: El corte de alto es mayor al original."
            
            # En planchas, se asume que el retazo es la pieza cortada en sí para el nuevo uso
            # o el sobrante principal. Según tu lógica, la responsabilidad recae en el usuario.
            # Registramos el trozo cortado como nuevo stock reutilizable.
            medida_retazo = f"{corte_largo}x{corte_alto}mm"
            desc_retazo = f"Corte de {producto[1]}"
            
            self.inv_model.agregar_producto(
                descripcion=desc_retazo, medida=medida_retazo, familia=producto[3],
                subfamilia="Retazos", material=producto[5], tipo_producto='plancha',
                largo=corte_largo, alto=corte_alto, galeria=producto[9], local=producto[10],
                stock=1, es_retazo=1, id_padre=id_producto
            )

        return True, "Corte procesado y retazo generado exitosamente."

    def obtener_historial_completo(self):
        return self.mov_model.obtener_historial()