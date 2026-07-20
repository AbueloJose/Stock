import customtkinter as ctk
from views.inventario_view import InventarioView
from views.movimientos_view import MovimientosView
from views.reportes_view import ReportesView
from views.formulario_view import FormularioView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Inventario")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==========================================
        # MENÚ LATERAL (SIDEBAR)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MR INGENIERIA\nInventario", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_inv = ctk.CTkButton(self.sidebar_frame, text="📦 Inventario", command=self.mostrar_inventario)
        self.btn_inv.grid(row=1, column=0, padx=20, pady=10)

        self.btn_mov = ctk.CTkButton(self.sidebar_frame, text="🔄 Movimientos", command=self.mostrar_movimientos)
        self.btn_mov.grid(row=2, column=0, padx=20, pady=10)

        self.btn_rep = ctk.CTkButton(self.sidebar_frame, text="📊 Reportes", command=self.mostrar_reportes)
        self.btn_rep.grid(row=3, column=0, padx=20, pady=10)

        self.btn_nuevo = ctk.CTkButton(self.sidebar_frame, text="➕ Nuevo Producto", command=self.mostrar_formulario)
        self.btn_nuevo.grid(row=4, column=0, padx=20, pady=10)

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.mostrar_inventario() # Pantalla por defecto al abrir

    def limpiar_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_inventario(self):
        self.limpiar_main_frame()
        vista = InventarioView(self.main_frame)
        vista.pack(fill="both", expand=True)

    def mostrar_movimientos(self):
        self.limpiar_main_frame()
        vista = MovimientosView(self.main_frame)
        vista.pack(fill="both", expand=True)

    def mostrar_reportes(self):
        self.limpiar_main_frame()
        vista = ReportesView(self.main_frame)
        vista.pack(fill="both", expand=True)

    def mostrar_formulario(self):
        self.limpiar_main_frame()
        vista = FormularioView(self.main_frame)
        vista.pack(fill="both", expand=True)