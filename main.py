import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, font
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
import os

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
        self.load_custom_font()
        self.setup_window()
        self.create_widgets()
        
    def load_custom_font(self):
        """Load Satoshi font from the Fonts directory"""
        try:
            # Get the path to the font file
            font_path = os.path.join(os.path.dirname(__file__), "Fonts", "TTF", "Satoshi-Variable.ttf")
            
            if os.path.exists(font_path):
                # Register the font with tkinter
                self.custom_font_family = "Satoshi"
                
                # Create font objects for different sizes and weights
                self.font_large = font.Font(family=self.custom_font_family, size=24, weight="bold")
                self.font_medium = font.Font(family=self.custom_font_family, size=16, weight="normal")
                self.font_small = font.Font(family=self.custom_font_family, size=12, weight="normal")
                self.font_button = font.Font(family=self.custom_font_family, size=14, weight="bold")
                
                print(f"Loaded custom font: {font_path}")
            else:
                print(f"Font file not found: {font_path}")
                # Fallback to system fonts
                self.custom_font_family = "Arial"
                self.font_large = font.Font(family="Arial", size=24, weight="bold")
                self.font_medium = font.Font(family="Arial", size=16, weight="normal")
                self.font_small = font.Font(family="Arial", size=12, weight="normal")
                self.font_button = font.Font(family="Arial", size=14, weight="bold")
                
        except Exception as e:
            print(f"Error loading custom font: {e}")
            # Fallback to system fonts
            self.custom_font_family = "Arial"
            self.font_large = font.Font(family="Arial", size=24, weight="bold")
            self.font_medium = font.Font(family="Arial", size=16, weight="normal")
            self.font_small = font.Font(family="Arial", size=12, weight="normal")
            self.font_button = font.Font(family="Arial", size=14, weight="bold")
        
    def setup_window(self):
        # Set window title
        self.root.title("Photobooth")
        
        # Make window fullscreen
        self.root.attributes('-fullscreen', True)
        
        # Disable window controls (minimize, maximize, close)
        self.root.overrideredirect(True)
        
        # Set background color to match the CSS design
        self.root.configure(bg='#e6f5ec')
        
        # Bind Alt+F2 key to exit with password
        self.root.bind('<Alt-F2>', self.show_password_dialog)
        
    def create_widgets(self):
        # Create main container frame with dotted pattern background
        main_frame = tk.Frame(self.root, bg='#e6f5ec')
        main_frame.pack(expand=True, fill='both')
        
        # Create a canvas for the dotted pattern background
        self.bg_canvas = tk.Canvas(main_frame, bg='#e6f5ec', highlightthickness=0)
        self.bg_canvas.pack(expand=True, fill='both')
        
        # Draw the dotted pattern
        self.draw_dotted_pattern()
        
        # Create wrapper frame for the options on top of canvas with light green background
        wrapper_frame = tk.Frame(self.bg_canvas, bg='#e6f5ec', relief='flat', bd=0)
        
        # Store wrapper frame reference for better management
        self.wrapper_frame = wrapper_frame
        
        self.wrapper_window = self.bg_canvas.create_window(
            self.bg_canvas.winfo_reqwidth() // 2,
            self.bg_canvas.winfo_reqheight() // 2,
            window=wrapper_frame,
            anchor='center'
        )
        
        # Bind canvas resize to redraw pattern and reposition wrapper
        self.bg_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Button frame with matching background
        button_frame = tk.Frame(wrapper_frame, bg='#e6f5ec')
        button_frame.pack(pady=(30, 30), padx=40)
        
        # QRIS Button - using Label to eliminate all visual effects
        self.qris_button = tk.Label(
            button_frame,
            text="Masuk Pakai QRIS",
            font=self.font_button,
            fg='white',
            bg='#5AA47C',
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.qris_button.bind("<Button-1>", lambda e: self.qris_login())
        self.qris_button.pack(pady=10, fill='x')
        
        # Card Button - using Label to eliminate all visual effects
        self.card_button = tk.Label(
            button_frame,
            text="Masuk Pakai Kartu",
            font=self.font_button,
            fg='white',
            bg='#FF8C42',
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.card_button.bind("<Button-1>", lambda e: self.card_login())
        self.card_button.pack(pady=10, fill='x')
        
        # Create overlay with main-img.png on main form
        self.create_main_overlay(self.bg_canvas)
        
        # Start network monitoring (for button state management only)
        self.start_network_monitoring()
    
    def create_main_overlay(self, canvas):
        """Create overlay with main-img.png for main welcome form"""
        def _create_overlay_after_render():
            """Create overlay after canvas is fully rendered"""
            try:
                # Load the overlay image
                img_path = os.path.join(os.path.dirname(__file__), "main-img.png")
                if os.path.exists(img_path):
                    # Load and resize image
                    pil_image = Image.open(img_path)
                    
                    # Convert to RGB for better performance (no transparency needed)
                    if pil_image.mode == 'RGBA':
                        # Create white background and paste image
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode == 'RGBA' else None)
                        pil_image = background
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # Get actual canvas dimensions after rendering
                    canvas.update_idletasks()  # Force update to get real dimensions
                    canvas_width = canvas.winfo_width()
                    canvas_height = canvas.winfo_height()
                    
                    # Use screen dimensions as fallback
                    if canvas_width <= 1:
                        canvas_width = self.root.winfo_screenwidth()
                    if canvas_height <= 1:
                        canvas_height = self.root.winfo_screenheight()
                    
                    # Calculate size (make it cover most of the screen) - optimized sizing
                    max_width = int(canvas_width * 0.7)  # Reduced from 0.8 for better performance
                    max_height = int(canvas_height * 0.7)
                    
                    # Use faster resampling for better performance
                    pil_image.thumbnail((max_width, max_height), Image.Resampling.BILINEAR)
                    self.main_overlay_image = ImageTk.PhotoImage(pil_image)
                    
                    # Create overlay label directly on canvas (no frame background)
                    image_label = tk.Label(
                        canvas,
                        image=self.main_overlay_image,
                        cursor='hand2',
                        bd=0,
                        highlightthickness=0,
                        bg=canvas['bg']  # Match canvas background
                    )
                    
                    # Bind click event to hide overlay
                    def hide_main_overlay(event=None):
                        if hasattr(self, 'main_overlay_window'):
                            canvas.delete(self.main_overlay_window)
                            delattr(self, 'main_overlay_window')
                            # Clear image reference for memory cleanup
                            if hasattr(self, 'main_overlay_image'):
                                delattr(self, 'main_overlay_image')
                    
                    image_label.bind('<Button-1>', hide_main_overlay)
                    
                    # Create window for overlay at center
                    self.main_overlay_window = canvas.create_window(
                        canvas_width // 2,
                        canvas_height // 2,
                        window=image_label,
                        anchor='center'
                    )
                    
                    # Force overlay to highest z-index
                    canvas.tag_raise(self.main_overlay_window)
                    
                    # Ensure wrapper frame stays below overlay
                    if hasattr(self, 'wrapper_window'):
                        canvas.tag_lower(self.wrapper_window, self.main_overlay_window)
                    
                    # Store canvas reference for later use
                    self.overlay_canvas = canvas
                    
                else:
                    print(f"Overlay image not found: {img_path}")
                    
            except Exception as e:
                print(f"Error creating main overlay: {e}")
        
        # Reduced delay for faster loading on all PCs
        canvas.after(50, _create_overlay_after_render)
    
    def draw_dotted_pattern_on_canvas(self, canvas):
        """Draw the dotted pattern background on a specific canvas"""
        canvas.delete("dots")  # Clear existing dots
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # If canvas not yet rendered, use default size
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        # Pattern settings (matching CSS: 30px 30px spacing)
        dot_spacing = 30
        dot_radius = 6  # 20% of 30px spacing
        dot_color = '#f3fbf6'
        
        # Draw dots in a grid pattern
        for x in range(0, canvas_width + dot_spacing, dot_spacing):
            for y in range(0, canvas_height + dot_spacing, dot_spacing):
                canvas.create_oval(
                    x - dot_radius, y - dot_radius,
                    x + dot_radius, y + dot_radius,
                    fill=dot_color, outline=dot_color, tags="dots"
                )
    
    def draw_dotted_pattern(self):
        """Draw the dotted pattern background similar to CSS radial-gradient"""
        self.draw_dotted_pattern_on_canvas(self.bg_canvas)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize events"""
        # Redraw the dotted pattern
        self.draw_dotted_pattern()
        
        # Get canvas dimensions
        canvas_width = event.width
        canvas_height = event.height
        
        # Update wrapper frame position using stored reference
        if hasattr(self, 'wrapper_window'):
            try:
                self.bg_canvas.coords(self.wrapper_window, canvas_width // 2, canvas_height // 2)
            except:
                pass
        
        # Also recenter overlay if it exists and ensure it stays on top
        if hasattr(self, 'main_overlay_window'):
            try:
                self.bg_canvas.coords(self.main_overlay_window, canvas_width//2, canvas_height//2)
                # Force overlay to stay on top after repositioning
                self.bg_canvas.tag_raise(self.main_overlay_window)
                # Ensure wrapper stays below overlay
                if hasattr(self, 'wrapper_window'):
                    self.bg_canvas.tag_lower(self.wrapper_window, self.main_overlay_window)
            except:
                # If overlay window is invalid, remove the reference
                if hasattr(self, 'main_overlay_window'):
                    delattr(self, 'main_overlay_window')
        
    def qris_login(self):
        """Replace main form with QRIS payment form"""
        # Check if buttons are disabled (offline)
        if hasattr(self, 'qris_button') and self.qris_button['state'] == 'disabled':
            return  # Don't proceed if offline
        
        print("QRIS login selected - Creating payment form")
        self.current_view = "qris"
        
        # Clear the main frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create new QRIS payment form
        self.create_qris_payment_form()
    
    def create_qris_payment_form(self):
        """Create the QRIS payment form interface"""
        # Create main container frame with dotted pattern background
        main_frame = tk.Frame(self.root, bg='#e6f5ec')
        main_frame.pack(expand=True, fill='both')
        
        # Create a canvas for the dotted pattern background
        bg_canvas = tk.Canvas(main_frame, bg='#e6f5ec', highlightthickness=0)
        bg_canvas.pack(expand=True, fill='both')
        
        # Draw the dotted pattern
        self.draw_dotted_pattern_on_canvas(bg_canvas)
        
        # Create wrapper frame for the QRIS payment on top of canvas
        wrapper_frame = tk.Frame(bg_canvas, bg='#A5DBEB', relief='flat', bd=0)
        self.qris_wrapper_window = bg_canvas.create_window(
            0, 0,  # Will be repositioned by configure event
            window=wrapper_frame,
            anchor='center'
        )
        
        # Bind canvas resize to redraw pattern and recenter wrapper
        def on_qris_canvas_configure(event):
            self.draw_dotted_pattern_on_canvas(bg_canvas)
            # Recenter the wrapper frame
            canvas_width = event.width
            canvas_height = event.height
            bg_canvas.coords(self.qris_wrapper_window, canvas_width//2, canvas_height//2)
        
        bg_canvas.bind('<Configure>', on_qris_canvas_configure)
        
        # Title label
        title_label = tk.Label(
            wrapper_frame,
            text="Tagihan QRIS 30.000",
            font=self.font_large,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        title_label.pack(pady=(30, 0))
        
        # Status label
        self.qris_status_label = tk.Label(
            wrapper_frame,
            text="Membuat transaksi...",
            font=self.font_medium,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        self.qris_status_label.pack(pady=(5, 10))
        
        # QR Code container
        self.qr_frame = tk.Frame(wrapper_frame, bg='#FFFFFF', relief='flat', bd=0)
        self.qr_frame.pack(pady=20, padx=40)
        
        # QR Code placeholder
        self.qr_label = tk.Label(
            self.qr_frame,
            text="Memuat QR Code...",
            font=self.font_small,
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
            font=self.font_small,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        instructions_label.pack(pady=10)
        
        # Back button
        back_button = tk.Button(
            wrapper_frame,
            text="Kembali",
            font=self.font_button,
            fg='#FFFFFF',
            bg='#DC3545',
            activebackground='#DC3545',
            activeforeground='#FFFFFF',
            disabledforeground='#FFFFFF',
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            command=self.back_to_main,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        back_button.pack(pady=(20, 30))
        
        # Start creating Tripay transaction
        threading.Thread(target=self.create_tripay_transaction, daemon=True).start()
    
    def card_login(self):
        """Replace main form with card login form"""
        # Check if buttons are disabled (offline)
        if hasattr(self, 'card_button') and self.card_button['state'] == 'disabled':
            return  # Don't proceed if offline
        
        print("Card login selected - Creating card form")
        self.current_view = "card"
        
        # Clear the main frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create new card login form
        self.create_card_login_form()
    
    def create_card_login_form(self):
        """Create the card login form interface"""
        # Initialize auto-submit timer
        self.auto_submit_timer = None
        self.is_processing = False
        
        # Create main container frame with dotted pattern background
        main_frame = tk.Frame(self.root, bg='#e6f5ec')
        main_frame.pack(expand=True, fill='both')
        
        # Create a canvas for the dotted pattern background
        bg_canvas = tk.Canvas(main_frame, bg='#e6f5ec', highlightthickness=0)
        bg_canvas.pack(expand=True, fill='both')
        
        # Draw the dotted pattern
        self.draw_dotted_pattern_on_canvas(bg_canvas)
        
        # Create wrapper frame for the card login on top of canvas
        wrapper_frame = tk.Frame(bg_canvas, bg='#A5DBEB', relief='flat', bd=0)
        self.card_wrapper_window = bg_canvas.create_window(
            0, 0,  # Will be repositioned by configure event
            window=wrapper_frame,
            anchor='center'
        )
        
        # Bind canvas resize to redraw pattern and recenter wrapper
        def on_card_canvas_configure(event):
            self.draw_dotted_pattern_on_canvas(bg_canvas)
            # Recenter the wrapper frame
            canvas_width = event.width
            canvas_height = event.height
            bg_canvas.coords(self.card_wrapper_window, canvas_width//2, canvas_height//2)
        
        bg_canvas.bind('<Configure>', on_card_canvas_configure)
        
        # Title label
        title_label = tk.Label(
            wrapper_frame,
            text="Masuk Dengan Kartu",
            font=self.font_large,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        title_label.pack(pady=(30, 0))
        
        # Status label for feedback
        self.card_status_label = tk.Label(
            wrapper_frame,
            text="Masukkan kode kartu Anda:",
            font=self.font_medium,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        self.card_status_label.pack(pady=(5, 20))
        
        # Card input container
        input_frame = tk.Frame(wrapper_frame, bg='#FFFFFF', relief='flat', bd=0)
        input_frame.pack(pady=20, padx=40)
        
        # Card input field
        self.card_input = tk.Entry(
            input_frame,
            font=self.font_medium,
            fg='#0A3766',
            bg='#FFFFFF',
            width=25,
            justify='center',
            relief='flat',
            bd=0,
            show='*',
            highlightthickness=0
        )
        self.card_input.pack(padx=20, pady=20)
        self.card_input.focus_set()  # Auto-focus on the input field
        
        # Bind events for auto-submit functionality
        self.card_input.bind('<KeyRelease>', self.on_card_input_change)
        self.card_input.bind('<Return>', self.process_card_input)
        
        # Instructions
        instructions_label = tk.Label(
            wrapper_frame,
            text="Ketik kode kartu atau tap kartu NFC",
            font=self.font_small,
            fg='#0A3766',
            bg='#A5DBEB'
        )
        instructions_label.pack(pady=10)
        
        # Back button (same style as QRIS form)
        back_button = tk.Button(
            wrapper_frame,
            text="Kembali",
            font=self.font_button,
            fg='#FFFFFF',
            bg='#DC3545',
            activebackground='#DC3545',
            activeforeground='#FFFFFF',
            disabledforeground='#FFFFFF',
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            command=self.back_to_main,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        back_button.pack(pady=(20, 30))
    
    def on_card_input_change(self, event=None):
        """Handle card input changes and set auto-submit timer"""
        if self.is_processing:
            return
            
        # Cancel existing timer
        if self.auto_submit_timer:
            self.root.after_cancel(self.auto_submit_timer)
        
        # Get current input
        card_code = self.card_input.get().strip()
        
        # Only set timer if there's input
        if card_code:
            # Set new timer for 2 seconds
            self.auto_submit_timer = self.root.after(2000, self.auto_submit_card)
    
    def auto_submit_card(self):
        """Auto-submit card verification after 2 seconds of inactivity"""
        if not self.is_processing:
            self.process_card_input()
    
    def process_card_input(self, event=None):
        """Process the card input when Enter is pressed or auto-submitted"""
        if self.is_processing:
            return
            
        card_code = self.card_input.get().strip()
        if not card_code:
            self.card_status_label.config(text="Silakan masukkan kode kartu terlebih dahulu", fg='#DC3545')
            return
        
        # Check internet connection first
        if not self.check_internet_connection():
            self.card_status_label.config(text="Tidak ada koneksi internet", fg='#DC3545')
            # Return to main form after 2 seconds
            self.root.after(2000, self.back_to_main)
            return
        
        # Set processing state
        self.is_processing = True
        self.card_status_label.config(text="Memverifikasi kartu...", fg='#0A3766')
        
        # Clear input immediately after validation
        self.card_input.delete(0, tk.END)
        self.card_input.config(state='disabled')
        
        # Cancel any pending auto-submit timer
        if self.auto_submit_timer:
            self.root.after_cancel(self.auto_submit_timer)
        
        # Start verification in background thread
        threading.Thread(target=self.verify_nfc_card, args=(card_code,), daemon=True).start()
    
    def verify_nfc_card(self, card_code):
        """Verify NFC card with the API"""
        try:
            # Prepare API request
            api_url = "https://card.snapbooth.click/api/nfc-verify"
            payload = {
                "haimanis": "LobanGPrMO928UhhhLewaTTT",
                "kamucantikbanged": card_code
            }
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            result = response.json()
            
            # Update UI in main thread
            self.root.after(0, self.handle_nfc_verification_response, response.status_code, result)
            
        except requests.exceptions.Timeout:
            self.root.after(0, self.handle_nfc_verification_error, "Timeout - koneksi terlalu lambat")
        except requests.exceptions.ConnectionError:
            self.root.after(0, self.handle_nfc_verification_error, "Tidak dapat terhubung ke server")
        except Exception as e:
            self.root.after(0, self.handle_nfc_verification_error, f"Error: {str(e)}")
    
    def handle_nfc_verification_response(self, status_code, result):
        """Handle NFC verification API response"""
        self.is_processing = False
        
        if status_code == 200 and result.get('success'):
            # Success - show success message briefly then go to photo start form
            self.card_status_label.config(text="Kartu berhasil diverifikasi!", fg='#28a745')
            # Clear all widgets and show photo start form after 1 second
            self.root.after(1000, self.show_photo_start_after_card_success)
        else:
            # Handle different error cases
            self.card_input.config(state='normal')
            error_message = result.get('message', 'Terjadi kesalahan')
            error_code = result.get('error_code', '')
            
            if status_code == 404 or error_code == 'NFC_UID_NOT_FOUND':
                self.card_status_label.config(text="UID kartu NFC tidak ditemukan", fg='#DC3545')
            elif status_code == 400 or error_code == 'NFC_CARD_DISABLED':
                self.card_status_label.config(text="Kartu NFC tidak aktif", fg='#DC3545')
            elif status_code == 401 or error_code == 'INVALID_HAI_MANIS':
                self.card_status_label.config(text="Autentikasi tidak valid", fg='#DC3545')
            elif status_code == 500 or error_code == 'INTERNAL_SERVER_ERROR':
                self.card_status_label.config(text="Terjadi kesalahan server", fg='#DC3545')
            else:
                self.card_status_label.config(text=error_message, fg='#DC3545')
            
            # Clear input and reset after 3 seconds
            self.root.after(3000, self.reset_card_form)
    
    def show_photo_start_after_card_success(self):
        """Clear card form and show photo start form"""
        # Clear all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create photo start form
        self.create_photo_start_form()
    
    def handle_nfc_verification_error(self, error_message):
        """Handle NFC verification errors"""
        self.is_processing = False
        self.card_input.config(state='normal')
        self.card_status_label.config(text=error_message, fg='#DC3545')
        
        # Return to main form after 3 seconds if it's a connection error
        if "terhubung" in error_message.lower() or "timeout" in error_message.lower():
            self.root.after(3000, self.back_to_main)
        else:
            self.root.after(3000, self.reset_card_form)
    
    def reset_card_form(self):
        """Reset the card form to initial state"""
        if hasattr(self, 'card_input') and self.card_input.winfo_exists():
            self.card_input.delete(0, tk.END)
            self.card_input.focus_set()
            self.card_status_label.config(text="Masukkan kode kartu Anda:", fg='#0A3766')
            self.is_processing = False
        
    def admin_login(self):
        print("Admin login selected")
        # Add your admin login logic here
    
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
        """Update button states based on network connectivity"""
        if self.check_internet_connection():
            # Enable buttons when online
            self.enable_main_buttons()
        else:
            # Disable buttons when offline
            self.disable_main_buttons()
    
    def enable_main_buttons(self):
        """Enable QRIS and Card buttons when online"""
        if hasattr(self, 'qris_button') and self.qris_button.winfo_exists():
            self.qris_button.config(
                bg='#5AA47C',
                cursor='hand2'
            )
            # Re-bind click event
            self.qris_button.bind("<Button-1>", lambda e: self.qris_login())
        if hasattr(self, 'card_button') and self.card_button.winfo_exists():
            self.card_button.config(
                bg='#FF8C42',
                cursor='hand2'
            )
            # Re-bind click event
            self.card_button.bind("<Button-1>", lambda e: self.card_login())
    
    def disable_main_buttons(self):
        """Disable QRIS and Card buttons when offline"""
        if hasattr(self, 'qris_button') and self.qris_button.winfo_exists():
            self.qris_button.config(
                bg='#666666',
                cursor='arrow'
            )
            # Unbind click event
            self.qris_button.unbind("<Button-1>")
        if hasattr(self, 'card_button') and self.card_button.winfo_exists():
            self.card_button.config(
                bg='#666666',
                cursor='arrow'
            )
            # Unbind click event
            self.card_button.unbind("<Button-1>")
    
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
            font=self.font_button,
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
            font=self.font_button,
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
                font=self.font_large,
                fg='white',
                bg='#0A3766',
                activebackground='#0A3766',
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
                font=self.font_large,
                fg='white',
                bg='#0A3766',
                activebackground='#0A3766',
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
                font=self.font_large,
                fg='white',
                bg='#0A3766',
                activebackground='#0A3766',
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
            font=self.font_button,
            fg='white',
            bg='#e74c3c',
            activebackground='#e74c3c',
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
            font=self.font_large,
            fg='white',
            bg='#0A3766',
            activebackground='#0A3766',
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
            font=self.font_button,
            fg='white',
            bg='#f39c12',
            activebackground='#f39c12',
            activeforeground='white',
            disabledforeground='white',
            width=5,
            height=2,
            relief='flat',
            bd=0,
            command=backspace,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        back_btn.pack(side=tk.LEFT, padx=5)
        
        def check_password():
            if self.entered_password == "282828":
                password_window.destroy()
                self.exit_app()
            else:
                self.show_custom_error("Error", "Kata sandi salah!")
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
                self.show_error("Gagal mendownload QR Code")
            
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
        
        # Create wrapper frame for the button only
        wrapper_frame = tk.Frame(main_frame, bg='#A5DBEB', relief='flat', bd=0)
        wrapper_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Mulai Foto button (centered)
        start_photo_button = tk.Button(
            wrapper_frame,
            text="Mulai Foto",
            font=self.font_large,
            fg='white',
            bg='#28a745',
            activebackground='#28a745',
            activeforeground='white',
            disabledforeground='white',
            relief='flat',
            bd=0,
            padx=50,
            pady=20,
            cursor='hand2',
            command=self.start_photo_session,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        start_photo_button.pack(padx=40, pady=40)
    
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
    
    def bring_dslr_booth_to_front(self):
        """Bring dslrBooth.exe window to front"""
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] and 'dslrBooth.exe' in process.info['name']:
                    # Use Windows API to bring window to front
                    import ctypes
                    from ctypes import wintypes
                    
                    # Get window handle
                    def enum_windows_proc(hwnd, lParam):
                        if ctypes.windll.user32.IsWindowVisible(hwnd):
                            pid = wintypes.DWORD()
                            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                            if pid.value == process.info['pid']:
                                # Bring window to front
                                ctypes.windll.user32.SetForegroundWindow(hwnd)
                                ctypes.windll.user32.BringWindowToTop(hwnd)
                                return False  # Stop enumeration
                        return True
                    
                    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                    ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
                    break
        except Exception as e:
            print(f"Error bringing dslrBooth to front: {e}")

    def start_photo_session(self):
        """Start the photo session with dslrBooth integration"""
        # First check if dslrBooth.exe is running
        if not self.is_dslr_booth_running():
            self.show_custom_error(
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
                    # Success - bring dslrBooth to front first
                    self.bring_dslr_booth_to_front()
                    
                    # Small delay to ensure dslrBooth is in front
                    self.root.after(500, self._hide_and_show_countdown)
                    
                    # Reset to main form for when countdown ends
                    self.current_view = "main"
                else:
                    # API returned error
                    error_msg = result.get("ErrorMessage", "Unknown error")
                    if "not on the start screen" in error_msg:
                        self.show_custom_error(
                            "Aplikasi Photobooth Tidak Siap",
                            "Harap minta tolong staff untuk memeriksa Aplikasi Photobooth sudah di dalam Event atau sudah terjalankan sebelumnya"
                        )
                    else:
                        self.show_custom_error("Error", f"Gagal memulai sesi foto: {error_msg}")
            else:
                self.show_custom_error("Error", f"Gagal terhubung ke aplikasi photobooth (HTTP {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            self.show_custom_error(
                "Koneksi Gagal",
                "Tidak dapat terhubung ke aplikasi photobooth. Pastikan aplikasi dslrBooth.exe sudah berjalan."
            )
        except requests.exceptions.Timeout:
            self.show_custom_error("Timeout", "Koneksi ke aplikasi photobooth timeout.")
        except Exception as e:
            self.show_custom_error("Error", f"Terjadi kesalahan: {str(e)}")
    
    def _hide_and_show_countdown(self):
        """Helper method to hide main window and show countdown"""
        # Hide main window
        self.root.withdraw()
        # Show countdown window
        self.show_countdown_window()
    
    def show_countdown_window(self):
        """Show countdown window for 8 minutes"""
        print("Creating countdown window...")
        
        # Create countdown window
        self.countdown_window = tk.Toplevel(self.root)
        
        # Make window completely transparent and frameless
        self.countdown_window.overrideredirect(True)
        self.countdown_window.attributes('-transparentcolor', 'black')
        self.countdown_window.configure(bg='black')
        
        # Set window size to full screen width but small height
        screen_width = self.countdown_window.winfo_screenwidth()
        window_width = screen_width
        window_height = 60
        
        # Position window at top of screen, full width
        x = 0
        y = 20  # Position at top of screen
        self.countdown_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window stay on top
        self.countdown_window.attributes('-topmost', True)
        self.countdown_window.resizable(False, False)
        
        # Create a container that will be centered in the full-width window
        container = tk.Frame(self.countdown_window, bg='black')
        container.pack(fill='both', expand=True)
        
        # Create the actual content frame that will be centered
        content_frame = tk.Frame(container, bg='black')
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Countdown time with white background - SOLID WHITE
        time_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=2, highlightbackground='white', highlightthickness=0)
        time_frame.pack(side='left', padx=(0, 3))
        
        self.time_label = tk.Label(
            time_frame,
            text="08:00",
            font=self.font_medium,
            fg='black',
            bg='white'
        )
        self.time_label.pack(padx=15, pady=8)
        
        # End session button - SAME HEIGHT AS COUNTDOWN
        end_session_button = tk.Button(
            content_frame,
            text="KELUAR",
            font=self.font_button,
            fg='white',
            bg='#DC3545',
            activebackground='#DC3545',
            activeforeground='white',
            disabledforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=7,
            cursor='hand2',
            command=self.confirm_end_session,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        end_session_button.pack(side='left')
        
        # Force window to appear and update
        self.countdown_window.update()
        self.countdown_window.lift()
        self.countdown_window.attributes('-topmost', True)
        
        print("Countdown window created and should be visible")
        
        # Start countdown (8 minutes = 480 seconds)
        self.countdown_seconds = 480
        self.update_countdown()
    
    def confirm_end_session(self):
        """Show confirmation dialog for ending session"""
        # Create confirmation dialog
        confirm_window = tk.Toplevel(self.countdown_window)
        confirm_window.title("Konfirmasi Akhiri Sesi")
        confirm_window.geometry("450x200")
        confirm_window.configure(bg='#A5DBEB')
        confirm_window.resizable(False, False)
        
        # Center the dialog on screen
        confirm_window.update_idletasks()
        x = (confirm_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (confirm_window.winfo_screenheight() // 2) - (200 // 2)
        confirm_window.geometry(f"450x200+{x}+{y}")
        
        # Make dialog modal and on top
        confirm_window.transient(self.countdown_window)
        confirm_window.grab_set()
        confirm_window.attributes('-topmost', True)
        
        # Warning message
        warning_label = tk.Label(
            confirm_window,
            text="Sesi anda akan berakhir ketika melanjutkan ini,\nharap pastikan anda selesai berfoto dan menyimpan hasilnya",
            font=self.font_small,
            fg='#0A3766',
            bg='#A5DBEB',
            justify='center'
        )
        warning_label.pack(pady=30)
        
        # Button frame
        button_frame = tk.Frame(confirm_window, bg='#A5DBEB')
        button_frame.pack(pady=20)
        
        # Yes button
        yes_button = tk.Button(
            button_frame,
            text="Iya",
            font=self.font_button,
            fg='white',
            bg='#DC3545',
            activebackground='#DC3545',
            activeforeground='white',
            disabledforeground='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.end_session_confirmed(confirm_window),
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        yes_button.pack(side='left', padx=10)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Batal",
            font=self.font_button,
            fg='white',
            bg='#6C757D',
            activebackground='#6C757D',
            activeforeground='white',
            disabledforeground='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=confirm_window.destroy,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        cancel_button.pack(side='left', padx=10)
    
    def end_session_confirmed(self, confirm_window):
        """Handle confirmed session termination"""
        # Close confirmation dialog
        confirm_window.destroy()
        
        # End the countdown and return to main window (same logic as countdown completion)
        if hasattr(self, 'countdown_window') and self.countdown_window.winfo_exists():
            self.countdown_window.destroy()
        
        # Show main window again
        self.root.deiconify()
        
        # Make main window topmost
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Reset to main form
        self.back_to_main()

    def update_countdown(self):
        """Update countdown timer"""
        if hasattr(self, 'countdown_window') and self.countdown_window.winfo_exists():
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
                
                # Make main window topmost
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after(100, lambda: self.root.attributes('-topmost', False))  # Remove topmost after brief moment
                
                self.back_to_main()  # Reset to main form

    def show_custom_error(self, title, message):
        """Show custom error dialog with modern styling"""
        # Create error dialog window
        error_window = tk.Toplevel(self.root)
        error_window.title(title)
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        error_window.configure(bg='#FFFFFF')
        error_window.transient(self.root)
        error_window.grab_set()
        
        # Center the window
        error_window.geometry("+{}+{}".format(
            int(error_window.winfo_screenwidth()/2 - 200),
            int(error_window.winfo_screenheight()/2 - 100)
        ))
        
        # Main container
        main_frame = tk.Frame(error_window, bg='#FFFFFF', relief='flat', bd=0)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text=title,
            font=self.font_medium,
            fg='#DC3545',
            bg='#FFFFFF'
        )
        title_label.pack(pady=(0, 10))
        
        # Message label
        message_label = tk.Label(
            main_frame,
            text=message,
            font=self.font_small,
            fg='#0A3766',
            bg='#FFFFFF',
            wraplength=350,
            justify='center'
        )
        message_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = tk.Button(
            main_frame,
            text="OK",
            font=self.font_small,
            fg='#FFFFFF',
            bg='#DC3545',
            activebackground='#DC3545',
            activeforeground='#FFFFFF',
            disabledforeground='#FFFFFF',
            relief='flat',
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2',
            command=error_window.destroy,
            highlightthickness=0,
            borderwidth=0,
            overrelief='flat'
        )
        ok_button.pack()
        
        # Focus on OK button and bind Enter key
        ok_button.focus_set()
        error_window.bind('<Return>', lambda e: error_window.destroy())
        error_window.bind('<Escape>', lambda e: error_window.destroy())
        
        # Wait for window to close
        error_window.wait_window()

    def show_error(self, message):
        """Show error message and return to main form"""
        self.qris_status_label.config(text=f"❌ {message}", fg='#dc3545')
        print(f"Error: {message}")
        # Auto return to main after 3 seconds on error
        self.root.after(3000, self.back_to_main)
    
    def back_to_main(self):
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
        
        # Clean up overlay references before destroying widgets
        if hasattr(self, 'main_overlay_window'):
            delattr(self, 'main_overlay_window')
        if hasattr(self, 'overlay_canvas'):
            delattr(self, 'overlay_canvas')
        if hasattr(self, 'main_overlay_image'):
            delattr(self, 'main_overlay_image')
        
        # Clear all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        print("Cleared all widgets")
        
        # Reset any state variables
        self.additional_options_visible = False
        print("Reset state variables")
        
        # Force garbage collection to clean up any lingering references
        import gc
        gc.collect()
        
        # Only recreate widgets, don't setup window again
        self.create_widgets()
        print("Recreated main form widgets")
        
        # Force update the display
        self.root.update()
        print("Updated display - main form should be visible now")

if __name__ == "__main__":
    app = PhotoboothApp()
    app.run()