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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

    root = ctk.CTk()
    root.title("Taller Don Julio - Acceso")

    root.report_callback_exception = lambda tipo, valor, tb: alertar_error(tipo, valor, tb)
    sys.excepthook = lambda tipo, valor, tb: alertar_error(tipo, valor, tb)

    root.after(80, maximizar_ventana, root)
    root.minsize(1024, 700)

    frame_login = ctk.CTkFrame(
        root, 
        width=650, 
        height=720, 
        corner_radius=30, 
        fg_color=("white", FONDO_TARJETA)
    )
    frame_login.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.60, relheight=0.85)

    img_llave = ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "llave_inglesa.png")), size=(175, 175))
    ctk.CTkLabel(
        frame_login, 
        text="",          
        image=img_llave
    ).pack(pady=(2, 2))

    ctk.CTkLabel(
        frame_login, 
        text="Sistema de Gestión Operativa", 
        font=("Inter", 17), 
        text_color=("gray40", TEXTO_GRIS)
    ).pack(pady=(0, 35))  

    def limpiar_error(e=None):
        label_error.configure(text="")

    ctk.CTkLabel(frame_login, text="👤 Usuario", font=("Inter", 18, "bold"), anchor="w").pack(fill="x", padx=85, pady=(0, 8))
    entry1 = ctk.CTkEntry(frame_login, placeholder_text="Ingrese su usuario", height=58, font=("Inter", 16))
    entry1.pack(fill="x", padx=85, pady=(0, 25))
    entry1.bind("<Key-Return>", lambda e: entry2.focus())
    entry1.bind("<Key>", limpiar_error)

    ctk.CTkLabel(frame_login, text="🔒 Contraseña", font=("Inter", 18, "bold"), anchor="w").pack(fill="x", padx=85, pady=(0, 8))
    entry2 = ctk.CTkEntry(frame_login, placeholder_text="Ingrese su contraseña", height=58, show="*", font=("Inter", 16))
    entry2.pack(fill="x", padx=85, pady=(0, 15))
    entry2.bind("<Key>", limpiar_error)

    def toggle_password_check():
        entry2.configure(show="" if check_var.get() == 1 else "*")

    check_var = ctk.IntVar(value=0)
    check_pass = ctk.CTkCheckBox(
        frame_login, 
        text="Mostrar contraseña", 
        variable=check_var, 
        command=toggle_password_check,
        font=("Inter", 15),
        checkbox_width=22,
        checkbox_height=22,
        border_width=2,
        fg_color=COLOR_ACENTO,
        hover_color=COLOR_ACENTO_OSCURO
    )
    check_pass.pack(anchor="w", padx=85, pady=(0, 25))

    label_error = ctk.CTkLabel(frame_login, text="", font=("Inter", 15, "bold"), text_color="#ff4444", wraplength=500)
    label_error.pack(pady=(0, 15))

    def validar_login():
        usuario = entry1.get().strip()
        clave = entry2.get().strip()

        if not usuario or not clave:
            label_error.configure(text="⚠️ Por favor, complete todos los campos")
            return

        db = Database()
        exito, mensaje, rol = db.verify_user(usuario, clave)

        if exito:
            for widget in root.winfo_children():
                widget.destroy()
            MenuTaller(root, rol, usuario)
        else:
            label_error.configure(text=f"❌ {mensaje}")
            entry2.delete(0, tk.END)
            entry2.focus()

    button = ctk.CTkButton(
        frame_login,
        text="Iniciar Sesión",
        height=62,
        font=("Inter", 18, "bold"),
        corner_radius=14,
        fg_color=COLOR_ACENTO,
        hover_color=COLOR_ACENTO_OSCURO,
        command=validar_login
    )
    button.pack(fill="x", padx=85, pady=(0, 35))

    entry2.bind("<Key-Return>", lambda e: validar_login())
    entry1.focus()

    root.mainloop()

if __name__ == "__main__":
    main()