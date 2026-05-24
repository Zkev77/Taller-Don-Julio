import tkinter as tk
from tkinter import messagebox

class MenuTaller:
    def __init__(self, root):
        self.root = root
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

        botones = [
            ("🏠 Inicio", self.mostrar_inicio),
            ("👥 Clientes", self.mostrar_clientes),
            ("🚗 Vehículos", self.mostrar_vehiculos),
            ("🛠️ Servicios/Reparaciones", self.mostrar_servicios),
            ("📦 Repuestos", self.mostrar_repuestos),
            ("📊 Reportes/Auditoría", self.mostrar_reportes),
            ("⚙️ Configuración", self.mostrar_config)
        ]

        for texto, comando in botones:
            btn = tk.Button(self.sidebar, text=texto, font=("Arial", 12), bg=self.color_sidebar, 
                            fg=self.color_texto, bd=0, activebackground=self.color_acento,
                            cursor="hand2", anchor="w", padx=20, pady=10, command=comando)
            btn.pack(fill="x")

        self.area_principal = tk.Frame(self.root, bg="#ffffff", bd=2, relief="flat")
        self.area_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.lbl_bienvenida = tk.Label(self.area_principal, text="Bienvenido al Sistema de Gestión Operativa", 
                                      font=("Arial", 20), bg="#ffffff", fg="#333")
        self.lbl_bienvenida.pack(pady=100)

        self.lbl_instruccion = tk.Label(self.area_principal, text="Seleccione una opción del menú para comenzar.", 
                                       font=("Arial", 12), bg="#ffffff", fg="#666")
        self.lbl_instruccion.pack()

    def limpiar_pantalla(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Panel de Control - Resumen Diario", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="[Aquí irán gráficas de servicios del día]", bg="white", fg="blue").pack()

    def mostrar_clientes(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Gestión de Clientes", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Button(self.area_principal, text="+ Nuevo Cliente", bg=self.color_acento, fg="white", padx=10).pack()

    def mostrar_servicios(self):
        self.limpiar_pantalla()
        tk.Label(self.area_principal, text="Ordenes de Servicio y Reparaciones", font=("Arial", 18), bg="white").pack(pady=20)
        tk.Label(self.area_principal, text="Control de: Diagnóstico -> Presupuesto -> Ejecución -> Salida", bg="white").pack()

    def mostrar_vehiculos(self): self.limpiar_pantalla(); tk.Label(self.area_principal, text="Registro de Vehículos", font=("Arial", 18), bg="white").pack(pady=20)
    def mostrar_repuestos(self): self.limpiar_pantalla(); tk.Label(self.area_principal, text="Inventario de Repuestos", font=("Arial", 18), bg="white").pack(pady=20)
    def mostrar_reportes(self): self.limpiar_pantalla(); tk.Label(self.area_principal, text="Auditoría y Reportes de Gestión", font=("Arial", 18), bg="white").pack(pady=20)
    def mostrar_config(self): self.limpiar_pantalla(); tk.Label(self.area_principal, text="Configuración de Usuarios y Roles", font=("Arial", 18), bg="white").pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuTaller(root)
    root.mainloop()
    
