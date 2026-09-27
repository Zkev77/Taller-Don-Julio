import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
import os
import sys
import subprocess
from colores_app import *

class GestionVehiculos:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        self.barra_herramientas = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_herramientas.pack(fill="x", pady=5)

        self.boton_agregar = ctk.CTkButton(
            self.barra_herramientas, text="+ Agregar Vehículo",
            fg_color=COLOR_ACENTO, text_color=TEXTO_BLANCO,
            command=self.abrir_formulario_agregar
        )
        if self.rol not in ['admin', 'secretaria']:
            self.boton_agregar.configure(state="disabled")
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
            command=self.eliminar_vehiculo
        )
        self.boton_eliminar.pack(side="left", padx=5)

        self.boton_exportar = ctk.CTkButton(
            self.barra_herramientas, text="📄 Exportar PDF",
            fg_color=COLOR_MORADO, text_color=TEXTO_BLANCO,
            command=self.exportar_pdf
        )
        self.boton_exportar.pack(side="left", padx=5)

        self.boton_refrescar = ctk.CTkButton(
            self.barra_herramientas, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.boton_refrescar.pack(side="left", padx=5)

        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0

        if self.rol == 'auditor':
            self.boton_agregar.configure(state="disabled")
            self.boton_editar.configure(state="disabled")
            self.boton_eliminar.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.boton_agregar.configure(state="disabled")
            self.boton_editar.configure(state="disabled")
            self.boton_eliminar.configure(state="disabled")
        elif self.rol in ['admin', 'secretaria']:
            pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol = ttk.Treeview(
            self.marco,
            columns=("ID", "Placa", "Marca", "Modelo", "Cliente"),
            show="headings"
        )
        self.arbol.heading("ID", text="ID")
        self.arbol.heading("Placa", text="Placa")
        self.arbol.heading("Marca", text="Marca")
        self.arbol.heading("Modelo", text="Modelo")
        self.arbol.heading("Cliente", text="Propietario")
        self.arbol.column("ID", width=50)
        self.arbol.column("Placa", width=100)
        self.arbol.column("Marca", width=100)
        self.arbol.column("Modelo", width=100)
        self.arbol.column("Cliente", width=200)

        scrollbar = ttk.Scrollbar(self.marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.arbol.get_children():
            self.arbol.delete(row)
        vehiculos = self.bd.listar_vehiculos()
        for v in vehiculos:
            self.arbol.insert("", "end", values=(v['id'], v['placa'], v['marca'], v['modelo'], v['cliente_nombre']))
        self.arbol.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.arbol.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un vehículo primero")
            return None
        elemento = self.arbol.item(seleccion)
        return elemento['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_vehiculo()

    def abrir_formulario_editar(self):
        id_vehiculo = self.obtener_seleccionado()
        if id_vehiculo:
            datos = self.bd.obtener_vehiculo_por_id(id_vehiculo)
            if datos:
                self._formulario_vehiculo(id_vehiculo, datos)

    def _formulario_vehiculo(self, id_vehiculo=None, datos=None):
        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Nuevo Vehículo" if id_vehiculo is None else "Editar Vehículo")
        ventana.geometry("450x350")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        def validar_longitud_y_caracter(caracter, texto_actual, longitud_maxima, alfanumerico=True):
            if caracter == '':
                return True
            if alfanumerico:
                if not caracter.isalnum():
                    return False
            else:
                if not (caracter.isalpha() or caracter.isspace()):
                    return False
            return len(texto_actual) < longitud_maxima

        validar_placa = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 8, True))
        validar_marca = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 30, False))
        validar_modelo = ventana.register(lambda c, t: validar_longitud_y_caracter(c, t, 30, False))

        clientes = self.bd.listar_clientes_combo()
        mapa_clientes = {c['nombre']: c['id'] for c in clientes}
        nombres_clientes = list(mapa_clientes.keys())

        ctk.CTkLabel(marco, text="Placa *:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        campo_placa = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_placa, '%S', '%P'))
        campo_placa.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Marca:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        campo_marca = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_marca, '%S', '%P'))
        campo_marca.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Modelo:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        campo_modelo = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_modelo, '%S', '%P'))
        campo_modelo.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Propietario *:", text_color=TEXTO_BLANCO).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        lista_cliente = ctk.CTkComboBox(marco, values=nombres_clientes, width=220, state="readonly")
        lista_cliente.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        if datos:
            campo_placa.insert(0, datos['placa'])
            campo_marca.insert(0, datos['marca'] or '')
            campo_modelo.insert(0, datos['modelo'] or '')
            cliente = self.bd.obtener_cliente_por_id(datos['cliente_id'])
            if cliente:
                lista_cliente.set(cliente['nombre'])

        def guardar():
            placa = campo_placa.get().strip().upper()
            marca = campo_marca.get().strip()
            modelo = campo_modelo.get().strip()
            cliente_nombre = lista_cliente.get()

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

            cliente_id = mapa_clientes.get(cliente_nombre)
            if not cliente_id:
                messagebox.showerror("Error", "Seleccione un cliente válido de la lista", parent=ventana)
                return

            if id_vehiculo is None:
                exito, mensaje, nuevo_id = self.bd.agregar_vehiculo(placa, marca, modelo, cliente_id)
            else:
                exito, mensaje = self.bd.actualizar_vehiculo(id_vehiculo, placa, marca, modelo, cliente_id)

            if exito:
                accion = "INSERT" if id_vehiculo is None else "UPDATE"
                desc = f"{accion} en vehiculos: {placa} - {marca} {modelo}"
                registro_id = nuevo_id if id_vehiculo is None else id_vehiculo
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="vehiculos",
                    registro_id=registro_id,
                    accion=accion,
                    descripcion=desc
                )
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        boton_guardar = ctk.CTkButton(marco, text="Guardar", fg_color=COLOR_VERDE, text_color=TEXTO_BLANCO, command=guardar)
        boton_guardar.grid(row=4, column=0, columnspan=2, pady=20)

        def convertir_mayusculas(event):
            contenido = campo_placa.get().upper()
            campo_placa.delete(0, ctk.END)
            campo_placa.insert(0, contenido)

        campo_placa.bind("<KeyRelease>", convertir_mayusculas)

    def eliminar_vehiculo(self):
        id_vehiculo = self.obtener_seleccionado()
        if not id_vehiculo:
            return

        datos_vehiculo = self.bd.obtener_vehiculo_por_id(id_vehiculo)
        placa = datos_vehiculo['placa'] if datos_vehiculo else "desconocida"

        if messagebox.askyesno("Confirmar", "¿Eliminar este vehículo?"):
            exito, mensaje = self.bd.eliminar_vehiculo(id_vehiculo)
            if exito:
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="vehiculos",
                    registro_id=id_vehiculo,
                    accion="DELETE",
                    descripcion=f"Eliminado vehículo ID {id_vehiculo} - Placa {placa}"
                )
                messagebox.showinfo("Éxito", "Vehículo eliminado", parent=self.marco)
                try:
                    self.cargar_datos()
                    self.arbol.update()
                    self.arbol.selection_remove(self.arbol.selection())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la lista: {e}", parent=self.marco)
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

        vehiculos = self.bd.listar_vehiculos()
        if not vehiculos:
            messagebox.showwarning("Sin datos", "No hay vehículos para exportar")
            return

        nombre_archivo = "vehiculos_taller.pdf"
        documento = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elementos = []
        estilos = getSampleStyleSheet()
        elementos.append(Paragraph("Listado de Vehículos - Taller Don Julio", estilos['Title']))

        datos = [["ID", "Placa", "Marca", "Modelo", "Propietario"]]
        for v in vehiculos:
            datos.append([v['id'], v['placa'], v['marca'], v['modelo'], v['cliente_nombre']])

        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
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