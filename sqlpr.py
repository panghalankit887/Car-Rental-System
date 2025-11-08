import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import sv_ttk
from datetime import datetime

def create_db():
    conn = sqlite3.connect("car_rental.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS cars (
        car_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT, brand TEXT, price_per_day INTEGER,
        status TEXT DEFAULT 'AVAILABLE')''')
    cur.execute('''CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, email TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS rentals (
        rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER, customer_id INTEGER,
        start_date TEXT, end_date TEXT, total_price INTEGER,
        status TEXT DEFAULT 'ACTIVE'
    )''')
    conn.commit()
    conn.close()

create_db()

def db_execute(query, params=(), commit=True):
    conn = sqlite3.connect("car_rental.db")
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return result

class CarRentalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental System")
        self.geometry("900x550")
        sv_ttk.set_theme("dark")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both")

        self.car_tab = ttk.Frame(self.tabs)
        self.customer_tab = ttk.Frame(self.tabs)
        self.rental_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.car_tab, text="Cars")
        self.tabs.add(self.customer_tab, text="Customers")
        self.tabs.add(self.rental_tab, text="Rentals")

        self.create_car_tab()
        self.create_customer_tab()
        self.create_rental_tab()

    # -- Car Tab --
    def create_car_tab(self):
        tab = self.car_tab
        ttk.Label(tab, text="Add Cars", font=("Segoe UI", 18)).grid(row=0, column=0, columnspan=4, pady=10)
        ttk.Label(tab, text="Model:").grid(row=1, column=0, pady=5)
        self.model_entry = ttk.Entry(tab)
        self.model_entry.grid(row=1, column=1)
        ttk.Label(tab, text="Brand:").grid(row=2, column=0, pady=5)
        self.brand_entry = ttk.Entry(tab)
        self.brand_entry.grid(row=2, column=1)
        ttk.Label(tab, text="Price/Day:").grid(row=3, column=0, pady=5)
        self.price_entry = ttk.Entry(tab)
        self.price_entry.grid(row=3, column=1)
        ttk.Button(tab, text="Add Car", style="Accent.TButton", command=self.add_car).grid(row=4, column=0, pady=8)
        ttk.Button(tab, text="Delete Car", command=self.delete_car).grid(row=4, column=1, pady=8)
        ttk.Button(tab, text="Search", command=self.search_car).grid(row=4, column=2, pady=8)
        ttk.Button(tab, text="Refresh", command=self.refresh_car_list).grid(row=4, column=3, pady=8)
        self.car_list = ttk.Treeview(tab, columns=("ID", "Model", "Brand", "Price", "Status"), show="headings", height=13)
        for col in ("ID", "Model", "Brand", "Price", "Status"):
            self.car_list.heading(col, text=col)
        self.car_list.grid(row=5, column=0, columnspan=4, pady=10)
        self.refresh_car_list()

    def add_car(self):
        model = self.model_entry.get()
        brand = self.brand_entry.get()
        try:
            price = int(self.price_entry.get())
            db_execute('INSERT INTO cars(model, brand, price_per_day) VALUES (?, ?, ?)', (model, brand, price))
            self.refresh_car_list()
        except ValueError:
            messagebox.showerror("Error", "Price must be an integer.")

    def delete_car(self):
        item = self.car_list.focus()
        if item:
            values = self.car_list.item(item, 'values')
            db_execute('DELETE FROM cars WHERE car_id=?', (values[0],))
            self.refresh_car_list()

    def search_car(self):
        query = simpledialog.askstring("Search", "Enter model or brand:")
        if query:
            rows = db_execute('SELECT * FROM cars WHERE model LIKE ? OR brand LIKE ?', (f'%{query}%', f'%{query}%'), commit=False)
            self.car_list.delete(*self.car_list.get_children())
            for row in rows:
                self.car_list.insert('', 'end', values=row)

    def refresh_car_list(self):
        self.car_list.delete(*self.car_list.get_children())
        for row in db_execute('SELECT * FROM cars', commit=False):
            self.car_list.insert('', 'end', values=row)

    # -- Customer Tab --
    def create_customer_tab(self):
        tab = self.customer_tab
        ttk.Label(tab, text="Add Customer", font=("Segoe UI", 18)).grid(row=0, column=0, columnspan=4, pady=10)
        ttk.Label(tab, text="Name:").grid(row=1, column=0, pady=5)
        self.name_entry = ttk.Entry(tab)
        self.name_entry.grid(row=1, column=1)
        ttk.Label(tab, text="Phone:").grid(row=2, column=0, pady=5)
        self.phone_entry = ttk.Entry(tab)
        self.phone_entry.grid(row=2, column=1)
        ttk.Label(tab, text="Email:").grid(row=3, column=0, pady=5)
        self.email_entry = ttk.Entry(tab)
        self.email_entry.grid(row=3, column=1)
        ttk.Button(tab, text="Add Customer", style="Accent.TButton", command=self.add_customer).grid(row=4, column=0, pady=8)
        ttk.Button(tab, text="Delete Customer", command=self.delete_customer).grid(row=4, column=1, pady=8)
        ttk.Button(tab, text="Search", command=self.search_customer).grid(row=4, column=2, pady=8)
        ttk.Button(tab, text="Refresh", command=self.refresh_customer_list).grid(row=4, column=3, pady=8)
        self.customer_list = ttk.Treeview(tab, columns=("ID", "Name", "Phone", "Email"), show="headings", height=13)
        for col in ("ID", "Name", "Phone", "Email"):
            self.customer_list.heading(col, text=col)
        self.customer_list.grid(row=5, column=0, columnspan=4, pady=10)
        self.refresh_customer_list()

    def add_customer(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        db_execute('INSERT INTO customers(name, phone, email) VALUES (?, ?, ?)', (name, phone, email))
        self.refresh_customer_list()

    def delete_customer(self):
        item = self.customer_list.focus()
        if item:
            values = self.customer_list.item(item, 'values')
            db_execute('DELETE FROM customers WHERE customer_id=?', (values[0],))
            self.refresh_customer_list()

    def search_customer(self):
        query = simpledialog.askstring("Search", "Enter customer name:")
        if query:
            rows = db_execute('SELECT * FROM customers WHERE name LIKE ?', (f'%{query}%',), commit=False)
            self.customer_list.delete(*self.customer_list.get_children())
            for row in rows:
                self.customer_list.insert('', 'end', values=row)

    def refresh_customer_list(self):
        self.customer_list.delete(*self.customer_list.get_children())
        for row in db_execute('SELECT * FROM customers', commit=False):
            self.customer_list.insert('', 'end', values=row)

    # -- Rentals Tab --
    def create_rental_tab(self):
        tab = self.rental_tab
        ttk.Label(tab, text="Book Rental", font=("Segoe UI", 18)).grid(row=0, column=0, columnspan=4, pady=10)
        ttk.Label(tab, text="Customer ID:").grid(row=1, column=0, pady=5)
        self.rent_cust = ttk.Entry(tab)
        self.rent_cust.grid(row=1, column=1)
        ttk.Label(tab, text="Car ID:").grid(row=2, column=0, pady=5)
        self.rent_car = ttk.Entry(tab)
        self.rent_car.grid(row=2, column=1)
        ttk.Label(tab, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, pady=5)
        self.rent_start = ttk.Entry(tab)
        self.rent_start.grid(row=3, column=1)
        ttk.Label(tab, text="End Date (YYYY-MM-DD):").grid(row=4, column=0, pady=5)
        self.rent_end = ttk.Entry(tab)
        self.rent_end.grid(row=4, column=1)
        ttk.Button(tab, text="Book Rental", style="Accent.TButton", command=self.book_rental).grid(row=5, column=0, pady=8)
        ttk.Button(tab, text="Return Car", command=self.return_car).grid(row=5, column=1, pady=8)
        ttk.Button(tab, text="Delete Rental", command=self.delete_rental).grid(row=5, column=2, pady=8)
        ttk.Button(tab, text="Refresh", command=self.refresh_rental_list).grid(row=5, column=3, pady=8)
        self.rental_list = ttk.Treeview(tab, columns=("ID", "Car", "Cust", "Start", "End", "Total", "Status"), show="headings", height=13)
        for col in ("ID", "Car", "Cust", "Start", "End", "Total", "Status"):
            self.rental_list.heading(col, text=col)
        self.rental_list.grid(row=6, column=0, columnspan=4, pady=10)
        self.refresh_rental_list()

    def book_rental(self):
        try:
            car_id = int(self.rent_car.get())
            cust_id = int(self.rent_cust.get())
            start = self.rent_start.get()
            end = self.rent_end.get()
            row = db_execute('SELECT price_per_day FROM cars WHERE car_id=? AND status="AVAILABLE"', (car_id,), commit=False)
            if row:
                price_per_day = row[0][0]
                days = (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days + 1
                total = price_per_day * days
                db_execute('INSERT INTO rentals(car_id, customer_id, start_date, end_date, total_price) VALUES (?, ?, ?, ?, ?)',
                           (car_id, cust_id, start, end, total))
                db_execute('UPDATE cars SET status="RENTED" WHERE car_id=?', (car_id,))
                self.refresh_rental_list()
                self.refresh_car_list()
            else:
                messagebox.showerror("Error", "Car not available.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_car(self):
        item = self.rental_list.focus()
        if item:
            values = self.rental_list.item(item, 'values')
            if values[6] == 'RETURNED':
                messagebox.showinfo("Info", "Car has already been returned.")
                return
            db_execute('UPDATE rentals SET status="RETURNED" WHERE rental_id=?', (values[0],))
            db_execute('UPDATE cars SET status="AVAILABLE" WHERE car_id=?', (values[1],))
            self.refresh_rental_list()
            self.refresh_car_list()

    def delete_rental(self):
        item = self.rental_list.focus()
        if item:
            values = self.rental_list.item(item, 'values')
            db_execute('DELETE FROM rentals WHERE rental_id=?', (values[0],))
            self.refresh_rental_list()

    def refresh_rental_list(self):
        self.rental_list.delete(*self.rental_list.get_children())
        for row in db_execute('SELECT * FROM rentals', commit=False):
            self.rental_list.insert('', 'end', values=row)

if __name__ == "__main__":
    app = CarRentalApp()
    app.mainloop()
