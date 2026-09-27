import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from utilidades import formatear_fecha
from colores_app import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GestionPresupuestos:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0

        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(self.marco, fg_color=FONDO_SIDEBAR)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        self.pestania_ordenes = self.tabview.add("📋 Cuentas por Cobrar")
        self.pestania_historial = self.tabview.add("📜 Historial de Pagos")
        self.pestania_graficas = self.tabview.add("📊 Estadísticas Financieras")

        self.configurar_pestania_ordenes()
        self.configurar_pestania_historial()
        self.configurar_pestania_graficas()

    def configurar_pestania_ordenes(self):
        barra_herramientas = ctk.CTkFrame(self.pestania_ordenes, fg_color="transparent")
        barra_herramientas.pack(fill="x", pady=5)

        boton_refrescar = ctk.CTkButton(
            barra_herramientas, text="⟳ Actualizar Lista",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.cargar_ordenes
        )
        boton_refrescar.pack(side="left", padx=5)

        etiqueta_instruccion = ctk.CTkLabel(
            barra_herramientas, text="💡 Haz doble clic en una orden para ver detalle",
            text_color=TEXTO_GRIS, font=("Inter", 11)
        )
        etiqueta_instruccion.pack(side="right", padx=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO,
                        fieldbackground=FONDO_TARJETA, rowheight=25)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol_ordenes = ttk.Treeview(
            self.pestania_ordenes,
            columns=("ID", "Cliente", "Vehículo", "Total USD", "Pagado USD", "Saldo USD", "Estado"),
            show="headings"
        )
        columnas = [
            ("ID", 50), ("Cliente", 150), ("Vehículo", 150),
            ("Total USD", 100), ("Pagado USD", 100), ("Saldo USD", 100), ("Estado", 100)
        ]
        for columna, width in columnas:
            self.arbol_ordenes.heading(columna, text=columna)
            self.arbol_ordenes.column(columna, width=width, anchor="center" if "USD" in columna or columna in ["ID", "Estado"] else "w")

        self.arbol_ordenes.tag_configure("pagado", foreground="#2ecc71")
        self.arbol_ordenes.tag_configure("pendiente", foreground="#e74c3c")

        scroll = ttk.Scrollbar(self.pestania_ordenes, orient="vertical", command=self.arbol_ordenes.yview)
        self.arbol_ordenes.configure(yscrollcommand=scroll.set)
        self.arbol_ordenes.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.arbol_ordenes.bind("<Double-Button-1>", self.on_orden_seleccionada)
        self.cargar_ordenes()

    def cargar_ordenes(self):
        for row in self.arbol_ordenes.get_children():
            self.arbol_ordenes.delete(row)

        consulta = """
            SELECT o.id, c.nombre as cliente, CONCAT(v.marca, ' ', v.modelo) as vehiculo,
                   o.total_orden_usd,
                   COALESCE(SUM(p.monto_ref_usd), 0) as pagado,
                   (o.total_orden_usd - COALESCE(SUM(p.monto_ref_usd), 0)) as saldo
            FROM ordenes o
            JOIN vehiculos v ON o.vehiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN pagos p ON o.id = p.orden_id
            GROUP BY o.id, c.nombre, v.marca, v.modelo, o.total_orden_usd
            ORDER BY o.id DESC
        """
        ordenes = self.bd.obtener_todos(consulta)
        for o in ordenes:
            saldo = o['saldo']
            estado = "Saldado" if saldo <= 0.01 else "Pendiente"
            tag = "pagado" if estado == "Saldado" else "pendiente"
            self.arbol_ordenes.insert("", "end", values=(
                o['id'],
                o['cliente'],
                o['vehiculo'],
                f"${o['total_orden_usd']:.2f}",
                f"${o['pagado']:.2f}",
                f"${max(0, saldo):.2f}",
                estado
            ), tags=(tag,))

    def configurar_pestania_historial(self):
        barra_herramientas = ctk.CTkFrame(self.pestania_historial, fg_color="transparent")
        barra_herramientas.pack(fill="x", pady=5)

        boton_refrescar = ctk.CTkButton(
            barra_herramientas, text="⟳ Refrescar Historial",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.cargar_historial
        )
        boton_refrescar.pack(side="left", padx=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO,
                        fieldbackground=FONDO_TARJETA, rowheight=25)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol_historial = ttk.Treeview(
            self.pestania_historial,
            columns=("ID", "Orden", "Cliente", "Vehículo", "Monto Original", "Moneda", "Tasa", "Monto USD", "Fecha", "Método", "Referencia"),
            show="headings"
        )
        columnas = [
            ("ID", 40), ("Orden", 50), ("Cliente", 150), ("Vehículo", 120),
            ("Monto Original", 100), ("Moneda", 60), ("Tasa", 80),
            ("Monto USD", 100), ("Fecha", 120), ("Método", 100), ("Referencia", 100)
        ]
        for columna, width in columnas:
            self.arbol_historial.heading(columna, text=columna)
            self.arbol_historial.column(columna, width=width, anchor="center" if "USD" in columna or columna in ["ID", "Orden", "Monto Original", "Monto USD"] else "w")

        scroll = ttk.Scrollbar(self.pestania_historial, orient="vertical", command=self.arbol_historial.yview)
        self.arbol_historial.configure(yscrollcommand=scroll.set)
        self.arbol_historial.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.cargar_historial()

    def cargar_historial(self):
        for row in self.arbol_historial.get_children():
            self.arbol_historial.delete(row)

        pagos = self.bd.obtener_historial_pagos()
        total_usd = 0
        for p in pagos:
            total_usd += p['monto_ref_usd']
            self.arbol_historial.insert("", "end", values=(
                p['id'],
                p['orden_id'],
                p['cliente'],
                p['vehiculo'],
                f"{p['monto_original']:.2f}",
                p['moneda'],
                f"{p['tasa_cambio']:.2f}",
                f"{p['monto_ref_usd']:.2f}",
                formatear_fecha(p["fecha_pago"]),
                p['metodo_pago'],
                p['referencia'] or ""
            ))

        self.etiqueta_total_historial = ctk.CTkLabel(
            self.pestania_historial,
            text=f"💰 Total recaudado: ${total_usd:.2f} USD",
            font=("Inter", 14, "bold"),
            text_color=COLOR_VERDE
        )
        self.etiqueta_total_historial.pack(anchor="e", padx=10, pady=5)

    def configurar_pestania_graficas(self):
        self.marco_graficas_container = ctk.CTkFrame(self.pestania_graficas, fg_color="transparent")
        self.marco_graficas_container.pack(fill="both", expand=True)
        self.renderizar_graficas()

    def renderizar_graficas(self):
        for widget in self.marco_graficas_container.winfo_children():
            widget.destroy()

        pagos_mensuales = self.bd.obtener_resumen_pagos()
        distribucion = self.bd.obtener_distribucion_monedas()

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

        canvas = FigureCanvasTkAgg(fig, master=self.marco_graficas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        def cerrar_grafica():
            plt.close(fig)

        self.marco_graficas_container.bind("<Destroy>", lambda e: cerrar_grafica())

    def on_orden_seleccionada(self, event):
        seleccion = self.arbol_ordenes.selection()
        if not seleccion:
            return
        elemento = self.arbol_ordenes.item(seleccion)
        id_orden = elemento['values'][0]
        self.abrir_detalle_orden(id_orden)

    def abrir_detalle_orden(self, id_orden):
        try:
            datos = self.bd.obtener_detalle_orden_pagos(id_orden)
            if not datos or datos.get('id') is None:
                messagebox.showerror("Error", f"No se encontró la orden #{id_orden}")
                return

            pagos = self.bd.listar_pagos_por_orden(id_orden)

            ventana = ctk.CTkToplevel(self.padre)
            ventana.title(f"Detalle de Orden #{id_orden}")
            ventana.geometry("700x500")
            ventana.resizable(False, False)

            def al_cerrar():
                ventana.destroy()

            ventana.protocol("WM_DELETE_WINDOW", al_cerrar)

            marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
            marco.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(marco, text=f"Orden #{id_orden}", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(marco, text=f"Cliente: {datos.get('cliente_nombre', 'N/A')}", text_color=TEXTO_GRIS).pack(anchor="w")
            ctk.CTkLabel(marco, text=f"Vehículo: {datos.get('vehiculo', 'N/A')}", text_color=TEXTO_GRIS).pack(anchor="w")
            ctk.CTkLabel(marco, text=f"Descripción: {datos.get('descripcion', '')[:60]}...", text_color=TEXTO_GRIS).pack(anchor="w", pady=(0, 10))

            marco_resumen = ctk.CTkFrame(marco, fg_color=FONDO_SIDEBAR, corner_radius=10)
            marco_resumen.pack(fill="x", pady=10)

            total = datos.get('total_orden_usd', 0) or 0
            pagado = datos.get('total_pagado', 0) or 0
            saldo = max(0, total - pagado)

            ctk.CTkLabel(marco_resumen, text=f"Total: ${total:.2f} USD", text_color=TEXTO_BLANCO).pack(side="left", padx=15, pady=5)
            ctk.CTkLabel(marco_resumen, text=f"Pagado: ${pagado:.2f} USD", text_color=COLOR_VERDE).pack(side="left", padx=15, pady=5)
            ctk.CTkLabel(marco_resumen, text=f"Saldo: ${saldo:.2f} USD", text_color=COLOR_ACENTO if saldo > 0 else COLOR_VERDE, font=("Inter", 12, "bold")).pack(side="left", padx=15, pady=5)

            if pagos:
                ctk.CTkLabel(marco, text="Historial de Pagos:", font=("Inter", 12, "bold"), text_color=TEXTO_BLANCO).pack(anchor="w", padx=10, pady=5)

                arbol_pagos = ttk.Treeview(
                    marco,
                    columns=("Monto", "Moneda", "Tasa", "Monto USD", "Fecha", "Método", "Referencia"),
                    show="headings"
                )
                encabezados = [("Monto", 100), ("Moneda", 80), ("Tasa", 80), ("Monto USD", 100), ("Fecha", 120), ("Método", 100), ("Referencia", 100)]
                for columna, width in encabezados:
                    arbol_pagos.heading(columna, text=columna)
                    arbol_pagos.column(columna, width=width, anchor="center")

                scroll = ttk.Scrollbar(marco, orient="vertical", command=arbol_pagos.yview)
                arbol_pagos.configure(yscrollcommand=scroll.set)
                arbol_pagos.pack(fill="both", expand=True, pady=5)
                scroll.pack(side="right", fill="y")

                for p in pagos:
                    arbol_pagos.insert("", "end", values=(
                        f"{p['monto_original']:.2f}",
                        p['moneda'],
                        f"{p['tasa_cambio']:.2f}",
                        f"{p['monto_ref_usd']:.2f}",
                        formatear_fecha(p["fecha_pago"]),
                        p['metodo_pago'],
                        p['referencia'] or ""
                    ))
            else:
                ctk.CTkLabel(marco, text="No hay pagos registrados para esta orden", text_color=TEXTO_GRIS).pack(pady=10)

            boton_cerrar = ctk.CTkButton(marco, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
            boton_cerrar.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar el detalle:\n{str(e)}")