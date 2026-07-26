import tkinter as tk
import customtkinter
from database import Database
from interfaz import MenuTaller

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.geometry('800x600')
root.title("Acceso al Sistema")
root.resizable(False, False)

def validar_login():
    usuario = entry1.get().strip()
    clave = entry2.get().strip()

    if not usuario or not clave:
        label_error.configure(text="Por favor, llene todos los campos")
        return

    db = Database()
    exito, mensaje, rol = db.verify_user(usuario, clave)

    if exito:
        root.destroy()   
        root_menu = tk.Tk()
        app = MenuTaller(root_menu, rol)   
        root_menu.mainloop()
    else:
        label_error.configure(text=mensaje)

def pasar_a_clave(event):
    entry2.focus()

def ejecutar_login(event):
    validar_login()

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

label = customtkinter.CTkLabel(master=frame, text='Taller Mecanico Don Julio', font=('Arial', 18, 'bold'))
label.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text='Usuario')
entry1.pack(pady=12, padx=10)
entry1.bind('<Key-Return>', pasar_a_clave)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text='Contraseña', show='*')
entry2.pack(pady=12, padx=10)
entry2.bind('<Key-Return>', ejecutar_login)

label_error = customtkinter.CTkLabel(master=frame, text="", font=('Arial', 10), text_color="red")
label_error.pack(pady=5)

button = customtkinter.CTkButton(master=frame, text='Iniciar Sesión', command=validar_login)
button.pack(pady=12, padx=10)

root.mainloop()