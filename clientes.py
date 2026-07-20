import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database import Database

class GestionClientes:
    def __init__(self, parent, rol):
        self.parent = parent
        self.rol = rol
        self.db = Database()
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = tk.Frame(self.frame, bg="white")
        self.toolbar.pack(fill="x", pady=5)

        self.btn_agregar = tk.Button(self.toolbar, text="+ Agregar Cliente", bg="#e67e22", fg="white",
                                     command=self.abrir_formulario_agregar)
        if self.rol != 'admin':
            self.btn_agregar.config(state="disabled")
        self.btn_agregar.pack(side="left", padx=5)

        self.btn_editar = tk.Button(self.toolbar, text="✏ Editar", bg="#3498db", fg="white",
                                    command=self.abrir_formulario_editar)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(self.toolbar, text="🗑 Eliminar", bg="#e74c3c", fg="white",
                                      command=self.eliminar_cliente)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_refrescar = tk.Button(self.toolbar, text="⟳ Refrescar", bg="#2c3e50", fg="white",
                                       command=self.cargar_datos)
        self.btn_refrescar.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Cédula", "Nombre", "Teléfono", "Email"),
                                 show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Cédula", text="Cédula / RIF")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Email", text="Email")
        self.tree.column("ID", width=50)
        self.tree.column("Cédula", width=120)
        self.tree.column("Nombre", width=200)
        self.tree.column("Teléfono", width=120)
        self.tree.column("Email", width=150)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        clientes = self.db.listar_clientes()
        for c in clientes:
            self.tree.insert("", "end", values=(
                c['id'],
                c['cedula'],
                c['nombre'],
                c['telefono'],
                c['email']
            ))
        self.tree.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Primero seleccione un cliente de la lista")
            return None
        item = self.tree.item(seleccion)
        return item['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_cliente()

    def abrir_formulario_editar(self):
        id_cliente = self.obtener_seleccionado()
        if id_cliente:
            datos = self.db.obtener_cliente_por_id(id_cliente)
            if datos:
                self._formulario_cliente(id_cliente, datos)

    def _formulario_cliente(self, id_cliente=None, datos=None):
        ventana = Toplevel(self.parent)
        ventana.title("Nuevo Cliente" if id_cliente is None else "Editar Cliente")
        ventana.geometry("500x400")
        ventana.resizable(False, False)
        ventana.configure(bg="white")

        def solo_digitos_y_longitud(caracter, texto_actual, max_len):
            if caracter == '':
                return True
            if caracter.isdigit() and len(texto_actual) <= max_len:
                return True
            return False

        def solo_letras_espacios_y_longitud(caracter, texto_actual, max_len):
            if caracter == '':
                return True
            if (caracter.isalpha() or caracter.isspace()) and len(texto_actual) <= max_len:
                return True
            return False

        vcmd_cedula_num = ventana.register(lambda c, t: solo_digitos_y_longitud(c, t, 8))
        vcmd_nombre = ventana.register(lambda c, t: solo_letras_espacios_y_longitud(c, t, 50))
        vcmd_telefono_num = ventana.register(lambda c, t: solo_digitos_y_longitud(c, t, 7))

        tk.Label(ventana, text="Tipo Cédula:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tipos = ['V', 'E']
        combo_tipo = ttk.Combobox(ventana, values=tipos, width=5, state="readonly")
        combo_tipo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        combo_tipo.set('V')

        tk.Label(ventana, text="Número Cédula:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_cedula_num = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_cedula_num, '%S', '%P'))
        entry_cedula_num.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Nombre completo:", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_nombre = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_nombre, '%S', '%P'))
        entry_nombre.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(ventana, text="Teléfono:", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        frame_telefono = tk.Frame(ventana, bg="white")
        frame_telefono.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        prefijos = ['0412', '0414', '0416', '0424', '0426', '0410']
        combo_prefijo = ttk.Combobox(frame_telefono, values=prefijos, width=6, state="readonly")
        combo_prefijo.pack(side="left", padx=(0, 5))
        combo_prefijo.set('0412')

        entry_telefono_num = tk.Entry(frame_telefono, width=20, validate="key", validatecommand=(vcmd_telefono_num, '%S', '%P'))
        entry_telefono_num.pack(side="left")

        tk.Label(ventana, text="Email:", bg="white").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        entry_email = tk.Entry(ventana, width=30)
        entry_email.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        if datos:
            cedula = datos['cedula']
            if '-' in cedula:
                tipo, numero = cedula.split('-', 1)
                combo_tipo.set(tipo)
                entry_cedula_num.insert(0, numero)
            else:
                combo_tipo.set('V')
                entry_cedula_num.insert(0, cedula)

            entry_nombre.insert(0, datos['nombre'])

            telefono = datos['telefono'] or ''
            if len(telefono) >= 4:
                prefijo_actual = telefono[:4]
                if prefijo_actual in prefijos:
                    combo_prefijo.set(prefijo_actual)
                    entry_telefono_num.insert(0, telefono[4:])
                else:
                    entry_telefono_num.insert(0, telefono)
            entry_email.insert(0, datos['email'] or '')

        def guardar():
            tipo = combo_tipo.get()
            cedula_num = entry_cedula_num.get().strip()
            nombre = entry_nombre.get().strip()
            prefijo = combo_prefijo.get()
            telefono_num = entry_telefono_num.get().strip()
            email = entry_email.get().strip()

            if not tipo:
                messagebox.showerror("Error", "Seleccione un tipo de cédula", parent=ventana)
                return
            if not cedula_num:
                messagebox.showerror("Error", "El número de cédula es obligatorio", parent=ventana)
                return
            if len(cedula_num) != 8:
                messagebox.showerror("Error", "La cédula debe tener exactamente 8 dígitos", parent=ventana)
                return
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio", parent=ventana)
                return
            if not prefijo or not telefono_num:
                messagebox.showerror("Error", "Debe seleccionar prefijo y escribir el número", parent=ventana)
                return
            if len(telefono_num) != 7:
                messagebox.showerror("Error", "El número debe tener exactamente 7 dígitos", parent=ventana)
                return

            cedula_completa = f"{tipo}-{cedula_num}"
            telefono_completo = prefijo + telefono_num

            telefono_existe = self.db.existe_telefono(telefono_completo, id_cliente)
            if telefono_existe:
                messagebox.showerror("Error", "El número de teléfono ya está registrado por otro cliente", parent=ventana)
                return

            if id_cliente is None:
                exito, mensaje, _ = self.db.agregar_cliente(cedula_completa, nombre, telefono_completo, email)
            else:
                exito, mensaje = self.db.actualizar_cliente(id_cliente, cedula_completa, nombre, telefono_completo, email)

            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = tk.Button(ventana, text="Guardar", bg="#27ae60", fg="white", command=guardar)
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def eliminar_cliente(self):
        id_cliente = self.obtener_seleccionado()
        if not id_cliente:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente? Se eliminarán también sus vehículos."):
            exito, mensaje = self.db.eliminar_cliente(id_cliente)
            if exito:
                messagebox.showinfo("Éxito", "Cliente eliminado", parent=self.frame)
                self.cargar_datos()
                self.tree.selection_remove(self.tree.selection())
            else:
                messagebox.showerror("Error", mensaje, parent=self.frame)