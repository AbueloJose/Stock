import customtkinter as ctk
from tkinter import ttk
from controllers.movimientos_ctrl import MovimientosController

class MovimientosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ctrl = MovimientosController()

        ctk.CTkLabel(self, text="Historial de Movimientos", font=("Arial", 20, "bold")).pack(pady=10)

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b", borderwidth=0)
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Arial', 10, 'bold'))

        cols = ("fecha", "desc", "tipo", "cant", "detalles")
        self.tabla = ttk.Treeview(self.table_frame, columns=cols, show="headings")

        self.tabla.heading("fecha", text="Fecha y Hora")
        self.tabla.heading("desc", text="Producto")
        self.tabla.heading("tipo", text="Tipo Movimiento")
        self.tabla.heading("cant", text="Cantidad")
        self.tabla.heading("detalles", text="Detalles")

        self.tabla.column("fecha", width=150)
        self.tabla.column("desc", width=250)
        self.tabla.column("tipo", width=120)
        self.tabla.column("cant", width=80, anchor="center")
        self.tabla.column("detalles", width=300)

        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.cargar_historial()

    def cargar_historial(self):
        datos = self.ctrl.obtener_historial_completo()
        for fila in datos:
            self.tabla.insert("", "end", values=fila)