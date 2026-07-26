import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
from database import Database

class GestionServicios:
    def __init__(self, parent, rol):
        self.parent = parent
        self.rol = rol
        self.db = Database()
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Toolbar
        self.toolbar = tk.Frame(self.frame, bg="white")
        self.toolbar.pack(fill="x", pady=5)

        self.btn_nuevo = tk.Button(self.toolbar, text="+ Nueva Orden", bg="#e67e22", fg="white",
                                   command=self.abrir_formulario_nueva_orden)
        self.btn_nuevo.pack(side="left", padx=5)

        self.btn_ver_detalle = tk.Button(self.toolbar, text="📋 Ver Detalle", bg="#3498db", fg="white",
                                         command=self.abrir_detalle_orden)
        self.btn_ver_detalle.pack(side="left", padx=5)

        self.btn_cambiar_estado = tk.Button(self.toolbar, text="🔄 Cambiar Estado", bg="#2ecc71", fg="white",
                                            command=self.cambiar_estado)
        self.btn_cambiar_estado.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(self.toolbar, text="🗑 Eliminar", bg="#e74c3c", fg="white",
                                      command=self.eliminar_orden)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_refrescar = tk.Button(self.toolbar, text="⟳ Refrescar", bg="#2c3e50", fg="white",
                                       command=self.cargar_datos)
        self.btn_refrescar.pack(side="left", padx=5)

        # Treeview
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Fecha", "Vehículo", "Cliente", "Descripción", "Estado"),
                                 show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Vehículo", text="Vehículo")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Estado", text="Estado")
        self.tree.column("ID", width=50)
        self.tree.column("Fecha", width=120)
        self.tree.column("Vehículo", width=120)
        self.tree.column("Cliente", width=150)
        self.tree.column("Descripción", width=300)
        self.tree.column("Estado", width=120)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        ordenes = self.db.listar_ordenes_completas()
        if ordenes:
            for o in ordenes:
                fecha = o['fecha'].strftime("%d/%m/%Y %H:%M") if o['fecha'] else ""
                self.tree.insert("", "end", values=(
                    o['id'],
                    fecha,
                    f"{o['marca']} {o['modelo']} ({o['placa']})",
                    o['cliente_nombre'],
                    o['descripcion'][:50] + ("..." if len(o['descripcion']) > 50 else ""),
                    o['estado']
                ))
        self.tree.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione una orden primero")
            return None
        item = self.tree.item(seleccion)
        return item['values'][0]  # ID

    def abrir_formulario_nueva_orden(self):
        """Abre la ventana para crear una nueva orden de servicio"""
        ventana = Toplevel(self.parent)
        ventana.title("Nueva Orden de Servicio")
        ventana.geometry("600x400")
        ventana.resizable(False, False)
        ventana.configure(bg="white")

        # Obtener vehículos para combobox
        vehiculos = self.db.listar_vehiculos_con_cliente()
        if not vehiculos:
            messagebox.showerror("Error", "No hay vehículos registrados. Cree un vehículo primero.", parent=ventana)
            ventana.destroy()
            return

        vehiculos_map = {f"{v['cliente_nombre']} - {v['placa']} ({v['marca']} {v['modelo']})": v['id'] for v in vehiculos}
        nombres_vehiculos = list(vehiculos_map.keys())

        tk.Label(ventana, text="Vehículo *:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        combo_vehiculo = ttk.Combobox(ventana, values=nombres_vehiculos, width=40)
        combo_vehiculo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Descripción de la falla:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = scrolledtext.ScrolledText(ventana, width=40, height=8)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10)

        def guardar():
            vehiculo_seleccionado = combo_vehiculo.get()
            descripcion = txt_descripcion.get("1.0", tk.END).strip()

            if not vehiculo_seleccionado:
                messagebox.showerror("Error", "Seleccione un vehículo", parent=ventana)
                return
            if not descripcion:
                messagebox.showerror("Error", "La descripción es obligatoria", parent=ventana)
                return

            vehiculo_id = vehiculos_map.get(vehiculo_seleccionado)
            if not vehiculo_id:
                messagebox.showerror("Error", "Vehículo no válido", parent=ventana)
                return

            exito, mensaje = self.db.crear_orden(vehiculo_id, descripcion, "Pendiente")
            if exito:
                messagebox.showinfo("Éxito", "Orden creada correctamente", parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = tk.Button(ventana, text="Crear Orden", bg="#27ae60", fg="white", command=guardar)
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=20)

    def abrir_detalle_orden(self):
        """Muestra una ventana con la información completa de la orden seleccionada"""
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return
        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden")
            return

        ventana = Toplevel(self.parent)
        ventana.title(f"Detalle de Orden #{id_orden}")
        ventana.geometry("600x400")
        ventana.configure(bg="white")

        tk.Label(ventana, text=f"ID: {datos['id']}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text=f"Fecha: {datos['fecha']}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text=f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})", bg="white", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text=f"Cliente: {datos['cliente_nombre']}", bg="white", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text=f"Estado: {datos['estado']}", bg="white", font=("Arial", 12, "bold"), fg="#e67e22").pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text="Descripción:", bg="white", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        tk.Label(ventana, text=datos['descripcion'], bg="white", wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)

        btn_cerrar = tk.Button(ventana, text="Cerrar", bg="#e74c3c", fg="white", command=ventana.destroy)
        btn_cerrar.pack(pady=10)

    def cambiar_estado(self):
        """Cambia el estado de la orden seleccionada"""
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        # Obtener el estado actual de la orden
        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden", parent=self.frame)
            return

        estado_actual = datos['estado']
        estados = ['Pendiente', 'Diagnóstico', 'Presupuesto', 'Ejecución', 'Finalizado', 'Entregado']

        ventana = Toplevel(self.parent)
        ventana.title("Cambiar Estado")
        ventana.geometry("300x180")
        ventana.configure(bg="white")

        tk.Label(ventana, text="Estado actual:", bg="white", font=("Arial", 10)).pack(pady=5)
        tk.Label(ventana, text=f"🔹 {estado_actual}", bg="white", font=("Arial", 10, "bold"), fg="#e67e22").pack(pady=5)

        tk.Label(ventana, text="Seleccione nuevo estado:", bg="white").pack(pady=5)
        combo_estado = ttk.Combobox(ventana, values=estados, width=20, state="readonly")
        combo_estado.pack(pady=5)
        combo_estado.set(estado_actual)  # <-- AQUÍ SE CARGA EL ESTADO ACTUAL

        def actualizar():
            nuevo_estado = combo_estado.get()
            if not nuevo_estado:
                messagebox.showerror("Error", "Seleccione un estado", parent=ventana)
                return
            if nuevo_estado == estado_actual:
                messagebox.showinfo("Aviso", "El estado seleccionado es el mismo", parent=ventana)
                ventana.destroy()
                return

            exito, mensaje = self.db.actualizar_estado_orden(id_orden, nuevo_estado)
            if exito:
                messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevo_estado}'", parent=ventana)
                ventana.destroy()
                self.cargar_datos()
                self.tree.update()  # Forzar redibujo inmediato
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = tk.Button(ventana, text="Actualizar", bg="#27ae60", fg="white", command=actualizar)
        btn_guardar.pack(pady=10)
        
    def eliminar_orden(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta orden permanentemente?"):
            exito, mensaje = self.db.eliminar_orden(id_orden)
            if exito:
                messagebox.showinfo("Éxito", "Orden eliminada", parent=self.frame)
                try:
                    self.cargar_datos()
                    self.tree.update()
                    self.tree.selection_remove(self.tree.selection())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la lista: {e}", parent=self.frame)
            else:
                messagebox.showerror("Error", mensaje, parent=self.frame)