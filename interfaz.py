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
from pytablericons import TablerIcons, OutlineIcon
from PIL import Image

class MenuTaller:
    def __init__(self, root, rol, usuario_actual):
        self.root = root
        self.root.withdraw()

        self.rol = rol
        self.usuario_actual = usuario_actual
        self.root.title("Taller Don Julio - Sistema de Gestión Operativa")

        self._maximizar_ventana()
        self.root.minsize(1024, 600)
        self.root.configure(bg=FONDO_PRINCIPAL)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.modulo_actual = None
        self.frames_modulos = {}

        self.sidebar = ctk.CTkFrame(self.root, fg_color=FONDO_SIDEBAR, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        img_auto = Image.open("carro.png")  
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

        icon_user = TablerIcons.load(OutlineIcon.USER, size=20, color=TEXTO_GRIS)
        icon_user_ctk = ctk.CTkImage(light_image=icon_user, dark_image=icon_user, size=(40, 40))

        self.lbl_usuario = ctk.CTkLabel(
            self.sidebar,
            text=f" {self.usuario_actual}\n({self.rol.upper()})",
            font=("Inter", 12),
            text_color=TEXTO_GRIS,
            justify="left",
            image=icon_user_ctk,
            compound="left"
        )
        self.lbl_usuario.pack(pady=(10, 20))

        ctk.CTkFrame(self.sidebar, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)

        self._crear_botones()

        ctk.CTkFrame(self.sidebar, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)
        btn_cerrar = ctk.CTkButton(
            self.sidebar,
            text=" Cerrar Sesión",
            font=("Inter", 13),
            fg_color="transparent",
            text_color=TEXTO_BLANCO,
            hover_color=COLOR_ACENTO,
            anchor="w",
            command=self.cerrar_sesion
        )

        icon_logout = TablerIcons.load(OutlineIcon.LOGOUT, size=20, color=TEXTO_BLANCO)
        icon_logout_ctk = ctk.CTkImage(light_image=icon_logout, dark_image=icon_logout, size=(20, 20))
        btn_cerrar.configure(image=icon_logout_ctk, compound="left")
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

    def _crear_icono(self, icono_enum, size=20, color=TEXTO_BLANCO):
        """Carga un icono de TablerIcons y lo convierte a CTkImage."""
        img = TablerIcons.load(icono_enum, size=size, color=color)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))

    def _maximizar_ventana(self):
        try:
            self.root.attributes('-zoomed', True)
        except Exception:
            self.root.state('zoomed')

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

        iconos = {
            "Inicio": OutlineIcon.HOME,
            "Presupuestos": OutlineIcon.COINS,
            "Clientes": OutlineIcon.USERS,
            "Vehículos": OutlineIcon.CAR,
            "Servicios/Reparaciones": OutlineIcon.TOOLS,
            "Repuestos": OutlineIcon.BOX,
            "Reportes/Auditoría": OutlineIcon.FILE_REPORT,
            "Configuración": OutlineIcon.SETTINGS
        }

        if self.rol == "admin":
            permitidos = list(opciones.keys())
        elif self.rol == "secretaria":
            permitidos = ["Inicio", "Clientes", "Vehículos", "Servicios/Reparaciones", "Presupuestos"]
        elif self.rol == "mecanico":
            permitidos = ["Inicio", "Vehículos", "Servicios/Reparaciones"]
        elif self.rol == "auditor":
            permitidos = ["Inicio", "Reportes/Auditoría", "Configuración"]
        else:
            permitidos = ["Inicio"]

        for texto in permitidos:
            icono_enum = iconos.get(texto)
            icono_ctk = None
            if icono_enum:
                img = TablerIcons.load(icono_enum, size=20, color=TEXTO_BLANCO)
                icono_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))

            btn = ctk.CTkButton(
                self.sidebar,
                text=f" {texto}",
                font=("Inter", 13),
                fg_color="transparent",
                text_color=TEXTO_BLANCO,
                hover_color=COLOR_ACENTO,
                anchor="w",
                command=opciones[texto]
            )
            if icono_ctk:
                btn.configure(image=icono_ctk, compound="left")
            btn.pack(fill="x", padx=10, pady=5)

    def _crear_modulos(self):
        modulos = {
            "clientes": GestionClientes,
            "vehiculos": GestionVehiculos,
            "servicios": GestionServicios,
            "repuestos": GestionRepuestos,
            "reportes": GestionReportes,
            "configuracion": GestionConfiguracion,
            "presupuestos": GestionPresupuestos
        }

        for nombre, clase in modulos.items():
            frame = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames_modulos[nombre] = frame
            clase(frame, self.rol, self.usuario_actual)
            frame.grid_remove()

        frame_inicio = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
        frame_inicio.grid(row=0, column=0, sticky="nsew")
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

        icon_stats = TablerIcons.load(OutlineIcon.CHART_BAR, size=20, color=COLOR_ACENTO)
        icon_stats_ctk = ctk.CTkImage(light_image=icon_stats, dark_image=icon_stats, size=(20, 20))

        self.lbl_stats = ctk.CTkLabel(
            self.frame_stats,
            text=" Cargando datos...",
            font=("Inter", 16, "bold"),
            text_color=COLOR_ACENTO,
            image=icon_stats_ctk,
            compound="left"
        )
        self.lbl_stats.pack(pady=15)

        frame_inicio.grid_remove()

    def _mostrar_modulo(self, nombre_frame):
        if self.modulo_actual == nombre_frame:
            return

        self.root.update()

        if self.modulo_actual:
            self.frames_modulos[self.modulo_actual].grid_remove()

        self.frames_modulos[nombre_frame].grid()
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