import customtkinter as ctk
from tkinter import messagebox
from controllers.inventario_ctrl import InventarioController

# --- BASE DE DATOS DE MATERIALES (Oficial MR Ingeniería SAC) ---
DB_MATERIALES = {
    "Termoplásticos": [
        "Nylon (Natural/Lubricado)", "Teflón (PTFE)", "Acetal (POM)", 
        "Polietileno (HDPE/UHMW)", "Polipropileno (PP)", "PVC", 
        "Poliuretano (PU)", "Ferrosel", "Baquelita"
    ],
    "Caucho": [
        "Caucho Natural SBR", "Neopreno CR", "Nitrilo NBR", 
        "Silicona", "Viton", "EPDM", "Caucho Sanitario", "Piso de Caucho"
    ],
    "Aislamiento": [
        "Fibra de Vidrio", "Fibra Cerámica", "Lana de Roca", 
        "Elastomérica", "Aislante Acústico", "Foil de Aluminio", "Cinta de Aluminio"
    ],
    "Empaquetaduras": [
        "Cordón (Grafito/Asbesto/Teflón)", "Plancha de Asbesto", 
        "No Asbesto", "Corcho Enjebado", "Fibra Vegetal", "Kit O-Rings"
    ],
    "Teflón Especialidades": [
        "Tela Teflón", "Tela Diafragma", "Sealon (Teflón Expandido)"
    ],
    "Pegamento": [
        "Pegamento al Frío"
    ]
}

DB_COLORES = {
    "Nylon (Natural/Lubricado)": ["Blanco Natural", "Negro", "Azul", "Moly Gris"],
    "Polietileno (HDPE/UHMW)": ["Blanco", "Negro", "Verde", "Amarillo", "Rojo"],
    "Acetal (POM)": ["Blanco", "Negro"],
    "Ferrosel": ["Marrón"],
    "Baquelita": ["Marrón", "Negro", "Rojo Caoba"],
    "Teflón (PTFE)": ["Blanco Virgen", "Carga Bronce", "Carga Carbón"],
    "Poliuretano (PU)": ["Rojo", "Amarillo"],
    "Fibra Cerámica": ["Blanco"],
    "Cordón (Grafito/Asbesto/Teflón)": ["Blanco (Asbesto)", "Grafitado", "Blanco (Teflón)"],
    "No Asbesto": ["Verde", "Azul", "Rojo"],
    "Silicona": ["Rojo", "Transparente", "Blanco"],
    "Neopreno CR": ["Negro"],
    "DEFAULT": ["Standard", "Blanco", "Negro", "Gris", "Rojo", "Transparente"]
}

def obtener_formatos_validos(material):
    # Reglas basadas en el catálogo web oficial
    if material == "Pegamento al Frío":
        return ["Galón", "Lata 1/4", "Lata 1/8"]
    if "Kit O-Rings" in material:
        return ["Caja / Kit"]
    if "Cinta" in material or "Tela" in material or "Sealon" in material:
        return ["Rollo / Cinta"]
    if material in ["Fibra Cerámica", "Lana de Roca", "Fibra de Vidrio", "Aislante Acústico"]:
        return ["Manta / Rollo", "Plancha / Tablero"]
    if material in ["Corcho Enjebado", "Fibra Vegetal", "No Asbesto", "Plancha de Asbesto"]:
        return ["Plancha / Lámina", "Rollo"]
    if "Cordón" in material:
        return ["Cordón Cuadrado", "Cordón Redondo"]
    if material in DB_MATERIALES["Caucho"]:
        return ["Plancha / Lámina", "Rollo / Tela", "Cordón / O-Ring"]
    
    # Termoplásticos por defecto
    return ["Barra Redonda", "Barra Cuadrada", "Plancha / Lámina", "Bocina (Tubo)"]


class FormularioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ctrl = InventarioController()

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scrollable_frame, text="Nuevo Producto de Materiales MR", font=("Arial", 20, "bold")).pack(pady=(10, 20))

        # ==========================================
        # SECCIÓN 1: SELECCIÓN DE MATERIAL
        # ==========================================
        frame_sel = ctk.CTkFrame(self.scrollable_frame)
        frame_sel.pack(pady=5, padx=20, fill="x")

        # Familia
        ctk.CTkLabel(frame_sel, text="Familia:").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.combo_cat = ctk.CTkComboBox(frame_sel, width=300, values=list(DB_MATERIALES.keys()), command=self.actualizar_materiales)
        self.combo_cat.grid(row=0, column=1, padx=10, pady=10)

        # Material
        ctk.CTkLabel(frame_sel, text="Material:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.combo_mat = ctk.CTkComboBox(frame_sel, width=300, values=["..."], command=self.al_cambiar_material)
        self.combo_mat.grid(row=1, column=1, padx=10, pady=10)

        # Color / Variante
        ctk.CTkLabel(frame_sel, text="Color / Aleación:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.combo_color = ctk.CTkComboBox(frame_sel, width=300, values=["..."], command=self.actualizar_preview)
        self.combo_color.grid(row=2, column=1, padx=10, pady=10)

        # Formato
        ctk.CTkLabel(frame_sel, text="Presentación:").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.combo_formato = ctk.CTkComboBox(frame_sel, width=300, values=["..."], command=self.configurar_medidas)
        self.combo_formato.grid(row=3, column=1, padx=10, pady=10)

        # ==========================================
        # SECCIÓN 2: DIMENSIONES
        # ==========================================
        ctk.CTkLabel(self.scrollable_frame, text="--- Dimensiones y Medidas ---", text_color="gray").pack(pady=(20, 5))
        
        self.frame_medidas = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent", height=80)
        self.frame_medidas.pack(pady=5, padx=20, fill="x")

        self.entry_dim1 = None
        self.entry_dim2 = None
        self.entry_dim3 = None

        # ==========================================
        # SECCIÓN 3: UBICACIÓN Y STOCK
        # ==========================================
        ctk.CTkLabel(self.scrollable_frame, text="--- Ubicación e Ingreso ---", text_color="gray").pack(pady=(20, 5))
        frame_ubi = ctk.CTkFrame(self.scrollable_frame)
        frame_ubi.pack(pady=5, padx=20, fill="x")

        # Galería
        ctk.CTkLabel(frame_ubi, text="Galería:").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.combo_galeria = ctk.CTkComboBox(frame_ubi, width=140, 
                                             values=["Tienda Central", "Galería Udampe", "Galería Aceros"],
                                             command=self.actualizar_sub_locales)
        self.combo_galeria.grid(row=0, column=1, padx=10, pady=10)

        # Local
        ctk.CTkLabel(frame_ubi, text="Local:").grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.combo_local = ctk.CTkComboBox(frame_ubi, width=140, values=["-"])
        self.combo_local.grid(row=0, column=3, padx=10, pady=10)

        # Stock Inicial
        ctk.CTkLabel(frame_ubi, text="Stock Inicial:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_stock = ctk.CTkEntry(frame_ubi, width=140, placeholder_text="Ej: 5")
        self.entry_stock.grid(row=1, column=1, padx=10, pady=10)

        # ==========================================
        # PREVIEW Y BOTÓN
        # ==========================================
        self.lbl_preview_nombre = ctk.CTkLabel(self.scrollable_frame, text="...", font=("Arial", 16, "bold"), text_color="#1f6aa5")
        self.lbl_preview_nombre.pack(pady=(20, 0))
        
        self.lbl_preview_medida = ctk.CTkLabel(self.scrollable_frame, text="...", font=("Arial", 14), text_color="gray")
        self.lbl_preview_medida.pack(pady=(0, 20))

        self.btn_save = ctk.CTkButton(self.scrollable_frame, text="💾 GUARDAR PRODUCTO EN INVENTARIO", command=self.guardar_producto, 
                                      fg_color="#28a745", hover_color="#218838", height=45, width=300, font=("Arial", 14, "bold"))
        self.btn_save.pack(pady=10)

        first_cat = list(DB_MATERIALES.keys())[0]
        self.combo_cat.set(first_cat)
        self.actualizar_materiales(first_cat)

    # --- LÓGICA DE ACTUALIZACIÓN DE UI ---

    def actualizar_materiales(self, categoria):
        mats = DB_MATERIALES.get(categoria, [])
        self.combo_mat.configure(values=mats)
        if mats:
            self.combo_mat.set(mats[0])
            self.al_cambiar_material(mats[0])

    def al_cambiar_material(self, material):
        colores = DB_COLORES.get(material, DB_COLORES["DEFAULT"])
        self.combo_color.configure(values=colores)
        self.combo_color.set(colores[0])
        
        formatos = obtener_formatos_validos(material)
        self.combo_formato.configure(values=formatos)
        self.combo_formato.set(formatos[0])
        
        self.configurar_medidas(formatos[0])

    def configurar_medidas(self, formato):
        for widget in self.frame_medidas.winfo_children():
            widget.destroy()
        self.entry_dim1 = self.entry_dim2 = self.entry_dim3 = None

        if "Plancha" in formato or "Lámina" in formato or "Tablero" in formato:
            self._crear_casilla("Espesor (mm):", 0, "Ej: 10")
            self._crear_casilla("Ancho (cm):", 1, "Ej: 100")
            self._crear_casilla("Largo (cm):", 2, "Ej: 200")

        elif "Barra" in formato:
            lbl = "Diámetro (mm):" if "Redonda" in formato else "Lado (mm):"
            self._crear_casilla(lbl, 0, "Ej: 50")
            ctk.CTkLabel(self.frame_medidas, text="* Largo automático fijado en 100 cm (1 metro) *", text_color="orange").pack(side="left", padx=20)

        elif "Manta" in formato or "Rollo" in formato:
            self._crear_casilla("Espesor (mm):", 0, "Ej: 2")
            self._crear_casilla("Ancho (cm):", 1, "Ej: 120")
            self._crear_casilla("Largo (metros):", 2, "Ej: 10")

        elif "Cordón" in formato:
            self._crear_casilla("Espesor (Pulg o mm):", 0, "Ej: 3/8'' o 10mm")
            self._crear_casilla("Venta / Peso:", 1, "Ej: Kilo")

        elif "Bocina" in formato:
            self._crear_casilla("Ø Ext (mm):", 0, "OD")
            self._crear_casilla("Ø Int (mm):", 1, "ID")
            self._crear_casilla("Largo (cm):", 2, "Ej: 30")
            
        elif formato in ["Galón", "Lata 1/4", "Lata 1/8", "Caja / Kit"]:
             ctk.CTkLabel(self.frame_medidas, text="Este producto no requiere medidas dimensionales.", text_color="gray").pack(side="left", padx=20, pady=20)

        self.actualizar_preview()

    def _crear_casilla(self, texto, posicion, placeholder):
        frame = ctk.CTkFrame(self.frame_medidas, fg_color="transparent")
        frame.pack(side="left", expand=True, padx=5, fill="y")
        ctk.CTkLabel(frame, text=texto, font=("Arial", 12)).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=120, placeholder_text=placeholder)
        entry.pack(pady=2)
        entry.bind("<KeyRelease>", self.actualizar_preview)

        if posicion == 0: self.entry_dim1 = entry
        elif posicion == 1: self.entry_dim2 = entry
        elif posicion == 2: self.entry_dim3 = entry

    def actualizar_sub_locales(self, eleccion):
        if eleccion == "Tienda Central":
            self.combo_local.configure(values=["-"], state="disabled")
            self.combo_local.set("-")
        elif eleccion == "Galería Udampe":
            self.combo_local.configure(values=["Tienda Kevin", "La 11", "Carreta"], state="normal")
            self.combo_local.set("Tienda Kevin")
        elif eleccion == "Galería Aceros":
            self.combo_local.configure(values=["Tienda Nueva", "B9", "A9"], state="normal")
            self.combo_local.set("Tienda Nueva")

    def actualizar_preview(self, event=None):
        mat = self.combo_mat.get()
        col = self.combo_color.get().split(" ")[0] 
        formato = self.combo_formato.get().split(" ")[0] 
        
        d1 = self.entry_dim1.get() if self.entry_dim1 and self.entry_dim1.get() else "?"
        d2 = self.entry_dim2.get() if self.entry_dim2 and self.entry_dim2.get() else "?"
        d3 = self.entry_dim3.get() if self.entry_dim3 and self.entry_dim3.get() else "?"

        if col == "Standard": col = ""
        nombre_desc = f"{self.combo_formato.get()} de {mat} {col}".strip()
        medidas_str = ""

        # Limpiamos las medidas para no repetir el espesor
        if "Plancha" in formato or "Lámina" in formato or "Tablero" in formato:
            medidas_str = f"{d2}cm x {d3}cm"
            
        elif "Barra" in formato:
            medidas_str = "100 cm" # Fijo y limpio
            
        elif "Manta" in formato or "Rollo" in formato:
             medidas_str = f"Ancho {d2}cm x {d3}mts"
             
        elif "Bocina" in formato:
             # Para la bocina, el D1 (Exterior) va al espesor, y aquí dejamos el D2 (Interior) y el Largo
             medidas_str = f"Interior Ø {d2}mm x {d3}cm"
             
        elif "Cordón" in formato:
             medidas_str = f"Presentación: {d2}"
             
        elif formato in ["Galón", "Lata 1/4", "Lata 1/8", "Caja / Kit"]:
             medidas_str = "Estándar"

        self.lbl_preview_nombre.configure(text=nombre_desc.upper())
        self.lbl_preview_medida.configure(text=medidas_str)

    def guardar_producto(self):
        if (self.entry_dim1 and not self.entry_dim1.get()) or not self.entry_stock.get():
            messagebox.showwarning("Atención", "Por favor completa las medidas y el stock.")
            return

        familia = self.combo_cat.get()
        subfamilia = self.combo_mat.get()
        color = self.combo_color.get()
        
        # Clasificamos lógicamente para el inventario
        tipo_prod = "barra" if "Barra" in self.combo_formato.get() else "plancha"
        
        descripcion = self.lbl_preview_nombre.cget("text")
        medida_texto = self.lbl_preview_medida.cget("text")
        
        espesor = self.entry_dim1.get() if self.entry_dim1 else "0"
        
        if tipo_prod == "barra":
            largo_cm = 100
        else:
            try:
                largo_cm = float(self.entry_dim3.get()) if self.entry_dim3 and self.entry_dim3.get().isdigit() else 0
            except ValueError:
                largo_cm = 0

        datos = {
            'descripcion': descripcion,
            'medida': medida_texto,
            'familia': familia,
            'subfamilia': subfamilia,
            'material': color, 
            'tipo_producto': tipo_prod,
            'largo': largo_cm,
            'alto': espesor,
            'galeria': self.combo_galeria.get(),
            'local': self.combo_local.get(),
            'stock': int(self.entry_stock.get() or 0)
        }

        exito, msj = self.ctrl.registrar_nuevo_producto(datos)
        
        if exito:
            messagebox.showinfo("Éxito", msj)
            if self.entry_dim1: self.entry_dim1.delete(0, 'end')
            if self.entry_dim2: self.entry_dim2.delete(0, 'end')
            if self.entry_dim3: self.entry_dim3.delete(0, 'end')
            self.entry_stock.delete(0, 'end')
            self.actualizar_preview()
        else:
            messagebox.showerror("Error", msj)