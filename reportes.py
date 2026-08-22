import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database import Database

class GestionReportes:
    def __init__(self, parent, rol, usuario_actual=None):  
        self.parent = parent
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.db = Database()
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        if self.rol not in ['admin', 'auditor']:
            tk.Label(self.frame, text="⛔ Acceso denegado\nSolo administradores y auditores pueden ver reportes",
                     font=("Arial", 14, "bold"), fg="red", bg="white", justify="center").pack(pady=50)
            return

        self.toolbar = tk.Frame(self.frame, bg="white")
        self.toolbar.pack(fill="x", pady=5)

        btn_estadisticas = tk.Button(self.toolbar, text="📊 Estadísticas", bg="#3498db", fg="white",
                                     command=self.mostrar_estadisticas)
        btn_estadisticas.pack(side="left", padx=5)

        btn_logs = tk.Button(self.toolbar, text="📋 Auditoría", bg="#2c3e50", fg="white",
                             command=self.mostrar_logs)
        btn_logs.pack(side="left", padx=5)

        btn_refrescar = tk.Button(self.toolbar, text="⟳ Refrescar", bg="#2c3e50", fg="white",
                                  command=self.cargar_datos)
        btn_refrescar.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Usuario", "Tabla", "Registro", "Acción", "Descripción", "Fecha"),
                                 show="headings")
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

        ventana = Toplevel(self.parent)
        ventana.title("📊 Estadísticas del Taller")
        ventana.geometry("500x450")
        ventana.configure(bg="white")
        ventana.resizable(False, False)

        tk.Label(ventana, text="📊 Estadísticas del Taller Don Julio", 
                 font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=15)

        frame_stats = tk.Frame(ventana, bg="white")
        frame_stats.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(frame_stats, text=f"👥 Clientes registrados: {stats['total_clientes']}", 
                 font=("Arial", 12), bg="white", fg="#2c3e50").pack(anchor="w", pady=5)

        tk.Label(frame_stats, text=f"🚗 Vehículos registrados: {stats['total_vehiculos']}", 
                 font=("Arial", 12), bg="white", fg="#2c3e50").pack(anchor="w", pady=5)

        tk.Label(frame_stats, text=f"📅 Órdenes este mes: {stats['ordenes_mes']}", 
                 font=("Arial", 12), bg="white", fg="#2c3e50").pack(anchor="w", pady=5)

        tk.Label(frame_stats, text=f"⚠️ Repuestos con bajo stock (< 5): {stats['repuestos_bajo_stock']}", 
                 font=("Arial", 12), bg="white", fg="#e74c3c").pack(anchor="w", pady=5)

        tk.Label(frame_stats, text="📋 Órdenes por estado:", 
                 font=("Arial", 12, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=(15, 5))

        estado_colores = {
            'Ingresado': '#f39c12',
            'Revisión': '#3498db',
            'Trabajando': '#2ecc71',
            'Completado': '#1abc9c',
            'Entregado': '#27ae60'
        }

        for estado in stats['ordenes_por_estado']:
            color = estado_colores.get(estado['estado'], '#2c3e50')
            tk.Label(frame_stats, text=f"  • {estado['estado']}: {estado['total']}", 
                     font=("Arial", 11), bg="white", fg=color).pack(anchor="w", pady=2)

        btn_cerrar = tk.Button(ventana, text="Cerrar", bg="#e74c3c", fg="white", 
                               command=ventana.destroy)
        btn_cerrar.pack(pady=15)

    def mostrar_logs(self):
        self.cargar_datos()
        messagebox.showinfo("Auditoría", "Registros de auditoría cargados", parent=self.frame)