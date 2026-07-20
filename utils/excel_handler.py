import pandas as pd
import os

class ExcelHandler:
    def __init__(self, folder_path="/sistema_inventario/assets/excel/"):
        self.folder_path = folder_path
        # Crea la carpeta automáticamente si no existe
        os.makedirs(self.folder_path, exist_ok=True)

    def exportar_inventario(self, datos, nombre_archivo="inventario_exportado.xlsx"):
        """Toma los datos de la base de datos y genera un Excel."""
        ruta_completa = os.path.join(self.folder_path, nombre_archivo)
        
        # 'datos' es la lista que viene del controlador: (id, desc, medida, fam, subfam, mat, galeria, local, stock)
        columnas = ["ID", "Descripción Técnica", "Medida", "Familia", "Subfamilia", "Material", "Galería", "Local", "Stock"]
        
        # Convertimos la información a una tabla de pandas y la guardamos en Excel
        df = pd.DataFrame(datos, columns=columnas)
        df.to_excel(ruta_completa, index=False)
        
        return ruta_completa

    def importar_catalogo_base(self, ruta_archivo):
        """Lee tu archivo Excel inteligente y extrae la información para el autocompletado."""
        try:
            # Asumimos que tu Excel tiene estas columnas exactas en la cabecera
            df = pd.read_excel(ruta_archivo)
            
            # Extraemos solo las columnas que nos importan para la base de conocimiento
            datos_filtrados = df[["familia", "subfamilia", "material", "descripcion_base"]]
            
            # Convertimos a una lista de tuplas para que SQLite la entienda
            return datos_filtrados.values.tolist()
        except Exception as e:
            return str(e)