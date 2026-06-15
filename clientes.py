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
        
        # Toolbar
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
        
        # Treeview
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
            self.tree.insert("", "end", values=(c['id'], c['cedula'], c['nombre'], c['telefono'], c['email']))
    
    def obtener_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Primero seleccione un cliente de la lista")
            return None
        item = self.tree.item(seleccion)
        return item['values'][0]  # ID
    
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
        ventana.geometry("400x300")
        ventana.resizable(False, False)
        ventana.configure(bg="white")
        
        # Campos
        tk.Label(ventana, text="Cédula / RIF:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_cedula = tk.Entry(ventana, width=30)
        entry_cedula.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(ventana, text="Nombre completo:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_nombre = tk.Entry(ventana, width=30)
        entry_nombre.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(ventana, text="Teléfono:", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_telefono = tk.Entry(ventana, width=30)
        entry_telefono.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(ventana, text="Email:", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        entry_email = tk.Entry(ventana, width=30)
        entry_email.grid(row=3, column=1, padx=10, pady=10)
        
        if datos:
            entry_cedula.insert(0, datos['cedula'])
            entry_nombre.insert(0, datos['nombre'])
            entry_telefono.insert(0, datos['telefono'] or '')
            entry_email.insert(0, datos['email'] or '')
        
        def guardar():
            cedula = entry_cedula.get().strip()
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            email = entry_email.get().strip()

            if not cedula or not nombre:
                messagebox.showwarning("Campos vacíos", "Cédula y nombre son obligatorios", parent=ventana)
                return

            if id_cliente is None:
                exito, mensaje, _ = self.db.agregar_cliente(cedula, nombre, telefono, email)
            else:
                exito, mensaje = self.db.actualizar_cliente(id_cliente, cedula, nombre, telefono, email)

            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)
        
        btn_guardar = tk.Button(ventana, text="Guardar", bg="#27ae60", fg="white", command=guardar)
        btn_guardar.grid(row=4, column=0, columnspan=2, pady=20)
    
    def eliminar_cliente(self):
        id_cliente = self.obtener_seleccionado()
        if not id_cliente:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente? Se eliminarán también sus vehículos."):
            exito, mensaje = self.db.eliminar_cliente(id_cliente)
            if exito:
                messagebox.showinfo("Éxito", "Cliente eliminado")
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje)