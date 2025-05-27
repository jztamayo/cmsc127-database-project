import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector

# DB connection (adjust password if needed)
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="student_org_db"
    )

# Fetch all student orgs
def get_orgs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT org_name FROM student_org")
    orgs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return orgs

# Fetch members by org_name
def get_members(org_name):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT m.member_id, m.username, m.gender, m.batch, m.degree_program, som.role, som.status
        FROM member m
        JOIN student_org_member som ON m.member_id = som.member_id
        WHERE som.org_name = %s
    """
    cursor.execute(query, (org_name,))
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members

# Add a new member
def add_member(org_name):
    username = simpledialog.askstring("Input", "Member username:")
    password = simpledialog.askstring("Input", "Password:")
    gender = simpledialog.askstring("Input", "Gender (M/F):")
    batch = simpledialog.askinteger("Input", "Batch (year):")
    degree = simpledialog.askstring("Input", "Degree program:")
    
    if None in (username, password, gender, batch, degree):
        messagebox.showerror("Error", "All fields are required.")
        return
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
            VALUES (%s, %s, %s, %s, %s, CURDATE())
        """, (username, password, gender, batch, degree))
        member_id = cursor.lastrowid
        # Add default membership details (active member, non-executive, current acad year and semester)
        cursor.execute("""
            INSERT INTO student_org_member (org_name, member_id, role, status, is_executive, acad_yr, semester)
            VALUES (%s, %s, %s, 'Active', 0, '24-25', 1)
        """, (org_name, member_id, 'Member'))
        conn.commit()
        messagebox.showinfo("Success", f"Member {username} added to {org_name}!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

# GUI App
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Organization Management System")
        self.geometry("1100x400")
        
        # Dropdown to select org
        tk.Label(self, text="Select Student Organization:").pack(pady=5)
        self.org_var = tk.StringVar()
        self.org_dropdown = ttk.Combobox(self, textvariable=self.org_var, values=get_orgs())
        self.org_dropdown.pack(pady=5)
        
        # Show members button
        tk.Button(self, text="Show Members", command=self.show_members).pack(pady=5)
        
        # Add member button
        tk.Button(self, text="Add Member", command=self.add_member).pack(pady=5)
        
        # Treeview for members
        columns = ("ID", "Username", "Gender", "Batch", "Degree", "Role", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70)
        self.tree.pack(expand=True, fill=tk.BOTH)
    
    def show_members(self):
        org = self.org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Please select an organization.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        members = get_members(org)
        for m in members:
            self.tree.insert("", tk.END, values=m)
    
    def add_member(self):
        org = self.org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Please select an organization.")
            return
        add_member(org)
        self.show_members()

if __name__ == "__main__":
    app = App()
    app.mainloop()

