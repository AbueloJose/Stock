from models.inventario_model import InventarioModel
from models.catalogo_model import CatalogoModel
from models.movimientos_model import MovimientosModel

class InventarioController:
    def __init__(self):
        self.inv_model = InventarioModel()
        self.cat_model = CatalogoModel()
        self.mov_model = MovimientosModel()

    def obtener_inventario_completo(self):
        return self.inv_model.obtener_todos()

    def buscar_y_filtrar(self, termino, galeria="Todo", local="-"):
        return self.inv_model.buscar_productos(termino, galeria, local)

    def autocompletar_formulario(self, termino):
        return self.cat_model.obtener_sugerencias(termino)

    def registrar_nuevo_producto(self, datos):
        try:
            self.inv_model.agregar_producto(
                descripcion=datos['descripcion'],
                medida=datos['medida'],
                familia=datos['familia'],
                subfamilia=datos['subfamilia'],
                material=datos['material'],
                tipo_producto=datos['tipo_producto'],
                largo=datos.get('largo'),
                alto=datos.get('alto'),
                galeria=datos['galeria'],
                local=datos['local'],
                stock=datos['stock']
            )
            return True, "Producto registrado correctamente."
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"

    def procesar_reposicion(self, id_producto, tipo_movimiento, cantidad, gal_origen, loc_origen, gal_destino, loc_destino):
        try:
            prod_orig = self.inv_model.obtener_por_id(id_producto)
            if not prod_orig: return False, "Producto no encontrado."

            if tipo_movimiento == "interna":
                if prod_orig[9] == gal_origen and prod_orig[10] == loc_origen:
                    if prod_orig[11] < cantidad:
                        return False, f"Stock insuficiente en origen ({prod_orig[11]})."
                    self.inv_model.actualizar_stock(id_producto, -cantidad)

                    self.mov_model.registrar_movimiento(
                        id_producto,
                        "Traslado Salida",
                        cantidad,
                        f"Traslado hacia {gal_destino} ({loc_destino})"
                    )
                else:
                    return False, "Conflicto de ubicación de origen."

            todos = self.inv_model.obtener_todos()
            id_destino_existente = None
            for p in todos:
                if p[1] == prod_orig[1] and p[7] == gal_destino and p[8] == loc_destino:
                    id_destino_existente = p[0]
                    break

            if id_destino_existente:
                self.inv_model.actualizar_stock(id_destino_existente, cantidad)
                id_producto_destino = id_destino_existente
            else:
                id_producto_destino = self.inv_model.agregar_producto(
                    descripcion=prod_orig[1], medida=prod_orig[2], familia=prod_orig[3],
                    subfamilia=prod_orig[4], material=prod_orig[5], tipo_producto=prod_orig[6],
                    largo=prod_orig[7], alto=prod_orig[8], galeria=gal_destino,
                    local=loc_destino, stock=cantidad
                )

            if tipo_movimiento == "interna":
                self.mov_model.registrar_movimiento(
                    id_producto_destino,
                    "Traslado Entrada",
                    cantidad,
                    f"Traslado recibido desde {gal_origen} ({loc_origen})"
                )
            else:
                self.mov_model.registrar_movimiento(
                    id_producto_destino,
                    "Reposición",
                    cantidad,
                    f"Ingreso de mercadería (Proveedor) en {gal_destino} ({loc_destino})"
                )

            return True, "Movimiento registrado exitosamente."
        except Exception as e:
            return False, f"Error de BD: {e}"

    def procesar_salida(self, id_producto, tipo_salida, datos):
        """Maneja las Ventas Directas y los Cortes con generación/transformación de Retazos"""
        try:
            if tipo_salida == "venta":
                prod_orig = self.inv_model.obtener_por_id(id_producto)
                if not prod_orig: return False, "El producto no existe."

                es_retazo_actual = prod_orig[12]
                stock_actual = prod_orig[11]

                self.inv_model.actualizar_stock(id_producto, -datos)

                self.mov_model.registrar_movimiento(
                    id_producto,
                    "Venta",
                    datos,
                    f"Venta directa de {datos} unidades"
                )

                nuevo_stock = stock_actual - datos

                # Si era un retazo único y se vendió por completo, eliminamos la fila
                # para que no quede un "zombie" con stock 0 en el inventario
                if es_retazo_actual == 1 and nuevo_stock <= 0:
                    self.inv_model.eliminar_producto(id_producto)
                    return True, f"Se registraron {datos} unidades vendidas. El retazo se vendió por completo y se eliminó del inventario."

                return True, f"Se registraron {datos} unidades vendidas correctamente."

            elif tipo_salida == "corte":
                prod_orig = self.inv_model.obtener_por_id(id_producto)
                if not prod_orig: return False, "El producto original no existe."

                vendido_cm = datos.get('vendido') or 0
                sobrante_cm = datos['sobrante']
                es_retazo_actual = prod_orig[12]
                largo_original = float(prod_orig[7]) if prod_orig[7] else 0

                # Validación física real: lo vendido + lo sobrante no puede exceder la medida actual
                total_solicitado = vendido_cm + sobrante_cm
                if largo_original and total_solicitado > largo_original:
                    return False, (
                        f"Error: la pieza mide {largo_original} cm.\n"
                        f"Vendido ({vendido_cm} cm) + Sobrante ({sobrante_cm} cm) = {total_solicitado} cm, "
                        f"lo cual EXCEDE la medida real por {total_solicitado - largo_original} cm."
                    )

                if es_retazo_actual == 1:
                    if sobrante_cm > 0:
                        nueva_medida_visual = f"{sobrante_cm} cm"
                        self.inv_model.actualizar_dimension_retazo(id_producto, nueva_medida_visual, sobrante_cm)

                        self.mov_model.registrar_movimiento(
                            id_producto,
                            "Corte",
                            1,
                            f"Retazo recortado ({vendido_cm} cm vendidos) -> queda en {sobrante_cm} cm"
                        )
                        return True, f"Retazo actualizado: ahora mide {sobrante_cm} cm."
                    else:
                        self.inv_model.eliminar_producto(id_producto)
                        self.mov_model.registrar_movimiento(
                            id_producto,
                            "Corte",
                            1,
                            f"Retazo consumido en su totalidad ({vendido_cm} cm vendidos)"
                        )
                        return True, "Retazo consumido por completo. Se eliminó del inventario."

                self.inv_model.actualizar_stock(id_producto, -1)
                self.mov_model.registrar_movimiento(
                    id_producto,
                    "Corte",
                    1,
                    f"Corte: {vendido_cm} cm vendidos / {sobrante_cm} cm de retazo"
                )

                desc_actual = prod_orig[1]
                desc_retazo = f"{desc_actual} (RETAZO)" if "(RETAZO)" not in desc_actual else desc_actual
                nueva_medida_visual = f"{sobrante_cm} cm"

                id_retazo = self.inv_model.agregar_producto(
                    descripcion=desc_retazo,
                    medida=nueva_medida_visual,
                    familia=prod_orig[3],
                    subfamilia=prod_orig[4],
                    material=prod_orig[5],
                    tipo_producto=prod_orig[6],
                    largo=sobrante_cm,
                    alto=prod_orig[8],
                    galeria=prod_orig[9],
                    local=prod_orig[10],
                    stock=1,
                    es_retazo=1,
                    id_padre=id_producto
                )

                self.mov_model.registrar_movimiento(
                    id_retazo,
                    "Ingreso por Corte",
                    1,
                    f"Retazo generado a partir de: {desc_actual}"
                )

                return True, "Corte procesado con éxito. Se generó un retazo en tu inventario."

        except Exception as e:
            return False, f"Error de procesamiento: {e}"
    def verificar_retazos_disponibles(self, id_producto, medida_requerida):
        """
        Antes de cortar una pieza NUEVA, revisa si ya existe un retazo
        que podría cubrir la medida solicitada, para evitar desperdiciar material.
        """
        producto = self.inv_model.obtener_por_id(id_producto)
        if not producto:
            return []

        familia, subfamilia, material, tipo_producto = producto[3], producto[4], producto[5], producto[6]

        return self.inv_model.buscar_retazos_disponibles(
            familia, subfamilia, material, tipo_producto,
            medida_requerida, excluir_id=id_producto
        )