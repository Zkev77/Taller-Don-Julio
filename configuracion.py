import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import customtkinter as ctk
from database import Database
import hashlib
import os
import subprocess
import datetime
from colores_app import *

class GestionConfiguracion:
    def __init__(self, padre, rol, usuario_actual):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.usuario_id = self.bd.obtener_id_usuario(usuario_actual) or 0
        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        if self.rol != 'auditor':
            ctk.CTkLabel(self.marco, text="⛔ Acceso denegado\nSolo el Auditor puede gestionar la configuración",
                         font=("Inter", 14, "bold"), text_color=TEXTO_GRIS).pack(pady=50)
            return

        self.pestanas = ttk.Notebook(self.marco)
        self.pestanas.pack(fill="both", expand=True)

        self.pestania_usuarios = ctk.CTkFrame(self.pestanas, fg_color=FONDO_TARJETA)
        self.pestanas.add(self.pestania_usuarios, text="👤 Usuarios")
        self._crear_pestania_usuarios()

        self.pestania_backup = ctk.CTkFrame(self.pestanas, fg_color=FONDO_TARJETA)
        self.pestanas.add(self.pestania_backup, text="💾 Respaldos")
        self._crear_pestania_backup()

    def _crear_pestania_usuarios(self):
        barra_herramientas = ctk.CTkFrame(self.pestania_usuarios, fg_color=FONDO_TARJETA)
        barra_herramientas.pack(fill="x", pady=5)

        boton_agregar = ctk.CTkButton(barra_herramientas, text="+ Agregar Usuario", fg_color=COLOR_ACENTO,
                                    command=self._agregar_usuario)
        boton_agregar.pack(side="left", padx=5)

        boton_editar = ctk.CTkButton(barra_herramientas, text="✏ Editar", fg_color=COLOR_AZUL,
                                   command=self._editar_usuario)
        boton_editar.pack(side="left", padx=5)

        boton_eliminar = ctk.CTkButton(barra_herramientas, text="🗑 Eliminar", fg_color=COLOR_ACENTO,
                                     command=self._eliminar_usuario)
        boton_eliminar.pack(side="left", padx=5)

        boton_refrescar = ctk.CTkButton(barra_herramientas, text="⟳ Refrescar", fg_color=FONDO_SIDEBAR,
                                      command=self._cargar_usuarios)
        boton_refrescar.pack(side="left", padx=5)

        self.arbol_usuarios = ttk.Treeview(self.pestania_usuarios, columns=("ID", "Usuario", "Rol"), show="headings")
        self.arbol_usuarios.heading("ID", text="ID")
        self.arbol_usuarios.heading("Usuario", text="Usuario")
        self.arbol_usuarios.heading("Rol", text="Rol")
        self.arbol_usuarios.column("ID", width=50)
        self.arbol_usuarios.column("Usuario", width=150)
        self.arbol_usuarios.column("Rol", width=120)

        scrollbar = ttk.Scrollbar(self.pestania_usuarios, orient="vertical", command=self.arbol_usuarios.yview)
        self.arbol_usuarios.configure(yscrollcommand=scrollbar.set)
        self.arbol_usuarios.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._cargar_usuarios()

    def _cargar_usuarios(self):
        for row in self.arbol_usuarios.get_children():
            self.arbol_usuarios.delete(row)
        usuarios = self.bd.obtener_todos("SELECT id, username, rol FROM usuarios ORDER BY id")
        for u in usuarios:
            self.arbol_usuarios.insert("", "end", values=(u['id'], u['username'], u['rol']))

    def _obtener_usuario_seleccionado(self):
        seleccion = self.arbol_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un usuario primero")
            return None
        elemento = self.arbol_usuarios.item(seleccion)
        return elemento['values'][0]

    def _agregar_usuario(self):
        self._formulario_usuario()

    def _editar_usuario(self):
        id_usuario = self._obtener_usuario_seleccionado()
        if id_usuario:
            datos = self.bd.obtener_todos("SELECT id, username, rol FROM usuarios WHERE id=%s", (id_usuario,))
            if datos:
                self._formulario_usuario(id_usuario, datos[0])

    def _formulario_usuario(self, id_usuario=None, datos=None):
        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("Nuevo Usuario" if id_usuario is None else "Editar Usuario")
        ventana.geometry("400x350")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(marco, text="Usuario:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        campo_nombre_usuario = ctk.CTkEntry(marco, width=250)
        campo_nombre_usuario.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(marco, text="Contraseña:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        campo_contrasena = ctk.CTkEntry(marco, width=250, show='*')
        campo_contrasena.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(marco, text="Rol:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        lista_rol = ctk.CTkComboBox(marco, values=['admin', 'mecanico', 'auditor', 'secretaria'], width=248, state="readonly")
        lista_rol.grid(row=2, column=1, padx=10, pady=10)
        lista_rol.set('mecanico')

        if datos:
            campo_nombre_usuario.insert(0, datos['username'])
            lista_rol.set(datos['rol'])

        def guardar():
            nombre_usuario = campo_nombre_usuario.get().strip()
            contrasena = campo_contrasena.get().strip()
            rol = lista_rol.get()

            if not nombre_usuario:
                messagebox.showerror("Error", "El usuario es obligatorio", parent=ventana)
                return
            if not rol:
                messagebox.showerror("Error", "Seleccione un rol", parent=ventana)
                return

            if id_usuario is None:
                if not contrasena:
                    messagebox.showerror("Error", "La contraseña es obligatoria", parent=ventana)
                    return
                hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
                exito, mensaje, nuevo_id = self.bd.ejecutar_consulta(
                    "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
                    (nombre_usuario, hash_contrasena, rol)
                )
                if exito:
                    self.bd.registrar_log(
                        usuario_id=self.usuario_id,
                        usuario_nombre=self.usuario_actual,
                        tabla="usuarios",
                        registro_id=nuevo_id,
                        accion="INSERT",
                        descripcion=f"Usuario '{nombre_usuario}' creado con rol '{rol}'"
                    )
            else:
                if contrasena:
                    hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
                    exito, mensaje, _ = self.bd.ejecutar_consulta(
                        "UPDATE usuarios SET username=%s, password=%s, rol=%s WHERE id=%s",
                        (nombre_usuario, hash_contrasena, rol, id_usuario)
                    )
                else:
                    exito, mensaje, _ = self.bd.ejecutar_consulta(
                        "UPDATE usuarios SET username=%s, rol=%s WHERE id=%s",
                        (nombre_usuario, rol, id_usuario)
                    )
                if exito:
                    self.bd.registrar_log(
                        usuario_id=self.usuario_id,
                        usuario_nombre=self.usuario_actual,
                        tabla="usuarios",
                        registro_id=id_usuario,
                        accion="UPDATE",
                        descripcion=f"Usuario '{nombre_usuario}' actualizado (rol '{rol}')"
                    )

            if exito:
                messagebox.showinfo("Éxito", "Usuario guardado correctamente", parent=ventana)
                ventana.destroy()
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        boton_guardar = ctk.CTkButton(marco, text="Guardar", fg_color=COLOR_VERDE, command=guardar)
        boton_guardar.grid(row=3, column=0, columnspan=2, pady=20)

    def _eliminar_usuario(self):
        id_usuario = self._obtener_usuario_seleccionado()
        if not id_usuario:
            return

        datos_usuario = self.bd.obtener_todos("SELECT id, username, rol FROM usuarios WHERE id=%s", (id_usuario,))
        if not datos_usuario:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        usuario_seleccionado = datos_usuario[0]
        id_usuario_actual = self.bd.obtener_id_usuario(self.usuario_actual)

        if id_usuario_actual is None:
            messagebox.showerror("Error", "No se pudo identificar al usuario actual")
            return

        if id_usuario == id_usuario_actual:
            messagebox.showerror("Error", "No puedes eliminarte a ti mismo mientras estás logueado")
            return

        if usuario_seleccionado['rol'] == 'admin':
            admins = self.bd.obtener_todos("SELECT COUNT(*) as total FROM usuarios WHERE rol='admin'")
            if admins and admins[0]['total'] <= 1:
                messagebox.showerror("Error", "No puedes eliminar al último administrador del sistema")
                return

        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{usuario_seleccionado['username']}' permanentemente?"):
            exito, mensaje, _ = self.bd.ejecutar_consulta("DELETE FROM usuarios WHERE id=%s", (id_usuario,))
            if exito:
                self.bd.registrar_log(
                    usuario_id=self.usuario_id,
                    usuario_nombre=self.usuario_actual,
                    tabla="usuarios",
                    registro_id=id_usuario,
                    accion="DELETE",
                    descripcion=f"Usuario '{usuario_seleccionado['username']}' eliminado"
                )
                messagebox.showinfo("Éxito", "Usuario eliminado")
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje)
    

    def _crear_pestania_backup(self):
        marco = ctk.CTkFrame(self.pestania_backup, fg_color=FONDO_TARJETA)
        marco.pack(pady=30)

        ctk.CTkLabel(marco, text="💾 Respaldos de Base de Datos", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(pady=10)
        informacion = """
        Esta opción permite exportar un respaldo de la base de datos completa.
        El archivo se guardará en la carpeta del proyecto.
        """
        ctk.CTkLabel(marco, text=informacion, text_color=TEXTO_GRIS, justify="center", font=("Inter", 10)).pack(pady=10)

        def exportar_backup():
            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"backup_taller_{fecha}.sql"
            try:
                import os
                import subprocess
                env = os.environ.copy()
                env['MYSQL_PWD'] = self.bd.contrasena
                comando = [
                    "mysqldump",
                    f"-u{self.bd.usuario}",
                    self.bd.base_datos
                ]
                with open(archivo, "w", encoding="utf-8") as f:
                    subprocess.run(comando, stdout=f, check=True, stderr=subprocess.PIPE, env=env)
                messagebox.showinfo("Éxito", f"Respaldo guardado correctamente en:\n{os.path.abspath(archivo)}")
            except FileNotFoundError:
                messagebox.showerror("Error", "mysqldump no está instalado o no se encuentra en el PATH.\n"
                                "En Linux: sudo apt install mysql-client\n"
                                "En Windows: agregue la ruta de MySQL al PATH")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el respaldo:\n{e}")

        boton_backup = ctk.CTkButton(marco, text="📥 Exportar Respaldo", fg_color=COLOR_AZUL, command=exportar_backup)
        boton_backup.pack(pady=20)