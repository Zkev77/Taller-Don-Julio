import hashlib
import tkinter as tk
import customtkinter
from interfaz import MenuTaller  

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.geometry('350x300')
root.title("Acceso al Sistema")
root.resizable(False, False)

def validar_login():
    usuario = entry1.get()
    clave = entry2.get()

    if not usuario or not clave:
        print("Por favor, llene todos los campos")
        return

    CLAVE_FIJA = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"

    clave_hash = hashlib.sha256(clave.encode()).hexdigest()

    if usuario == "admin" and clave_hash == CLAVE_FIJA:
        root.destroy()  
        
        root_menu = tk.Tk()
        app = MenuTaller(root_menu)
        root_menu.mainloop()
    else:
        print("Usuario o contraseña incorrectos")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

label = customtkinter.CTkLabel(master=frame, text='Taller Don Julio', font=('Arial', 18, 'bold'))
label.pack(pady=12, padx=10)

# Aquí es donde se definen entry1 y entry2 para que la función los pueda leer
entry1 = customtkinter.CTkEntry(master=frame, placeholder_text='Username')
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text='Password', show='*')
entry2.pack(pady=12, padx=10)

button = customtkinter.CTkButton(master=frame, text='Iniciar Sesión', command=validar_login)
button.pack(pady=12, padx=10)

root.mainloop()