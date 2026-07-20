import customtkinter as ctk
from tkinter import messagebox
from controllers.movimientos_ctrl import MovimientosController

class ModalCortesView(ctk.CTkToplevel):
    def __init__(self, master, id_producto, desc_producto, callback_actualizar):
        super().__init__(master)
        self.title("Registrar Corte")
        self.geometry("400x300")
        self.ctrl = MovimientosController()
        self.id_producto = id_producto
        self.callback = callback_actualizar

        # Hacer que la ventana sea modal (bloquea la de atrás)
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text=f"Corte para:\n{desc_producto}", font=("Arial", 14, "bold")).pack(pady=15)

        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=10)

        ctk.CTkLabel(self.frame_inputs, text="Largo a cortar (mm):").grid(row=0, column=0, padx=10, pady=10)
        self.ent_largo = ctk.CTkEntry(self.frame_inputs, width=100)
        self.ent_largo.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.frame_inputs, text="Alto a cortar (si es plancha):").grid(row=1, column=0, padx=10, pady=10)
        self.ent_alto = ctk.CTkEntry(self.frame_inputs, width=100)
        self.ent_alto.grid(row=1, column=1, padx=10, pady=10)

        self.btn_confirmar = ctk.CTkButton(self, text="Confirmar Corte", fg_color="#b03a2e", hover_color="#7b241c", command=self.procesar)
        self.btn_confirmar.pack(pady=20)

    def procesar(self):
        try:
            largo = float(self.ent_largo.get())
            alto_val = self.ent_alto.get()
            alto = float(alto_val) if alto_val.strip() != "" else None

            exito, msj = self.ctrl.procesar_corte(self.id_producto, largo, alto)
            if exito:
                messagebox.showinfo("Éxito", msj)
                self.callback() # Actualiza la tabla de atrás
                self.destroy()
            else:
                messagebox.showerror("Error", msj)
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")