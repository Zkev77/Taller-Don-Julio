import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from utilidades import BAJO_STOCK, formatear_fecha
from colores_app import *

class GestionReportes:
    def __init__(self, padre, rol, usuario_actual=None):
        self.padre = padre
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.bd = Database()
        self.marco = ctk.CTkFrame(padre, fg_color=FONDO_TARJETA)
        self.marco.pack(fill="both", expand=True, padx=10, pady=10)

        if self.rol not in ['admin', 'auditor']:
            ctk.CTkLabel(
                self.marco,
                text="⛔ Acceso denegado\nSolo administradores y auditores pueden ver reportes",
                font=("Inter", 14, "bold"),
                text_color=TEXTO_GRIS,
                justify="center"
            ).pack(pady=50)
            return

        self.barra_herramientas = ctk.CTkFrame(self.marco, fg_color=FONDO_TARJETA)
        self.barra_herramientas.pack(fill="x", pady=5)

        self.boton_estadisticas = ctk.CTkButton(
            self.barra_herramientas,
            text="📊 Estadísticas",
            fg_color=COLOR_ACENTO,
            text_color=TEXTO_BLANCO,
            command=self.mostrar_estadisticas
        )
        self.boton_estadisticas.pack(side="left", padx=5)

        self.boton_refrescar = ctk.CTkButton(
            self.barra_herramientas,
            text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR,
            text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.boton_refrescar.pack(side="left", padx=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.arbol = ttk.Treeview(
            self.marco,
            columns=("ID", "Usuario", "Tabla", "Registro", "Acción", "Descripción", "Fecha"),
            show="headings"
        )
        self.arbol.heading("ID", text="ID")
        self.arbol.heading("Usuario", text="Usuario")
        self.arbol.heading("Tabla", text="Tabla")
        self.arbol.heading("Registro", text="Registro")
        self.arbol.heading("Acción", text="Acción")
        self.arbol.heading("Descripción", text="Descripción")
        self.arbol.heading("Fecha", text="Fecha")
        self.arbol.column("ID", width=50)
        self.arbol.column("Usuario", width=100)
        self.arbol.column("Tabla", width=100)
        self.arbol.column("Registro", width=60)
        self.arbol.column("Acción", width=80)
        self.arbol.column("Descripción", width=250)
        self.arbol.column("Fecha", width=150)

        scrollbar = ttk.Scrollbar(self.marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.arbol.get_children():
            self.arbol.delete(row)
        registros = self.bd.listar_logs(200)
        for registro in registros:
            accion_colores = {
                'INSERT': '🟢 INSERT',
                'UPDATE': '🟡 UPDATE',
                'DELETE': '🔴 DELETE'
            }
            accion_mostrada = accion_colores.get(registro['accion'], registro['accion'])
            self.arbol.insert("", "end", values=(
                registro['id'],
                registro['usuario_nombre'] or 'Sistema',
                registro['tabla_afectada'],
                registro['registro_id'],
                accion_mostrada,
                registro['descripcion'][:60] + ("..." if len(registro['descripcion'] or '') > 60 else ""),
                formatear_fecha(registro["fecha_hora"])
            ))
        self.arbol.update_idletasks()

    def mostrar_estadisticas(self):
        estadisticas = self.bd.obtener_estadisticas_taller()

        ventana = ctk.CTkToplevel(self.padre)
        ventana.title("📊 Estadísticas del Taller")
        ventana.geometry("500x450")
        ventana.resizable(False, False)

        marco = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            marco,
            text="📊 Estadísticas del Taller Don Julio",
            font=("Inter", 16, "bold"),
            text_color=TEXTO_BLANCO
        ).pack(pady=15)

        marco_estadisticas = ctk.CTkFrame(marco, fg_color="transparent")
        marco_estadisticas.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            marco_estadisticas,
            text=f"👥 Clientes registrados: {estadisticas['total_clientes']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            marco_estadisticas,
            text=f"🚗 Vehículos registrados: {estadisticas['total_vehiculos']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            marco_estadisticas,
            text=f"📅 Órdenes este mes: {estadisticas['ordenes_mes']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            marco_estadisticas,
            text=f"⚠️ Repuestos con bajo stock (< {BAJO_STOCK}): {estadisticas['repuestos_bajo_stock']}",
            font=("Inter", 12),
            text_color=COLOR_ACENTO
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            marco_estadisticas,
            text="📋 Órdenes por estado:",
            font=("Inter", 12, "bold"),
            text_color=TEXTO_BLANCO
        ).pack(anchor="w", pady=(15, 5))

        estado_colores = {
            'Ingresado': COLOR_AMARILLO,
            'Revisión': COLOR_AZUL,
            'Trabajando': COLOR_VERDE,
            'Completado': '#1abc9c',
            'Entregado': '#27ae60'
        }

        for estado in estadisticas['ordenes_por_estado']:
            color = estado_colores.get(estado['estado'], TEXTO_GRIS)
            ctk.CTkLabel(
                marco_estadisticas,
                text=f"  • {estado['estado']}: {estado['total']}",
                font=("Inter", 11),
                text_color=color
            ).pack(anchor="w", pady=2)

        boton_cerrar = ctk.CTkButton(
            marco,
            text="Cerrar",
            fg_color=COLOR_ACENTO,
            text_color=TEXTO_BLANCO,
            command=ventana.destroy
        )
        boton_cerrar.pack(pady=15)