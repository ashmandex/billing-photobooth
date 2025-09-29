import tkinter as tk
from tkinter import ttk
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
        
        # Bind ESC key to exit (for development purposes)
        self.root.bind('<Escape>', self.exit_app)
        
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
        
        # Exit button (hidden, only accessible via right-click)
        self.root.bind('<Button-3>', self.show_exit_menu)
        
    def qris_login(self):
        print("QRIS login selected")
        # Add your QRIS login logic here
        
    def card_login(self):
        print("Card login selected")
        # Add your card login logic here
        
    def show_exit_menu(self, event):
        # Create context menu for exit option
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Exit Application", command=self.exit_app)
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def exit_app(self, event=None):
        self.root.quit()
        sys.exit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PhotoboothApp()
    app.run()