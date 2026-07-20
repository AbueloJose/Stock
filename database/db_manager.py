import sqlite3
import os

class DBManager:
    def __init__(self, db_path="assets/db/inventario.db"):
        self.db_path = db_path
        self._asegurar_directorios()
        self._iniciar_base_datos()

    def _asegurar_directorios(self):
        # Crea las carpetas si no existen para evitar errores al guardar
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_conexion(self):
        # Retorna una conexión activa a SQLite
        return sqlite3.connect(self.db_path)

    def _iniciar_base_datos(self):
        # Lee el schema.sql y crea las tablas si la base de datos es nueva
        schema_path = "database/schema.sql"
        if not os.path.exists(self.db_path):
            if os.path.exists(schema_path):
                with self.get_conexion() as conn:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        conn.executescript(f.read())
            else:
                print(f"Error: No se encontró el archivo {schema_path}")

    def ejecutar_consulta(self, query, parametros=()):
        # Para INSERT, UPDATE, DELETE
        with self.get_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parametros)
            conn.commit()
            return cursor

    def obtener_datos(self, query, parametros=()):
        # Para SELECT
        with self.get_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parametros)
            return cursor.fetchall()