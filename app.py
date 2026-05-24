import tkinter as tk
from tkinter import messagebox
import database
import time
import math

# ==========================================
# MODERN THEME (DARK NEON SPACE)
# ==========================================
BG_COLOR = "#0F172A"       # Deep slate
CARD_COLOR = "#1E293B"     # Slightly lighter
PRIMARY = "#3B82F6"        # Vibrant Blue
PRIMARY_HOVER = "#60A5FA"
ACCENT = "#8B5CF6"         # Purple Accent
TEXT_MAIN = "#F8FAFC"
TEXT_DIM = "#94A3B8"
DANGER = "#EF4444"

# ==========================================
# ANIMATION ENGINE (60 FPS)
# ==========================================
class Animator:
    _animations = []
    _root = None

    @classmethod
    def init(cls, root):
        cls._root = root
        cls._tick()

    @classmethod
    def _tick(cls):
        now = time.time()
        active = []
        for anim in cls._animations:
            elapsed = now - anim['start']
            progress = min(1.0, elapsed / anim['duration'])
            
            # Easing: easeOutCubic
            eased = 1 - math.pow(1 - progress, 3)
            
            # Calculate current value
            current = anim['start_val'] + (anim['end_val'] - anim['start_val']) * eased
            
            # Callback
            anim['callback'](current)
            
            if progress < 1.0:
                active.append(anim)
            else:
                if 'on_complete' in anim and anim['on_complete']:
                    anim['on_complete']()
                    
        cls._animations = active
        cls._root.after(16, cls._tick) # ~60fps

    @classmethod
    def animate(cls, start_val, end_val, duration, callback, on_complete=None):
        cls._animations.append({
            'start_val': start_val,
            'end_val': end_val,
            'duration': duration,
            'start': time.time(),
            'callback': callback,
            'on_complete': on_complete
        })

# Helper to draw rounded rectangle on a canvas
def create_round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1,
        x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius,
        x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2,
        x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# ==========================================
# CUSTOM WIDGETS
# ==========================================
class AnimatedButton(tk.Canvas):
    def __init__(self, master, text, width, height, bg=PRIMARY, hover_bg=PRIMARY_HOVER, fg=TEXT_MAIN, command=None, radius=15):
        super().__init__(master, width=width, height=height, bg=BG_COLOR, highlightthickness=0, cursor="hand2")
        self.command = command
        self.base_bg = bg
        self.hover_bg = hover_bg
        self.rect_id = create_round_rectangle(self, 2, 2, width-2, height-2, radius=radius, fill=self.base_bg, outline="")
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg, font=("Segoe UI", 11, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, e):
        self.itemconfig(self.rect_id, fill=self.hover_bg)
        Animator.animate(2, 4, 0.2, lambda v: self.move(self.text_id, 0, v - float(self.coords(self.text_id)[1] - self.winfo_height()/2)))

    def on_leave(self, e):
        self.itemconfig(self.rect_id, fill=self.base_bg)
        Animator.animate(4, 2, 0.2, lambda v: self.move(self.text_id, 0, v - float(self.coords(self.text_id)[1] - self.winfo_height()/2)))

    def on_click(self, e):
        # "Bounce" effect
        self.move(self.text_id, 0, 2)
        
    def on_release(self, e):
        self.move(self.text_id, 0, -2)
        if self.command:
            self.command()

class FlightCard(tk.Canvas):
    def __init__(self, master, flight, width, on_book):
        super().__init__(master, width=width, height=100, bg=BG_COLOR, highlightthickness=0)
        self.flight = flight
        self.on_book = on_book
        self.rect = create_round_rectangle(self, 10, 10, width-10, 90, radius=20, fill=CARD_COLOR, outline="")
        
        # Details
        self.create_text(30, 35, text=flight.origin, fill=TEXT_MAIN, font=("Segoe UI", 16, "bold"), anchor="w")
        self.create_text(30, 65, text=f"Departs: {flight.departure_time}", fill=TEXT_DIM, font=("Segoe UI", 10), anchor="w")
        
        self.create_text(150, 35, text="➔", fill=ACCENT, font=("Segoe UI", 18, "bold"), anchor="w")
        self.create_text(210, 35, text=flight.destination, fill=TEXT_MAIN, font=("Segoe UI", 16, "bold"), anchor="w")
        self.create_text(210, 65, text=f"Seats: {flight.available_seats}/{flight.capacity}", fill=TEXT_DIM, font=("Segoe UI", 10), anchor="w")
        
        self.create_text(width - 160, 50, text=flight.formatted_price, fill=TEXT_MAIN, font=("Segoe UI", 16, "bold"), anchor="e")
        
        # Action
        self.btn = AnimatedButton(self, "Book", 100, 40, command=lambda: self.on_book(flight), radius=10)
        self.btn_window = self.create_window(width - 80, 50, window=self.btn)
        
        # Hover effect on card
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill="#273549"))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=CARD_COLOR))

class BookingCard(tk.Canvas):
    def __init__(self, master, booking_data, width, on_cancel):
        super().__init__(master, width=width, height=100, bg=BG_COLOR, highlightthickness=0)
        # booking_data: (Ref ID, Origin, Destination, Departure, Price, Status)
        self.booking_data = booking_data
        self.rect = create_round_rectangle(self, 10, 10, width-10, 90, radius=20, fill=CARD_COLOR, outline="")
        
        self.create_text(30, 30, text=f"Ref #{booking_data[0]}", fill=ACCENT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.create_text(30, 55, text=f"{booking_data[1]} ➔ {booking_data[2]}", fill=TEXT_MAIN, font=("Segoe UI", 14, "bold"), anchor="w")
        self.create_text(30, 75, text=booking_data[3], fill=TEXT_DIM, font=("Segoe UI", 10), anchor="w")
        
        # price
        self.create_text(width - 160, 50, text=f"${booking_data[4]:,.2f}", fill=TEXT_MAIN, font=("Segoe UI", 14, "bold"), anchor="e")
        
        # status
        color = PRIMARY if booking_data[5] == 'Confirmed' else DANGER
        self.create_text(width - 250, 50, text=booking_data[5], fill=color, font=("Segoe UI", 12, "bold"), anchor="e")
        
        if booking_data[5] == 'Confirmed':
            self.btn = AnimatedButton(self, "Cancel", 100, 40, bg=DANGER, hover_bg="#DC2626", command=lambda: on_cancel(booking_data[0]), radius=10)
            self.btn_window = self.create_window(width - 80, 50, window=self.btn)

# ==========================================
# MAIN APP
# ==========================================
class SkyReserveElite(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SkyReserve Elite - Animated Edition")
        self.geometry("1100x750")
        self.configure(bg=BG_COLOR)
        
        Animator.init(self)
        self.current_user = "Bola Hosny"
        
        # Custom Sidebar
        self.sidebar_w = 250
        self.sidebar = tk.Canvas(self, width=self.sidebar_w, height=750, bg=CARD_COLOR, highlightthickness=0)
        self.sidebar.place(x=0, y=0, relheight=1)
        
        self.sidebar.create_text(125, 60, text="✈ SkyReserve", fill=PRIMARY, font=("Segoe UI", 22, "bold"), justify="center")
        self.sidebar.create_text(125, 100, text="E  L  I  T  E", fill=ACCENT, font=("Segoe UI", 10, "bold"), justify="center")
        
        self.sidebar.create_text(125, 150, text=f"Welcome,\n{self.current_user}", fill=TEXT_DIM, font=("Segoe UI", 12), justify="center")
        
        # Sidebar Nav
        self.nav_indicator = create_round_rectangle(self.sidebar, 15, 200, 235, 250, radius=15, fill=PRIMARY, outline="")
        
        self.btn_s = self.sidebar.create_text(125, 225, text="🔍 Search Flights", fill=TEXT_MAIN, font=("Segoe UI", 12, "bold"))
        self.btn_b = self.sidebar.create_text(125, 285, text="🗂 My Bookings", fill=TEXT_DIM, font=("Segoe UI", 12, "bold"))
        
        self.sidebar.tag_bind(self.btn_s, "<Button-1>", lambda e: self.nav_to("search"))
        self.sidebar.tag_bind(self.btn_b, "<Button-1>", lambda e: self.nav_to("bookings"))
        
        # Main Content Area
        self.content = tk.Frame(self, bg=BG_COLOR)
        self.content.place(x=250, y=0, relwidth=1.0, width=-250, relheight=1)
        
        self.views = {}
        self.active_view = None
        self.setup_search_view()
        self.setup_bookings_view()
        
        self.nav_to("search", animate_indicator=False)

    def nav_to(self, view_name, animate_indicator=True):
        if self.active_view == view_name: return
        
        # Animate Indicator
        target_y = 200 if view_name == "search" else 260
        current_coords = self.sidebar.coords(self.nav_indicator)
        if current_coords and animate_indicator:
            start_y = current_coords[1] # y1
            Animator.animate(start_y, target_y, 0.3, lambda y: self.move_indicator(y))
            
            # Color transition
            if view_name == "search":
                self.sidebar.itemconfig(self.btn_s, fill=TEXT_MAIN)
                self.sidebar.itemconfig(self.btn_b, fill=TEXT_DIM)
            else:
                self.sidebar.itemconfig(self.btn_s, fill=TEXT_DIM)
                self.sidebar.itemconfig(self.btn_b, fill=TEXT_MAIN)
        else:
            self.move_indicator(target_y)
            
        # Animate Screen Slide
        if self.active_view:
            old_view = self.views[self.active_view]
            # Slide old view down
            Animator.animate(0, 800, 0.4, lambda y: old_view.place(y=y), on_complete=lambda: old_view.place_forget())
            
        self.active_view = view_name
        new_view = self.views[view_name]
        # Slide new view up
        new_view.place(x=0, y=800, relwidth=1, relheight=1)
        new_view.tkraise()
        Animator.animate(800, 0, 0.5, lambda y: new_view.place(y=y))
        
        # Reload data
        if view_name == "search":
            self.load_flights()
        elif view_name == "bookings":
            self.load_bookings()

    def move_indicator(self, y):
        # We need to recreate or move polygon. Recreating is easier for rounded rects in pure tk
        self.sidebar.delete(self.nav_indicator)
        self.nav_indicator = create_round_rectangle(self.sidebar, 15, y, 235, y+50, radius=15, fill=PRIMARY, outline="")
        self.sidebar.tag_lower(self.nav_indicator)

    def setup_search_view(self):
        v = tk.Frame(self.content, bg=BG_COLOR)
        self.views["search"] = v
        
        tk.Label(v, text="Find Your Next Journey", font=("Segoe UI", 28, "bold"), bg=BG_COLOR, fg=TEXT_MAIN).pack(pady=(40, 20), anchor="w", padx=50)
        
        # Search controls inside a Canvas
        sc = tk.Canvas(v, width=750, height=80, bg=BG_COLOR, highlightthickness=0)
        sc.pack(pady=10, padx=50, anchor="w")
        create_round_rectangle(sc, 0, 0, 750, 80, radius=20, fill=CARD_COLOR, outline="")
        
        sc.create_text(20, 40, text="Origin:", fill=TEXT_DIM, font=("Segoe UI", 12))
        self.ent_origin = tk.Entry(sc, bg=BG_COLOR, fg=TEXT_MAIN, font=("Segoe UI", 12), insertbackground=TEXT_MAIN, bd=0, highlightthickness=1, highlightbackground=CARD_COLOR, highlightcolor=PRIMARY)
        sc.create_window(150, 40, window=self.ent_origin, width=150)
        
        sc.create_text(350, 40, text="Destination:", fill=TEXT_DIM, font=("Segoe UI", 12))
        self.ent_dest = tk.Entry(sc, bg=BG_COLOR, fg=TEXT_MAIN, font=("Segoe UI", 12), insertbackground=TEXT_MAIN, bd=0, highlightthickness=1, highlightbackground=CARD_COLOR, highlightcolor=PRIMARY)
        sc.create_window(500, 40, window=self.ent_dest, width=150)
        
        btn = AnimatedButton(sc, "Search", 120, 40, command=self.load_flights, radius=10)
        sc.create_window(670, 40, window=btn)
        
        # Results area
        self.f_results = tk.Frame(v, bg=BG_COLOR)
        self.f_results.pack(fill="both", expand=True, padx=40, pady=20)

    def setup_bookings_view(self):
        v = tk.Frame(self.content, bg=BG_COLOR)
        self.views["bookings"] = v
        
        tk.Label(v, text="My Reservations", font=("Segoe UI", 28, "bold"), bg=BG_COLOR, fg=TEXT_MAIN).pack(pady=(40, 20), anchor="w", padx=50)
        
        self.b_results = tk.Frame(v, bg=BG_COLOR)
        self.b_results.pack(fill="both", expand=True, padx=40, pady=20)

    def load_flights(self):
        for w in self.f_results.winfo_children():
            w.destroy()
            
        ori = self.ent_origin.get().strip()
        dst = self.ent_dest.get().strip()
        flights = database.search_flights(ori, dst)
        
        # Staggered animation entrance
        for i, f in enumerate(flights):
            card = FlightCard(self.f_results, f, 770, self.do_booking)
            # Start off-screen
            card.pack(pady=5)
            card.place(x=0, y=500 + i*150) 
            # Slide in
            target_y = i * 110
            Animator.animate(500 + i*150, target_y, 0.4 + i*0.1, lambda y, c=card: c.place(y=y))

    def load_bookings(self):
        for w in self.b_results.winfo_children():
            w.destroy()
            
        bookings = database.get_user_bookings(self.current_user)
        for i, b in enumerate(bookings):
            card = BookingCard(self.b_results, b, 770, self.do_cancel)
            card.pack(pady=5)
            card.place(x=0, y=500 + i*150)
            target_y = i * 110
            Animator.animate(500 + i*150, target_y, 0.4 + i*0.1, lambda y, c=card: c.place(y=y))

    def do_booking(self, flight):
        # Custom Modal Overlay
        self.overlay = tk.Canvas(self, width=1100, height=750, bg=BG_COLOR, highlightthickness=0)
        self.overlay.place(x=0, y=0)
        
        # We simulate opacity by just making it the BG_COLOR but maybe we draw a massive rectangle
        # Tkinter lacks opacity for widgets natively, so we just use a solid color blocking everything
        
        modal_w, modal_h = 400, 300
        cx, cy = 550, 375
        
        self.modal = create_round_rectangle(self.overlay, cx-modal_w/2, cy-modal_h/2, cx+modal_w/2, cy+modal_h/2, radius=30, fill=CARD_COLOR, outline="")
        
        self.overlay.create_text(cx, cy-90, text="Confirm Booking", fill=TEXT_MAIN, font=("Segoe UI", 20, "bold"))
        self.overlay.create_text(cx, cy-30, text=f"{flight.origin} ➔ {flight.destination}", fill=ACCENT, font=("Segoe UI", 16, "bold"))
        self.overlay.create_text(cx, cy+10, text=f"Departure: {flight.departure_time}\nPrice: {flight.formatted_price}", fill=TEXT_DIM, font=("Segoe UI", 12), justify="center")
        
        def confirm():
            database.create_booking(flight.id, self.current_user)
            self.overlay.destroy()
            self.nav_to("bookings")
            
        def cancel():
            self.overlay.destroy()
            
        b1 = AnimatedButton(self.overlay, "Confirm", 130, 45, command=confirm, radius=10)
        b2 = AnimatedButton(self.overlay, "Cancel", 130, 45, bg=BG_COLOR, hover_bg="#334155", command=cancel, radius=10)
        
        self.overlay.create_window(cx - 75, cy + 90, window=b1)
        self.overlay.create_window(cx + 75, cy + 90, window=b2)

    def do_cancel(self, bid):
        # Quick custom modal
        self.overlay = tk.Canvas(self, width=1100, height=750, bg=BG_COLOR, highlightthickness=0)
        self.overlay.place(x=0, y=0)
        
        cx, cy = 550, 375
        create_round_rectangle(self.overlay, cx-200, cy-120, cx+200, cy+120, radius=30, fill=CARD_COLOR, outline="")
        self.overlay.create_text(cx, cy-50, text="Cancel Reservation?", fill=DANGER, font=("Segoe UI", 20, "bold"))
        self.overlay.create_text(cx, cy-10, text="Are you sure you want to cancel this ticket?", fill=TEXT_DIM, font=("Segoe UI", 12))
        
        def confirm():
            database.cancel_booking(bid)
            self.overlay.destroy()
            self.load_bookings()
            
        def cancel():
            self.overlay.destroy()
            
        b1 = AnimatedButton(self.overlay, "Yes, Cancel", 130, 45, bg=DANGER, hover_bg="#DC2626", command=confirm, radius=10)
        b2 = AnimatedButton(self.overlay, "No, Keep", 130, 45, bg=BG_COLOR, hover_bg="#334155", command=cancel, radius=10)
        
        self.overlay.create_window(cx - 75, cy + 60, window=b1)
        self.overlay.create_window(cx + 75, cy + 60, window=b2)


if __name__ == "__main__":
    database.init_db()
    app = SkyReserveElite()
    app.mainloop()
