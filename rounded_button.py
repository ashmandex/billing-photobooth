import tkinter as tk
from tkinter import Canvas

class RoundedButton(Canvas):
    def __init__(self, parent, text="", command=None, bg_color="#0A3766", fg_color="white", 
                 hover_color="#0A3766", font=("Arial", 18, "bold"), width=200, height=50, 
                 corner_radius=15, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.font = font
        self.corner_radius = corner_radius
        self.text = text
        self.width = width
        self.height = height
        
        # Configure canvas background to match parent
        self.configure(bg=parent.cget('bg'))
        
        # Draw the button
        self.draw_button()
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def draw_button(self, hover=False):
        self.delete("all")
        
        # Choose color based on hover state
        current_bg = self.hover_color if hover else self.bg_color
        
        # Draw rounded rectangle
        self.create_rounded_rectangle(
            2, 2, self.width-2, self.height-2, 
            self.corner_radius, fill=current_bg, outline=""
        )
        
        # Draw text
        self.create_text(
            self.width//2, self.height//2, 
            text=self.text, fill=self.fg_color, 
            font=self.font, anchor="center"
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        
        # Top side
        points.extend([x1 + radius, y1])
        points.extend([x2 - radius, y1])
        
        # Top right corner
        for i in range(0, 90, 5):
            angle = i * 3.14159 / 180
            px = x2 - radius + radius * (1 - tk.math.cos(angle))
            py = y1 + radius - radius * tk.math.sin(angle)
            points.extend([px, py])
        
        # Right side
        points.extend([x2, y1 + radius])
        points.extend([x2, y2 - radius])
        
        # Bottom right corner
        for i in range(90, 180, 5):
            angle = i * 3.14159 / 180
            px = x2 - radius + radius * (1 - tk.math.cos(angle))
            py = y2 - radius + radius * tk.math.sin(angle)
            points.extend([px, py])
        
        # Bottom side
        points.extend([x2 - radius, y2])
        points.extend([x1 + radius, y2])
        
        # Bottom left corner
        for i in range(180, 270, 5):
            angle = i * 3.14159 / 180
            px = x1 + radius + radius * (1 - tk.math.cos(angle))
            py = y2 - radius + radius * tk.math.sin(angle)
            points.extend([px, py])
        
        # Left side
        points.extend([x1, y2 - radius])
        points.extend([x1, y1 + radius])
        
        # Top left corner
        for i in range(270, 360, 5):
            angle = i * 3.14159 / 180
            px = x1 + radius + radius * (1 - tk.math.cos(angle))
            py = y1 + radius - radius * tk.math.sin(angle)
            points.extend([px, py])
        
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def on_enter(self, event):
        self.draw_button(hover=True)
        self.configure(cursor="hand2")
    
    def on_leave(self, event):
        self.draw_button(hover=False)
        self.configure(cursor="")

class RoundedFrame(Canvas):
    def __init__(self, parent, bg_color="#A5DBEB", width=400, height=300, 
                 corner_radius=20, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        
        # Configure canvas background to match parent
        self.configure(bg=parent.cget('bg'))
        
        # Draw the frame
        self.draw_frame()
        
    def draw_frame(self):
        self.delete("all")
        
        # Draw rounded rectangle
        self.create_rounded_rectangle(
            0, 0, self.width, self.height, 
            self.corner_radius, fill=self.bg_color, outline=""
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        
        # Simplified rounded rectangle using arcs
        return self.create_rectangle(x1, y1, x2, y2, **kwargs)