import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from colores_app import *

class GestionClientes:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0

        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        self.barra_herramientas = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_herramientas.pack(fill="x", pady=5)

        self.boton_agregar = ctk.CTkButton(
            self.barra_herramientas, text="+ Agregar Cliente",
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
            command=self.eliminar_cliente
        )
        self.boton_eliminar.pack(side="left", padx=5)

        self.boton_refrescar = ctk.CTkButton(
            self.barra_herramientas, text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR, text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.boton_refrescar.pack(side="left", padx=5)

        if self.rol == 'auditor':
            self.boton_agregar.configure(state="disabled")
            self.boton_editar.configure(state="disabled")
            self.boton_eliminar.configure(state="disabled")
        elif self.rol == 'mecanico':
            self.barra_herramientas.pack_forget()
            ctk.CTkLabel(
                self.marco,
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

        self.arbol = ttk.Treeview(
            self.marco,
            columns=("ID", "Cédula", "Nombre", "Teléfono", "Email"),
            show="headings"
        )
        self.arbol.heading("ID", text="ID")
        self.arbol.heading("Cédula", text="Cédula / RIF")
        self.arbol.heading("Nombre", text="Nombre")
        self.arbol.heading("Teléfono", text="Teléfono")
        self.arbol.heading("Email", text="Email")
        self.arbol.column("ID", width=50)
        self.arbol.column("Cédula", width=120)
        self.arbol.column("Nombre", width=200)
        self.arbol.column("Teléfono", width=120)
        self.arbol.column("Email", width=150)

        scrollbar = ttk.Scrollbar(self.marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.arbol.get_children():
            self.arbol.delete(row)
        clientes = self.bd.listar_clientes()
        for c in clientes:
            self.arbol.insert("", "end", values=(
                c['id'],
                c['cedula'],
                c['nombre'],
                c['telefono'],
                c['email']
            ))
        self.arbol.update_idletasks()

    def obtener_seleccionado(self):
        seleccion = self.arbol.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Primero seleccione un cliente de la lista")
            return None
        elemento = self.arbol.item(seleccion)
        return elemento['values'][0]

    def abrir_formulario_agregar(self):
        self._formulario_cliente()

    def abrir_formulario_editar(self):
        id_cliente = self.obtener_seleccionado()
        if id_cliente:
            datos = self.bd.obtener_cliente_por_id(id_cliente)
            if datos:
                self._formulario_cliente(id_cliente, datos)

    def _formulario_cliente(self, id_cliente=None, datos=None):
        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Nuevo Cliente" if id_cliente is None else "Editar Cliente")
        ventana.geometry("500x400")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        def solo_digitos_y_longitud(caracter, texto_actual, longitud_maxima):
            if caracter == '':
                return True
            if caracter.isdigit() and len(texto_actual) <= longitud_maxima:
                return True
            return False

        def solo_letras_espacios_y_longitud(caracter, texto_actual, longitud_maxima):
            if caracter == '':
                return True
            if (caracter.isalpha() or caracter.isspace()) and len(texto_actual) <= longitud_maxima:
                return True
            return False

        validar_cedula_num = ventana.register(lambda c, t: solo_digitos_y_longitud(c, t, 8))
        validar_nombre = ventana.register(lambda c, t: solo_letras_espacios_y_longitud(c, t, 50))
        validar_telefono_num = ventana.register(lambda c, t: solo_digitos_y_longitud(c, t, 7))

        ctk.CTkLabel(marco, text="Tipo Cédula:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tipos = ['V', 'E']
        lista_tipo = ctk.CTkComboBox(marco, values=tipos, width=80, state="readonly")
        lista_tipo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        lista_tipo.set('V')

        ctk.CTkLabel(marco, text="Número Cédula:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        campo_cedula_num = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_cedula_num, '%S', '%P'))
        campo_cedula_num.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Nombre completo:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        campo_nombre = ctk.CTkEntry(marco, width=250, validate="key", validatecommand=(validar_nombre, '%S', '%P'))
        campo_nombre.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(marco, text="Teléfono:", text_color=TEXTO_BLANCO).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        marco_telefono = ctk.CTkFrame(marco, fg_color="transparent")
        marco_telefono.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        prefijos = ['0412', '0414', '0416', '0424', '0426']
        lista_prefijo = ctk.CTkComboBox(marco_telefono, values=prefijos, width=80, state="readonly")
        lista_prefijo.pack(side="left", padx=(0, 5))
        lista_prefijo.set('0412')

        campo_telefono_num = ctk.CTkEntry(marco_telefono, width=150, validate="key", validatecommand=(validar_telefono_num, '%S', '%P'))
        campo_telefono_num.pack(side="left")

        ctk.CTkLabel(marco, text="Email:", text_color=TEXTO_BLANCO).grid(row=4, column=0, padx=10, pady=10, sticky="e")
        campo_email = ctk.CTkEntry(marco, width=250)
        campo_email.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        if datos:
            cedula = datos['cedula']
            if '-' in cedula:
                tipo, numero = cedula.split('-', 1)
                lista_tipo.set(tipo)
                campo_cedula_num.insert(0, numero)
            else:
                lista_tipo.set('V')
                campo_cedula_num.insert(0, cedula)

            campo_nombre.insert(0, datos['nombre'])

            telefono = datos['telefono'] or ''
            if len(telefono) >= 4:
                prefijo_actual = telefono[:4]
                if prefijo_actual in prefijos:
                    lista_prefijo.set(prefijo_actual)
                    campo_telefono_num.insert(0, telefono[4:])
                else:
                    campo_telefono_num.insert(0, telefono)
            campo_email.insert(0, datos['email'] or '')

        def guardar():
            tipo = lista_tipo.get()
            cedula_num = campo_cedula_num.get().strip()
            nombre = campo_nombre.get().strip()
            prefijo = lista_prefijo.get()
            telefono_num = campo_telefono_num.get().strip()
            email = campo_email.get().strip()

            if not tipo:
                messagebox.showerror("Error", "Seleccione un tipo de cédula", parent=ventana)
                return
            if not cedula_num:
                messagebox.showerror("Error", "El número de cédula es obligatorio", parent=ventana)
                return
            if len(cedula_num) < 6 or len(cedula_num) > 8:
                messagebox.showerror("Error", "La cédula debe tener entre 6 y 8 dígitos", parent=ventana)
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

            telefono_existe = self.bd.existe_telefono(telefono_completo, id_cliente)
            if telefono_existe:
                messagebox.showerror("Error", "El número de teléfono ya está registrado por otro cliente", parent=ventana)
                return

            if id_cliente is None:
                exito, mensaje, nuevo_id = self.bd.agregar_cliente(cedula_completa, nombre, telefono_completo, email)
            else:
                exito, mensaje = self.bd.actualizar_cliente(id_cliente, cedula_completa, nombre, telefono_completo, email)

            if exito:
                accion = "INSERT" if id_cliente is None else "UPDATE"
                desc = f"{accion} en clientes: {cedula_completa} - {nombre}"
                registro_id = nuevo_id if id_cliente is None else id_cliente
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="clientes",
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
        boton_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def eliminar_cliente(self):
        id_cliente = self.obtener_seleccionado()
        if not id_cliente:
            return

        datos_cliente = self.bd.obtener_cliente_por_id(id_cliente)
        nombre_cliente = datos_cliente['nombre'] if datos_cliente else "desconocido"

        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente? Se eliminarán también sus vehículos."):
            exito, mensaje = self.bd.eliminar_cliente(id_cliente)
            if exito:
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="clientes",
                    registro_id=id_cliente,
                    accion="DELETE",
                    descripcion=f"Eliminado cliente ID {id_cliente} - {nombre_cliente}"
                )
                messagebox.showinfo("Éxito", "Cliente eliminado", parent=self.marco)
                try:
                    self.cargar_datos()
                    self.arbol.update()
                    self.arbol.selection_remove(self.arbol.selection())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la lista: {e}", parent=self.marco)
            else:
                messagebox.showerror("Error", mensaje, parent=self.marco)