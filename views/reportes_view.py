import customtkinter as ctk
from tkinter import messagebox
from controllers.reportes_ctrl import ReportesController
from utils.excel_handler import ExcelHandler
from utils.pdf_handler import PDFHandler
import os

class ReportesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ctrl = ReportesController()
        self.excel_h = ExcelHandler()
        self.pdf_h = PDFHandler()

        ctk.CTkLabel(self, text="Exportación e Importación de Datos", font=("Arial", 20, "bold")).pack(pady=20)

        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=20)

        # Botón Exportar Excel
        self.btn_excel = ctk.CTkButton(self.frame_btns, text="📗 Exportar Inventario a Excel", width=250, height=50, fg_color="#1E8449", hover_color="#145A32", command=self.exportar_excel)
        self.btn_excel.grid(row=0, column=0, padx=20, pady=20)

        # Botón Exportar PDF
        self.btn_pdf = ctk.CTkButton(self.frame_btns, text="📕 Generar PDF de Salidas", width=250, height=50, fg_color="#CB4335", hover_color="#922B21", command=self.exportar_pdf)
        self.btn_pdf.grid(row=0, column=1, padx=20, pady=20)

    def exportar_excel(self):
        try:
            datos = self.ctrl.preparar_datos_excel_inventario()
            ruta = self.excel_h.exportar_inventario(datos)
            # Abrir la carpeta automáticamente en Windows
            os.startfile(os.path.dirname(ruta))
            messagebox.showinfo("Éxito", f"Excel generado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al exportar: {e}")

    def exportar_pdf(self):
        try:
            datos = self.ctrl.preparar_datos_pdf_salidas()
            ruta = self.pdf_h.generar_reporte_salidas(datos)
            os.startfile(os.path.dirname(ruta))
            messagebox.showinfo("Éxito", f"PDF generado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al exportar: {e}")