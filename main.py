import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sys
import socket
import threading
import time
import requests
import json
import hashlib
import hmac
from datetime import datetime
from PIL import Image, ImageTk
import io
import base64
import subprocess
import psutil

class PhotoboothApp:
    def __init__(self):
        # Tripay configuration - Using PHP Forwarder for localhost compatibility
        self.USE_PHP_FORWARDER = True
        self.PHP_FORWARDER_CONFIG = {
            "baseUrl": "https://forwarder.snapbooth.click/tripay-forwarder.php",
            "apiKey": "KnSJAP2881392SQIisuQ"
        }
        
        # Production credentials (matching Next.js config)
        self.TRIPAY_API_KEY = "aNe8LAdn2lRfj4lrkfFkTz3vqzJJ8k646ccQyOLg"
        self.TRIPAY_PRIVATE_KEY = "GmsLp-OwNlg-XG9Zp-0Plas-zw5lo"
        self.TRIPAY_MERCHANT_CODE = "T44241"
        self.TRIPAY_BASE_URL = self.PHP_FORWARDER_CONFIG["baseUrl"] if self.USE_PHP_FORWARDER else "https://tripay.co.id/api"
        
        # UI state
        self.current_view = "main"  # Track current view: "main" or "qris"
        self.transaction_data = None
        self.payment_status_thread = None
        
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
            pady=10
        )
        title_label.pack(pady=(30, 0))
        
        # Subtitle label
        subtitle_label = tk.Label(
            wrapper_frame,
            text="Pilih metode untuk masuk:",
            font=('Arial', 16),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        subtitle_label.pack(pady=(5, 20))
        
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
        
        # Network status indicator box (outside the wrapper_frame)
        self.network_status_frame = tk.Frame(main_frame, bg='#FFFFFF')
        self.network_status_frame.pack(pady=(20, 0))
        
        self.network_status_box = tk.Label(
            self.network_status_frame,
            text="Checking...",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#FFA500',  # Orange for initial checking state
            width=15,
            height=1,
            relief='raised',
            bd=2
        )
        self.network_status_box.pack()
        
        # Start network monitoring
        self.start_network_monitoring()
        
    def qris_login(self):
        """Replace main form with QRIS payment form"""
        print("QRIS login selected - Creating payment form")
        self.current_view = "qris"
        
        # Clear the main frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create new QRIS payment form
        self.create_qris_payment_form()
    
    def create_qris_payment_form(self):
        """Create the QRIS payment form interface"""
        # Create main container frame
        main_frame = tk.Frame(self.root, bg='#FFFFFF')
        main_frame.pack(expand=True, fill='both')
        
        # Create wrapper frame for the QRIS payment
        wrapper_frame = tk.Frame(main_frame, bg='#A5DBEB', relief='raised', bd=3)
        wrapper_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title label
        title_label = tk.Label(
            wrapper_frame,
            text="Tagihan QRIS 30.000",
            font=('Arial', 20, 'bold'),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        title_label.pack(pady=(30, 0))
        
        # Status label
        self.qris_status_label = tk.Label(
            wrapper_frame,
            text="Membuat transaksi...",
            font=('Arial', 14),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        self.qris_status_label.pack(pady=(5, 10))
        
        # QR Code container
        self.qr_frame = tk.Frame(wrapper_frame, bg='#FFFFFF', relief='solid', bd=2)
        self.qr_frame.pack(pady=20, padx=40)
        
        # QR Code placeholder
        self.qr_label = tk.Label(
            self.qr_frame,
            text="Memuat QR Code...",
            font=('Arial', 12),
            fg='#666666',
            bg='#FFFFFF',
            width=30,
            height=15
        )
        self.qr_label.pack(padx=20, pady=20)
        
        # Payment instructions
        instructions_label = tk.Label(
            wrapper_frame,
            text="Support semua Bank Indonesia",
            font=('Arial', 12),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        instructions_label.pack(pady=10)
        
        # Back button
        back_button = tk.Button(
            wrapper_frame,
            text="Kembali",
            font=('Arial', 14, 'bold'),
            fg='#FFFFFF',
            bg='#DC3545',
            activebackground='#C82333',
            activeforeground='#FFFFFF',
            relief='flat',
            padx=30,
            pady=10,
            command=self.back_to_main
        )
        back_button.pack(pady=(20, 30))
        
        # Start creating Tripay transaction
        threading.Thread(target=self.create_tripay_transaction, daemon=True).start()
    
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
    
    def check_internet_connection(self):
        """Check if internet connection is available"""
        try:
            # Try to connect to Google's DNS server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            try:
                # Fallback: try to connect to Cloudflare DNS
                socket.create_connection(("1.1.1.1", 53), timeout=3)
                return True
            except OSError:
                return False
    
    def update_network_status(self):
        """Update the network status indicator"""
        if self.check_internet_connection():
            # Online - Green background, "Ready" text
            self.network_status_box.config(
                text="Ready",
                bg='#28a745',  # Green
                fg='white'
            )
        else:
            # Offline - Red background, "Offline" text
            self.network_status_box.config(
                text="Offline",
                bg='#dc3545',  # Red
                fg='white'
            )
    
    def network_monitor_thread(self):
        """Background thread to continuously monitor network status"""
        while True:
            try:
                self.update_network_status()
                time.sleep(2)  # Check every 2 seconds
            except:
                # If there's an error, continue monitoring
                time.sleep(5)
    
    def start_network_monitoring(self):
        """Start the network monitoring in a separate thread"""
        monitor_thread = threading.Thread(target=self.network_monitor_thread, daemon=True)
        monitor_thread.start()
        
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

    def generate_signature(self, payload):
        """Generate HMAC signature for Tripay API"""
        return hmac.new(
            self.TRIPAY_PRIVATE_KEY.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def generate_merchant_ref(self):
        """Generate unique merchant reference"""
        timestamp = int(datetime.now().timestamp())
        return f"PHOTOBOOTH-{timestamp}"
    
    def create_tripay_transaction(self):
        """Create QRIS transaction with Tripay API using PHP forwarder"""
        try:
            # Update status
            self.root.after(0, lambda: self.qris_status_label.config(text="Membuat transaksi QRIS..."))
            
            # Generate merchant reference (matching Next.js logic)
            timestamp = int(datetime.now().timestamp())
            import random
            import string
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            merchant_ref = f"SNAPBOOTH-{timestamp}-{random_str}"
            
            # Prepare transaction data for PHP forwarder
            payload_data = {
                "amount": 1000,
                "customerDetails": {
                    "first_name": "Customer Photobooth",
                    "email": "customer@photobooth.com",
                    "phone": "081234567890"
                },
                "merchantRef": merchant_ref,
                "method": "QRIS"
            }
            
            if self.USE_PHP_FORWARDER:
                # Use PHP forwarder (matching Next.js implementation)
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.PHP_FORWARDER_CONFIG["apiKey"],
                    "Accept": "application/json"
                }
                
                # Make request to PHP forwarder
                response = requests.post(
                    f"{self.TRIPAY_BASE_URL}?action=create-transaction",
                    headers=headers,
                    json=payload_data,
                    timeout=30
                )
            else:
                # Direct API call (fallback)
                payload_string = json.dumps(payload_data, separators=(',', ':'))
                signature = self.generate_signature(payload_string)
                
                headers = {
                    "Authorization": f"Bearer {self.TRIPAY_API_KEY}",
                    "Content-Type": "application/json",
                    "X-Signature": signature
                }
                
                response = requests.post(
                    f"{self.TRIPAY_BASE_URL}/transaction/create",
                    headers=headers,
                    json=payload_data,
                    timeout=30
                )
            
            print(f"Response Status: {response.status_code}")
            response_text = response.text
            print(f"Raw Response: {response_text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Parsed Response: {json.dumps(result, indent=2)}")
                
                if result.get('success'):
                    self.transaction_data = result['data']
                    self.root.after(0, self.display_qr_code)
                else:
                    error_msg = result.get('message', 'Unknown error')
                    self.root.after(0, lambda: self.show_error(f"Gagal membuat transaksi: {error_msg}"))
            else:
                self.root.after(0, lambda: self.show_error(f"HTTP Error: {response.status_code}"))
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            self.root.after(0, lambda: self.show_network_error())
        except Exception as e:
            print(f"Error: {e}")
            self.root.after(0, lambda: self.show_error(f"Error: {str(e)}"))
    
    def display_qr_code(self):
        """Display the QR code from transaction data"""
        try:
            if not self.transaction_data:
                self.show_error("QR Code tidak tersedia")
                return
            
            # Update status
            self.qris_status_label.config(text="Scan QR untuk bayar")
            
            # Get QR code URL from transaction data
            qr_url = self.transaction_data.get('qr_url')
            if not qr_url:
                self.show_error("QR Code URL tidak tersedia")
                return
            
            # Download QR code image from URL
            response = requests.get(qr_url, timeout=10)
            if response.status_code == 200:
                # Load QR code image
                qr_image = Image.open(io.BytesIO(response.content))
                
                # Resize QR code for display
                qr_image = qr_image.resize((250, 250), Image.Resampling.LANCZOS)
                qr_photo = ImageTk.PhotoImage(qr_image)
                
                # Update QR label
                self.qr_label.config(
                    image=qr_photo,
                    text="",
                    width=250,
                    height=250
                )
                self.qr_label.image = qr_photo  # Keep a reference
                
                # Start payment status monitoring
                threading.Thread(target=self.monitor_payment_status, daemon=True).start()
            else:
                self.show_error("Gagal mengunduh QR Code")
            
        except Exception as e:
            print(f"QR Code display error: {e}")
            self.show_error(f"Error displaying QR code: {str(e)}")
    
    def monitor_payment_status(self):
        """Monitor payment status using PHP forwarder"""
        self.monitoring = True
        
        def check_status():
            while self.monitoring and self.transaction_data:
                try:
                    reference = self.transaction_data.get('reference')
                    if not reference:
                        break
                    
                    if self.USE_PHP_FORWARDER:
                        # Use PHP forwarder for status check
                        headers = {
                            "Content-Type": "application/json",
                            "X-API-Key": self.PHP_FORWARDER_CONFIG["apiKey"],
                            "Accept": "application/json"
                        }
                        
                        response = requests.get(
                            f"{self.TRIPAY_BASE_URL}?action=check-status&reference={reference}",
                            headers=headers,
                            timeout=10
                        )
                    else:
                        # Direct API call (fallback)
                        headers = {
                            "Authorization": f"Bearer {self.TRIPAY_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        response = requests.get(
                            f"{self.TRIPAY_BASE_URL}/transaction/detail?reference={reference}",
                            headers=headers,
                            timeout=10
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            status = result['data'].get('status')
                            if status == 'PAID':
                                self.root.after(0, self.payment_success)
                                break
                            elif status in ['EXPIRED', 'FAILED', 'CANCELLED']:
                                self.root.after(0, lambda: self.show_error(f"Pembayaran {status.lower()}"))
                                break
                    
                except requests.exceptions.RequestException:
                    # Network error during monitoring - return to main
                    self.root.after(0, self.show_network_error)
                    break
                except Exception as e:
                    print(f"Status check error: {e}")
                    break
                
                time.sleep(5)
        
        # Start monitoring in separate thread
        import threading
        status_thread = threading.Thread(target=check_status, daemon=True)
        status_thread.start()
    
    def show_network_error(self):
        """Handle network error - return to main form"""
        self.qris_status_label.config(text="Koneksi terputus. Kembali ke menu utama...")
        self.root.after(2000, self.back_to_main)  # Return to main after 2 seconds
    
    def payment_success(self):
        """Handle successful payment - show new form with 'Mulai Foto' button"""
        # Stop monitoring thread
        if hasattr(self, 'monitoring') and self.monitoring:
            self.monitoring = False
        
        # Clear all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create new payment success form
        self.create_photo_start_form()
    
    def create_photo_start_form(self):
        """Create form with centered 'Mulai Foto' button"""
        # Create main container frame
        main_frame = tk.Frame(self.root, bg='#FFFFFF')
        main_frame.pack(expand=True, fill='both')
        
        # Create wrapper frame for the success message and button
        wrapper_frame = tk.Frame(main_frame, bg='#A5DBEB', relief='raised', bd=3)
        wrapper_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Success message
        success_label = tk.Label(
            wrapper_frame,
            text="✅ Pembayaran Berhasil!",
            font=('Arial', 24, 'bold'),
            fg='#28a745',
            bg='#A5DBEB'
        )
        success_label.pack(pady=(30, 20))
        
        # Instructions
        instruction_label = tk.Label(
            wrapper_frame,
            text="Silakan mulai sesi foto Anda",
            font=('Arial', 16),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        instruction_label.pack(pady=(0, 30))
        
        # Mulai Foto button (centered)
        start_photo_button = tk.Button(
            wrapper_frame,
            text="Mulai Foto",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#28a745',
            activebackground='#218838',
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=50,
            pady=20,
            cursor='hand2',
            command=self.start_photo_session
        )
        start_photo_button.pack(pady=(0, 40))
    
    def is_dslr_booth_running(self):
        """Check if dslrBooth.exe is running"""
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] and 'dslrBooth.exe' in process.info['name']:
                    return True
            return False
        except Exception as e:
            print(f"Error checking dslrBooth process: {e}")
            return False
    
    def start_photo_session(self):
        """Start the photo session with dslrBooth integration"""
        # First check if dslrBooth.exe is running
        if not self.is_dslr_booth_running():
            messagebox.showerror(
                "Aplikasi Photobooth Tidak Aktif",
                "Harap jalankan aplikasi dslrBooth.exe terlebih dahulu sebelum memulai sesi foto."
            )
            return
        
        # Call the API to start photo session
        try:
            response = requests.get(
                "http://localhost:1500/api/start?mode=print&password=JVKDAWKr1SnmWqHv",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("IsSuccessful"):
                    # Success - hide main window and show countdown
                    self.root.withdraw()  # Hide main window
                    self.show_countdown_window()
                    # Reset to main form for when countdown ends
                    self.current_view = "main"
                else:
                    # API returned error
                    error_msg = result.get("ErrorMessage", "Unknown error")
                    if "not on the start screen" in error_msg:
                        messagebox.showerror(
                            "Aplikasi Photobooth Tidak Siap",
                            "Harap minta tolong staff untuk memeriksa Aplikasi Photobooth sudah di dalam Event atau sudah terjalankan sebelumnya"
                        )
                    else:
                        messagebox.showerror("Error", f"Gagal memulai sesi foto: {error_msg}")
            else:
                messagebox.showerror("Error", f"Gagal terhubung ke aplikasi photobooth (HTTP {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                "Koneksi Gagal",
                "Tidak dapat terhubung ke aplikasi photobooth. Pastikan aplikasi dslrBooth.exe sudah berjalan."
            )
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "Koneksi ke aplikasi photobooth timeout.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    def show_countdown_window(self):
        """Show countdown window for 8 minutes"""
        # Create countdown window
        self.countdown_window = tk.Toplevel()
        self.countdown_window.title("Sesi Foto Aktif")
        self.countdown_window.geometry("400x200")
        self.countdown_window.configure(bg='#A5DBEB')
        self.countdown_window.resizable(False, False)
        
        # Make window stay on top and center it
        self.countdown_window.attributes('-topmost', True)
        self.countdown_window.transient(self.root)
        
        # Center the window at top of screen
        self.countdown_window.update_idletasks()
        screen_width = self.countdown_window.winfo_screenwidth()
        x = (screen_width // 2) - (400 // 2)
        y = 50  # Position at top of screen
        self.countdown_window.geometry(f"400x200+{x}+{y}")
        
        # Prevent window from being moved or closed
        self.countdown_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.countdown_window.overrideredirect(True)
        
        # Countdown label
        self.countdown_label = tk.Label(
            self.countdown_window,
            text="Sesi Foto Aktif",
            font=('Arial', 16, 'bold'),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        self.countdown_label.pack(pady=20)
        
        # Time remaining label
        self.time_label = tk.Label(
            self.countdown_window,
            text="08:00",
            font=('Arial', 24, 'bold'),
            fg='#DC3545',
            bg='#A5DBEB'
        )
        self.time_label.pack(pady=10)
        
        # Status label
        status_label = tk.Label(
            self.countdown_window,
            text="Silakan ikuti instruksi di aplikasi photobooth",
            font=('Arial', 12),
            fg='#0A3766',
            bg='#A5DBEB'
        )
        status_label.pack(pady=10)
        
        # Start countdown (8 minutes = 480 seconds)
        self.countdown_seconds = 480
        self.update_countdown()
    
    def update_countdown(self):
        """Update countdown timer"""
        if self.countdown_seconds > 0:
            # Calculate minutes and seconds
            minutes = self.countdown_seconds // 60
            seconds = self.countdown_seconds % 60
            
            # Update display
            time_text = f"{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=time_text)
            
            # Decrease counter
            self.countdown_seconds -= 1
            
            # Schedule next update
            self.root.after(1000, self.update_countdown)
        else:
            # Countdown finished - close countdown window and show main window
            self.countdown_window.destroy()
            self.root.deiconify()  # Show main window again
            self.back_to_main()  # Reset to main form

    def show_error(self, message):
        """Show error message and return to main form"""
        self.qris_status_label.config(text=f"❌ {message}", fg='#dc3545')
        print(f"Error: {message}")
        # Auto return to main after 3 seconds on error
        self.root.after(3000, self.back_to_main)
    
    def back_to_main(self):
        """Return to main form with all buttons"""
        """Return to main form with all buttons"""
        print("Back to main called - starting cleanup...")
        
        # Stop any monitoring
        if hasattr(self, 'monitoring'):
            self.monitoring = False
            print("Stopped monitoring")
        
        # Clear transaction data
        self.transaction_data = None
        self.current_view = "main"
        print("Cleared transaction data")
        
        # Clear all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        print("Cleared all widgets")
        
        # Reset any state variables
        self.additional_options_visible = False
        print("Reset state variables")
        
        # Only recreate widgets, don't setup window again
        self.create_widgets()
        print("Recreated main form widgets")
        
        # Force update the display
        self.root.update()
        print("Updated display - main form should be visible now")

if __name__ == "__main__":
    app = PhotoboothApp()
    app.run()