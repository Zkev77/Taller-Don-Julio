import tkinter as tk
import customtkinter
from database import Database
from interfaz import MenuTaller

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.geometry('350x300')
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

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

label = customtkinter.CTkLabel(master=frame, text='Taller Don Julio', font=('Arial', 18, 'bold'))
label.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text='Username')
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text='Password', show='*')
entry2.pack(pady=12, padx=10)

label_error = customtkinter.CTkLabel(master=frame, text="", font=('Arial', 10), text_color="red")
label_error.pack(pady=5)

button = customtkinter.CTkButton(master=frame, text='Iniciar Sesión', command=validar_login)
button.pack(pady=12, padx=10)

root.mainloop()