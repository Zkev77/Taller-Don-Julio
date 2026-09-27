import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from utilidades import BAJO_STOCK, formatear_fecha, registrar_validador
from colores_app import *


class GestionRepuestos:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0
        self.puede_editar = rol in ['admin', 'secretaria']
        self.repuestos = []

        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        self.barra_herramientas = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_herramientas.pack(fill="x", pady=5)

        self.boton_agregar = ctk.CTkButton(
            self.barra_herramientas, text="+ Agregar Repuesto",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_agregar
        )
        self.boton_agregar.pack(side="left", padx=5)

        self.boton_editar = ctk.CTkButton(
            self.barra_herramientas, text="✏ Editar",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_editar
        )
        self.boton_editar.pack(side="left", padx=5)

        self.boton_eliminar = ctk.CTkButton(
            self.barra_herramientas, text="🗑 Eliminar",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.eliminar_repuesto
        )
        self.boton_eliminar.pack(side="left", padx=5)

        self.boton_reponer = ctk.CTkButton(
            self.barra_herramientas, text="📦 Reponer Stock",
            fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO,
            command=self.reponer_stock
        )
        self.boton_reponer.pack(side="left", padx=5)

        self.boton_refrescar = ctk.CTkButton(
            self.barra_herramientas, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.boton_refrescar.pack(side="left", padx=5)

        self.boton_pdf = ctk.CTkButton(
            self.barra_herramientas, text="📄 Exportar PDF",
            fg_color=COLOR_MORADO, text_color=TEXTO_BLANCO,
            command=self.exportar_pdf
        )
        self.boton_pdf.pack(side="left", padx=5)

        self.boton_historial = ctk.CTkButton(
            self.barra_herramientas, text="🕓 Historial",
            fg_color=COLOR_AZUL, text_color=TEXTO_BLANCO,
            command=self.ver_historial
        )
        self.boton_historial.pack(side="left", padx=5)

        if self.rol == 'auditor':
            self.boton_agregar.configure(state="disabled")
            self.boton_editar.configure(state="disabled")
            self.boton_eliminar.configure(state="disabled")
            self.boton_reponer.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.barra_herramientas.pack_forget()
            ctk.CTkLabel(
                self.marco,
                text="⛔ Acceso denegado para mecánicos",
                font=("Inter", 12),
                text_color=TEXTO_GRIS
            ).pack(pady=20)
            return

        self.barra_busqueda = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_busqueda.pack(fill="x", pady=5)

        ctk.CTkLabel(self.barra_busqueda, text="🔍 Buscar:", text_color=TEXTO_BLANCO).pack(side="left", padx=(5, 5))
        self.var_buscar = ctk.StringVar()
        self.campo_buscar = ctk.CTkEntry(
            self.barra_busqueda, textvariable=self.var_buscar,
            width=300, placeholder_text="Nombre o proveedor"
        )
        self.campo_buscar.pack(side="left", padx=5)
        self.var_buscar.trace_add("write", self._aplicar_filtro)

        self.etiqueta_alerta = ctk.CTkLabel(
            self.barra_busqueda, text="",
            font=("Inter", 12, "bold"), text_color=COLOR_ACENTO
        )
        self.etiqueta_alerta.pack(side="right", padx=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol = ttk.Treeview(
            self.marco,
            columns=("ID", "Nombre", "Descripción", "Precio", "Stock", "Proveedor"),
            show="headings"
        )
        self.arbol.heading("ID", text="ID")
        self.arbol.heading("Nombre", text="Nombre")
        self.arbol.heading("Descripción", text="Descripción")
        self.arbol.heading("Precio", text="Precio USD")
        self.arbol.heading("Stock", text="Stock")
        self.arbol.heading("Proveedor", text="Proveedor")
        self.arbol.column("ID", width=50)
        self.arbol.column("Nombre", width=150)
        self.arbol.column("Descripción", width=250)
        self.arbol.column("Precio", width=100)
        self.arbol.column("Stock", width=80, anchor="center")
        self.arbol.column("Proveedor", width=150)
        self.arbol.tag_configure("bajo", foreground=COLOR_ACENTO)

        scrollbar = ttk.Scrollbar(self.marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        self.repuestos = self.bd.listar_repuestos() or []
        self._aplicar_filtro()

    def _aplicar_filtro(self, *args):
        texto = self.var_buscar.get().strip().lower()
        for row in self.arbol.get_children():
            self.arbol.delete(row)

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
            self.arbol.insert("", "end", values=(
                r['id'],
                r['nombre'],
                descripcion[:40] + ("..." if len(descripcion) > 40 else ""),
                f"{r['precio']:.2f}",
                stock,
                r['proveedor'] or ''
            ), tags=("bajo",) if bajo else ())

        if bajos:
            self.etiqueta_alerta.configure(text=f"⚠ {bajos} con stock bajo (< {BAJO_STOCK})")
        else:
            self.etiqueta_alerta.configure(text="")

    def obtener_seleccionado(self):
        seleccion = self.arbol.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un repuesto primero")
            return None
        elemento = self.arbol.item(seleccion)
        return elemento['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_repuesto()

    def abrir_formulario_editar(self):
        id_repuesto = self.obtener_seleccionado()
        if id_repuesto:
            datos = self.bd.obtener_repuesto_por_id(id_repuesto)
            if datos:
                self._formulario_repuesto(id_repuesto, datos)
            else:
                messagebox.showerror("Error", "No se encontraron datos del repuesto", parent=self.marco)

    def _formulario_repuesto(self, id_repuesto=None, datos=None):
        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Nuevo Repuesto" if id_repuesto is None else "Editar Repuesto")
        ventana.geometry("450x400")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        def solo_letras_numeros_espacios(caracter, texto_actual, longitud_maxima):
            if caracter == '':
                return True
            if (caracter.isalnum() or caracter.isspace()) and len(texto_actual) <= longitud_maxima:
                return True
            return False

        def solo_digitos(caracter, texto_actual, longitud_maxima):
            if caracter == '':
                return True
            if caracter.isdigit() and len(texto_actual) <= longitud_maxima:
                return True
            return False

        validar_nombre = ventana.register(lambda c, t: solo_letras_numeros_espacios(c, t, 100))
        validar_precio = registrar_validador(ventana, 10)
        validar_stock = ventana.register(lambda c, t: solo_digitos(c, t, 6))
        validar_proveedor = ventana.register(lambda c, t: solo_letras_numeros_espacios(c, t, 100))

        ctk.CTkLabel(marco, text="Nombre *:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        campo_nombre = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_nombre, '%S', '%P'))
        campo_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Descripción:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = ctk.CTkTextbox(marco, width=250, height=80)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Precio *:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        campo_precio = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_precio, '%S', '%P'))
        campo_precio.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Stock:", text_color=TEXTO_BLANCO).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        campo_stock = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_stock, '%S', '%P'))
        campo_stock.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        campo_stock.insert(0, "0")

        ctk.CTkLabel(marco, text="Proveedor:", text_color=TEXTO_BLANCO).grid(row=4, column=0, padx=10, pady=10, sticky="e")
        campo_proveedor = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_proveedor, '%S', '%P'))
        campo_proveedor.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        stock_anterior = 0
        if datos:
            campo_nombre.insert(0, datos['nombre'])
            txt_descripcion.insert("1.0", datos['descripcion'] or '')
            campo_precio.insert(0, str(datos['precio']))
            campo_stock.delete(0, ctk.END)
            campo_stock.insert(0, str(datos['stock']))
            campo_proveedor.insert(0, datos['proveedor'] or '')
            stock_anterior = datos['stock'] or 0

        def guardar():
            nombre = campo_nombre.get().strip()
            descripcion = txt_descripcion.get("1.0", ctk.END).strip()
            precio = campo_precio.get().strip()
            stock = campo_stock.get().strip()
            proveedor = campo_proveedor.get().strip()

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
                exito, mensaje, nuevo_id = self.bd.agregar_repuesto(nombre, descripcion, precio_val, stock_val, proveedor)
            else:
                exito, mensaje = self.bd.actualizar_repuesto(id_repuesto, nombre, descripcion, precio_val, stock_val, proveedor)

            if exito:
                registro_id = nuevo_id if id_repuesto is None else id_repuesto
                accion = "INSERT" if id_repuesto is None else "UPDATE"
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=registro_id,
                    accion=accion,
                    descripcion=f"{accion} en repuestos: {nombre}"
                )

                if id_repuesto is None:
                    if stock_val > 0:
                        self.bd.registrar_movimiento(registro_id, "ENTRADA", stock_val,
                                                     "Stock inicial", self.usuario_id, self.usuario_actual)
                else:
                    diferencia = stock_val - stock_anterior
                    if diferencia != 0:
                        tipo = "ENTRADA" if diferencia > 0 else "SALIDA"
                        self.bd.registrar_movimiento(registro_id, tipo, abs(diferencia),
                                                     "Ajuste manual", self.usuario_id, self.usuario_actual)

                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        boton_guardar = ctk.CTkButton(marco, text="Guardar", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        boton_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def reponer_stock(self):
        id_repuesto = self.obtener_seleccionado()
        if not id_repuesto:
            return
        datos = self.bd.obtener_repuesto_por_id(id_repuesto)
        if not datos:
            messagebox.showerror("Error", "No se encontró el repuesto", parent=self.marco)
            return

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Reponer Stock")
        ventana.geometry("400x250")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(marco, text=datos['nombre'], font=("Inter", 14, "bold"), text_color=TEXTO_BLANCO).pack(pady=5)
        ctk.CTkLabel(marco, text=f"Stock actual: {datos['stock']}", text_color=TEXTO_GRIS).pack(pady=5)
        ctk.CTkLabel(marco, text="Cantidad a ingresar:", text_color=TEXTO_BLANCO).pack(pady=5)
        campo_cantidad = ctk.CTkEntry(marco, width=150)
        campo_cantidad.pack(pady=5)

        def guardar():
            try:
                cantidad = int(campo_cantidad.get().strip())
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida (mayor a 0)", parent=ventana)
                return

            exito, mensaje = self.bd.incrementar_stock(id_repuesto, cantidad)
            if exito:
                self.bd.registrar_movimiento(id_repuesto, "ENTRADA", cantidad,
                                             "Reposición de stock", self.usuario_id, self.usuario_actual)
                self.bd.registrar_log(
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

        boton_guardar = ctk.CTkButton(marco, text="Agregar al Stock", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        boton_guardar.pack(pady=15)

    def eliminar_repuesto(self):
        id_repuesto = self.obtener_seleccionado()
        if not id_repuesto:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este repuesto?"):
            exito, mensaje = self.bd.eliminar_repuesto(id_repuesto)
            if exito:
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=id_repuesto,
                    accion="DELETE",
                    descripcion=f"Eliminado repuesto ID {id_repuesto}"
                )
                messagebox.showinfo("Éxito", "Repuesto eliminado", parent=self.marco)
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=self.marco)

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

        nombre_archivo = "repuestos_taller.pdf"
        documento = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elementos = []
        estilos = getSampleStyleSheet()
        elementos.append(Paragraph("Inventario de Repuestos - Taller Don Julio", estilos['Title']))

        datos = [["ID", "Nombre", "Precio USD", "Stock", "Proveedor"]]
        for r in self.repuestos:
            datos.append([r['id'], r['nombre'], f"{r['precio']:.2f}", r['stock'] or 0, r['proveedor'] or ''])

        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elementos.append(tabla)
        documento.build(elementos)

        messagebox.showinfo("Exportado", f"PDF guardado como {os.path.abspath(nombre_archivo)}", parent=self.marco)

        try:
            if sys.platform == 'win32':
                os.startfile(nombre_archivo)
            else:
                subprocess.call(['xdg-open', nombre_archivo])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {e}", parent=self.marco)

    def ver_historial(self):
        movimientos = self.bd.listar_movimientos(200) or []

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Historial de Movimientos de Inventario")
        ventana.geometry("820x500")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            marco, text="Movimientos de Inventario",
            font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO
        ).pack(pady=10)

        arbol = ttk.Treeview(
            marco,
            columns=("ID", "Repuesto", "Tipo", "Cantidad", "Motivo", "Usuario", "Fecha"),
            show="headings"
        )
        columnas = [
            ("ID", 50), ("Repuesto", 150), ("Tipo", 80), ("Cantidad", 80),
            ("Motivo", 200), ("Usuario", 100), ("Fecha", 130)
        ]
        for columna, width in columnas:
            arbol.heading(columna, text=columna)
            arbol.column(columna, width=width, anchor="center")

        scroll = ttk.Scrollbar(marco, orient="vertical", command=arbol.yview)
        arbol.configure(yscrollcommand=scroll.set)
        arbol.pack(side="left", fill="both", expand=True, pady=5)
        scroll.pack(side="right", fill="y")

        for m in movimientos:
            arbol.insert("", "end", values=(
                m['id'],
                m['repuesto'],
                m['tipo'],
                m['cantidad'],
                m['motivo'] or '',
                m['usuario_nombre'] or 'Sistema',
                formatear_fecha(m['fecha_hora'])
            ))

        if not movimientos:
            ctk.CTkLabel(marco, text="No hay movimientos registrados", text_color=TEXTO_GRIS).pack(pady=10)

        boton_cerrar = ctk.CTkButton(marco, text="Cerrar", fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO, command=ventana.destroy)
        boton_cerrar.pack(pady=10)
