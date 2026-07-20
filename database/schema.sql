-- Tabla base de conocimiento (lo que vendrá del Excel)
CREATE TABLE IF NOT EXISTS catalogo_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    familia TEXT,
    subfamilia TEXT,
    material TEXT,
    descripcion_base TEXT
);

-- Tabla núcleo del inventario
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    medida TEXT NOT NULL,
    familia TEXT,
    subfamilia TEXT,
    material TEXT,
    tipo_producto TEXT CHECK(tipo_producto IN ('barra', 'plancha')) NOT NULL,
    largo REAL,
    alto REAL, -- Será NULL si es barra
    galeria TEXT,
    local TEXT,
    stock INTEGER DEFAULT 0,
    es_retazo INTEGER DEFAULT 0, -- 0 es Falso, 1 es Verdadero
    id_producto_padre INTEGER -- Para rastrear de dónde salió el retazo
);

-- Tabla auditable de movimientos
CREATE TABLE IF NOT EXISTS movimientos (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER,
    tipo_movimiento TEXT NOT NULL, -- Corte, Venta, Traslado, Reposicion
    cantidad INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    detalles TEXT, -- Ej. "Corte de plancha a 500x500" o "Traslado a Local 2"
    FOREIGN KEY(id_producto) REFERENCES inventario(id)
);