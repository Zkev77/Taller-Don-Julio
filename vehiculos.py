import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database import Database
import os
import sys
import subprocess

class GestionVehiculos:
    def __init__(self, parent, rol):
        self.parent = parent
        self.rol = rol
        self.db = Database()
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.toolbar = tk.Frame(self.frame, bg="white")
        self.toolbar.pack(fill="x", pady=5)

        self.btn_agregar = tk.Button(self.toolbar, text="+ Agregar Vehículo", bg="#e67e22", fg="white",
                                     command=self.abrir_formulario_agregar)
        if self.rol != 'admin':
            self.btn_agregar.config(state="disabled")
        self.btn_agregar.pack(side="left", padx=5)

        self.btn_editar = tk.Button(self.toolbar, text="✏ Editar", bg="#3498db", fg="white",
                                    command=self.abrir_formulario_editar)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(self.toolbar, text="🗑 Eliminar", bg="#e74c3c", fg="white",
                                      command=self.eliminar_vehiculo)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_exportar = tk.Button(self.toolbar, text="📄 Exportar PDF", bg="#9b59b6", fg="white",
                                      command=self.exportar_pdf)
        self.btn_exportar.pack(side="left", padx=5)

        self.btn_refrescar = tk.Button(self.toolbar, text="⟳ Refrescar", bg="#2c3e50", fg="white",
                                       command=self.cargar_datos)
        self.btn_refrescar.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Placa", "Marca", "Modelo", "Cliente"),
                                 show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("Marca", text="Marca")
        self.tree.heading("Modelo", text="Modelo")
        self.tree.heading("Cliente", text="Propietario")
        self.tree.column("ID", width=50)
        self.tree.column("Placa", width=100)
        self.tree.column("Marca", width=100)
        self.tree.column("Modelo", width=100)
        self.tree.column("Cliente", width=200)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        vehiculos = self.db.listar_vehiculos()
        for v in vehiculos:
            self.tree.insert("", "end", values=(v['id'], v['placa'], v['marca'], v['modelo'], v['cliente_nombre']))
        self.tree.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un vehículo primero")
            return None
        item = self.tree.item(seleccion)
        return item['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_vehiculo()

    def abrir_formulario_editar(self):
        id_vehiculo = self.obtener_seleccionado()
        if id_vehiculo:
            datos = self.db.obtener_vehiculo_por_id(id_vehiculo)
            if datos:
                self._formulario_vehiculo(id_vehiculo, datos)

    def _formulario_vehiculo(self, id_vehiculo=None, datos=None):
        ventana = Toplevel(self.parent)
        ventana.title("Nuevo Vehículo" if id_vehiculo is None else "Editar Vehículo")
        ventana.geometry("450x350")
        ventana.resizable(False, False)
        ventana.configure(bg="white")

        def validar_longitud_y_caracter(caracter, texto_actual, max_len, alfanumerico=True):
            if caracter == '':
                return True
            if alfanumerico:
                if not caracter.isalnum():
                    return False
            else:
                if not (caracter.isalpha() or caracter.isspace()):
                    return False
            return len(texto_actual) < max_len

        vcmd_placa = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 10, True))
        vcmd_marca = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 30, False))
        vcmd_modelo = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 30, False))

        clientes = self.db.listar_clientes_combobox()
        cliente_map = {c['nombre']: c['id'] for c in clientes}
        nombres_clientes = list(cliente_map.keys())

        tk.Label(ventana, text="Placa *:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_placa = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_placa, '%S', '%P'))
        entry_placa.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(ventana, text="Marca:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_marca = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_marca, '%S', '%P'))
        entry_marca.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(ventana, text="Modelo:", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_modelo = tk.Entry(ventana, width=30, validate="key", validatecommand=(vcmd_modelo, '%S', '%P'))
        entry_modelo.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(ventana, text="Propietario *:", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        combo_cliente = ttk.Combobox(ventana, values=nombres_clientes, width=27)
        combo_cliente.grid(row=3, column=1, padx=10, pady=10)

        if datos:
            entry_placa.insert(0, datos['placa'])
            entry_marca.insert(0, datos['marca'] or '')
            entry_modelo.insert(0, datos['modelo'] or '')
            cliente = self.db.obtener_cliente_por_id(datos['cliente_id'])
            if cliente:
                combo_cliente.set(cliente['nombre'])

        def guardar():
            placa = entry_placa.get().strip().upper()
            marca = entry_marca.get().strip()
            modelo = entry_modelo.get().strip()
            cliente_nombre = combo_cliente.get()

            if not placa:
                messagebox.showerror("Error", "La placa es obligatoria", parent=ventana)
                return
            if not placa.isalnum():
                messagebox.showerror("Error", "La placa solo debe contener letras y números", parent=ventana)
                return
            if len(placa) < 6:
                messagebox.showerror("Error", "La placa debe tener al menos 6 caracteres", parent=ventana)
                return
            if not cliente_nombre:
                messagebox.showerror("Error", "Debe seleccionar un propietario", parent=ventana)
                return

            cliente_id = cliente_map.get(cliente_nombre)
            if not cliente_id:
                messagebox.showerror("Error", "Seleccione un cliente válido de la lista", parent=ventana)
                return

            if id_vehiculo is None:
                exito, mensaje, _ = self.db.agregar_vehiculo(placa, marca, modelo, cliente_id)
            else:
                exito, mensaje = self.db.actualizar_vehiculo(id_vehiculo, placa, marca, modelo, cliente_id)

            if exito:
                accion = "INSERT" if id_vehiculo is None else "UPDATE"
                desc = f"{accion} en vehiculos: {placa} - {marca} {modelo}"
                self.db.registrar_log(
                    usuario_id=1,
                    usuario_nombre="admin",
                    tabla="vehiculos",
                    registro_id=id_vehiculo or 0,  # Si es nuevo, usa el último ID o 0
                    accion=accion,
                    descripcion=desc
                )
                messagebox.showinfo("Éxito", mensaje, parent=ventana)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = tk.Button(ventana, text="Guardar", bg="#27ae60", fg="white", command=guardar)
        btn_guardar.grid(row=4, column=0, columnspan=2, pady=20)

        def convertir_mayusculas(event):
            contenido = entry_placa.get().upper()
            entry_placa.delete(0, tk.END)
            entry_placa.insert(0, contenido)

        entry_placa.bind("<KeyRelease>", convertir_mayusculas)

    def eliminar_vehiculo(self):
        id_vehiculo = self.obtener_seleccionado()
        if not id_vehiculo:
            return

        datos_vehiculo = self.db.obtener_vehiculo_por_id(id_vehiculo)
        placa = datos_vehiculo['placa'] if datos_vehiculo else "desconocida"

        if messagebox.askyesno("Confirmar", "¿Eliminar este vehículo?"):
            exito, mensaje = self.db.eliminar_vehiculo(id_vehiculo)
            if exito:
                self.db.registrar_log(
                    usuario_id=1,
                    usuario_nombre="admin",
                    tabla="vehiculos",
                    registro_id=id_vehiculo,
                    accion="DELETE",
                    descripcion=f"Eliminado vehículo ID {id_vehiculo} - Placa {placa}"
                )
                messagebox.showinfo("Éxito", "Vehículo eliminado", parent=self.frame)
                try:
                    self.cargar_datos()
                    self.tree.update()
                    self.tree.selection_remove(self.tree.selection())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la lista: {e}", parent=self.frame)
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

        vehiculos = self.db.listar_vehiculos()
        if not vehiculos:
            messagebox.showwarning("Sin datos", "No hay vehículos para exportar")
            return

        filename = "vehiculos_taller.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Listado de Vehículos - Taller Don Julio", styles['Title']))

        data = [["ID", "Placa", "Marca", "Modelo", "Propietario"]]
        for v in vehiculos:
            data.append([v['id'], v['placa'], v['marca'], v['modelo'], v['cliente_nombre']])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
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