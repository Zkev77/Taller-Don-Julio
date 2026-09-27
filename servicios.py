import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from utilidades import formatear_fecha, registrar_validador
from colores_app import *

class GestionServicios:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0

        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        self.barra_herramientas = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_herramientas.pack(fill="x", pady=5)

        self.boton_nuevo = ctk.CTkButton(
            self.barra_herramientas, text="+ Nueva Orden",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_nueva_orden
        )
        self.boton_nuevo.pack(side="left", padx=5)

        self.boton_ver_detalle = ctk.CTkButton(
            self.barra_herramientas, text="📋 Ver Detalle",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.abrir_detalle_orden
        )
        self.boton_ver_detalle.pack(side="left", padx=5)

        self.boton_registrar_pago = ctk.CTkButton(
            self.barra_herramientas, text="💰 Registrar Pago",
            fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO,
            command=self.abrir_ventana_pago
        )
        self.boton_registrar_pago.pack(side="left", padx=5)

        self.boton_cambiar_estado = ctk.CTkButton(
            self.barra_herramientas, text="🔄 Cambiar Estado",
            fg_color=COLOR_AMARILLO, text_color=TEXTO_BLANCO,
            command=self.cambiar_estado
        )
        self.boton_cambiar_estado.pack(side="left", padx=5)

        self.boton_eliminar = ctk.CTkButton(
            self.barra_herramientas, text="🗑 Eliminar",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.eliminar_orden
        )
        self.boton_eliminar.pack(side="left", padx=5)

        self.boton_refrescar = ctk.CTkButton(
            self.barra_herramientas, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.boton_refrescar.pack(side="left", padx=5)

        if self.rol == 'auditor':
            self.boton_nuevo.configure(state="disabled")
            self.boton_registrar_pago.configure(state="disabled")
            self.boton_cambiar_estado.configure(state="disabled")
            self.boton_eliminar.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.boton_eliminar.configure(state="disabled")
        elif self.rol in ['admin', 'secretaria']:
            pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol = ttk.Treeview(
            self.marco,
            columns=("ID", "Fecha", "Vehículo", "Cliente", "Descripción", "Estado", "Total USD"),
            show="headings"
        )
        self.arbol.heading("ID", text="ID")
        self.arbol.heading("Fecha", text="Fecha")
        self.arbol.heading("Vehículo", text="Vehículo")
        self.arbol.heading("Cliente", text="Cliente")
        self.arbol.heading("Descripción", text="Descripción")
        self.arbol.heading("Estado", text="Estado")
        self.arbol.heading("Total USD", text="Total USD")
        self.arbol.column("ID", width=50)
        self.arbol.column("Fecha", width=120)
        self.arbol.column("Vehículo", width=120)
        self.arbol.column("Cliente", width=150)
        self.arbol.column("Descripción", width=300)
        self.arbol.column("Estado", width=120)
        self.arbol.column("Total USD", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(self.marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.arbol.get_children():
            self.arbol.delete(row)
        ordenes = self.bd.listar_ordenes_completas()
        if ordenes:
            for o in ordenes:
                fecha = formatear_fecha(o['fecha'])
                self.arbol.insert("", "end", values=(
                    o['id'],
                    fecha,
                    f"{o['marca']} {o['modelo']} ({o['placa']})",
                    o['cliente_nombre'],
                    o['descripcion'][:50] + ("..." if len(o['descripcion']) > 50 else ""),
                    o['estado'],
                    f"${o.get('total_orden_usd', 0):.2f}"
                ))
        self.arbol.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.arbol.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione una orden primero")
            return None
        elemento = self.arbol.item(seleccion)
        return elemento['values'][0]

    def abrir_formulario_nueva_orden(self):
        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Nueva Orden de Servicio")
        ventana.geometry("600x450")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        vehiculos = self.bd.listar_vehiculos_con_cliente()
        if not vehiculos:
            messagebox.showerror("Error", "No hay vehículos registrados. Cree un vehículo primero.", parent=ventana)
            ventana.destroy()
            return

        mapa_vehiculos = {f"{v['cliente_nombre']} - {v['placa']} ({v['marca']} {v['modelo']})": v['id'] for v in vehiculos}
        nombres_vehiculos = list(mapa_vehiculos.keys())

        ctk.CTkLabel(marco, text="Vehículo *:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        lista_vehiculo = ctk.CTkComboBox(marco, values=nombres_vehiculos, width=350, state="readonly")
        lista_vehiculo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Descripción de la falla:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = ctk.CTkTextbox(marco, width=350, height=120)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        validar_total = registrar_validador(ventana, 10)

        ctk.CTkLabel(marco, text="Total Orden (USD):", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        campo_total = ctk.CTkEntry(marco, width=150, validate="key", validatecommand=(validar_total, '%S', '%P'))
        campo_total.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        campo_total.insert(0, "0.00")

        def guardar():
            vehiculo_seleccionado = lista_vehiculo.get()
            descripcion = txt_descripcion.get("1.0", ctk.END).strip()
            total_str = campo_total.get().strip()

            if not vehiculo_seleccionado:
                messagebox.showerror("Error", "Seleccione un vehículo", parent=ventana)
                return
            if not descripcion:
                messagebox.showerror("Error", "La descripción es obligatoria", parent=ventana)
                return

            try:
                total_orden = float(total_str) if total_str else 0.0
                if total_orden < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese un total válido (número positivo)", parent=ventana)
                return

            vehiculo_id = mapa_vehiculos.get(vehiculo_seleccionado)
            if not vehiculo_id:
                messagebox.showerror("Error", "Vehículo no válido", parent=ventana)
                return

            try:
                exito, mensaje, nuevo_id = self.bd.crear_orden(vehiculo_id, descripcion, "Ingresado", total_orden)
                if exito:
                    self.bd.registrar_log(
                        usuario_id=self.usuario_id,
                        usuario_nombre=self.usuario_actual,
                        tabla="ordenes",
                        registro_id=nuevo_id,
                        accion="INSERT",
                        descripcion=f"Nueva orden: {descripcion[:50]}... (Total: ${total_orden:.2f} USD)"
                    )
                    messagebox.showinfo("Éxito", "Orden creada correctamente", parent=ventana)
                    ventana.destroy()
                    self.cargar_datos()
                    self.arbol.update_idletasks()
                    self.arbol.update()
                else:
                    messagebox.showerror("Error", mensaje, parent=ventana)
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado al guardar la orden: {e}", parent=ventana)

        boton_guardar = ctk.CTkButton(marco, text="Crear Orden", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        boton_guardar.grid(row=3, column=0, columnspan=2, pady=20)

    def abrir_ventana_pago(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.bd.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden")
            return

        finanzas = self.bd.obtener_detalle_orden_pagos(id_orden)
        if not finanzas:
            finanzas = {'total_orden_usd': 0, 'total_pagado': 0}

        total = finanzas['total_orden_usd'] or 0
        pagado = finanzas['total_pagado'] or 0
        saldo = max(0, total - pagado)

        if saldo <= 0:
            messagebox.showinfo("Aviso", "Esta orden ya está completamente pagada", parent=self.padre)
            return

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title(f"Registrar Pago - Orden #{id_orden}")
        ventana.geometry("600x500")
        ventana.resizable(False, False)

        marco_principal = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(marco_principal, text=f"Orden #{id_orden}", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(marco_principal, text=f"Cliente: {datos['cliente_nombre']}", text_color=TEXTO_GRIS).pack(anchor="w")
        ctk.CTkLabel(marco_principal, text=f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})", text_color=TEXTO_GRIS).pack(anchor="w")
        ctk.CTkLabel(marco_principal, text=f"Descripción: {datos['descripcion'][:60]}...", text_color=TEXTO_GRIS).pack(anchor="w", pady=(0, 10))

        marco_resumen = ctk.CTkFrame(marco_principal, fg_color=FONDO_SIDEBAR, corner_radius=10)
        marco_resumen.pack(fill="x", pady=10)

        ctk.CTkLabel(marco_resumen, text=f"Total: ${total:.2f} USD", text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(marco_resumen, text=f"Pagado: ${pagado:.2f} USD", text_color=COLOR_VERDE).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(marco_resumen, text=f"Saldo: ${saldo:.2f} USD", text_color=COLOR_ACENTO, font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=5)

        marco_formulario = ctk.CTkFrame(marco_principal, fg_color="transparent")
        marco_formulario.pack(fill="x", pady=10)

        ctk.CTkLabel(marco_formulario, text="Moneda:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        lista_moneda = ctk.CTkComboBox(marco_formulario, values=["USD", "COP", "BS"], width=120, state="readonly")
        lista_moneda.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        lista_moneda.set("USD")

        validar_tasa = registrar_validador(ventana, 12)
        validar_monto = registrar_validador(ventana, 12)

        ctk.CTkLabel(marco_formulario, text="Tasa (1 USD =):", text_color=TEXTO_BLANCO).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        campo_tasa = ctk.CTkEntry(marco_formulario, width=120, validate="key", validatecommand=(validar_tasa, '%S', '%P'))
        campo_tasa.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        campo_tasa.insert(0, "1.00")

        ctk.CTkLabel(marco_formulario, text="Monto:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        campo_monto = ctk.CTkEntry(marco_formulario, width=150, validate="key", validatecommand=(validar_monto, '%S', '%P'))
        campo_monto.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(marco_formulario, text="Método:", text_color=TEXTO_BLANCO).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        lista_metodo = ctk.CTkComboBox(marco_formulario, values=["Efectivo", "Transferencia", "Pago Movil", "Zelle", "Otro"], width=150, state="readonly")
        lista_metodo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        lista_metodo.set("Efectivo")

        ctk.CTkLabel(marco_formulario, text="Referencia:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        campo_referencia = ctk.CTkEntry(marco_formulario, width=350)
        campo_referencia.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        def cambiar_moneda(opcion):
            campo_tasa.delete(0, ctk.END)
            if opcion == "USD":
                campo_tasa.insert(0, "1.00")
            elif opcion == "COP":
                campo_tasa.insert(0, "4000.00")
            elif opcion == "BS":
                campo_tasa.insert(0, "45.00")

        lista_moneda.configure(command=cambiar_moneda)

        def registrar_pago():
            try:
                tasa = float(campo_tasa.get().strip())
                monto = float(campo_monto.get().strip())
                if tasa <= 0 or monto <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Tasa y monto deben ser números positivos", parent=ventana)
                return

            moneda = lista_moneda.get()
            monto_ref_usd = monto if moneda == "USD" else (monto / tasa)
            metodo = lista_metodo.get()
            referencia = campo_referencia.get().strip()

            if monto_ref_usd > saldo:
                messagebox.showerror("Error", f"El monto en USD (${monto_ref_usd:.2f}) supera el saldo pendiente (${saldo:.2f})", parent=ventana)
                return

            exito, mensaje, _ = self.bd.registrar_pago(
                id_orden, monto, moneda, tasa, monto_ref_usd, metodo, referencia
            )

            if exito:
                messagebox.showinfo("Éxito", "Pago registrado correctamente", parent=ventana)
                ventana.destroy()
                self.cargar_datos()
                self.arbol.update_idletasks()
                self.arbol.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        boton_guardar = ctk.CTkButton(marco_principal, text="Registrar Pago", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=registrar_pago)
        boton_guardar.pack(pady=15)

        boton_cancelar = ctk.CTkButton(marco_principal, text="Cancelar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
        boton_cancelar.pack(pady=5)

    def abrir_detalle_orden(self):
        """Vista de solo lectura con los datos de la orden."""
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.bd.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden", parent=self.padre)
            return

        finanzas = self.bd.obtener_detalle_orden_pagos(id_orden) or {}
        total = finanzas.get('total_orden_usd') or 0
        pagado = finanzas.get('total_pagado') or 0
        saldo = max(0, total - pagado)

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title(f"Detalle de Orden #{id_orden}")
        ventana.geometry("540x520")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(marco, text="Datos de la orden", text_color=TEXTO_BLANCO,
                     font=("Inter", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        filas = [
            f"ID: {datos['id']}",
            f"Fecha: {datos['fecha']}",
            f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})",
            f"Cliente: {datos['cliente_nombre']}",
        ]
        for fila in filas:
            ctk.CTkLabel(marco, text=fila, text_color=TEXTO_BLANCO,
                         font=("Inter", 12)).pack(anchor="w", padx=10, pady=4)

        ctk.CTkLabel(marco, text=f"Estado: {datos['estado']}", text_color=COLOR_ACENTO,
                     font=("Inter", 12, "bold")).pack(anchor="w", padx=10, pady=4)
        ctk.CTkLabel(marco, text="Descripción:", text_color=TEXTO_BLANCO,
                     font=("Inter", 12)).pack(anchor="w", padx=10, pady=4)
        ctk.CTkLabel(marco, text=datos['descripcion'], text_color=TEXTO_GRIS,
                     wraplength=470, justify="left").pack(anchor="w", padx=10, pady=4)

        marco_resumen = ctk.CTkFrame(marco, fg_color=FONDO_SIDEBAR, corner_radius=10)
        marco_resumen.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(marco_resumen, text=f"Total: ${total:.2f} USD",
                     text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=8)
        ctk.CTkLabel(marco_resumen, text=f"Pagado: ${pagado:.2f} USD",
                     text_color=COLOR_VERDE).pack(side="left", padx=15, pady=8)
        ctk.CTkLabel(marco_resumen, text=f"Saldo: ${saldo:.2f} USD",
                     text_color=COLOR_ACENTO if saldo > 0 else COLOR_VERDE,
                     font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=8)

        ctk.CTkButton(marco, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
                      command=ventana.destroy).pack(pady=10)

    def cambiar_estado(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.bd.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden", parent=self.marco)
            return

        estado_actual = datos['estado']
        estados = ['Ingresado', 'Revisión', 'Trabajando', 'Completado', 'Entregado']

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Cambiar Estado")
        ventana.geometry("300x250")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(marco, text="Estado actual:", text_color=TEXTO_BLANCO, font=("Inter", 10)).pack(pady=5)
        ctk.CTkLabel(marco, text=f"🔹 {estado_actual}", text_color=COLOR_ACENTO, font=("Inter", 10, "bold")).pack(pady=5)

        ctk.CTkLabel(marco, text="Seleccione nuevo estado:", text_color=TEXTO_BLANCO).pack(pady=5)
        lista_estado = ctk.CTkComboBox(marco, values=estados, width=200, state="readonly")
        lista_estado.pack(pady=5)
        lista_estado.set(estado_actual)

        def actualizar():
            nuevo_estado = lista_estado.get()
            if not nuevo_estado:
                messagebox.showerror("Error", "Seleccione un estado", parent=ventana)
                return
            if nuevo_estado == estado_actual:
                messagebox.showinfo("Aviso", "El estado seleccionado es el mismo", parent=ventana)
                ventana.destroy()
                return

            exito, mensaje = self.bd.actualizar_estado_orden(id_orden, nuevo_estado)
            if exito:
                self.bd.registrar_log(
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
                self.arbol.update_idletasks()
                self.arbol.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        lista_estado.bind("<Key-Return>", lambda e: actualizar())

        boton_guardar = ctk.CTkButton(
            marco,
            text="Guardar",
            fg_color=COLOR_VERDE,
            text_color=TEXTO_BLANCO,
            command=actualizar
        )
        boton_guardar.pack(pady=10)

    def eliminar_orden(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        # Los pagos se borran en cascada con la orden, asi que se impide perder ese registro.
        finanzas = self.bd.obtener_detalle_orden_pagos(id_orden) or {}
        pagado = finanzas.get('total_pagado') or 0
        if pagado > 0:
            messagebox.showwarning(
                "No se puede eliminar",
                f"Esta orden tiene ${float(pagado):,.2f} USD registrados en pagos.\n\n"
                "Si se eliminara, ese dinero se perdería del registro.\n"
                "Las órdenes con pagos asociados no se pueden eliminar.",
                parent=self.marco
            )
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar esta orden permanentemente?", parent=self.marco):
            return

        exito, mensaje = self.bd.eliminar_orden(id_orden)
        if exito:
            self.bd.registrar_log(
                usuario_id=self.usuario_id,
                usuario_nombre=self.usuario_actual,
                tabla="ordenes",
                registro_id=id_orden,
                accion="DELETE",
                descripcion=f"Eliminada orden ID {id_orden}"
            )
            messagebox.showinfo("Éxito", "Orden eliminada", parent=self.marco)
            self.cargar_datos()
            self.arbol.update_idletasks()
            self.arbol.update()