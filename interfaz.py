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
    def __init__(self, raiz, rol, usuario_actual):
        self.raiz = raiz
        self.raiz.withdraw()

        self.rol = rol
        self.usuario_actual = usuario_actual
        self.raiz.title("Taller Don Julio - Sistema de Gestión Operativa")

        self.raiz.minsize(1024, 600)
        self.raiz.configure(bg=FONDO_PRINCIPAL)

        self.modulo_actual = None
        self.marcos_modulos = {}

        self.panel_lateral = ctk.CTkFrame(self.raiz, fg_color=FONDO_SIDEBAR, width=220, corner_radius=0)
        self.panel_lateral.pack(side="left", fill="y")

        imagen_auto = Image.open(os.path.join(BASE_DIR, "carro.png"))  
        imagen_auto_ctk = ctk.CTkImage(light_image=imagen_auto, dark_image=imagen_auto, size=(50, 50)) 

        self.etiqueta_titulo = ctk.CTkLabel(
            self.panel_lateral,
            text="TALLER\nDON JULIO",
            font=("Inter", 18, "bold"),
            text_color=COLOR_ACENTO,
            image=imagen_auto_ctk,
            compound="left"
        )
        self.etiqueta_titulo.pack(pady=(30, 10))

        ctk.CTkFrame(self.panel_lateral, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)

        self.etiqueta_usuario = ctk.CTkLabel(
            self.panel_lateral,
            text=f" 👤 {self.usuario_actual}\n({self.rol.upper()})",
            font=("Inter", 12),
            text_color=TEXTO_GRIS,
            justify="left"
        )
        self.etiqueta_usuario.pack(pady=(10, 20))

        ctk.CTkFrame(self.panel_lateral, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)

        self._crear_botones()

        ctk.CTkFrame(self.panel_lateral, height=2, fg_color=SEPARADOR).pack(fill="x", padx=20, pady=10)
        boton_cerrar = ctk.CTkButton(
            self.panel_lateral,
            text=" ↩ Cerrar Sesión",
            font=("Inter", 13),
            fg_color="transparent",
            text_color=TEXTO_BLANCO,
            hover_color=COLOR_ACENTO,
            anchor="w",
            command=self.cerrar_sesion
        )
        boton_cerrar.pack(fill="x", padx=10, pady=10)

        self.area_principal = ctk.CTkFrame(self.raiz, fg_color=FONDO_PRINCIPAL, corner_radius=0)
        self.area_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.contenedor_modulos = ctk.CTkFrame(self.area_principal, fg_color=FONDO_PRINCIPAL)
        self.contenedor_modulos.pack(fill="both", expand=True)

        self.contenedor_modulos.grid_rowconfigure(0, weight=1)
        self.contenedor_modulos.grid_columnconfigure(0, weight=1)

        self._crear_modulos()
        self.mostrar_inicio()
        self.raiz.deiconify()
        self.raiz.after(80, self._maximizar_ventana)

    def _maximizar_ventana(self):
        if sys.platform == "linux":
            try:
                self.raiz.attributes('-zoomed', True)
                return
            except Exception:
                pass
        try:
            self.raiz.state('zoomed')
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
            boton = ctk.CTkButton(
                self.panel_lateral,
                text=f" {emoji} {texto}",
                font=("Inter", 13),
                fg_color="transparent",
                text_color=TEXTO_BLANCO,
                hover_color=COLOR_ACENTO,
                anchor="w",
                command=opciones[texto]
            )
            boton.pack(fill="x", padx=10, pady=5)

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

        marco_inicio = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
        marco_inicio.place(x=0, y=0, relwidth=1, relheight=1)
        self.marcos_modulos["inicio"] = marco_inicio

        ctk.CTkLabel(
            marco_inicio,
            text=f"Panel de Control - Rol: {self.rol.upper()}",
            font=("Inter", 24, "bold"),
            text_color=TEXTO_BLANCO
        ).pack(pady=30)

        ctk.CTkLabel(
            marco_inicio,
            text="Bienvenido al sistema de gestión del Taller Don Julio\n\n"
                 "Utilice el menú lateral para acceder a las funciones.",
            font=("Inter", 14),
            text_color=TEXTO_GRIS,
            justify="center"
        ).pack(pady=10)

        self.marco_estadisticas = ctk.CTkFrame(marco_inicio, fg_color=FONDO_TARJETA, corner_radius=10)
        self.marco_estadisticas.pack(pady=20, padx=20, fill="x")

        self.etiqueta_estadisticas = ctk.CTkLabel(
            self.marco_estadisticas,
            text=" 📊 Cargando datos...",
            font=("Inter", 16, "bold"),
            text_color=COLOR_ACENTO
        )
        self.etiqueta_estadisticas.pack(pady=15)

        self.marco_tarjetas = ctk.CTkFrame(self.marco_estadisticas, fg_color="transparent")
        self.marco_tarjetas.pack(fill="x", padx=20, pady=(0, 20))

        self.etiqueta_recaudado_mes = self._crear_tarjeta(
            self.marco_tarjetas, "💵 Recaudado este mes", "$0.00 USD", COLOR_AZUL)
        self.etiqueta_recaudado_total = self._crear_tarjeta(
            self.marco_tarjetas, "🏆 Recaudado histórico", "$0.00 USD", COLOR_VERDE)

    def _crear_tarjeta(self, contenedor, titulo, valor, color):
        """Crea una tarjeta con un titulo y una cifra grande, y devuelve la etiqueta del valor."""
        tarjeta = ctk.CTkFrame(contenedor, fg_color=FONDO_SIDEBAR, corner_radius=10)
        tarjeta.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(tarjeta, text=titulo, font=("Inter", 12), text_color=TEXTO_GRIS).pack(pady=(12, 2))
        etiqueta_valor = ctk.CTkLabel(tarjeta, text=valor, font=("Inter", 22, "bold"), text_color=color)
        etiqueta_valor.pack(pady=(0, 12))
        return etiqueta_valor

    def _obtener_frame_modulo(self, nombre):
        """Crea el módulo la primera vez que se abre (carga diferida)."""
        if nombre not in self.marcos_modulos:
            marco = ctk.CTkFrame(self.contenedor_modulos, fg_color=FONDO_PRINCIPAL)
            clase = self.modulos_clases.get(nombre)
            if clase:
                clase(marco, self.rol, self.usuario_actual)
            marco.place(x=0, y=0, relwidth=1, relheight=1)
            self.marcos_modulos[nombre] = marco
        return self.marcos_modulos[nombre]

    def _mostrar_modulo(self, nombre_marco):
        if self.modulo_actual == nombre_marco:
            return

        self._obtener_frame_modulo(nombre_marco).tkraise()
        self.modulo_actual = nombre_marco

    def mostrar_inicio(self):
        try:
            bd = Database()
            clientes = bd.listar_clientes()
            vehiculos = bd.listar_vehiculos()
            num_clientes = len(clientes) if clientes else 0
            num_vehiculos = len(vehiculos) if vehiculos else 0
            self.etiqueta_estadisticas.configure(text=f" Clientes: {num_clientes}   |   Vehículos: {num_vehiculos}")

            totales = bd.obtener_totales_recaudados() or {}
            self.etiqueta_recaudado_mes.configure(
                text=f"${float(totales.get('mes') or 0):,.2f} USD")
            self.etiqueta_recaudado_total.configure(
                text=f"${float(totales.get('total') or 0):,.2f} USD")
        except Exception:
            self.etiqueta_estadisticas.configure(text=" Sistema listo para operar")

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
        self.raiz.destroy()
        import login
        login.main()