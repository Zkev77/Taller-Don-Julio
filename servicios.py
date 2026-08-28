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

        self.btn_registrar_pago = ctk.CTkButton(
            self.toolbar, text="💰 Registrar Pago",
            fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO,
            command=self.abrir_ventana_pago
        )
        self.btn_registrar_pago.pack(side="left", padx=5)

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
            columns=("ID", "Fecha", "Vehículo", "Cliente", "Descripción", "Estado", "Total USD"),
            show="headings"
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Vehículo", text="Vehículo")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Total USD", text="Total USD")
        self.tree.column("ID", width=50)
        self.tree.column("Fecha", width=120)
        self.tree.column("Vehículo", width=120)
        self.tree.column("Cliente", width=150)
        self.tree.column("Descripción", width=300)
        self.tree.column("Estado", width=120)
        self.tree.column("Total USD", width=120, anchor="center")

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
                    o['estado'],
                    f"${o.get('total_orden_usd', 0):.2f}"
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
        ventana.geometry("600x450")
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

        ctk.CTkLabel(frame, text="Total Orden (USD):", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_total = ctk.CTkEntry(frame, width=150)
        entry_total.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        entry_total.insert(0, "0.00")

        def guardar():
            vehiculo_seleccionado = combo_vehiculo.get()
            descripcion = txt_descripcion.get("1.0", ctk.END).strip()
            total_str = entry_total.get().strip()

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

            vehiculo_id = vehiculos_map.get(vehiculo_seleccionado)
            if not vehiculo_id:
                messagebox.showerror("Error", "Vehículo no válido", parent=ventana)
                return

            exito, mensaje, nuevo_id = self.db.crear_orden(vehiculo_id, descripcion, "Ingresado")
            if exito:
                self.db.execute_query("UPDATE ordenes SET total_orden_usd = %s WHERE id = %s", (total_orden, nuevo_id))
                self.db.registrar_log(
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
                self.tree.update_idletasks()
                self.tree.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Crear Orden", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        btn_guardar.grid(row=3, column=0, columnspan=2, pady=20)

    def abrir_ventana_pago(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden")
            return

        finanzas = self.db.obtener_detalle_orden_pagos(id_orden)
        if not finanzas:
            finanzas = {'total_orden_usd': 0, 'total_pagado': 0}

        total = finanzas['total_orden_usd'] or 0
        pagado = finanzas['total_pagado'] or 0
        saldo = max(0, total - pagado)

        if saldo <= 0:
            messagebox.showinfo("Aviso", "Esta orden ya está completamente pagada")
            return

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title(f"Registrar Pago - Orden #{id_orden}")
        ventana.geometry("600x500")
        ventana.resizable(False, False)

        main_frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text=f"Orden #{id_orden}", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(main_frame, text=f"Cliente: {datos['cliente_nombre']}", text_color=TEXTO_GRIS).pack(anchor="w")
        ctk.CTkLabel(main_frame, text=f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})", text_color=TEXTO_GRIS).pack(anchor="w")
        ctk.CTkLabel(main_frame, text=f"Descripción: {datos['descripcion'][:60]}...", text_color=TEXTO_GRIS).pack(anchor="w", pady=(0, 10))

        resumen_frame = ctk.CTkFrame(main_frame, fg_color=FONDO_SIDEBAR, corner_radius=10)
        resumen_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(resumen_frame, text=f"Total: ${total:.2f} USD", text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(resumen_frame, text=f"Pagado: ${pagado:.2f} USD", text_color=COLOR_VERDE).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(resumen_frame, text=f"Saldo: ${saldo:.2f} USD", text_color=COLOR_ACENTO, font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=5)

        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(form_frame, text="Moneda:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        combo_moneda = ctk.CTkComboBox(form_frame, values=["USD", "COP", "BS"], width=120, state="readonly")
        combo_moneda.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        combo_moneda.set("USD")

        ctk.CTkLabel(form_frame, text="Tasa (1 USD =):", text_color=TEXTO_BLANCO).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        entry_tasa = ctk.CTkEntry(form_frame, width=120)
        entry_tasa.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        entry_tasa.insert(0, "1.00")

        ctk.CTkLabel(form_frame, text="Monto:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_monto = ctk.CTkEntry(form_frame, width=150)
        entry_monto.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Método:", text_color=TEXTO_BLANCO).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        combo_metodo = ctk.CTkComboBox(form_frame, values=["Efectivo", "Transferencia", "Pago Movil", "Zelle", "Otro"], width=150, state="readonly")
        combo_metodo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        combo_metodo.set("Efectivo")

        ctk.CTkLabel(form_frame, text="Referencia:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_referencia = ctk.CTkEntry(form_frame, width=350)
        entry_referencia.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        def cambiar_moneda(choice):
            entry_tasa.delete(0, ctk.END)
            if choice == "USD":
                entry_tasa.insert(0, "1.00")
            elif choice == "COP":
                entry_tasa.insert(0, "4000.00")
            elif choice == "BS":
                entry_tasa.insert(0, "45.00")

        combo_moneda.configure(command=cambiar_moneda)

        def registrar_pago():
            try:
                tasa = float(entry_tasa.get().strip())
                monto = float(entry_monto.get().strip())
                if tasa <= 0 or monto <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Tasa y monto deben ser números positivos", parent=ventana)
                return

            moneda = combo_moneda.get()
            monto_ref_usd = monto if moneda == "USD" else (monto / tasa)
            metodo = combo_metodo.get()
            referencia = entry_referencia.get().strip()

            if monto_ref_usd > saldo:
                messagebox.showerror("Error", f"El monto en USD (${monto_ref_usd:.2f}) supera el saldo pendiente (${saldo:.2f})", parent=ventana)
                return

            exito, mensaje, _ = self.db.registrar_pago(
                id_orden, monto, moneda, tasa, monto_ref_usd, metodo, referencia
            )

            if exito:
                messagebox.showinfo("Éxito", "Pago registrado correctamente", parent=ventana)
                ventana.destroy()
                self.cargar_datos()
                self.tree.update_idletasks()
                self.tree.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(main_frame, text="Registrar Pago", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=registrar_pago)
        btn_guardar.pack(pady=15)

        btn_cancelar = ctk.CTkButton(main_frame, text="Cancelar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
        btn_cancelar.pack(pady=5)

    def abrir_detalle_orden(self):
        id_orden = self.obtener_seleccionado()
        if not id_orden:
            return

        datos = self.db.obtener_orden_completa(id_orden)
        if not datos:
            messagebox.showerror("Error", "No se encontró la orden")
            return

        finanzas = self.db.obtener_detalle_orden_pagos(id_orden)
        if not finanzas:
            finanzas = {'total_orden_usd': 0, 'total_pagado': 0}
        pagos = self.db.listar_pagos_por_orden(id_orden)

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title(f"Detalle de Orden #{id_orden}")
        ventana.geometry("900x700")
        ventana.resizable(False, False)

        tabview = ctk.CTkTabview(ventana, fg_color=FONDO_SIDEBAR)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        tab_info = tabview.add("📋 Información")
        tab_pagos = tabview.add("💰 Pagos")

        frame_info = ctk.CTkFrame(tab_info, fg_color=FONDO_TARJETA)
        frame_info.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_info, text=f"ID: {datos['id']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text=f"Fecha: {datos['fecha']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text=f"Vehículo: {datos['marca']} {datos['modelo']} ({datos['placa']})", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text=f"Cliente: {datos['cliente_nombre']}", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text=f"Estado: {datos['estado']}", text_color=COLOR_ACENTO, font=("Inter", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text="Descripción:", text_color=TEXTO_BLANCO, font=("Inter", 12)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(frame_info, text=datos['descripcion'], text_color=TEXTO_GRIS, wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)

        frame_pagos = ctk.CTkFrame(tab_pagos, fg_color=FONDO_TARJETA)
        frame_pagos.pack(fill="both", expand=True, padx=10, pady=10)

        resumen_frame = ctk.CTkFrame(frame_pagos, fg_color=FONDO_SIDEBAR, corner_radius=10)
        resumen_frame.pack(fill="x", pady=5)

        total = finanzas['total_orden_usd'] or 0
        pagado = finanzas['total_pagado'] or 0
        saldo = max(0, total - pagado)

        ctk.CTkLabel(resumen_frame, text=f"Total: ${total:.2f} USD", text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(resumen_frame, text=f"Pagado: ${pagado:.2f} USD", text_color=COLOR_VERDE).pack(side="left", padx=15, pady=5)
        ctk.CTkLabel(resumen_frame, text=f"Saldo: ${saldo:.2f} USD", text_color=COLOR_ACENTO if saldo > 0 else COLOR_VERDE, font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=5)

        tree_pagos = ttk.Treeview(
            frame_pagos,
            columns=("ID", "Monto", "Moneda", "Tasa", "Monto USD", "Fecha", "Método", "Referencia"),
            show="headings"
        )
        encabezados = [("ID", 50), ("Monto", 100), ("Moneda", 80), ("Tasa", 80), ("Monto USD", 100), ("Fecha", 120), ("Método", 100), ("Referencia", 100)]
        for col, width in encabezados:
            tree_pagos.heading(col, text=col)
            tree_pagos.column(col, width=width, anchor="center")

        scroll = ttk.Scrollbar(frame_pagos, orient="vertical", command=tree_pagos.yview)
        tree_pagos.configure(yscrollcommand=scroll.set)
        tree_pagos.pack(side="left", fill="both", expand=True, pady=5)
        scroll.pack(side="right", fill="y")

        for p in pagos:
            tree_pagos.insert("", "end", values=(
                p['id'],
                f"{p['monto_original']:.2f}",
                p['moneda'],
                f"{p['tasa_cambio']:.2f}",
                f"{p['monto_ref_usd']:.2f}",
                p['fecha_pago'].strftime("%d/%m/%Y %H:%M"),
                p['metodo_pago'],
                p['referencia'] or ""
            ))

        if self.rol in ['admin', 'secretaria', 'auditor'] and saldo > 0:
            form_frame = ctk.CTkFrame(frame_pagos, fg_color=FONDO_SIDEBAR, corner_radius=10)
            form_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(form_frame, text="Registrar Pago", font=("Inter", 12, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", padx=10, pady=5)

            grid = ctk.CTkFrame(form_frame, fg_color="transparent")
            grid.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(grid, text="Moneda:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=5, pady=5)
            combo_moneda = ctk.CTkComboBox(grid, values=["USD", "COP", "BS"], width=90, state="readonly")
            combo_moneda.grid(row=0, column=1, padx=5, pady=5)
            combo_moneda.set("USD")

            ctk.CTkLabel(grid, text="Tasa (1 USD):", text_color=TEXTO_BLANCO).grid(row=0, column=2, padx=5, pady=5)
            entry_tasa = ctk.CTkEntry(grid, width=90)
            entry_tasa.grid(row=0, column=3, padx=5, pady=5)
            entry_tasa.insert(0, "1.00")

            ctk.CTkLabel(grid, text="Monto:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=5, pady=5)
            entry_monto = ctk.CTkEntry(grid, width=120)
            entry_monto.grid(row=1, column=1, padx=5, pady=5)

            ctk.CTkLabel(grid, text="Método:", text_color=TEXTO_BLANCO).grid(row=1, column=2, padx=5, pady=5)
            combo_metodo = ctk.CTkComboBox(grid, values=["Efectivo", "Transferencia", "Pago Movil", "Zelle", "Otro"], width=120, state="readonly")
            combo_metodo.grid(row=1, column=3, padx=5, pady=5)
            combo_metodo.set("Efectivo")

            ctk.CTkLabel(grid, text="Referencia:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=5, pady=5)
            entry_referencia = ctk.CTkEntry(grid, width=300)
            entry_referencia.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

            def cambiar_moneda(choice):
                entry_tasa.delete(0, ctk.END)
                if choice == "USD":
                    entry_tasa.insert(0, "1.00")
                elif choice == "COP":
                    entry_tasa.insert(0, "4000.00")
                elif choice == "BS":
                    entry_tasa.insert(0, "45.00")

            combo_moneda.configure(command=cambiar_moneda)

            def registrar_pago_detalle():
                try:
                    tasa = float(entry_tasa.get().strip())
                    monto = float(entry_monto.get().strip())
                    if tasa <= 0 or monto <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Tasa y monto deben ser números válidos", parent=ventana)
                    return

                moneda = combo_moneda.get()
                monto_ref_usd = monto if moneda == "USD" else (monto / tasa)
                metodo = combo_metodo.get()
                referencia = entry_referencia.get().strip()

                if monto_ref_usd > saldo:
                    messagebox.showerror("Error", f"El monto en USD (${monto_ref_usd:.2f}) supera el saldo pendiente (${saldo:.2f})", parent=ventana)
                    return

                exito, mensaje, _ = self.db.registrar_pago(
                    id_orden, monto, moneda, tasa, monto_ref_usd, metodo, referencia
                )

                if exito:
                    messagebox.showinfo("Éxito", "Pago registrado correctamente", parent=ventana)
                    ventana.destroy()
                    self.cargar_datos()
                    self.abrir_detalle_orden()
                else:
                    messagebox.showerror("Error", mensaje, parent=ventana)

            btn_guardar = ctk.CTkButton(form_frame, text="Registrar Pago", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=registrar_pago_detalle)
            btn_guardar.pack(pady=10)

        elif saldo <= 0:
            ctk.CTkLabel(frame_pagos, text="✅ Esta orden está completamente pagada", text_color=COLOR_VERDE, font=("Inter", 12, "bold")).pack(pady=10)

        btn_cerrar = ctk.CTkButton(frame_pagos, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
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