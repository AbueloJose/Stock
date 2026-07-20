import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.inventario_ctrl import InventarioController

class InventarioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ctrl = InventarioController()
        
        # ==========================================
        # TOP FRAME (BÚSQUEDA Y FILTROS)
        # ==========================================
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", pady=(0, 10))
        
        self.entry_buscar = ctk.CTkEntry(self.top_frame, placeholder_text="Ej: HDPE 10mm...", width=250)
        self.entry_buscar.pack(side="left", padx=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", self.actualizar_busqueda_en_vivo)
        
        self.btn_buscar = ctk.CTkButton(self.top_frame, text="🔍 Buscar", width=100, command=self.cargar_datos)
        self.btn_buscar.pack(side="left")

        self.var_sub_local = ctk.StringVar(value="-")
        self.dropdown_sub = ctk.CTkOptionMenu(
            self.top_frame, variable=self.var_sub_local, values=["-"], state="disabled",
            width=140, command=self.al_cambiar_sub_local
        )
        self.dropdown_sub.pack(side="right", padx=(10, 0))

        self.var_local = ctk.StringVar(value="Todo")
        self.dropdown_main = ctk.CTkOptionMenu(
            self.top_frame, variable=self.var_local,
            values=["Todo", "Tienda Central", "Galería Udampe", "Galería Aceros"],
            command=self.actualizar_sub_locales, width=160
        )
        self.dropdown_main.pack(side="right")

        # ==========================================
        # TABLA DE INVENTARIO
        # ==========================================
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Arial', 10, 'bold'))
        
        cols = ("id", "desc", "espesor", "medida", "familia", "mat", "color", "gal", "loc", "stock")
        self.tabla = ttk.Treeview(self.table_frame, columns=cols, show="headings")
        
        encabezados = ["ID", "Descripción", "Espesor", "Medida", "Familia", "Material", "Color", "Galería", "Local", "Stock"]
        anchos = [30, 220, 70, 120, 100, 100, 80, 100, 100, 60]
        
        for col, enc, ancho in zip(cols, encabezados, anchos):
            self.tabla.heading(col, text=enc)
            if col in ("id", "espesor", "stock", "medida"):
                self.tabla.column(col, width=ancho, anchor="center")
            else:
                self.tabla.column(col, width=ancho, anchor="w")
            
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabla.bind("<Double-1>", self.abrir_panel_movimiento)
        self.cargar_datos()

    def actualizar_busqueda_en_vivo(self, event): self.cargar_datos()

    def actualizar_sub_locales(self, eleccion):
        if eleccion == "Todo" or eleccion == "Tienda Central":
            self.dropdown_sub.configure(values=["-"], state="disabled")
            self.var_sub_local.set("-")
        elif eleccion == "Galería Udampe":
            self.dropdown_sub.configure(values=["Todos", "Tienda Kevin", "La 11", "Carreta"], state="normal")
            self.var_sub_local.set("Todos")
        elif eleccion == "Galería Aceros":
            self.dropdown_sub.configure(values=["Todos", "Tienda Nueva", "B9", "A9"], state="normal")
            self.var_sub_local.set("Todos")
        self.cargar_datos() 

    def al_cambiar_sub_local(self, eleccion): self.cargar_datos()

    def cargar_datos(self):
        self.tabla.delete(*self.tabla.get_children())
        datos = self.ctrl.buscar_y_filtrar(self.entry_buscar.get(), self.var_local.get(), self.var_sub_local.get())
        for fila in datos:
            fila_lista = list(fila)
            espesor_original = str(fila_lista[2]).strip()
            if espesor_original in ("0", "0.0", "?", "", "None"):
                fila_lista[2] = "-"
            else:
                try:
                    valor_num = float(espesor_original)
                    fila_lista[2] = f"{int(valor_num)} mm" if valor_num.is_integer() else f"{valor_num} mm"
                except ValueError:
                    fila_lista[2] = espesor_original
            self.tabla.insert("", "end", values=fila_lista)

    # ==========================================
    # PANEL SUPERPUESTO DE NAVEGACIÓN
    # ==========================================
    def abrir_panel_movimiento(self, event):
        seleccion = self.tabla.selection()
        if not seleccion: return
            
        valores = self.tabla.item(seleccion[0])['values']

        self.panel_movimiento = ctk.CTkFrame(self, fg_color="#1e1e1e") 
        self.panel_movimiento.place(relx=0, rely=0, relwidth=1, relheight=1)

        ctk.CTkButton(self.panel_movimiento, text="⬅ Volver al Inventario", command=self.cerrar_panel_movimiento,
                      fg_color="transparent", border_width=1, hover_color="#333333").pack(anchor="nw", padx=20, pady=20)

        self.centro = ctk.CTkFrame(self.panel_movimiento, fg_color="transparent")
        self.centro.pack(expand=True, fill="both", padx=50, pady=10)

        ctk.CTkLabel(self.centro, text="Gestión de Movimiento", font=("Arial", 28, "bold")).pack(pady=(0, 20))
        ctk.CTkLabel(self.centro, text=f"{valores[1]}", font=("Arial", 20), text_color="#3a7ebf", wraplength=600).pack(pady=5)
        ctk.CTkLabel(self.centro, text=f"Stock Actual en {valores[7]} ({valores[8]}): {valores[9]}", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)

        self.frame_btns = ctk.CTkFrame(self.centro, fg_color="transparent")
        self.frame_btns.pack(pady=10)

        ctk.CTkButton(self.frame_btns, text="🟢 ENTRADA / REPONER", fg_color="#28a745", hover_color="#218838", 
                      font=("Arial", 16, "bold"), height=60, width=220, command=lambda: self.preparar_formulario("reponer", valores)).pack(side="left", padx=20)

        ctk.CTkButton(self.frame_btns, text="🔴 SALIDA / VENTA", fg_color="#dc3545", hover_color="#c82333", 
                      font=("Arial", 16, "bold"), height=60, width=220, command=lambda: self.preparar_formulario("venta", valores)).pack(side="right", padx=20)

    def cerrar_panel_movimiento(self):
        if hasattr(self, "panel_movimiento"):
            self.panel_movimiento.destroy()
            self.cargar_datos()

    def preparar_formulario(self, tipo, valores):
        self.frame_btns.pack_forget() # Ocultar botones principales
        if tipo == "reponer":
            self.dibujar_formulario_reponer(valores)
        else:
            self.dibujar_formulario_venta(valores)

    # ==========================================
    # FORMULARIO DE REPOSICIÓN DUAL
    # ==========================================
    def dibujar_formulario_reponer(self, valores):
        self.tipo_repo_var = ctk.StringVar(value="externa")
        frame_radios = ctk.CTkFrame(self.centro, fg_color="transparent")
        frame_radios.pack(pady=10)
        ctk.CTkRadioButton(frame_radios, text="Externa (Proveedor)", variable=self.tipo_repo_var, value="externa", command=lambda: self.actualizar_campos_repo(valores), font=("Arial", 14)).pack(side="left", padx=20)
        ctk.CTkRadioButton(frame_radios, text="Interna (Traslado)", variable=self.tipo_repo_var, value="interna", command=lambda: self.actualizar_campos_repo(valores), font=("Arial", 14)).pack(side="left", padx=20)

        self.frame_campos_r = ctk.CTkFrame(self.centro, fg_color="#2b2b2b", corner_radius=10)
        self.frame_campos_r.pack(pady=20, padx=20, fill="x")
        self.actualizar_campos_repo(valores)

    def actualizar_campos_repo(self, valores):
        for widget in self.frame_campos_r.winfo_children(): widget.destroy()
        tipo = self.tipo_repo_var.get()
        self.var_cant_repo = ctk.StringVar()
        self.var_gal_destino = ctk.StringVar(value=valores[7])
        self.var_loc_destino = ctk.StringVar(value=valores[8])

        if tipo == "externa":
            ctk.CTkLabel(self.frame_campos_r, text="Cantidad a Ingresar:", font=("Arial", 14)).grid(row=0, column=0, padx=15, pady=15, sticky="e")
            ctk.CTkEntry(self.frame_campos_r, textvariable=self.var_cant_repo, width=100, justify="center").grid(row=0, column=1, padx=15, pady=15, sticky="w")
            ctk.CTkLabel(self.frame_campos_r, text="Galería Destino:").grid(row=1, column=0, padx=15, pady=15, sticky="e")
            combo_gal = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_gal_destino, values=["Tienda Central", "Galería Udampe", "Galería Aceros"], command=lambda e: self.actualizar_combo_local(e, combo_loc))
            combo_gal.grid(row=1, column=1, padx=15, pady=15, sticky="w")
            ctk.CTkLabel(self.frame_campos_r, text="Local Destino:").grid(row=1, column=2, padx=15, pady=15, sticky="e")
            combo_loc = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_loc_destino, values=["-"])
            combo_loc.grid(row=1, column=3, padx=15, pady=15, sticky="w")
            self.actualizar_combo_local(valores[7], combo_loc)
            combo_loc.set(valores[8])

        elif tipo == "interna":
            self.var_gal_origen = ctk.StringVar(value=valores[7])
            self.var_loc_origen = ctk.StringVar(value=valores[8])
            ctk.CTkLabel(self.frame_campos_r, text="De (Origen):", font=("Arial", 14, "bold"), text_color="#dc3545").grid(row=0, column=0, padx=15, pady=10, sticky="e")
            combo_gal_o = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_gal_origen, values=["Tienda Central", "Galería Udampe", "Galería Aceros"], command=lambda e: self.actualizar_combo_local(e, combo_loc_o))
            combo_gal_o.grid(row=0, column=1, padx=10, pady=10)
            combo_loc_o = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_loc_origen, values=["-"])
            combo_loc_o.grid(row=0, column=2, padx=10, pady=10)
            self.actualizar_combo_local(valores[7], combo_loc_o)
            combo_loc_o.set(valores[8])

            ctk.CTkLabel(self.frame_campos_r, text="Hacia (Destino):", font=("Arial", 14, "bold"), text_color="#28a745").grid(row=1, column=0, padx=15, pady=10, sticky="e")
            combo_gal_d = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_gal_destino, values=["Tienda Central", "Galería Udampe", "Galería Aceros"], command=lambda e: self.actualizar_combo_local(e, combo_loc_d))
            combo_gal_d.grid(row=1, column=1, padx=10, pady=10)
            combo_loc_d = ctk.CTkComboBox(self.frame_campos_r, variable=self.var_loc_destino, values=["-"])
            combo_loc_d.grid(row=1, column=2, padx=10, pady=10)
            self.actualizar_combo_local(valores[7], combo_loc_d)

            ctk.CTkLabel(self.frame_campos_r, text="Cantidad a Trasladar:", font=("Arial", 14)).grid(row=2, column=0, padx=15, pady=20, sticky="e")
            ctk.CTkEntry(self.frame_campos_r, textvariable=self.var_cant_repo, width=100, justify="center").grid(row=2, column=1, padx=10, pady=20, sticky="w")

        ctk.CTkButton(self.frame_campos_r, text="💾 CONFIRMAR MOVIMIENTO", font=("Arial", 14, "bold"), height=45, fg_color="#1E8449", hover_color="#145A32", command=lambda: self.procesar_guardado_repo(valores)).grid(row=3, column=0, columnspan=4, pady=20)

    # ==========================================
    # FORMULARIO DE VENTAS Y CORTES DUAL
    # ==========================================
    def dibujar_formulario_venta(self, valores):
        # NUEVO: Mostramos el espesor y la medida actual de la pieza seleccionada,
        # para que quede claro cuál barra/plancha es antes de cortarla.
        espesor_actual = valores[2]
        medida_actual = valores[3]
        ctk.CTkLabel(
            self.centro,
            text=f"📏 Espesor: {espesor_actual}   |   Medida actual: {medida_actual}",
            font=("Arial", 15, "bold"),
            text_color="#f0ad4e"
        ).pack(pady=(0, 15))

        self.tipo_salida_var = ctk.StringVar(value="venta")
        frame_radios = ctk.CTkFrame(self.centro, fg_color="transparent")
        frame_radios.pack(pady=10)

        ctk.CTkRadioButton(frame_radios, text="Venta Completa", variable=self.tipo_salida_var, value="venta", command=self.actualizar_campos_venta, font=("Arial", 14)).pack(side="left", padx=20)
        ctk.CTkRadioButton(frame_radios, text="Corte a Medida (Generar Retazo)", variable=self.tipo_salida_var, value="corte", command=self.actualizar_campos_venta, font=("Arial", 14)).pack(side="left", padx=20)

        self.frame_campos_v = ctk.CTkFrame(self.centro, fg_color="#2b2b2b", corner_radius=10)
        self.frame_campos_v.pack(pady=20, padx=20, fill="x")
        
        self.valores_activos = valores
        self.actualizar_campos_venta()

    def actualizar_campos_venta(self):
        for widget in self.frame_campos_v.winfo_children(): widget.destroy()
        tipo = self.tipo_salida_var.get()
        
        if tipo == "venta":
            self.var_cant_venta = ctk.StringVar()
            ctk.CTkLabel(self.frame_campos_v, text="Unidades Enteras a Vender:", font=("Arial", 14)).grid(row=0, column=0, padx=15, pady=25, sticky="e")
            ctk.CTkEntry(self.frame_campos_v, textvariable=self.var_cant_venta, width=100, justify="center").grid(row=0, column=1, padx=15, pady=25, sticky="w")

        elif tipo == "corte":
            self.var_corte_vendido = ctk.StringVar()
            self.var_corte_sobrante = ctk.StringVar()
            
            ctk.CTkLabel(self.frame_campos_v, text="Medida que se Lleva el Cliente (cm):", font=("Arial", 14), text_color="#3a7ebf").grid(row=0, column=0, padx=15, pady=20, sticky="e")
            ctk.CTkEntry(self.frame_campos_v, textvariable=self.var_corte_vendido, width=100, justify="center").grid(row=0, column=1, padx=15, pady=20, sticky="w")
            
            ctk.CTkLabel(self.frame_campos_v, text="Medida Sobrante / Retazo (cm):", font=("Arial", 14), text_color="#dc3545").grid(row=1, column=0, padx=15, pady=10, sticky="e")
            ctk.CTkEntry(self.frame_campos_v, textvariable=self.var_corte_sobrante, width=100, justify="center").grid(row=1, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkButton(self.frame_campos_v, text="💾 CONFIRMAR SALIDA", font=("Arial", 14, "bold"), height=45, fg_color="#dc3545", hover_color="#c82333", command=self.procesar_guardado_venta).grid(row=2, column=0, columnspan=2, pady=25)

    def actualizar_combo_local(self, eleccion, combo_destino):
        if eleccion == "Tienda Central":
            combo_destino.configure(values=["-"], state="disabled")
            combo_destino.set("-")
        elif eleccion == "Galería Udampe":
            combo_destino.configure(values=["Tienda Kevin", "La 11", "Carreta"], state="normal")
            combo_destino.set("Tienda Kevin")
        elif eleccion == "Galería Aceros":
            combo_destino.configure(values=["Tienda Nueva", "B9", "A9"], state="normal")
            combo_destino.set("Tienda Nueva")

    def procesar_guardado_repo(self, valores):
        tipo = self.tipo_repo_var.get()
        cant = self.var_cant_repo.get()

        if not cant.isdigit() or int(cant) <= 0:
            messagebox.showwarning("Atención", "Ingrese una cantidad válida mayor a 0.")
            return

        gal_dest = self.var_gal_destino.get()
        loc_dest = self.var_loc_destino.get()

        if tipo == "externa":
            if messagebox.askyesno("Confirmar Ingreso", f"¿Confirmas el INGRESO de {cant} unidades a {gal_dest} ({loc_dest})?"):
                exito, msj = self.ctrl.procesar_reposicion(valores[0], "externa", int(cant), None, None, gal_dest, loc_dest)
                self.mostrar_resultado(exito, msj)
        else:
            gal_orig = self.var_gal_origen.get()
            loc_orig = self.var_loc_origen.get()
            if gal_orig == gal_dest and loc_orig == loc_dest:
                messagebox.showerror("Error", "El origen y el destino no pueden ser iguales.")
                return
            if messagebox.askyesno("Confirmar Traslado", f"¿Confirmas el TRASLADO de {cant} unidades\nDe: {gal_orig}\nA: {gal_dest}?"):
                exito, msj = self.ctrl.procesar_reposicion(valores[0], "interna", int(cant), gal_orig, loc_orig, gal_dest, loc_dest)
                self.mostrar_resultado(exito, msj)

    def procesar_guardado_venta(self):
        valores = self.valores_activos
        tipo = self.tipo_salida_var.get()
        stock_actual = int(valores[9])

        if tipo == "venta":
            cant = self.var_cant_venta.get()
            if not cant.isdigit() or int(cant) <= 0:
                messagebox.showwarning("Atención", "Ingrese una cantidad válida mayor a 0.")
                return
            if int(cant) > stock_actual:
                messagebox.showerror("Error", "Stock insuficiente para esta venta.")
                return

            if messagebox.askyesno("Confirmar Venta", f"¿Confirmas la VENTA de {cant} unidades?"):
                exito, msj = self.ctrl.procesar_salida(valores[0], "venta", int(cant))
                self.mostrar_resultado(exito, msj)

        elif tipo == "corte":
            vendido = self.var_corte_vendido.get()
            sobrante = self.var_corte_sobrante.get()

            if not vendido.replace('.','',1).isdigit() or not sobrante.replace('.','',1).isdigit():
                messagebox.showwarning("Atención", "Ingrese medidas numéricas válidas para el corte.")
                return

            if stock_actual < 1:
                messagebox.showerror("Error", "No tienes stock de esta pieza para realizar el corte.")
                return

            # NUEVO: Verificar si ya existe un retazo que serviría para esta medida
            retazos_disponibles = self.ctrl.verificar_retazos_disponibles(valores[0], float(vendido))
            if retazos_disponibles:
                lineas = "\n".join([
                    f"• {r[2]} cm en {r[3]} ({r[4]}) — Stock: {r[5]}"
                    for r in retazos_disponibles
                ])
                continuar = messagebox.askyesno(
                    "⚠️ Ya existe un retazo similar",
                    f"Encontramos retazo(s) que podrían cubrir esta medida ({vendido} cm):\n\n"
                    f"{lineas}\n\n"
                    f"¿Deseas continuar cortando una pieza NUEVA de todas formas?\n"
                    f"(Se recomienda usar el retazo existente para evitar desperdiciar material)"
                )
                if not continuar:
                    return

            msg = f"¿Confirmas el corte a medida?\n\n- Se descontará 1 pieza original de tu inventario.\n- Se creará y guardará un RETAZO de {sobrante} cm en tu stock."
            if messagebox.askyesno("Confirmar Corte", msg):
                datos_corte = {'vendido': float(vendido), 'sobrante': float(sobrante)}
                exito, msj = self.ctrl.procesar_salida(valores[0], "corte", datos_corte)
                self.mostrar_resultado(exito, msj)

    def mostrar_resultado(self, exito, msj):
        if exito:
            messagebox.showinfo("Éxito", msj)
            self.cerrar_panel_movimiento()
        else:
            messagebox.showerror("Error", msj)