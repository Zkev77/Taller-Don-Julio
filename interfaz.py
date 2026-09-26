import os
import sys
import customtkinter as ctk
from clientes import GestionClientes
from vehiculos import GestionVehiculos
from servicios import GestionServicios
from repuestos import GestionRepuestos
from reportes import GestionReportes
from configuracion import GestionConfiguracion
from presupuesto import GestionPresupuestos
from database import Database
from colores_app import *
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MenuTaller:
    def __init__(self, root, rol, usuario_actual):
        self.root = root
        self.root.withdraw()

        self.rol = rol
        self.usuario_actual = usuario_actual
        self.root.title("Taller Don Julio - Sistema de Gestión Operativa")

        self.root.minsize(1024, 600)
        self.root.configure(bg=FONDO_PRINCIPAL)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.modulo_actual = None
        self.frames_modulos = {}

        self.sidebar = ctk.CTkFrame(self.root, fg_color=FONDO_SIDEBAR, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        img_auto = Image.open(os.path.join(BASE_DIR, "carro.png"))  
        img_auto_ctk = ctk.CTkImage(light_image=img_auto, dark_image=img_auto, size=(50, 50)) 

        self.lbl_titulo = ctk.CTkLabel(
            self.sidebar,
            text="TALLER\nDON JULIO",
            font=("Inter", 18, "bold"),
            text_color=COLOR_ACENTO,
            image=img_auto_ctk,
            compound="left"
        )
        self.lbl_titulo.pack(pady=(30, 10))

        ctk.CTkFrame(self.sidebar, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)

        self.lbl_usuario = ctk.CTkLabel(
            self.sidebar,
            text=f" 👤 {self.usuario_actual}\n({self.rol.upper()})",
            font=("Inter", 12),
            text_color=TEXTO_GRIS,
            justify="left"
        )
        self.lbl_usuario.pack(pady=(10, 20))

        ctk.CTkFrame(self.sidebar, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)

        self._crear_botones()

        ctk.CTkFrame(self.sidebar, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)
        btn_cerrar = ctk.CTkButton(
            self.sidebar,
            text=" ↩ Cerrar Sesión",
            font=("Inter", 13),
            fg_color="transparent",
            text_color=TEXTO_BLANCO,
            hover_color=COLOR_ACENTO,
            anchor="w",
            command=self.cerrar_sesion
        )
        btn_cerrar.pack(fill="x", padx=10, pady=10)

        self.area_principal = ctk.CTkFrame(self.root, fg_color=FONDO_PRINCIPAL, corner_radius=0)
        self.area_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.contenedor_modulos = ctk.CTkFrame(self.area_principal, fg_color=FONDO_PRINCIPAL)
        self.contenedor_modulos.pack(fill="both", expand=True)

        self.contenedor_modulos.grid_rowconfigure(0, weight=1)
        self.contenedor_modulos.grid_columnconfigure(0, weight=1)

        self._crear_modulos()
        self.mostrar_inicio()
        self.root.deiconify()
        self.root.after(80, self._maximizar_ventana)

    def _maximizar_ventana(self):
        if sys.platform == "linux":
            try:
                self.root.attributes('-zoomed', True)
                return
            except Exception:
                pass
        try:
            self.root.state('zoomed')
        except Exception:
            pass

    def _crear_botones(self):
        opciones = {
            "Inicio": self.mostrar_inicio,
            "Presupuestos": self.mostrar_presupuestos,
            "Clientes": self.mostrar_clientes,
            "Vehículos": self.mostrar_vehiculos,
            "Servicios/Reparaciones": self.mostrar_servicios,
            "Repuestos": self.mostrar_repuestos,
            "Reportes/Auditoría": self.mostrar_reportes,
            "Configuración": self.mostrar_config
        }

        emojis = {
            "Inicio": "🏠",
            "Presupuestos": "💰",
            "Clientes": "👥",
            "Vehículos": "🚗",
            "Servicios/Reparaciones": "🔧",
            "Repuestos": "📦",
            "Reportes/Auditoría": "📊",
            "Configuración": "⚙"
        }

        if self.rol == "admin":
            permitidos = list(opciones.keys())
        elif self.rol == "secretaria":
            permitidos = ["Inicio", "Clientes", "Vehículos", "Servicios/Reparaciones", "Presupuestos"]
        elif self.rol == "mecanico":
            permitidos = ["Inicio", "Vehículos", "Servicios/Reparaciones"]
        elif self.rol == "auditor":
            permitidos = ["Inicio", "Presupuestos", "Clientes", "Vehículos",
                          "Servicios/Reparaciones", "Repuestos",
                          "Reportes/Auditoría", "Configuración"]
        else:
            permitidos = ["Inicio"]

        for texto in permitidos:
            emoji = emojis.get(texto, "")
            btn = ctk.CTkButton(
                self.sidebar,
                text=f" {emoji} {texto}",
                font=("Inter", 13),
                fg_color="transparent",
                text_color=TEXTO_BLANCO,
                hover_color=COLOR_ACENTO,
                anchor="w",
                command=opciones[texto]
            )
            btn.pack(fill="x", padx=10, pady=5)

    def _crear_modulos(self):
        self.modulos_clases = {
            "clientes": GestionClientes,
            "vehiculos": GestionVehiculos,
            "servicios": GestionServicios,
            "repuestos": GestionRepuestos,
            "reportes": GestionReportes,
            "configuracion": GestionConfiguracion,
            "presupuestos": GestionPresupuestos
        }

        frame_inicio = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
        frame_inicio.place(x=0, y=0, relwidth=1, relheight=1)
        self.frames_modulos["inicio"] = frame_inicio

        ctk.CTkLabel(
            frame_inicio,
            text=f"Panel de Control - Rol: {self.rol.upper()}",
            font=("Inter", 24, "bold"),
            text_color=TEXTO_BLANCO
        ).pack(pady=30)

        ctk.CTkLabel(
            frame_inicio,
            text="Bienvenido al sistema de gestión del Taller Don Julio\n\n"
                 "Utilice el menú lateral para acceder a las funciones.",
            font=("Inter", 14),
            text_color=TEXTO_GRIS,
            justify="center"
        ).pack(pady=10)

        self.frame_stats = ctk.CTkFrame(frame_inicio, fg_color=FONDO_TARJETA, corner_radius=10)
        self.frame_stats.pack(pady=20, padx=20, fill="x")

        self.lbl_stats = ctk.CTkLabel(
            self.frame_stats,
            text=" 📊 Cargando datos...",
            font=("Inter", 16, "bold"),
            text_color=COLOR_ACENTO
        )
        self.lbl_stats.pack(pady=15)

    def _obtener_frame_modulo(self, nombre):
        """Crea el módulo la primera vez que se abre (carga diferida)."""
        if nombre not in self.frames_modulos:
            frame = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
            clase = self.modulos_clases.get(nombre)
            if clase:
                clase(frame, self.rol, self.usuario_actual)
            frame.place(x=0, y=0, relwidth=1, relheight=1)
            self.frames_modulos[nombre] = frame
        return self.frames_modulos[nombre]

    def _mostrar_modulo(self, nombre_frame):
        if self.modulo_actual == nombre_frame:
            return

        self._obtener_frame_modulo(nombre_frame).tkraise()
        self.modulo_actual = nombre_frame

    def mostrar_inicio(self):
        try:
            db = Database()
            clientes = db.listar_clientes()
            vehiculos = db.listar_vehiculos()
            num_clientes = len(clientes) if clientes else 0
            num_vehiculos = len(vehiculos) if vehiculos else 0
            self.lbl_stats.configure(text=f" Clientes: {num_clientes}   |   Vehículos: {num_vehiculos}")
        except Exception:
            self.lbl_stats.configure(text=" Sistema listo para operar")

        self._mostrar_modulo("inicio")

    def mostrar_presupuestos(self):
        self._mostrar_modulo("presupuestos")

    def mostrar_clientes(self):
        self._mostrar_modulo("clientes")

    def mostrar_vehiculos(self):
        self._mostrar_modulo("vehiculos")

    def mostrar_servicios(self):
        self._mostrar_modulo("servicios")

    def mostrar_repuestos(self):
        self._mostrar_modulo("repuestos")

    def mostrar_reportes(self):
        self._mostrar_modulo("reportes")

    def mostrar_config(self):
        self._mostrar_modulo("configuracion")

    def cerrar_sesion(self):
        self.root.destroy()
        import login
        login.main()