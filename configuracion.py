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
    def __init__(self, parent, rol, usuario_actual):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        if self.rol != 'auditor':
            ctk.CTkLabel(self.frame, text="⛔ Acceso denegado\nSolo el Auditor puede gestionar la configuración",
                         font=("Inter", 14, "bold"), text_color=TEXTO_GRIS).pack(pady=50)
            return

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab_usuarios = ctk.CTkFrame(self.notebook, fg_color=FONDO_TARJETA)
        self.notebook.add(self.tab_usuarios, text="👤 Usuarios")
        self._crear_pestania_usuarios()

        self.tab_password = ctk.CTkFrame(self.notebook, fg_color=FONDO_TARJETA)
        self.notebook.add(self.tab_password, text="🔑 Cambiar Contraseña")
        self._crear_pestania_password()

        self.tab_backup = ctk.CTkFrame(self.notebook, fg_color=FONDO_TARJETA)
        self.notebook.add(self.tab_backup, text="💾 Respaldos")
        self._crear_pestania_backup()

    def _crear_pestania_usuarios(self):
        toolbar = ctk.CTkFrame(self.tab_usuarios, fg_color=FONDO_TARJETA)
        toolbar.pack(fill="x", pady=5)

        btn_agregar = ctk.CTkButton(toolbar, text="+ Agregar Usuario", fg_color=COLOR_ACENTO,
                                    command=self._agregar_usuario)
        btn_agregar.pack(side="left", padx=5)

        btn_editar = ctk.CTkButton(toolbar, text="✏ Editar", fg_color=COLOR_AZUL,
                                   command=self._editar_usuario)
        btn_editar.pack(side="left", padx=5)

        btn_eliminar = ctk.CTkButton(toolbar, text="🗑 Eliminar", fg_color=COLOR_ACENTO,
                                     command=self._eliminar_usuario)
        btn_eliminar.pack(side="left", padx=5)

        btn_refrescar = ctk.CTkButton(toolbar, text="⟳ Refrescar", fg_color=FONDO_SIDEBAR,
                                      command=self._cargar_usuarios)
        btn_refrescar.pack(side="left", padx=5)

        self.tree_usuarios = ttk.Treeview(self.tab_usuarios, columns=("ID", "Usuario", "Rol"), show="headings")
        self.tree_usuarios.heading("ID", text="ID")
        self.tree_usuarios.heading("Usuario", text="Usuario")
        self.tree_usuarios.heading("Rol", text="Rol")
        self.tree_usuarios.column("ID", width=50)
        self.tree_usuarios.column("Usuario", width=150)
        self.tree_usuarios.column("Rol", width=120)

        scrollbar = ttk.Scrollbar(self.tab_usuarios, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)
        self.tree_usuarios.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._cargar_usuarios()

    def _cargar_usuarios(self):
        for row in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(row)
        usuarios = self.db.fetch_all("SELECT id, username, rol FROM usuarios ORDER BY id")
        for u in usuarios:
            self.tree_usuarios.insert("", "end", values=(u['id'], u['username'], u['rol']))

    def _obtener_usuario_seleccionado(self):
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Seleccione un usuario primero")
            return None
        item = self.tree_usuarios.item(seleccion)
        return item['values'][0]

    def _agregar_usuario(self):
        self._formulario_usuario()

    def _editar_usuario(self):
        id_usuario = self._obtener_usuario_seleccionado()
        if id_usuario:
            datos = self.db.fetch_all("SELECT id, username, rol FROM usuarios WHERE id=%s", (id_usuario,))
            if datos:
                self._formulario_usuario(id_usuario, datos[0])

    def _formulario_usuario(self, id_usuario=None, datos=None):
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo Usuario" if id_usuario is None else "Editar Usuario")
        ventana.geometry("400x350")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Usuario:", text_color=TEXTO_BLANCO).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_username = ctk.CTkEntry(frame, width=250)
        entry_username.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Contraseña:", text_color=TEXTO_BLANCO).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_password = ctk.CTkEntry(frame, width=250, show='*')
        entry_password.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Rol:", text_color=TEXTO_BLANCO).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        combo_rol = ctk.CTkComboBox(frame, values=['admin', 'mecanico', 'auditor', 'secretaria'], width=248)
        combo_rol.grid(row=2, column=1, padx=10, pady=10)
        combo_rol.set('mecanico')

        if datos:
            entry_username.insert(0, datos['username'])
            combo_rol.set(datos['rol'])

        def guardar():
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            rol = combo_rol.get()

            if not username:
                messagebox.showerror("Error", "El usuario es obligatorio", parent=ventana)
                return
            if not rol:
                messagebox.showerror("Error", "Seleccione un rol", parent=ventana)
                return

            if id_usuario is None:
                if not password:
                    messagebox.showerror("Error", "La contraseña es obligatoria", parent=ventana)
                    return
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                exito, mensaje, _ = self.db.execute_query(
                    "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
                    (username, password_hash, rol)
                )
            else:
                if password:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    exito, mensaje, _ = self.db.execute_query(
                        "UPDATE usuarios SET username=%s, password=%s, rol=%s WHERE id=%s",
                        (username, password_hash, rol, id_usuario)
                    )
                else:
                    exito, mensaje, _ = self.db.execute_query(
                        "UPDATE usuarios SET username=%s, rol=%s WHERE id=%s",
                        (username, rol, id_usuario)
                    )

            if exito:
                messagebox.showinfo("Éxito", "Usuario guardado correctamente", parent=ventana)
                ventana.destroy()
                self._cargar_usuarios()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)

        btn_guardar = ctk.CTkButton(frame, text="Guardar", fg_color=COLOR_VERDE, command=guardar)
        btn_guardar.grid(row=3, column=0, columnspan=2, pady=20)

    def _eliminar_usuario(self):
                id_usuario = self._obtener_usuario_seleccionado()
                if not id_usuario:
                    return
    
                datos_usuario = self.db.fetch_all("SELECT id, username, rol FROM usuarios WHERE id=%s", (id_usuario,))
                if not datos_usuario:
                    messagebox.showerror("Error", "Usuario no encontrado")
                    return
    
                usuario_seleccionado = datos_usuario[0]
                id_usuario_actual = self.db.obtener_id_usuario(self.usuario_actual)
    
                if id_usuario_actual is None:
                    messagebox.showerror("Error", "No se pudo identificar al usuario actual")
                    return
    
                if id_usuario == id_usuario_actual:
                    messagebox.showerror("Error", "No puedes eliminarte a ti mismo mientras estás logueado")
                    return
    
                if usuario_seleccionado['rol'] == 'admin':
                    admins = self.db.fetch_all("SELECT COUNT(*) as total FROM usuarios WHERE rol='admin'")
                    if admins and admins[0]['total'] <= 1:
                        messagebox.showerror("Error", "No puedes eliminar al último administrador del sistema")
                        return
    
                if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{usuario_seleccionado['username']}' permanentemente?"):
                    exito, mensaje, _ = self.db.execute_query("DELETE FROM usuarios WHERE id=%s", (id_usuario,))
                    if exito:
                        messagebox.showinfo("Éxito", "Usuario eliminado")
                        self._cargar_usuarios()
                    else:
                        messagebox.showerror("Error", mensaje)
    
    def _crear_pestania_password(self):
        frame = ctk.CTkFrame(self.tab_password, fg_color=FONDO_TARJETA)
        frame.pack(pady=30)

        ctk.CTkLabel(frame, text="🔐 Cambiar Contraseña", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(pady=10)
        ctk.CTkLabel(frame, text="Usuario actual:", text_color=TEXTO_GRIS).pack(pady=5)
        ctk.CTkLabel(frame, text=self.usuario_actual, font=("Inter", 12, "bold"), text_color=COLOR_ACENTO).pack(pady=5)
        ctk.CTkLabel(frame, text="Nueva contraseña:", text_color=TEXTO_GRIS).pack(pady=5)
        entry_nueva = ctk.CTkEntry(frame, width=250, show='*')
        entry_nueva.pack(pady=5)
        ctk.CTkLabel(frame, text="Confirmar contraseña:", text_color=TEXTO_GRIS).pack(pady=5)
        entry_confirmar = ctk.CTkEntry(frame, width=250, show='*')
        entry_confirmar.pack(pady=5)

        def cambiar_password():
            nueva = entry_nueva.get().strip()
            confirmar = entry_confirmar.get().strip()
            if not nueva:
                messagebox.showerror("Error", "La nueva contraseña es obligatoria")
                return
            if nueva != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            if len(nueva) < 4:
                messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
                return
            password_hash = hashlib.sha256(nueva.encode()).hexdigest()
            exito, mensaje, _ = self.db.execute_query(
                "UPDATE usuarios SET password=%s WHERE username=%s",
                (password_hash, self.usuario_actual)
            )
            if exito:
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                entry_nueva.delete(0, tk.END)
                entry_confirmar.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)

        btn_guardar = ctk.CTkButton(frame, text="Actualizar Contraseña", fg_color=COLOR_VERDE, command=cambiar_password)
        btn_guardar.pack(pady=20)

    def _crear_pestania_backup(self):
        frame = ctk.CTkFrame(self.tab_backup, fg_color=FONDO_TARJETA)
        frame.pack(pady=30)

        ctk.CTkLabel(frame, text="💾 Respaldos de Base de Datos", font=("Inter", 16, "bold"), text_color=TEXTO_BLANCO).pack(pady=10)
        info = """
        Esta opción permite exportar un respaldo de la base de datos completa.
        El archivo se guardará en la carpeta del proyecto.
        """
        ctk.CTkLabel(frame, text=info, text_color=TEXTO_GRIS, justify="center", font=("Inter", 10)).pack(pady=10)

        def exportar_backup():
            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"backup_taller_{fecha}.sql"
            try:
                import os
                import subprocess
                env = os.environ.copy()
                env['MYSQL_PWD'] = self.db.password
                comando = [
                    "mysqldump",
                    f"-u{self.db.user}",
                    self.db.database
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

        btn_backup = ctk.CTkButton(frame, text="📥 Exportar Respaldo", fg_color=COLOR_AZUL, command=exportar_backup)
        btn_backup.pack(pady=20)