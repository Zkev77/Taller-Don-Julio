import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from colores_app import *

class GestionReportes:
    def __init__(self, parent, rol, usuario_actual=None):
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.frame = ctk.CTkFrame(parent, fg_color=FONDO_TARJETA)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        if self.rol not in ['admin', 'auditor']:
            ctk.CTkLabel(
                self.frame,
                text="⛔ Acceso denegado\nSolo administradores y auditores pueden ver reportes",
                font=("Inter", 14, "bold"),
                text_color=TEXTO_GRIS,
                justify="center"
            ).pack(pady=50)
            return

        self.toolbar = ctk.CTkFrame(self.frame, fg_color=FONDO_TARJETA)
        self.toolbar.pack(fill="x", pady=5)

        self.btn_estadisticas = ctk.CTkButton(
            self.toolbar,
            text="📊 Estadísticas",
            fg_color=COLOR_ACENTO,
            text_color=TEXTO_BLANCO,
            command=self.mostrar_estadisticas
        )
        self.btn_estadisticas.pack(side="left", padx=5)

        self.btn_refrescar = ctk.CTkButton(
            self.toolbar,
            text="⟳ Refrescar",
            fg_color=FONDO_SIDEBAR,
            text_color=TEXTO_BLANCO,
            command=self.cargar_datos
        )
        self.btn_refrescar.pack(side="left", padx=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=FONDO_TARJETA, foreground=TEXTO_BLANCO, fieldbackground=FONDO_TARJETA)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)])

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Usuario", "Tabla", "Registro", "Acción", "Descripción", "Fecha"),
            show="headings"
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Tabla", text="Tabla")
        self.tree.heading("Registro", text="Registro")
        self.tree.heading("Acción", text="Acción")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.column("ID", width=50)
        self.tree.column("Usuario", width=100)
        self.tree.column("Tabla", width=100)
        self.tree.column("Registro", width=60)
        self.tree.column("Acción", width=80)
        self.tree.column("Descripción", width=250)
        self.tree.column("Fecha", width=150)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        logs = self.db.listar_logs(200)
        for log in logs:
            accion_colores = {
                'INSERT': '🟢 INSERT',
                'UPDATE': '🟡 UPDATE',
                'DELETE': '🔴 DELETE'
            }
            accion_mostrada = accion_colores.get(log['accion'], log['accion'])
            self.tree.insert("", "end", values=(
                log['id'],
                log['usuario_nombre'] or 'Sistema',
                log['tabla_afectada'],
                log['registro_id'],
                accion_mostrada,
                log['descripcion'][:60] + ("..." if len(log['descripcion'] or '') > 60 else ""),
                log['fecha_hora'].strftime("%d/%m/%Y %H:%M") if log['fecha_hora'] else ""
            ))
        self.tree.update_idletasks()

    def mostrar_estadisticas(self):
        stats = self.db.obtener_estadisticas_taller()

        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("📊 Estadísticas del Taller")
        ventana.geometry("500x450")
        ventana.resizable(False, False)

        frame = ctk.CTkFrame(ventana, fg_color=FONDO_TARJETA)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="📊 Estadísticas del Taller Don Julio",
            font=("Inter", 16, "bold"),
            text_color=TEXTO_BLANCO
        ).pack(pady=15)

        frame_stats = ctk.CTkFrame(frame, fg_color="transparent")
        frame_stats.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            frame_stats,
            text=f"👥 Clientes registrados: {stats['total_clientes']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            frame_stats,
            text=f"🚗 Vehículos registrados: {stats['total_vehiculos']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            frame_stats,
            text=f"📅 Órdenes este mes: {stats['ordenes_mes']}",
            font=("Inter", 12),
            text_color=TEXTO_GRIS
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            frame_stats,
            text=f"⚠️ Repuestos con bajo stock (< 5): {stats['repuestos_bajo_stock']}",
            font=("Inter", 12),
            text_color=COLOR_ACENTO
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            frame_stats,
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

        for estado in stats['ordenes_por_estado']:
            color = estado_colores.get(estado['estado'], TEXTO_GRIS)
            ctk.CTkLabel(
                frame_stats,
                text=f"  • {estado['estado']}: {estado['total']}",
                font=("Inter", 11),
                text_color=color
            ).pack(anchor="w", pady=2)

        btn_cerrar = ctk.CTkButton(
            frame,
            text="Cerrar",
            fg_color=COLOR_ACENTO,
            text_color=TEXTO_BLANCO,
            command=ventana.destroy
        )
        btn_cerrar.pack(pady=15)