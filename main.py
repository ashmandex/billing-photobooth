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
        
        # Admin Button (initially hidden)
        self.admin_button = tk.Button(
            button_frame,
            text="Masuk Via Admin",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#1063C2',
            activebackground='#1063C2',
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.admin_login
        )
        
        # Exit Button (initially hidden)
        self.exit_button = tk.Button(
            button_frame,
            text="Keluar Aplikasi",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#C22121',
            activebackground='#C22121',
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.show_password_dialog
        )
        
        # Toggle button for additional options
        self.toggle_button = tk.Button(
            wrapper_frame,
            text="Tampilkan opsi lain",
            font=('Arial', 14),
            fg='#0A3766',
            bg='#A5DBEB',
            activebackground='#A5DBEB',
            activeforeground='#0A3766',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.toggle_additional_options
        )
        self.toggle_button.pack(pady=(10, 20))
        
        # Track visibility state
        self.additional_options_visible = False
        
    def qris_login(self):
        print("QRIS login selected")
        # Add your QRIS login logic here
        
    def card_login(self):
        print("Card login selected")
        # Add your card login logic here
        
    def admin_login(self):
        print("Admin login selected")
        # Add your admin login logic here
        
    def toggle_additional_options(self):
        if self.additional_options_visible:
            # Hide the buttons
            self.admin_button.pack_forget()
            self.exit_button.pack_forget()
            self.toggle_button.config(text="Tampilkan opsi lain")
            self.additional_options_visible = False
        else:
            # Show the buttons
            self.admin_button.pack(pady=10, fill='x')
            self.exit_button.pack(pady=10, fill='x')
            self.toggle_button.config(text="Sembunyikan opsi lain")
            self.additional_options_visible = True
        
    def show_password_dialog(self, event=None):
        # Create a custom password dialog with numeric keypad
        password_window = tk.Toplevel(self.root)
        password_window.title("Master Password")
        password_window.geometry("500x750")
        password_window.configure(bg='#A5DBEB')
        password_window.resizable(False, False)
        
        # Center the dialog
        password_window.transient(self.root)
        password_window.grab_set()
        
        # Center the window on screen
        password_window.update_idletasks()
        x = (password_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (password_window.winfo_screenheight() // 2) - (650 // 2)
        password_window.geometry(f"500x650+{x}+{y}")
        
        # Password label
        label = tk.Label(
            password_window,
            text="Masukkan kata sandi master:",
            font=('Arial', 14, 'bold'),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        label.pack(pady=20)
        
        # Password display (shows asterisks)
        self.password_var = tk.StringVar()
        self.entered_password = ""
        
        password_display = tk.Label(
            password_window,
            textvariable=self.password_var,
            font=('Arial', 18, 'bold'),
            fg='#0A3766',
            bg='white',
            width=15,
            height=2,
            relief='sunken',
            bd=2
        )
        password_display.pack(pady=10)
        
        # Keypad frame
        keypad_frame = tk.Frame(password_window, bg='#A5DBEB')
        keypad_frame.pack(pady=20)
        
        # Function to add number to password
        def add_number(num):
            if len(self.entered_password) < 6:  # Limit password length to 6 digits
                self.entered_password += str(num)
                self.password_var.set('*' * len(self.entered_password))
                # Auto-submit when 6 digits are entered
                if len(self.entered_password) == 6:
                    check_password()
        
        # Function to clear password
        def clear_password():
            self.entered_password = ""
            self.password_var.set("")
        
        # Function to backspace
        def backspace():
            if self.entered_password:
                self.entered_password = self.entered_password[:-1]
                self.password_var.set('*' * len(self.entered_password))
        
        # Create number buttons (1-9) in proper phone layout
        # Row 1: 1, 2, 3
        row1_frame = tk.Frame(keypad_frame, bg='#A5DBEB')
        row1_frame.pack(pady=5)
        for num in [1, 2, 3]:
            btn = tk.Button(
                row1_frame,
                text=str(num),
                font=('Arial', 20, 'bold'),
                fg='white',
                bg='#0A3766',
                activebackground='#2980b9',
                activeforeground='white',
                width=5,
                height=2,
                relief='raised',
                bd=3,
                command=lambda n=num: add_number(n)
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Row 2: 4, 5, 6
        row2_frame = tk.Frame(keypad_frame, bg='#A5DBEB')
        row2_frame.pack(pady=5)
        for num in [4, 5, 6]:
            btn = tk.Button(
                row2_frame,
                text=str(num),
                font=('Arial', 20, 'bold'),
                fg='white',
                bg='#0A3766',
                activebackground='#2980b9',
                activeforeground='white',
                width=5,
                height=2,
                relief='raised',
                bd=3,
                command=lambda n=num: add_number(n)
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Row 3: 7, 8, 9
        row3_frame = tk.Frame(keypad_frame, bg='#A5DBEB')
        row3_frame.pack(pady=5)
        for num in [7, 8, 9]:
            btn = tk.Button(
                row3_frame,
                text=str(num),
                font=('Arial', 20, 'bold'),
                fg='white',
                bg='#0A3766',
                activebackground='#2980b9',
                activeforeground='white',
                width=5,
                height=2,
                relief='raised',
                bd=3,
                command=lambda n=num: add_number(n)
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Row 4: Clear, 0, Backspace
        row4_frame = tk.Frame(keypad_frame, bg='#A5DBEB')
        row4_frame.pack(pady=5)
        
        # Clear button
        clear_btn = tk.Button(
            row4_frame,
            text="Clear",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#e74c3c',
            activebackground='#c0392b',
            activeforeground='white',
            width=5,
            height=2,
            relief='raised',
            bd=3,
            command=clear_password
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Zero button
        zero_btn = tk.Button(
            row4_frame,
            text="0",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#0A3766',
            activebackground='#2980b9',
            activeforeground='white',
            width=5,
            height=2,
            relief='raised',
            bd=3,
            command=lambda: add_number(0)
        )
        zero_btn.pack(side=tk.LEFT, padx=5)
        
        # Backspace button
        back_btn = tk.Button(
            row4_frame,
            text="Hapus",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#f39c12',
            activebackground='#e67e22',
            activeforeground='white',
            width=5,
            height=2,
            relief='raised',
            bd=3,
            command=backspace
        )
        back_btn.pack(side=tk.LEFT, padx=5)
        
        def check_password():
            if self.entered_password == "282828":
                password_window.destroy()
                self.exit_app()
            else:
                messagebox.showerror("Error", "Kata sandi salah!")
                clear_password()
        
        def cancel():
            password_window.destroy()
            
    def exit_app(self, event=None):
        self.root.quit()
        sys.exit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PhotoboothApp()
    app.run()