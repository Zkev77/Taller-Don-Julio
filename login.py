import tkinter as tk
import customtkinter as ctk
import os
import sys
import traceback
import datetime
from database import Database
from interfaz import MenuTaller
from colores_app import *
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def registrar_error(tipo, valor, tb):
    mensaje = "".join(traceback.format_exception(tipo, valor, tb))
    try:
        with open(os.path.join(BASE_DIR, "error.log"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now():%d/%m/%Y %H:%M:%S}]\n{mensaje}\n")
    except Exception:
        pass
    return mensaje

def alertar_error(tipo, valor, tb):
    mensaje = registrar_error(tipo, valor, tb)
    try:
        tk.messagebox.showerror("Error inesperado", f"{tipo.__name__}: {valor}\n\nSe guardaron los detalles en error.log")
    except Exception:
        pass

def maximizar_ventana(ventana):
    if sys.platform == "linux":
        try:
            ventana.attributes('-zoomed', True)
            return
        except Exception:
            pass
    try:
        ventana.state('zoomed')
    except Exception:
        pass

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    raiz = ctk.CTk()
    raiz.title("Taller Don Julio - Acceso")

    raiz.report_callback_exception = lambda tipo, valor, tb: alertar_error(tipo, valor, tb)
    sys.excepthook = lambda tipo, valor, tb: alertar_error(tipo, valor, tb)

    raiz.after(80, maximizar_ventana, raiz)
    raiz.minsize(1024, 700)

    marco_login = ctk.CTkFrame(
        raiz, 
        width=650, 
        height=720, 
        corner_radius=30, 
        fg_color=("white", FONDO_TARJETA)
    )
    marco_login.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.60, relheight=0.85)

    imagen_llave = ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "llave_inglesa.png")), size=(175, 175))
    ctk.CTkLabel(
        marco_login, 
        text="",          
        image=imagen_llave
    ).pack(pady=(2, 2))

    ctk.CTkLabel(
        marco_login, 
        text="Sistema de Gestión Operativa", 
        font=("Inter", 17), 
        text_color=("gray40", TEXTO_GRIS)
    ).pack(pady=(0, 35))  

    def limpiar_error(e=None):
        etiqueta_error.configure(text="")

    ctk.CTkLabel(marco_login, text="👤 Usuario", font=("Inter", 18, "bold"), anchor="w").pack(fill="x", padx=85, pady=(0, 8))
    campo1 = ctk.CTkEntry(marco_login, placeholder_text="Ingrese su usuario", height=58, font=("Inter", 16))
    campo1.pack(fill="x", padx=85, pady=(0, 25))
    campo1.bind("<Key-Return>", lambda e: campo2.focus())
    campo1.bind("<Key>", limpiar_error)

    ctk.CTkLabel(marco_login, text="🔒 Contraseña", font=("Inter", 18, "bold"), anchor="w").pack(fill="x", padx=85, pady=(0, 8))
    campo2 = ctk.CTkEntry(marco_login, placeholder_text="Ingrese su contraseña", height=58, show="*", font=("Inter", 16))
    campo2.pack(fill="x", padx=85, pady=(0, 15))
    campo2.bind("<Key>", limpiar_error)

    def alternar_verificacion_contrasena():
        campo2.configure(show="" if var_verificacion.get() == 1 else "*")

    var_verificacion = ctk.IntVar(value=0)
    verificacion_contrasena = ctk.CTkCheckBox(
        marco_login, 
        text="Mostrar contraseña", 
        variable=var_verificacion, 
        command=alternar_verificacion_contrasena,
        font=("Inter", 15),
        checkbox_width=22,
        checkbox_height=22,
        border_width=2,
        fg_color=COLOR_ACENTO,
        hover_color=COLOR_ACENTO_OSCURO
    )
    verificacion_contrasena.pack(anchor="w", padx=85, pady=(0, 25))

    etiqueta_error = ctk.CTkLabel(marco_login, text="", font=("Inter", 15, "bold"), text_color="#ff4444", wraplength=500)
    etiqueta_error.pack(pady=(0, 15))

    def validar_login():
        usuario = campo1.get().strip()
        clave = campo2.get().strip()

        if not usuario or not clave:
            etiqueta_error.configure(text="⚠️ Por favor, complete todos los campos")
            return

        bd = Database()
        exito, mensaje, rol = bd.verificar_usuario(usuario, clave)

        if exito:
            for widget in raiz.winfo_children():
                widget.destroy()
            MenuTaller(raiz, rol, usuario)
        else:
            etiqueta_error.configure(text=f"❌ {mensaje}")
            campo2.delete(0, tk.END)
            campo2.focus()

    boton = ctk.CTkButton(
        marco_login,
        text="Iniciar Sesión",
        height=62,
        font=("Inter", 18, "bold"),
        corner_radius=14,
        fg_color=COLOR_ACENTO,
        hover_color=COLOR_ACENTO_OSCURO,
        command=validar_login
    )
    boton.pack(fill="x", padx=85, pady=(0, 35))

    campo2.bind("<Key-Return>", lambda e: validar_login())
    campo1.focus()

    raiz.mainloop()

if __name__ == "__main__":
    main()