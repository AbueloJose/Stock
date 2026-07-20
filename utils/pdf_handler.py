from fpdf import FPDF
import os
from datetime import datetime

class PDFHandler:
    def __init__(self, folder_path="/sistema_inventario/assets/reportes"):
        self.folder_path = folder_path
        os.makedirs(self.folder_path, exist_ok=True)

    def generar_reporte_salidas(self, datos_salidas):
        """Crea un PDF limpio y profesional con el historial de salidas."""
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración del Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Reporte de Salidas de Inventario", ln=True, align='C')
        
        # Configuración de Fecha
        pdf.set_font("Arial", '', 10)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf.cell(0, 10, f"Generado el: {fecha_actual}", ln=True, align='C')
        pdf.ln(10) # Salto de línea

        # Encabezados de la Tabla
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(35, 10, "Fecha", border=1)
        pdf.cell(65, 10, "Producto", border=1)
        pdf.cell(30, 10, "Movimiento", border=1)
        pdf.cell(20, 10, "Cant.", border=1, align='C')
        pdf.cell(40, 10, "Detalles", border=1)
        pdf.ln()

        # Filas de Datos
        pdf.set_font("Arial", '', 9)
        for fila in datos_salidas:
            # fila = (fecha_hora, descripcion, tipo_movimiento, cantidad, detalles)
            fecha_corta = str(fila[0])[:16] # Cortar los segundos para que quepa bien
            desc_corta = str(fila[1])[:32] # Truncar descripciones muy largas
            detalles_cortos = str(fila[4])[:20] if fila[4] else ""
            
            # abs(fila[3]) convierte la cantidad a positivo para el reporte
            cantidad_positiva = str(abs(fila[3]))

            pdf.cell(35, 10, fecha_corta, border=1)
            pdf.cell(65, 10, desc_corta, border=1)
            pdf.cell(30, 10, str(fila[2]), border=1)
            pdf.cell(20, 10, cantidad_positiva, border=1, align='C')
            pdf.cell(40, 10, detalles_cortos, border=1)
            pdf.ln()

        # Generar archivo con nombre dinámico
        nombre_archivo = f"Reporte_Salidas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_completa = os.path.join(self.folder_path, nombre_archivo)
        
        pdf.output(ruta_completa)
        return ruta_completa