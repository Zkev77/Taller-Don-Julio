import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from colores_app import *

class GestionServicios:
    def __init__(self, parent, rol, usuario_actual):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.usuario_id = self.db.obtener_id_usuario(usuario_actual) or 0

        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = ctk.CTkFrame(self.frame, fg_color=FONDO_TARJETA)
        self.toolbar.pack(fill="x", pady=5)

        self.btn_nuevo = ctk.CTkButton(
            self.toolbar, text="+ Nueva Orden",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_nueva_orden
        )
        self.btn_nuevo.pack(side="left", padx=5)

        self.btn_ver_detalle = ctk.CTkButton(
            self.toolbar, text="📋 Ver Detalle",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.abrir_detalle_orden
        )
        self.btn_ver_detalle.pack(side="left", padx=5)

        self.btn_cambiar_estado = ctk.CTkButton(
            self.toolbar, text="🔄 Cambiar Estado",
            fg_color=COLOR_AMARILLO, text_color=TEXTO_BLANCO,
            command=self.cambiar_estado
        )
        self.btn_cambiar_estado.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(
            self.toolbar, text="🗑 Eliminar",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.eliminar_orden
        )
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_refrescar = ctk.CTkButton(
            self.toolbar, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.btn_refrescar.pack(side="left", padx=5)

        if self.rol == 'auditor':
            self.btn_nuevo.configure(state="disabled")
            self.btn_cambiar_estado.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.btn_eliminar.configure(state="disabled")
        elif self.rol in ['admin', 'secretaria']:
            pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Fecha", "Vehículo", "Cliente", "Descripción", "Estado"),
            show="headings"
        )
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
        return item['values'][0]

    def abrir_formulario_nueva_orden(self):
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nueva Orden de Servicio")
        ventana.geometry("600x400")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        vehiculos = self.db.listar_vehiculos_con_cliente()
        if not vehiculos:
            messagebox.showerror("Error", "No hay vehículos registrados. Cree un vehículo primero.", parent=ventana)
            ventana.destroy()
            return

        vehiculos_map = {f"{v['cliente_nombre']} - {v['placa']} ({v['marca']} {v['modelo']})": v['id'] for v in vehiculos}
        nombres_vehiculos = list(vehiculos_map.keys())

        ctk.CTkLabel(frame, text="Vehículo *:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        combo_vehiculo = ctk.CTkComboBox(frame, values=nombres_vehiculos, width=350, state="readonly")
        combo_vehiculo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Descripción de la falla:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = ctk.CTkTextbox(frame, width=350, height=120)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        def guardar():
            vehiculo_seleccionado = combo_vehiculo.get()
            descripcion = txt_descripcion.get("1.0", ctk.END).strip()

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

            exito, mensaje, nuevo_id = self.db.crear_orden(vehiculo_id, descripcion, "Ingresado")
            if exito:
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="ordenes",
                    registro_id=nuevo_id,
                    accion="INSERT",
                    descripcion=f"Nueva orden: {descripcion[:50]}..."
                )
                messagebox.showinfo("Éxito", "Orden creada correctamente")
                ventana.destroy()
                self.cargar_datos()
                self.tree.update_idletasks()
                self.tree.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Crear Orden", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        btn_guardar.grid(row=2, column=0, columnspan=2, pady=20)

    def abrir_detalle_orden(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return
        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden")
            return

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title(f"Detalle de Orden #{id_orden}")
        ventana.geometry("600x400")

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"ID: {datos['id']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text=f"Fecha: {datos['fecha']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text=f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text=f"Cliente: {datos['cliente_nombre']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text=f"Estado: {datos['estado']}", text_color=COLOR_ACENTO, font=("Inter", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Descripción:", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame, text=datos['descripcion'], text_color=TEXTO_GRIS, wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)

        btn_cerrar = ctk.CTkButton(frame, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
        btn_cerrar.pack(pady=10)

    def cambiar_estado(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden", parent=self.frame)
            return

        estado_actual = datos['estado']
        estados = ['Ingresado', 'Revisión', 'Trabajando', 'Completado', 'Entregado']

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Cambiar Estado")
        ventana.geometry("300x250")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Estado actual:", text_color=TEXTO_BLANCO, font=("Inter", 10)).pack(pady=5)
        ctk.CTkLabel(frame, text=f"🔹 {estado_actual}", text_color=COLOR_ACENTO, font=("Inter", 10, "bold")).pack(pady=5)

        ctk.CTkLabel(frame, text="Seleccione nuevo estado:", text_color=TEXTO_BLANCO).pack(pady=5)
        combo_estado = ctk.CTkComboBox(frame, values=estados, width=200, state="readonly")
        combo_estado.pack(pady=5)
        combo_estado.set(estado_actual)

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
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="ordenes",
                    registro_id=id_orden,
                    accion="UPDATE",
                    descripcion=f"Estado cambiado de '{estado_actual}' a '{nuevo_estado}'"
                )
                messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevo_estado}'")
                ventana.destroy()
                self.cargar_datos()
                self.tree.update_idletasks()
                self.tree.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        combo_estado.bind("<Key-Return>", lambda e: actualizar())

        btn_guardar = ctk.CTkButton(
            frame,
            text="Guardar",
            fg_color=COLOR_VERDE,
            text_color=TEXTO_BLANCO,
            command=actualizar
        )
        btn_guardar.pack(pady=10)

    def eliminar_orden(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta orden permanentemente?"):
            exito, mensaje = self.db.eliminar_orden(id_orden)
            if exito:
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="ordenes",
                    registro_id=id_orden,
                    accion="DELETE",
                    descripcion=f"Eliminada orden ID {id_orden}"
                )
                messagebox.showinfo("Éxito", "Orden eliminada", parent=self.frame)
                self.cargar_datos()
                self.tree.update_idletasks()
                self.tree.update()