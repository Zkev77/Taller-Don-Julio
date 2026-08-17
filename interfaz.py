import customtkinter as ctk
from clientes import GestionClientes
from vehiculos import GestionVehiculos
from database import Database
from servicios import GestionServicios
from repuestos import GestionRepuestos
from reportes import GestionReportes


# Configuración global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MenuTaller:
    def __init__(self, root, rol):
        self.root = root
        self.rol = rol
        self.root.title("Taller Don Julio - Sistema de Gestión Operativa")
        self.root.geometry("1100x600")
        self.root.resizable(True, True)
        self.root.minsize(900, 500)

        self.color_sidebar = "#1a1a2e"
        self.color_acento = "#e67e22"
        self.color_texto = "#ffffff"

        # Sidebar (CustomTkinter)
        self.sidebar = ctk.CTkFrame(self.root, fg_color=self.color_sidebar, width=250, height=600, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_titulo = ctk.CTkLabel(self.sidebar, text="🚗 DON JULIO\nSISTEMA", font=("Inter", 20, "bold"),
                                       text_color=self.color_acento)
        self.lbl_titulo.pack(pady=30)

        # Botones del menú (CustomTkinter)
        self.botones = {
            "🏠 Inicio": self.mostrar_inicio,
            "👥 Clientes": self.mostrar_clientes,
            "🚗 Vehículos": self.mostrar_vehiculos,
            "🛠️ Servicios/Reparaciones": self.mostrar_servicios,
            "📦 Repuestos": self.mostrar_repuestos,
            "📊 Reportes/Auditoría": self.mostrar_reportes,
            "⚙️ Configuración": self.mostrar_config
        }

        for texto, comando in self.botones.items():
            if self._is_button_allowed(texto):
                btn = ctk.CTkButton(self.sidebar, text=texto, font=("Inter", 13),
                                    fg_color="transparent", text_color=self.color_texto,
                                    hover_color=self.color_acento, anchor="w",
                                    command=comando)
                btn.pack(fill="x", padx=10, pady=5)

        self.area_principal = ctk.CTkFrame(self.root, fg_color="#2a2a3e", corner_radius=15)
        self.area_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.mostrar_inicio()

    def _is_button_allowed(self, texto):
        if self.rol == 'admin':
            return True
        elif self.rol == 'mecanico':
            if texto in ["⚙️ Configuración", "📊 Reportes/Auditoría"]:
                return False
            return True
        return True

    def limpiar_pantalla(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_pantalla()
        ctk.CTkLabel(self.area_principal, text=f"Panel de Control - Rol: {self.rol.upper()}",
                     font=("Inter", 24, "bold")).pack(pady=30)
        ctk.CTkLabel(self.area_principal, text="Bienvenido al sistema de gestión del Taller Don Julio\n\n"
                                               "Utilice el menú lateral para acceder a las funciones.",
                     font=("Inter", 14)).pack(pady=10)

        db = Database()
        clientes = db.listar_clientes()
        vehiculos = db.listar_vehiculos()
        num_clientes = len(clientes) if clientes else 0
        num_vehiculos = len(vehiculos) if vehiculos else 0

        frame_stats = ctk.CTkFrame(self.area_principal, fg_color="#3a3a5e", corner_radius=10)
        frame_stats.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(frame_stats, text=f"📊 Clientes: {num_clientes}   |   🚗 Vehículos: {num_vehiculos}",
                     font=("Inter", 16, "bold"), text_color=self.color_acento).pack(pady=15)

    def mostrar_clientes(self):
        self.limpiar_pantalla()
        GestionClientes(self.area_principal, self.rol)

    def mostrar_vehiculos(self):
        self.limpiar_pantalla()
        GestionVehiculos(self.area_principal, self.rol)

    def mostrar_servicios(self):
        self.limpiar_pantalla()
        GestionServicios(self.area_principal, self.rol)

    def mostrar_repuestos(self):
        self.limpiar_pantalla()
        GestionRepuestos(self.area_principal, self.rol)

    def mostrar_reportes(self):
        self.limpiar_pantalla()
        GestionReportes(self.area_principal, self.rol)

    def mostrar_config(self):
        self.limpiar_pantalla()
