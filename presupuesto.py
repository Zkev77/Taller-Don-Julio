import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from colores_app import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GestionPresupuestos:
    def __init__(self, parent, rol, usuario_actual):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.usuario_id = self.db.obtener_id_usuario(usuario_actual) or 0

        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(self.frame, fg_color=FONDO_SIDEBAR)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_ordenes = self.tabview.add("📋 Cuentas por Cobrar")
        self.tab_historial = self.tabview.add("📜 Historial de Pagos")
        self.tab_graficas = self.tabview.add("📊 Estadísticas Financieras")

        self.setup_tab_ordenes()
        self.setup_tab_historial()
        self.setup_tab_graficas()

    def setup_tab_ordenes(self):
        toolbar = ctk.CTkFrame(self.tab_ordenes, fg_color="transparent")
        toolbar.pack(fill="x", pady=5)

        btn_refrescar = ctk.CTkButton(
            toolbar, text="⟳ Actualizar Lista",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.cargar_ordenes
        )
        btn_refrescar.pack(side="left", padx=5)

        lbl_instruccion = ctk.CTkLabel(
            toolbar, text="💡 Haz doble clic en una orden para ver detalle",
            text_color=TEXTO_GRIS, font=("Inter", 11)
        )
        lbl_instruccion.pack(side="right", padx=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO,
                        fieldbackground=FONDO_TARJETA, rowheight=25)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.tree_ordenes = ttk.Treeview(
            self.tab_ordenes,
            columns=("ID", "Cliente", "Vehículo", "Total USD", "Pagado USD", "Saldo USD", "Estado"),
            show="headings"
        )
        columnas = [
            ("ID", 50), ("Cliente", 150), ("Vehículo", 150),
            ("Total USD", 100), ("Pagado USD", 100), ("Saldo USD", 100), ("Estado", 100)
        ]
        for col, width in columnas:
            self.tree_ordenes.heading(col, text=col)
            self.tree_ordenes.column(col, width=width, anchor="center" if "USD" in col or col in ["ID", "Estado"] else "w")

        self.tree_ordenes.tag_configure("pagado", foreground="#2ecc71")
        self.tree_ordenes.tag_configure("pendiente", foreground="#e74c3c")

        scroll = ttk.Scrollbar(self.tab_ordenes, orient="vertical", command=self.tree_ordenes.yview)
        self.tree_ordenes.configure(yscrollcommand=scroll.set)
        self.tree_ordenes.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree_ordenes.bind("<Double-Button-1>", self.on_orden_seleccionada)
        self.cargar_ordenes()

    def cargar_ordenes(self):
        for row in self.tree_ordenes.get_children():
            self.tree_ordenes.delete(row)

        query = """
            SELECT o.id, c.nombre as cliente, CONCAT(v.marca, ' ', v.modelo) as vehiculo,
                   o.total_orden_usd,
                   COALESCE(SUM(p.monto_ref_usd), 0) as pagado,
                   (o.total_orden_usd - COALESCE(SUM(p.monto_ref_usd), 0)) as saldo
            FROM ordenes o
            JOIN vehiculos v ON o.vehiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN pagos p ON o.id = p.orden_id
            GROUP BY o.id
            ORDER BY o.id DESC
        """
        ordenes = self.db.fetch_all(query)
        for o in ordenes:
            saldo = o['saldo']
            estado = "Saldado" if saldo <= 0.01 else "Pendiente"
            tag = "pagado" if estado == "Saldado" else "pendiente"
            self.tree_ordenes.insert("", "end", values=(
                o['id'],
                o['cliente'],
                o['vehiculo'],
                f"${o['total_orden_usd']:.2f}",
                f"${o['pagado']:.2f}",
                f"${max(0, saldo):.2f}",
                estado
            ), tags=(tag,))

    def setup_tab_historial(self):
        toolbar = ctk.CTkFrame(self.tab_historial, fg_color="transparent")
        toolbar.pack(fill="x", pady=5)

        btn_refrescar = ctk.CTkButton(
            toolbar, text="⟳ Refrescar Historial",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.cargar_historial
        )
        btn_refrescar.pack(side="left", padx=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO,
                        fieldbackground=FONDO_TARJETA, rowheight=25)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.tree_historial = ttk.Treeview(
            self.tab_historial,
            columns=("ID", "Orden", "Cliente", "Vehículo", "Monto Original", "Moneda", "Tasa", "Monto USD", "Fecha", "Método", "Referencia"),
            show="headings"
        )
        columnas = [
            ("ID", 40), ("Orden", 50), ("Cliente", 150), ("Vehículo", 120),
            ("Monto Original", 100), ("Moneda", 60), ("Tasa", 80),
            ("Monto USD", 100), ("Fecha", 120), ("Método", 100), ("Referencia", 100)
        ]
        for col, width in columnas:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=width, anchor="center" if "USD" in col or col in ["ID", "Orden", "Monto Original", "Monto USD"] else "w")

        scroll = ttk.Scrollbar(self.tab_historial, orient="vertical", command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scroll.set)
        self.tree_historial.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.cargar_historial()

    def cargar_historial(self):
        for row in self.tree_historial.get_children():
            self.tree_historial.delete(row)

        pagos = self.db.obtener_historial_pagos()
        total_usd = 0
        for p in pagos:
            total_usd += p['monto_ref_usd']
            self.tree_historial.insert("", "end", values=(
                p['id'],
                p['orden_id'],
                p['cliente'],
                p['vehiculo'],
                f"{p['monto_original']:.2f}",
                p['moneda'],
                f"{p['tasa_cambio']:.2f}",
                f"{p['monto_ref_usd']:.2f}",
                p['fecha_pago'].strftime("%d/%m/%Y %H:%M"),
                p['metodo_pago'],
                p['referencia'] or ""
            ))

        self.lbl_total_historial = ctk.CTkLabel(
            self.tab_historial,
            text=f"💰 Total recaudado: ${total_usd:.2f} USD",
            font=("Inter", 14, "bold"),
            text_color=COLOR_VERDE
        )
        self.lbl_total_historial.pack(anchor="e", padx=10, pady=5)

    def setup_tab_graficas(self):
        self.frame_graficas_container = ctk.CTkFrame(self.tab_graficas, fg_color="transparent")
        self.frame_graficas_container.pack(fill="both", expand=True)
        self.renderizar_graficas()

    def renderizar_graficas(self):
        for widget in self.frame_graficas_container.winfo_children():
            widget.destroy()

        pagos_mensuales = self.db.obtener_resumen_pagos()
        distribucion = self.db.obtener_distribucion_monedas()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
        fig.patch.set_facecolor(FONDO_TARJETA)

        ax1.set_facecolor(FONDO_TARJETA)
        if pagos_mensuales:
            meses = [p['mes'] for p in pagos_mensuales]
            totales = [float(p['total_usd']) for p in pagos_mensuales]
            ax1.bar(meses, totales, color=COLOR_ACENTO)
            ax1.set_title("Ingresos por Mes (USD)", color=TEXTO_BLANCO)
            ax1.tick_params(colors=TEXTO_GRIS)
        else:
            ax1.text(0.5, 0.5, "Sin datos de ingresos", ha='center', va='center', color=TEXTO_GRIS)
            ax1.set_title("Ingresos por Mes", color=TEXTO_BLANCO)

        ax2.set_facecolor(FONDO_TARJETA)
        if distribucion:
            monedas = [d['moneda'] for d in distribucion]
            montos = [float(d['total_usd']) for d in distribucion]
            lista_colores = []
            for m in monedas:
                if m == "USD":
                    lista_colores.append(COLOR_ACENTO)
                elif m == "COP":
                    lista_colores.append(COLOR_AZUL)
                else:
                    lista_colores.append(COLOR_VERDE)

            ax2.pie(montos, labels=monedas, autopct='%1.1f%%', colors=lista_colores, textprops={'color': TEXTO_BLANCO})
            ax2.set_title("Cobros por Moneda", color=TEXTO_BLANCO)
        else:
            ax2.text(0.5, 0.5, "Sin datos de monedas", ha='center', va='center', color=TEXTO_GRIS)
            ax2.set_title("Distribución por Moneda", color=TEXTO_BLANCO)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        def on_cerrar():
            plt.close(fig)

        self.frame_graficas_container.bind("<Destroy>", lambda e: on_cerrar())

    def on_orden_seleccionada(self, event):
        seleccion = self.tree_ordenes.selection()
        if not seleccion:
            return
        item = self.tree_ordenes.item(seleccion)
        id_orden = item['values'][0]
        self.abrir_detalle_orden(id_orden)

    def abrir_detalle_orden(self, id_orden):
        try:
            datos = self.db.obtener_detalle_orden_pagos(id_orden)
            if not datos or datos.get('id') is None:
                messagebox.showerror("Error", f"No se encontró la orden #{id_orden}")
                return

            pagos = self.db.listar_pagos_por_orden(id_orden)

            ventana = ctk.CTkToplevel(self.parent)
            ventana.title(f"Detalle de Orden #{id_orden}")
            ventana.geometry("700x500")
            ventana.resizable(False, False)

            def al_cerrar():
                ventana.destroy()

            ventana.protocol("WM_DELETE_WINDOW", al_cerrar)

            frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
            frame.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(frame, text=f"Orden #{id_orden}", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text=f"Cliente: {datos.get('cliente_nombre', 'N/A')}", text_color=TEXTO_GRIS).pack(anchor="w")
            ctk.CTkLabel(frame, text=f"Vehículo: {datos.get('vehiculo', 'N/A')}", text_color=TEXTO_GRIS).pack(anchor="w")
            ctk.CTkLabel(frame, text=f"Descripción: {datos.get('descripcion', '')[:60]}...", text_color=TEXTO_GRIS).pack(anchor="w", pady=(0, 10))

            resumen_frame = ctk.CTkFrame(frame, fg_color=FONDO_SIDEBAR, corner_radius=10)
            resumen_frame.pack(fill="x", pady=10)

            total = datos.get('total_orden_usd', 0) or 0
            pagado = datos.get('total_pagado', 0) or 0
            saldo = max(0, total - pagado)

            ctk.CTkLabel(resumen_frame, text=f"Total: ${total:.2f} USD", text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=5)
            ctk.CTkLabel(resumen_frame, text=f"Pagado: ${pagado:.2f} USD", text_color=COLOR_VERDE).pack(side="left", padx=15, pady=5)
            ctk.CTkLabel(resumen_frame, text=f"Saldo: ${saldo:.2f} USD", text_color=COLOR_ACENTO if saldo > 0 else COLOR_VERDE, font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=5)

            if pagos:
                ctk.CTkLabel(frame, text="Historial de Pagos:", font=("Inter", 12, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", padx=10, pady=5)

                tree_pagos = ttk.Treeview(
                    frame,
                    columns=("Monto", "Moneda", "Tasa", "Monto USD", "Fecha", "Método", "Referencia"),
                    show="headings"
                )
                encabezados = [("Monto", 100), ("Moneda", 80), ("Tasa", 80), ("Monto USD", 100), ("Fecha", 120), ("Método", 100), ("Referencia", 100)]
                for col, width in encabezados:
                    tree_pagos.heading(col, text=col)
                    tree_pagos.column(col, width=width, anchor="center")

                scroll = ttk.Scrollbar(frame, orient="vertical", command=tree_pagos.yview)
                tree_pagos.configure(yscrollcommand=scroll.set)
                tree_pagos.pack(fill="both", expand=True, pady=5)
                scroll.pack(side="right", fill="y")

                for p in pagos:
                    tree_pagos.insert("", "end", values=(
                        f"{p['monto_original']:.2f}",
                        p['moneda'],
                        f"{p['tasa_cambio']:.2f}",
                        f"{p['monto_ref_usd']:.2f}",
                        p['fecha_pago'].strftime("%d/%m/%Y %H:%M"),
                        p['metodo_pago'],
                        p['referencia'] or ""
                    ))
            else:
                ctk.CTkLabel(frame, text="No hay pagos registrados para esta orden", text_color=TEXTO_GRIS).pack(pady=10)

            btn_cerrar = ctk.CTkButton(frame, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
            btn_cerrar.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar el detalle:\n{str(e)}")