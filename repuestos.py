import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from utilidades import formatear_fecha
from colores_app import *

BAJO_STOCK = 5


class GestionRepuestos:
    def __init__(self, parent, rol, usuario_actual):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.usuario_id = self.db.obtener_id_usuario(usuario_actual) or 0
        self.puede_editar = rol in ['admin', 'secretaria']
        self.repuestos = []

        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = ctk.CTkFrame(self.frame, fg_color=FONDO_TARJETA)
        self.toolbar.pack(fill="x", pady=5)

        self.btn_agregar = ctk.CTkButton(
            self.toolbar, text="+ Agregar Repuesto",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_agregar
        )
        self.btn_agregar.pack(side="left", padx=5)

        self.btn_editar = ctk.CTkButton(
            self.toolbar, text="✏ Editar",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_editar
        )
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(
            self.toolbar, text="🗑 Eliminar",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.eliminar_repuesto
        )
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_reponer = ctk.CTkButton(
            self.toolbar, text="📦 Reponer Stock",
            fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO,
            command=self.reponer_stock
        )
        self.btn_reponer.pack(side="left", padx=5)

        self.btn_refrescar = ctk.CTkButton(
            self.toolbar, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.btn_refrescar.pack(side="left", padx=5)

        self.btn_pdf = ctk.CTkButton(
            self.toolbar, text="📄 Exportar PDF",
            fg_color=COLOR_MORADO, text_color=TEXTO_BLANCO,
            command=self.exportar_pdf
        )
        self.btn_pdf.pack(side="left", padx=5)

        self.btn_historial = ctk.CTkButton(
            self.toolbar, text="🕓 Historial",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.ver_historial
        )
        self.btn_historial.pack(side="left", padx=5)

        if self.rol == 'auditor':
            self.btn_agregar.configure(state="disabled")
            self.btn_editar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.btn_reponer.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.toolbar.pack_forget()
            ctk.CTkLabel(
                self.frame,
                text="⛔ Acceso denegado para mecánicos",
                font=("Inter", 12),
                text_color=TEXTO_GRIS
            ).pack(pady=20)
            return

        self.barra_busqueda = ctk.CTkFrame(self.frame, fg_color=FONDO_TARJETA)
        self.barra_busqueda.pack(fill="x", pady=5)

        ctk.CTkLabel(self.barra_busqueda, text="🔍 Buscar:", text_color=TEXTO_BLANCO).pack(side="left", padx=(5, 5))
        self.var_buscar = ctk.StringVar()
        self.entry_buscar = ctk.CTkEntry(
            self.barra_busqueda, textvariable=self.var_buscar,
            width=300, placeholder_text="Nombre o proveedor"
        )
        self.entry_buscar.pack(side="left", padx=5)
        self.var_buscar.trace_add("write", self._aplicar_filtro)

        self.lbl_alerta = ctk.CTkLabel(
            self.barra_busqueda, text="",
            font=("Inter", 12, "bold"), text_color=COLOR_ACENTO
        )
        self.lbl_alerta.pack(side="right", padx=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Nombre", "Descripción", "Precio", "Stock", "Proveedor"),
            show="headings"
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Precio", text="Precio USD")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Proveedor", text="Proveedor")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=150)
        self.tree.column("Descripción", width=250)
        self.tree.column("Precio", width=100)
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Proveedor", width=150)
        self.tree.tag_configure("bajo", foreground=COLOR_ACENTO)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        self.repuestos = self.db.listar_repuestos() or []
        self._aplicar_filtro()

    def _aplicar_filtro(self, *args):
        texto = self.var_buscar.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        bajos = 0
        for r in self.repuestos:
            nombre = (r['nombre'] or '').lower()
            proveedor = (r['proveedor'] or '').lower()
            if texto and texto not in nombre and texto not in proveedor:
                continue
            stock = r['stock'] or 0
            bajo = stock < BAJO_STOCK
            if bajo:
                bajos += 1
            descripcion = r['descripcion'] or ''
            self.tree.insert("", "end", values=(
                r['id'],
                r['nombre'],
                descripcion[:40] + ("..." if len(descripcion) > 40 else ""),
                f"{r['precio']:.2f}",
                stock,
                r['proveedor'] or ''
            ), tags=("bajo",) if bajo else ())

        if bajos:
            self.lbl_alerta.configure(text=f"⚠ {bajos} con stock bajo (< {BAJO_STOCK})")
        else:
            self.lbl_alerta.configure(text="")

    def obtener_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un repuesto primero")
            return None
        item = self.tree.item(seleccion)
        return item['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_repuesto()

    def abrir_formulario_editar(self):
        id_repuesto = self.obtener_seleccionado()
        if id_repuesto:
            datos = self.db.obtener_repuesto_por_id(id_repuesto)
            if datos:
                self._formulario_repuesto(id_repuesto, datos)
            else:
                messagebox.showerror("Error", "No se encontraron datos del repuesto", parent=self.frame)

    def _formulario_repuesto(self, id_repuesto=None, datos=None):
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo Repuesto" if id_repuesto is None else "Editar Repuesto")
        ventana.geometry("450x400")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        def solo_letras_numeros_espacios(caracter, texto_actual, max_len):
            if caracter == '':
                return True
            if (caracter.isalnum() or caracter.isspace()) and len(texto_actual) <= max_len:
                return True
            return False

        def solo_numeros_y_punto(caracter, texto_actual, max_len):
            if caracter == '':
                return True
            if (caracter.isdigit() or caracter == '.') and len(texto_actual) <= max_len:
                return True
            return False

        def solo_digitos(caracter, texto_actual, max_len):
            if caracter == '':
                return True
            if caracter.isdigit() and len(texto_actual) <= max_len:
                return True
            return False

        vcmd_nombre = ventana.register(lambda c, t: solo_letras_numeros_espacios(c, t, 100))
        vcmd_precio = ventana.register(lambda c, t: solo_numeros_y_punto(c, t, 10))
        vcmd_stock = ventana.register(lambda c, t: solo_digitos(c, t, 6))
        vcmd_proveedor = ventana.register(lambda c, t: solo_letras_numeros_espacios(c, t, 100))

        ctk.CTkLabel(frame, text="Nombre *:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_nombre = ctk.CTkEntry(frame, width=250, validate="key", validatecommand=(vcmd_nombre, '%S', '%P'))
        entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Descripción:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = ctk.CTkTextbox(frame, width=250, height=80)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Precio *:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_precio = ctk.CTkEntry(frame, width=250, validate="key", validatecommand=(vcmd_precio, '%S', '%P'))
        entry_precio.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Stock:", text_color=TEXTO_BLANCO).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        entry_stock = ctk.CTkEntry(frame, width=250, validate="key", validatecommand=(vcmd_stock, '%S', '%P'))
        entry_stock.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        entry_stock.insert(0, "0")

        ctk.CTkLabel(frame, text="Proveedor:", text_color=TEXTO_BLANCO).grid(row=4, column=0, padx=10, pady=10, sticky="e")
        entry_proveedor = ctk.CTkEntry(frame, width=250, validate="key", validatecommand=(vcmd_proveedor, '%S', '%P'))
        entry_proveedor.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        stock_anterior = 0
        if datos:
            entry_nombre.insert(0, datos['nombre'])
            txt_descripcion.insert("1.0", datos['descripcion'] or '')
            entry_precio.insert(0, str(datos['precio']))
            entry_stock.delete(0, ctk.END)
            entry_stock.insert(0, str(datos['stock']))
            entry_proveedor.insert(0, datos['proveedor'] or '')
            stock_anterior = datos['stock'] or 0

        def guardar():
            nombre = entry_nombre.get().strip()
            descripcion = txt_descripcion.get("1.0", ctk.END).strip()
            precio = entry_precio.get().strip()
            stock = entry_stock.get().strip()
            proveedor = entry_proveedor.get().strip()

            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio", parent=ventana)
                return
            if not precio:
                messagebox.showerror("Error", "El precio es obligatorio", parent=ventana)
                return
            try:
                precio_val = float(precio)
                if precio_val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Precio inválido (debe ser número positivo)", parent=ventana)
                return
            try:
                stock_val = int(stock) if stock else 0
            except ValueError:
                messagebox.showerror("Error", "Stock debe ser un número entero", parent=ventana)
                return

            if id_repuesto is None:
                exito, mensaje, nuevo_id = self.db.agregar_repuesto(nombre, descripcion, precio_val, stock_val, proveedor)
            else:
                exito, mensaje = self.db.actualizar_repuesto(id_repuesto, nombre, descripcion, precio_val, stock_val, proveedor)

            if exito:
                registro_id = nuevo_id if id_repuesto is None else id_repuesto
                accion = "INSERT" if id_repuesto is None else "UPDATE"
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=registro_id,
                    accion=accion,
                    descripcion=f"{accion} en repuestos: {nombre}"
                )

                if id_repuesto is None:
                    if stock_val > 0:
                        self.db.registrar_movimiento(registro_id, "ENTRADA", stock_val,
                                                     "Stock inicial", self.usuario_id, self.usuario_actual)
                else:
                    diferencia = stock_val - stock_anterior
                    if diferencia != 0:
                        tipo = "ENTRADA" if diferencia > 0 else "SALIDA"
                        self.db.registrar_movimiento(registro_id, tipo, abs(diferencia),
                                                     "Ajuste manual", self.usuario_id, self.usuario_actual)

                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Guardar", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def reponer_stock(self):
        id_repuesto = self.obtener_seleccionado()
        if not id_repuesto:
            return
        datos = self.db.obtener_repuesto_por_id(id_repuesto)
        if not datos:
            messagebox.showerror("Error", "No se encontró el repuesto", parent=self.frame)
            return

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Reponer Stock")
        ventana.geometry("400x250")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=datos['nombre'], font=("Inter", 14, "bold"), text_color=TEXTO_BLANCO).pack(pady=5)
        ctk.CTkLabel(frame, text=f"Stock actual: {datos['stock']}", text_color=TEXTO_GRIS).pack(pady=5)
        ctk.CTkLabel(frame, text="Cantidad a ingresar:", text_color=TEXTO_BLANCO).pack(pady=5)
        entry_cantidad = ctk.CTkEntry(frame, width=150)
        entry_cantidad.pack(pady=5)

        def guardar():
            try:
                cantidad = int(entry_cantidad.get().strip())
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida (mayor a 0)", parent=ventana)
                return

            exito, mensaje = self.db.incrementar_stock(id_repuesto, cantidad)
            if exito:
                self.db.registrar_movimiento(id_repuesto, "ENTRADA", cantidad,
                                             "Reposición de stock", self.usuario_id, self.usuario_actual)
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=id_repuesto,
                    accion="UPDATE",
                    descripcion=f"Reposición de stock de '{datos['nombre']}' (+{cantidad})"
                )
                messagebox.showinfo("Éxito", "Stock actualizado", parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Agregar al Stock", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        btn_guardar.pack(pady=15)

    def eliminar_repuesto(self):
        id_repuesto = self.obtener_seleccionado()
        if not id_repuesto:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este repuesto?"):
            exito, mensaje = self.db.eliminar_repuesto(id_repuesto)
            if exito:
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=id_repuesto,
                    accion="DELETE",
                    descripcion=f"Eliminado repuesto ID {id_repuesto}"
                )
                messagebox.showinfo("Éxito", "Repuesto eliminado", parent=self.frame)
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=self.frame)

    def exportar_pdf(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            messagebox.showerror("Error", "No está instalada la librería 'reportlab'. Ejecute: pip install reportlab")
            return

        if not self.repuestos:
            messagebox.showwarning("Sin datos", "No hay repuestos para exportar")
            return

        filename = "repuestos_taller.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Inventario de Repuestos - Taller Don Julio", styles['Title']))

        data = [["ID", "Nombre", "Precio USD", "Stock", "Proveedor"]]
        for r in self.repuestos:
            data.append([r['id'], r['nombre'], f"{r['precio']:.2f}", r['stock'] or 0, r['proveedor'] or ''])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        doc.build(elements)

        messagebox.showinfo("Exportado", f"PDF guardado como {os.path.abspath(filename)}", parent=self.frame)

        try:
            if sys.platform == 'win32':
                os.startfile(filename)
            else:
                subprocess.call(['xdg-open', filename])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {e}", parent=self.frame)

    def ver_historial(self):
        movimientos = self.db.listar_movimientos(200) or []

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Historial de Movimientos de Inventario")
        ventana.geometry("820x500")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame, text="Movimientos de Inventario",
            font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO
        ).pack(pady=10)

        tree = ttk.Treeview(
            frame,
            columns=("ID", "Repuesto", "Tipo", "Cantidad", "Motivo", "Usuario", "Fecha"),
            show="headings"
        )
        columnas = [
            ("ID", 50), ("Repuesto", 150), ("Tipo", 80), ("Cantidad", 80),
            ("Motivo", 200), ("Usuario", 100), ("Fecha", 130)
        ]
        for col, width in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True, pady=5)
        scroll.pack(side="right", fill="y")

        for m in movimientos:
            tree.insert("", "end", values=(
                m['id'],
                m['repuesto'],
                m['tipo'],
                m['cantidad'],
                m['motivo'] or '',
                m['usuario_nombre'] or 'Sistema',
                formatear_fecha(m['fecha_hora'])
            ))

        if not movimientos:
            ctk.CTkLabel(frame, text="No hay movimientos registrados", text_color=TEXTO_GRIS).pack(pady=10)

        btn_cerrar = ctk.CTkButton(frame, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
        btn_cerrar.pack(pady=10)
