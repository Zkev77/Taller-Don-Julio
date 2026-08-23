import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from colores_app import *

class GestionRepuestos:
    def __init__(self, parent, rol, usuario_actual):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = ctk.CTkFrame(self.frame, fg_color=FONDO_TARJETA)
        self.toolbar.pack(fill="x", pady=5)

        self.btn_agregar = ctk.CTkButton(
            self.toolbar, text="+ Agregar Repuesto",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_agregar
        )
        if self.rol not in ['admin', 'secretaria']:
            self.btn_agregar.configure(state="disabled")
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

        self.btn_refrescar = ctk.CTkButton(
            self.toolbar, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.btn_refrescar.pack(side="left", padx=5)

        self.usuario_id = self.db.obtener_id_usuario(usuario_actual) or 0

        if self.rol == 'auditor':
            self.btn_agregar.configure(state="disabled")
            self.btn_editar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.toolbar.pack_forget()
            ctk.CTkLabel(
                self.frame,
                text="⛔ Acceso denegado para mecánicos",
                font=("Inter", 12),
                text_color=TEXTO_GRIS
            ).pack(pady=20)
            return
        elif self.rol in ['admin', 'secretaria']:
            pass

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
        self.tree.column("Stock", width=80)
        self.tree.column("Proveedor", width=150)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        repuestos = self.db.listar_repuestos()
        for r in repuestos:
            self.tree.insert("", "end", values=(
                r['id'],
                r['nombre'],
                r['descripcion'][:40] + ("..." if len(r['descripcion'] or '') > 40 else ""),
                f"{r['precio']:.2f}",
                r['stock'],
                r['proveedor'] or ''
            ))
        self.tree.update_idletasks()

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

        if datos:
            entry_nombre.insert(0, datos['nombre'])
            txt_descripcion.insert("1.0", datos['descripcion'] or '')
            entry_precio.insert(0, str(datos['precio']))
            entry_stock.insert(0, str(datos['stock']))
            entry_proveedor.insert(0, datos['proveedor'] or '')

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
                exito, mensaje, _ = self.db.agregar_repuesto(nombre, descripcion, precio_val, stock_val, proveedor)
            else:
                exito, mensaje = self.db.actualizar_repuesto(id_repuesto, nombre, descripcion, precio_val, stock_val, proveedor)

            if exito:
                accion = "INSERT" if id_repuesto is None else "UPDATE"
                desc = f"{accion} en repuestos: {nombre}"
                self.db.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="repuestos",
                    registro_id=id_repuesto or 0,
                    accion=accion,
                    descripcion=desc
                )
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_datos()
                self.tree.update_idletasks()
                self.tree.update()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Guardar", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

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
                try:
                    self.cargar_datos()
                    self.tree.update()
                    self.tree.selection_remove(self.tree.selection())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la lista: {e}", parent=self.frame)
            else:
                messagebox.showerror("Error", mensaje, parent=self.frame)