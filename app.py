import tkinter as tk
from tkinter import ttk, messagebox
import database

# Modern Color Palettes
THEMES = {
    "light": {
        "bg": "#f8f9fa",
        "fg": "#212529",
        "header_bg": "#ffffff",
        "card_bg": "#ffffff",
        "primary": "#0d6efd",
        "secondary": "#6c757d",
        "accent": "#0dcaf0",
        "text_dim": "#6c757d",
        "border": "#dee2e6"
    },
    "dark": {
        "bg": "#121212",
        "fg": "#e0e0e0",
        "header_bg": "#1e1e1e",
        "card_bg": "#1e1e1e",
        "primary": "#3700b3",
        "secondary": "#03dac6",
        "accent": "#bb86fc",
        "text_dim": "#b0b0b0",
        "border": "#333333"
    }
}

class FlightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SkyReserve - Modern Flight Management")
        self.geometry("1000x700")
        
        # Theme State
        self.current_theme_name = "light"
        self.colors = THEMES[self.current_theme_name]
        
        # Mock Current User
        self.current_user = "John Doe"
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.main_container = tk.Frame(self, bg=self.colors["bg"])
        self.main_container.pack(fill="both", expand=True)
        
        self.create_widgets()
        self.apply_theme()

    def toggle_theme(self):
        self.current_theme_name = "dark" if self.current_theme_name == "light" else "light"
        self.colors = THEMES[self.current_theme_name]
        self.apply_theme()

    def apply_theme(self):
        c = self.colors
        self.configure(bg=c["bg"])
        self.main_container.configure(bg=c["bg"])
        self.header_frame.configure(bg=c["header_bg"])
        self.header_label.configure(bg=c["header_bg"], fg=c["primary"])
        self.user_label.configure(bg=c["header_bg"], fg=c["text_dim"])
        self.theme_btn.configure(text=f"切换 {'Light' if self.current_theme_name == 'dark' else 'Dark'} Mode")

        # Styles for ttk widgets
        self.style.configure("TNotebook", background=c["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=c["border"], foreground=c["fg"], padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", c["primary"])], foreground=[("selected", "white")])
        
        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Card.TFrame", background=c["card_bg"], relief="flat")
        self.style.configure("Treeview", background=c["card_bg"], foreground=c["fg"], fieldbackground=c["card_bg"], borderwidth=0)
        self.style.configure("Treeview.Heading", background=c["border"], foreground=c["fg"], font=("Helvetica", 10, "bold"))
        self.style.map("Treeview", background=[("selected", c["primary"])], foreground=[("selected", "white")])

        for tab in [self.search_tab, self.bookings_tab]:
            tab.configure(bg=c["bg"])
            
        self.search_form.configure(style="TFrame")
        self.load_flights()
        self.load_user_bookings()

    def create_widgets(self):
        # Top Header
        self.header_frame = tk.Frame(self.main_container, height=70, padx=40)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_label = tk.Label(self.header_frame, text="SkyReserve", font=("Impact", 24))
        self.header_label.pack(side="left")
        
        self.theme_btn = tk.Button(self.header_frame, command=self.toggle_theme, relief="flat", padx=10)
        self.theme_btn.pack(side="right", padx=10)
        
        self.user_label = tk.Label(self.header_frame, text=f"Passenger: {self.current_user}", font=("Helvetica", 10))
        self.user_label.pack(side="right", padx=20)
        
        # Tabs
        self.tab_control = ttk.Notebook(self.main_container)
        self.search_tab = tk.Frame(self.tab_control)
        self.bookings_tab = tk.Frame(self.tab_control)
        
        self.tab_control.add(self.search_tab, text=" ✈  Flight Search ")
        self.tab_control.add(self.bookings_tab, text=" 🗂  My Bookings ")
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=20)
        
        self.setup_search_tab()
        self.setup_bookings_tab()

    def setup_search_tab(self):
        # Modern Search Bar
        self.search_form = ttk.Frame(self.search_tab, padding=20)
        self.search_form.pack(fill="x")
        
        controls = tk.Frame(self.search_form, bg=self.colors["bg"])
        controls.pack(pady=10)
        
        tk.Label(controls, text="From:", bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=0, column=0, padx=5)
        self.origin_entry = ttk.Entry(controls, width=20)
        self.origin_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(controls, text="To:", bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=0, column=2, padx=5)
        self.dest_entry = ttk.Entry(controls, width=20)
        self.dest_entry.grid(row=0, column=3, padx=10)
        
        ttk.Button(controls, text="Search Flights", command=self.load_flights).grid(row=0, column=4, padx=20)

        # Flights List
        list_container = tk.Frame(self.search_tab, bg=self.colors["bg"])
        list_container.pack(fill="both", expand=True, padx=20)
        
        cols = ("ID", "Origin", "Destination", "Departure", "Price", "Seats")
        self.flight_tree = ttk.Treeview(list_container, columns=cols, show="headings", height=12)
        
        for col in cols:
            self.flight_tree.heading(col, text=col)
            self.flight_tree.column(col, width=120, anchor="center")
            
        self.flight_tree.pack(side="left", fill="both", expand=True)
        
        # Action Bar
        action_bar = tk.Frame(self.search_tab, bg=self.colors["bg"], pady=20)
        action_bar.pack(fill="x")
        ttk.Button(action_bar, text="Confirm Reservation", command=self.handle_booking).pack()

    def setup_bookings_tab(self):
        list_container = tk.Frame(self.bookings_tab, bg=self.colors["bg"], pady=20)
        list_container.pack(fill="both", expand=True, padx=20)
        
        cols = ("Ref ID", "Origin", "Destination", "Departure", "Price", "Status")
        self.booking_tree = ttk.Treeview(list_container, columns=cols, show="headings", height=15)
        
        for col in cols:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=120, anchor="center")
            
        self.booking_tree.pack(side="left", fill="both", expand=True)
        
        btn_frame = tk.Frame(self.bookings_tab, bg=self.colors["bg"], pady=20)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Update List", command=self.load_user_bookings).pack(side="left", padx=50)
        ttk.Button(btn_frame, text="Cancel Ticket", command=self.handle_cancellation).pack(side="right", padx=50)

    def load_flights(self):
        for item in self.flight_tree.get_children():
            self.flight_tree.delete(item)
        
        origin = self.origin_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        flights = database.search_flights(origin, dest)
        for f in flights:
            # Using model specific properties/methods
            status_text = f"{f.available_seats}/{f.capacity}"
            self.flight_tree.insert("", "end", values=(
                f.id, f.origin, f.destination, f.departure_time, 
                f.formatted_price, status_text
            ))

    def load_user_bookings(self):
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)
        bookings = database.get_user_bookings(self.current_user)
        for b in bookings:
            # Format price as currency
            row_data = list(b)
            row_data[4] = f"${row_data[4]:,.2f}"
            self.booking_tree.insert("", "end", values=tuple(row_data))

    def handle_booking(self):
        sel = self.flight_tree.selection()
        if not sel:
            messagebox.showwarning("Oops", "Please pick a flight first!")
            return
        
        # Get flight ID from selection
        values = self.flight_tree.item(sel[0])['values']
        fid = values[0]
        
        # Custom "Professional Modal" Design
        self.show_booking_modal(values)

    def show_booking_modal(self, flight_values):
        modal = tk.Toplevel(self)
        modal.title("Confirm Your Reservation")
        modal.geometry("400x300")
        modal.configure(bg=self.colors["header_bg"])
        modal.transient(self)
        modal.grab_set()
        
        # Centering
        main_x = self.winfo_x() + (self.winfo_width()//2) - 200
        main_y = self.winfo_y() + (self.winfo_height()//2) - 150
        modal.geometry(f"+{main_x}+{main_y}")

        tk.Label(modal, text="Reservation Details", font=("Helvetica", 14, "bold"), 
                 bg=self.colors["header_bg"], fg=self.colors["primary"]).pack(pady=20)
        
        details = f"From: {flight_values[1]}\nTo: {flight_values[2]}\nTime: {flight_values[3]}\nPrice: {flight_values[4]}"
        tk.Label(modal, text=details, font=("Helvetica", 10), justify="left",
                 bg=self.colors["header_bg"], fg=self.colors["fg"]).pack(pady=10)

        btn_frame = tk.Frame(modal, bg=self.colors["header_bg"])
        btn_frame.pack(side="bottom", pady=30)
        
        def confirm():
            database.create_booking(flight_values[0], self.current_user)
            modal.destroy()
            self.load_flights()
            self.load_user_bookings()
            messagebox.showinfo("Success", "Ticket reserved! Safe travels.")

        ttk.Button(btn_frame, text="Confirm & Pay", command=confirm).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=modal.destroy).pack(side="left", padx=10)

    def handle_cancellation(self):
        sel = self.booking_tree.selection()
        if not sel: return
        bid = self.booking_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Cancel", "Cancel this reservation?"):
            database.cancel_booking(bid)
            self.load_user_bookings()

if __name__ == "__main__":
    database.init_db()
    app = FlightApp()
    app.mainloop()

if __name__ == "__main__":
    database.init_db()
    app = FlightApp()
    app.mainloop()
