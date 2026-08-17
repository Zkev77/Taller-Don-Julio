import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database import Database

class GestionRepuestos:
    def __init__(self, parent, rol):
        self.parent = parent
        self.rol = rol
        self.db = Database()
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = tk.Frame(self.frame, bg="white")
        self.toolbar.pack(fill="x", pady=5)

        self.btn_agregar = tk.Button(self.toolbar, text="+ Agregar Repuesto", bg="#e67e22", fg="white",
                                     command=self.abrir_formulario_agregar)
        if self.rol != 'admin':
            self.btn_agregar.config(state="disabled")
        self.btn_agregar.pack(side="left", padx=5)

        self.btn_editar = tk.Button(self.toolbar, text="✏ Editar", bg="#3498db", fg="white",
                                    command=self.abrir_formulario_editar)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(self.toolbar, text="🗑 Eliminar", bg="#e74c3c", fg="white",
                                      command=self.eliminar_repuesto)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_refrescar = tk.Button(self.toolbar, text="⟳ Refrescar", bg="#2c3e50", fg="white",
                                       command=self.cargar_datos)
        self.btn_refrescar.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Descripción", "Precio", "Stock", "Proveedor"),
                                 show="headings")
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

    def _formulario_repuesto(self, id_repuesto=None, datos=None):
        ventana = Toplevel(self.parent)
        ventana.title("Nuevo Repuesto" if id_repuesto is None else "Editar Repuesto")
        ventana.geometry("450x400")
        ventana.resizable(False, False)
        ventana.configure(bg="white")

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

        tk.Label(ventana, text="Nombre *:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_nombre = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_nombre, '%S', '%P'))
        entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Descripción:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="ne")
        txt_descripcion = tk.Text(ventana, width=30, height=4)
        txt_descripcion.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Precio *:", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_precio = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_precio, '%S', '%P'))
        entry_precio.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Stock:", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        entry_stock = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_stock, '%S', '%P'))
        entry_stock.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        entry_stock.insert(0, "0")

        tk.Label(ventana, text="Proveedor:", bg="white").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        entry_proveedor = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_proveedor, '%S', '%P'))
        entry_proveedor.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        if datos:
            entry_nombre.insert(0, datos['nombre'])
            txt_descripcion.insert("1.0", datos['descripcion'] or '')
            entry_precio.insert(0, str(datos['precio']))
            entry_stock.insert(0, str(datos['stock']))
            entry_proveedor.insert(0, datos['proveedor'] or '')

        def guardar():
            nombre = entry_nombre.get().strip()
            descripcion = txt_descripcion.get("1.0", tk.END).strip()
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
                    usuario_id=1,
                    usuario_nombre="admin",
                    tabla="repuestos",
                    registro_id=id_repuesto or 0,
                    accion=accion,
                    descripcion=desc
                )
                messagebox.showinfo("Éxito", mensaje, parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = tk.Button(ventana, text="Guardar", bg="#27ae60", fg="white", command=guardar)
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def eliminar_repuesto(self):
        id_repuesto = self.obtener_seleccionado()
        if not id_repuesto:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este repuesto?"):
            exito, mensaje = self.db.eliminar_repuesto(id_repuesto)
            if exito:
                self.db.registrar_log(
                    usuario_id=1,
                    usuario_nombre="admin",
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