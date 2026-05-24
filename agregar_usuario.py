import tkinter as tk
from tkinter import messagebox
from database import insertar_cliente

class FormularioRegistro:
    
    CAMPOS_REQUERIDOS = ['cedula', 'nombre', 'telefono', 'marca', 'modelo', 'placa']
    CAMPOS_OPCIONALES = ['email']
    
    def __init__(self, contenedor):
        self.contenedor = contenedor
        self.entries = {}
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        form_frame = self._crear_contenedor_formulario()
        
        self._crear_titulo(form_frame)
        
        self._crear_seccion_cliente(form_frame)
        self._crear_seccion_vehiculo(form_frame)
        
        self._crear_boton_guardar(form_frame)
    
    def _crear_contenedor_formulario(self):
        form_frame = tk.Frame(self.contenedor, bg="white")
        form_frame.pack(pady=20, padx=20)
        return form_frame
    
    def _crear_titulo(self, parent):
        """Crea el título del formulario"""
        titulo = tk.Label(
            parent, 
            text="Registro de Entrada: Cliente y Vehículo", 
            font=("Arial", 16, "bold"), 
            bg="white", 
            fg="#2c3e50"
        )
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 20))
    
    def _crear_seccion_cliente(self, parent):
        """Crea la sección de datos del cliente"""
        # Título sección
        self._crear_subtitulo(parent, "👥 Datos del Propietario", row=1, col=0, col_span=2)
        
        # Campos
        campos_cliente = [
            ("Cédula / RIF *:", "cedula", 2),
            ("Nombre Completo *:", "nombre", 3),
            ("Teléfono *:", "telefono", 4),
            ("Correo (Opcional):", "email", 5)
        ]
        
        for texto, clave, fila in campos_cliente:
            self._crear_campo(parent, texto, clave, fila, columna=0)
    
    def _crear_seccion_vehiculo(self, parent):
        """Crea la sección de datos del vehículo"""
        # Título sección
        self._crear_subtitulo(parent, "🚗 Datos del Vehículo", row=1, col=2, col_span=2, padx_extra=30)
        
        # Campos
        campos_vehiculo = [
            ("Marca *:", "marca", 2),
            ("Modelo *:", "modelo", 3),
            ("Placa / Matrícula *:", "placa", 4)
        ]
        
        for texto, clave, fila in campos_vehiculo:
            self._crear_campo(parent, texto, clave, fila, columna=2, padx_label=30)
    
    def _crear_subtitulo(self, parent, texto, row, col, col_span=1, padx_extra=0):
        """Crea un subtítulo de sección"""
        lbl = tk.Label(
            parent, 
            text=texto, 
            font=("Arial", 11, "bold"), 
            bg="white", 
            fg="#e67e22"
        )
        lbl.grid(row=row, column=col, columnspan=col_span, sticky="w", pady=(10, 5), padx=(padx_extra, 0))
    
    def _crear_campo(self, parent, label_text, entry_key, row, columna, padx_label=0):
        """Crea un par label + entry en el formulario"""
        # Label
        lbl = tk.Label(parent, text=label_text, bg="white", font=("Arial", 10))
        lbl.grid(row=row, column=columna, sticky="w", pady=5, padx=(padx_label, 0))
        
        # Entry
        entry = tk.Entry(parent, font=("Arial", 11), width=25, bd=1, relief="solid")
        entry.grid(row=row, column=columna + 1, pady=5, padx=10, ipady=3)
        
        # Guardar referencia
        self.entries[entry_key] = entry
    
    def _crear_boton_guardar(self, parent):
        """Crea el botón de guardar"""
        btn_guardar = tk.Button(
            parent, 
            text="Registrar Ingreso Completo", 
            font=("Arial", 11, "bold"),
            bg="#e67e22", 
            fg="white", 
            activebackground="#d35400", 
            activeforeground="white",
            bd=0, 
            cursor="hand2",
            command=self._guardar_registro
        )
        btn_guardar.grid(row=7, column=0, columnspan=4, pady=30, ipadx=25, ipady=6)
    
    def _obtener_datos(self):
        """Obtiene y limpia los datos del formulario"""
        datos = {}
        for key, entry in self.entries.items():
            valor = entry.get().strip()
            if key == 'placa':
                valor = valor.upper()
            datos[key] = valor
        return datos
    
    def _validar_campos(self, datos):
        """Valida que los campos requeridos no estén vacíos"""
        vacios = [campo for campo in self.CAMPOS_REQUERIDOS if not datos.get(campo)]
        
        if vacios:
            campos_faltantes = ", ".join(vacios)
            messagebox.showwarning(
                "Campos vacíos", 
                f"Por favor, llene los siguientes campos obligatorios:\n{campos_faltantes}\n\n(El correo es opcional)"
            )
            return False
        return True
    
    def _limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
    
    def _guardar_registro(self):
        """Guarda el registro en la base de datos"""
        # Obtener datos
        datos = self._obtener_datos()
        
        # Validar
        if not self._validar_campos(datos):
            return
        
        # Enviar a BD
        exito, mensaje = insertar_cliente(
            datos['cedula'], datos['nombre'], datos['telefono'], 
            datos['email'], datos['marca'], datos['modelo'], datos['placa']
        )
        
        # Mostrar resultado
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self._limpiar_campos()
        else:
            messagebox.showerror("Error", mensaje)

# Función de compatibilidad con código existente
def mostrar_formulario_cliente(contenedor):
    """Función principal para mostrar el formulario"""
    return FormularioRegistro(contenedor)