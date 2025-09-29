import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sys

class PhotoboothApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        # Set window title
        self.root.title("Photobooth")
        
        # Make window fullscreen
        self.root.attributes('-fullscreen', True)
        
        # Disable window controls (minimize, maximize, close)
        self.root.overrideredirect(True)
        
        # Set background color
        self.root.configure(bg='#FFFFFF')
        
        # Bind Alt+F2 key to exit with password
        self.root.bind('<Alt-F2>', self.show_password_dialog)
        
    def create_widgets(self):
        # Create main container frame
        main_frame = tk.Frame(self.root, bg='#FFFFFF')
        main_frame.pack(expand=True, fill='both')
        
        # Create wrapper frame for the options
        wrapper_frame = tk.Frame(main_frame, bg='#A5DBEB', relief='raised', bd=3)
        wrapper_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title label
        title_label = tk.Label(
            wrapper_frame,
            text="SELAMAT DATANG",
            font=('Arial', 24, 'bold'),
            fg='#0A3766',
            bg='#A5DBEB',
            pady=20
        )
        title_label.pack(pady=(30, 20))
        
        # Subtitle label
        subtitle_label = tk.Label(
            wrapper_frame,
            text="Pilih metode untuk masuk:",
            font=('Arial', 16),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Button frame
        button_frame = tk.Frame(wrapper_frame, bg='#A5DBEB')
        button_frame.pack(pady=(0, 30), padx=40)
        
        # QRIS Button
        qris_button = tk.Button(
            button_frame,
            text="Masuk Pakai QRIS",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#0A3766',
            activebackground='#0A3766',
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.qris_login
        )
        qris_button.pack(pady=10, fill='x')
        
        # Card Button
        card_button = tk.Button(
            button_frame,
            text="Masuk Pakai Kartu",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#0A6641',
            activebackground='#0A6641',
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.card_login
        )
        card_button.pack(pady=10, fill='x')
        
    def qris_login(self):
        print("QRIS login selected")
        # Add your QRIS login logic here
        
    def card_login(self):
        print("Card login selected")
        # Add your card login logic here
        
    def show_password_dialog(self, event=None):
        # Create a custom password dialog
        password_window = tk.Toplevel(self.root)
        password_window.title("Master Password")
        password_window.geometry("300x150")
        password_window.configure(bg='#A5DBEB')
        password_window.resizable(False, False)
        
        # Center the dialog
        password_window.transient(self.root)
        password_window.grab_set()
        
        # Center the window on screen
        password_window.update_idletasks()
        x = (password_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (password_window.winfo_screenheight() // 2) - (150 // 2)
        password_window.geometry(f"300x150+{x}+{y}")
        
        # Password label
        label = tk.Label(
            password_window,
            text="Masukkan kata sandi master:",
            font=('Arial', 12),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        label.pack(pady=20)
        
        # Password entry
        password_entry = tk.Entry(
            password_window,
            font=('Arial', 12),
            show='*',
            width=20,
            justify='center'
        )
        password_entry.pack(pady=10)
        password_entry.focus()
        
        # Button frame
        button_frame = tk.Frame(password_window, bg='#A5DBEB')
        button_frame.pack(pady=10)
        
        def check_password():
            entered_password = password_entry.get()
            if entered_password == "282828":
                password_window.destroy()
                self.exit_app()
            else:
                messagebox.showerror("Error", "Kata sandi salah!")
                password_entry.delete(0, tk.END)
                password_entry.focus()
        
        def cancel():
            password_window.destroy()
        
        # OK Button
        ok_button = tk.Button(
            button_frame,
            text="OK",
            font=('Arial', 10),
            fg='white',
            bg='#0A3766',
            command=check_password,
            padx=20
        )
        ok_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel Button
        cancel_button = tk.Button(
            button_frame,
            text="Batal",
            font=('Arial', 10),
            fg='white',
            bg='#0A6641',
            command=cancel,
            padx=20
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to check password
        password_entry.bind('<Return>', lambda e: check_password())
        password_window.bind('<Escape>', lambda e: cancel())
            
    def exit_app(self, event=None):
        self.root.quit()
        sys.exit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PhotoboothApp()
    app.run()