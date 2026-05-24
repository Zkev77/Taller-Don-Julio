import customtkinter
from interfaz import MenuTaller  
import tkinter as tk  

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.geometry('350x300')
root.title("Acceso al Sistema")
root.resizable(False, False)

def login():
    usuario_correcto = "admin"
    clave_correcta = "1234"

    if entry1.get() == usuario_correcto and entry2.get() == clave_correcta:
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

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text='Username')
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text='Password', show='*')
entry2.pack(pady=12, padx=10)

button = customtkinter.CTkButton(master=frame, text='Iniciar Sesión', command=login)
button.pack(pady=12, padx=10)

root.mainloop()