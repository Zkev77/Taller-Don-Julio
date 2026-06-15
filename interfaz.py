import tkinter as tk
from clientes import GestionClientes
from vehiculos import GestionVehiculos

class MenuTaller:
    def __init__(self, root, rol):
        self.root = root
        self.rol = rol
        self.root.title("Taller Don Julio - Sistema de Gestión Operativa")
        self.root.geometry("1100x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.color_sidebar = "#1a1a1a"
        self.color_acento = "#e67e22"
        self.color_texto = "#ffffff"

        self.sidebar = tk.Frame(self.root, bg=self.color_sidebar, width=250, height=600)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_titulo = tk.Label(self.sidebar, text="DON JULIO\nSISTEMA", font=("Arial", 18, "bold"),
                                   bg=self.color_sidebar, fg=self.color_acento, pady=20)
        self.lbl_titulo.pack()

        # Diccionario de botones
        self.botones = {
            "🏠 Inicio": self.mostrar_inicio,
            "👥 Clientes": self.mostrar_clientes,
            "🚗 Vehículos": self.mostrar_vehiculos,
            "🛠️ Servicios/Reparaciones": self.mostrar_servicios,
            "📦 Repuestos": self.mostrar_repuestos,
            "📊 Reportes/Auditoría": self.mostrar_reportes,
            "⚙️ Configuración": self.mostrar_config
        }

        # Mostrar solo botones permitidos según rol
        for texto, comando in self.botones.items():
            if self._is_button_allowed(texto):
                btn = tk.Button(self.sidebar, text=texto, font=("Arial", 12),
                                bg=self.color_sidebar, fg=self.color_texto,
                                bd=0, activebackground=self.color_acento,
                                cursor="hand2", anchor="w", padx=20, pady=10,
                                command=comando)
                btn.pack(fill="x")

        self.area_principal = tk.Frame(self.root, bg="#ffffff", bd=2, relief="flat")
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
        tk.Label(self.area_principal, text=f"Panel de Control - Rol: {self.rol.upper()}",
                 font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="Bienvenido al sistema de gestión del Taller Don Julio\n\n"
                                           "Utilice el menú lateral para acceder a las diferentes funciones.",
                 bg="white", justify="center").pack(pady=20)

    def mostrar_clientes(self):
        self.limpiar_pantalla()
        GestionClientes(self.area_principal, self.rol)

    def mostrar_vehiculos(self):
        self.limpiar_pantalla()
        GestionVehiculos(self.area_principal, self.rol)

    def mostrar_servicios(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Órdenes de Servicio", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="Diagnóstico → Presupuesto → Ejecución → Entrega", bg="white").pack()
        tk.Label(self.area_principal, text="[Módulo en desarrollo - próximamente]", bg="white", fg="blue").pack(pady=20)

    def mostrar_repuestos(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Inventario de Repuestos", font=("Arial", 18), bg="white").pack(pady=20)
        if self.rol != 'admin':
            tk.Label(self.area_principal, text="(Solo lectura - consulta de stock)", bg="white", fg="blue").pack()
        tk.Label(self.area_principal, text="[Módulo en desarrollo - próximamente]", bg="white", fg="blue").pack(pady=20)

    def mostrar_reportes(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Auditoría y Reportes", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="[Reportes financieros y de gestión - solo admin]", bg="white").pack()

    def mostrar_config(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Configuración de Usuarios y Roles", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="[Gestión de usuarios - solo administrador]", bg="white").pack()