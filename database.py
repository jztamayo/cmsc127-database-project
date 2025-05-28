import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector

# DB connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="student_org_db",
        autocommit=False,
        connection_timeout=10,
        sql_mode='STRICT_TRANS_TABLES'
    )

# Fetch orgs
def get_orgs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT org_name FROM student_org")
    orgs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return orgs

# Fetch members of org
def get_members(org_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.member_id, m.username, m.gender, m.batch, m.degree_program, som.role, som.status
        FROM member m
        JOIN student_org_member som ON m.member_id = som.member_id
        WHERE som.org_name = %s
    """, (org_name,))
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members

def get_executive_members(org_name, acad_yr):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT member_id, org_name, role, status, is_executive, acad_yr, semester
        FROM student_org_member
        WHERE role != 'Member' AND acad_yr = %s AND org_name = %s
    """
    cursor.execute(query, (acad_yr, org_name))
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return data, columns


# Fetch unpaid members
def get_unpaid_members(org_name, acad_yr=None, semester=None):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT m.member_id, f.fee_id, mem.org_name, m.username, pays.status, 
               f.purpose, f.amount, f.acad_yr, mem.semester, f.due_date 
        FROM member m
        JOIN member_pays_fee pays ON m.member_id = pays.member_id
        JOIN fee f ON pays.fee_id = f.fee_id
        JOIN student_org_member mem ON m.member_id = mem.member_id
        WHERE mem.org_name = %s AND pays.status = 'Unpaid'
    """
    params = [org_name]
    if acad_yr:
        query += " AND f.acad_yr = %s"
        params.append(acad_yr)
    if semester:
        query += " AND mem.semester = %s"
        params.append(semester)
    query += " ORDER BY m.username, f.due_date"

    cursor.execute(query, params)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return results, columns

def get_active_percentage(org_name, acad_yr, semester):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT org_name, acad_yr, semester,
               COUNT(*) AS total_members,
               SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_members,
               ROUND(SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS active_percentage
        FROM student_org_member
        WHERE org_name = %s AND acad_yr = %s AND semester = %s
        GROUP BY org_name, acad_yr, semester
    """
    cursor.execute(query, (org_name, acad_yr, semester))
    result = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return result, columns


def get_late_payments(org_name, acad_yr, semester):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT mpf.member_id, mpf.fee_id, mpf.status, mpf.payment_date,
               f.purpose, f.amount, f.due_date,
               som.org_name, som.acad_yr, som.semester
        FROM member_pays_fee mpf
        JOIN fee f USING(fee_id)
        JOIN student_org_member som USING(member_id)
        WHERE mpf.payment_date > f.due_date
          AND som.org_name = %s
          AND som.acad_yr = %s
          AND som.semester = %s
        ORDER BY mpf.payment_date
    """
    cursor.execute(query, (org_name, acad_yr, semester))
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return data, columns

def get_fee_summary_by_org(org_name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT member_pays_fee.status, SUM(fee.amount) AS total_amount
            FROM member_pays_fee
            JOIN fee USING(fee_id)
            JOIN student_org_member USING(member_id)
            WHERE student_org_member.org_name = %s
            GROUP BY member_pays_fee.status
        """, (org_name,))
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return data, columns
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

def get_highest_debt_members(org_name, acad_yr, semester):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT member_id, student_org_member.org_name, username, fee_id, purpose, amount, due_date, 
                   student_org_member.acad_yr, semester
            FROM member 
            JOIN member_pays_fee USING(member_id) 
            JOIN student_org_member USING(member_id) 
            JOIN fee USING(fee_id)
            WHERE member_pays_fee.status = 'Unpaid'
              AND student_org_member.org_name = %s
              AND student_org_member.acad_yr = %s
              AND semester = %s
            ORDER BY amount DESC
        """, (org_name, acad_yr, semester))
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return data, columns
    finally:
        cursor.close()
        conn.close()

def get_org_roles(org_name, role):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM student_org_member 
            WHERE role != 'Member' AND org_name = %s AND role = %s
            ORDER BY acad_yr DESC
        """, (org_name, role))
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return data, columns
    finally:
        cursor.close()
        conn.close()

def get_alumni_members(org_name, acad_yr, semester):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT member_id, org_name, username, status, degree_program, batch, acad_yr, semester 
            FROM student_org_member 
            JOIN member USING(member_id)
            WHERE status = 'Alumni' AND org_name = %s AND acad_yr = %s AND semester = %s
        """, (org_name, acad_yr, semester))
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return results, columns
    finally:
        cursor.close()
        conn.close()

def get_completed_membership_fees(member_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT fee_id, purpose, amount, due_date, member_pays_fee.status, student_org_member.org_name 
            FROM student_org_member 
            JOIN member_pays_fee USING(member_id) 
            JOIN fee USING(fee_id) 
            WHERE member_id = %s 
              AND member_pays_fee.status = 'Unpaid' 
              AND purpose = 'Membership'
        """, (member_id,))
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return data, columns
    finally:
        cursor.close()
        conn.close()





# Add a member
def add_member(org_name):
    username = simpledialog.askstring("Input", "Member username:")
    password = simpledialog.askstring("Input", "Password:")
    gender = simpledialog.askstring("Input", "Gender (M/F):")
    batch = simpledialog.askinteger("Input", "Batch (year):")
    degree = simpledialog.askstring("Input", "Degree program (max 10 chars):")
    
    if None in (username, password, gender, batch, degree):
        messagebox.showerror("Error", "All fields are required.")
        return
    if len(username) > 25 or len(password) > 45 or len(degree) > 10 or gender.upper() not in ['M', 'F']:
        messagebox.showerror("Error", "Invalid input.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("""
            INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
            VALUES (%s, %s, %s, %s, %s, CURDATE())
        """, (username, password, gender.upper(), batch, degree))
        member_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO student_org_member (org_name, member_id, role, status, is_executive, acad_yr, semester)
            VALUES (%s, %s, 'Member', 'Active', 0, '24-25', 2)
        """, (org_name, member_id))

        cursor.execute("""
            INSERT INTO fee (org_name, purpose, acad_yr, due_date, amount)
            VALUES (%s, 'Membership', '24-25', CURDATE(), 200)
        """, (org_name,))

        fee_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO member_pays_fee (member_id, fee_id, status, payment_date)
            VALUES (%s, %s, 'Unpaid', NULL)
        """, (member_id, fee_id))

        conn.commit()
        messagebox.showinfo("Success", f"{username}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

def update_member(member_id, username, degree_program):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE member 
            SET username = %s, degree_program = %s 
            WHERE member_id = %s
        """, (username, degree_program, member_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def update_member_fee_status(member_id, fee_id, status, payment_date=None):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        if status == "Completed" and payment_date is None:
            payment_date = datetime.date.today()

        cursor.execute("""
            UPDATE member_pays_fee 
            SET status = %s, payment_date = %s 
            WHERE member_id = %s AND fee_id = %s
        """, (status, payment_date, member_id, fee_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def update_student_org_member(org_name, member_id, acad_yr, semester, role, status, is_executive):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE student_org_member 
            SET role = %s, status = %s, is_executive = %s
            WHERE org_name = %s AND member_id = %s AND acad_yr = %s AND semester = %s
        """, (role, status, is_executive, org_name, member_id, acad_yr, semester))
        conn.commit()
        return cursor.rowcount > 0  # True if updated, False if no match found
    finally:
        cursor.close()
        conn.close()


def delete_member(member_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Step 1: Delete from member_pays_fee
        cursor.execute("""
            DELETE FROM member_pays_fee
            WHERE member_id = %s
        """, (member_id,))

        # Step 2: Delete from student_org_member
        cursor.execute("""
            DELETE FROM student_org_member
            WHERE member_id = %s
        """, (member_id,))

        # Step 3: Delete from member table
        cursor.execute("""
            DELETE FROM member
            WHERE member_id = %s
        """, (member_id,))

        conn.commit()
        return cursor.rowcount > 0  # Returns True if deletion was successful
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def delete_fee(fee_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Step 1: Delete related records from member_pays_fee
        cursor.execute("""
            DELETE FROM member_pays_fee
            WHERE fee_id = %s
        """, (fee_id,))

        # Step 2: Delete the fee from the fee table
        cursor.execute("""
            DELETE FROM fee
            WHERE fee_id = %s
        """, (fee_id,))

        conn.commit()
        return cursor.rowcount > 0  # True if fee was successfully deleted
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Main GUI App
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Organization Management System")
        self.geometry("1200x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        self.members_frame = ttk.Frame(self.notebook)
        self.unpaid_frame = ttk.Frame(self.notebook)
        self.query_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.members_frame, text="Members")
        self.roles_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.roles_tab, text="Org Roles")
        self.setup_roles_tab()
        self.notebook.add(self.unpaid_frame, text="Unpaid Fees")
        

        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Member Stats")
        self.setup_stats_tab()

        self.fee_summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fee_summary_frame, text="Fee Summary")
        self.setup_fee_summary_tab()

        self.highest_debt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.highest_debt_frame, text="Highest Debt")
        self.setup_highest_debt_tab()

        self.alumni_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.alumni_tab, text="Alumni")
        self.setup_alumni_tab()

        self.my_membership_completed_fees_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.my_membership_completed_fees_tab, text="Membership Fees")
        self.setup_completed_membership_tab()

        self.update_member_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_member_tab, text="Update User")
        self.setup_update_member_tab()

        self.update_fee_status_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_fee_status_tab, text="Update Fee")
        self.setup_update_fee_status_tab()

        self.update_org_member_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_org_member_tab, text="Update Member")
        self.setup_update_org_member_tab()

        self.delete_member_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_member_tab, text="Delete Member")
        self.setup_delete_member_tab()

        self.delete_fee_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_fee_tab, text="Delete Fee")
        self.setup_delete_fee_tab()




        self.setup_members_tab()
        self.setup_unpaid_tab()

    def setup_delete_fee_tab(self):
        frame = tk.Frame(self.delete_fee_tab, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Enter Fee ID to Delete:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.delete_fee_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.delete_fee_id_var).grid(row=0, column=1, pady=5)

        tk.Button(frame, text="Delete Fee", command=self.perform_delete_fee).grid(row=1, columnspan=2, pady=10)


    def setup_delete_member_tab(self):
        frame = tk.Frame(self.delete_member_tab, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Enter Member ID to Delete:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.delete_member_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.delete_member_id_var).grid(row=0, column=1, pady=5)

        tk.Button(frame, text="Delete Member", command=self.perform_delete_member).grid(row=1, columnspan=2, pady=10)


    def setup_update_org_member_tab(self):
        frame = tk.Frame(self.update_org_member_tab, padx=20, pady=20)
        frame.pack()

        labels = ["Org Name", "Member ID", "Academic Year", "Semester", "Role", "Status", "Is Executive (1/0)"]
        self.update_fields = {}

        for i, label in enumerate(labels):
            tk.Label(frame, text=label + ":").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(frame)
            entry.grid(row=i, column=1, pady=2)
            self.update_fields[label] = entry

        tk.Button(frame, text="Update Member Info", command=self.perform_update_student_org_member).grid(row=len(labels), columnspan=2, pady=10)


    def setup_update_fee_status_tab(self):
        frame = tk.Frame(self.update_fee_status_tab, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Member ID:").grid(row=0, column=0)
        self.fee_update_member_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.fee_update_member_id_var).grid(row=0, column=1)

        tk.Label(frame, text="Fee ID:").grid(row=1, column=0)
        self.fee_update_fee_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.fee_update_fee_id_var).grid(row=1, column=1)

        tk.Label(frame, text="Status:").grid(row=2, column=0)
        self.fee_update_status_var = tk.StringVar()
        status_menu = ttk.Combobox(frame, textvariable=self.fee_update_status_var, values=["Unpaid", "Completed"], state="readonly")
        status_menu.grid(row=2, column=1)

        tk.Label(frame, text="Payment Date (YYYY-MM-DD):").grid(row=3, column=0)
        self.fee_update_date_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.fee_update_date_var).grid(row=3, column=1)

        tk.Button(frame, text="Update Fee Status", command=self.perform_update_fee_status).grid(row=4, column=0, columnspan=2, pady=10)


    def setup_update_member_tab(self):
        frame = tk.Frame(self.update_member_tab, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Member ID:").grid(row=0, column=0, sticky="e")
        self.update_member_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.update_member_id_var).grid(row=0, column=1)

        tk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e")
        self.update_username_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.update_username_var).grid(row=1, column=1)


        tk.Label(frame, text="Degree Program:").grid(row=3, column=0, sticky="e")
        self.update_degree_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.update_degree_var).grid(row=3, column=1)

        tk.Button(frame, text="Update Member", command=self.perform_update_member).grid(row=4, column=0, columnspan=2, pady=10)


    def setup_completed_membership_tab(self):
        top = tk.Frame(self.my_membership_completed_fees_tab)
        top.pack(pady=10)

        tk.Label(top, text="Member ID:").grid(row=0, column=0)
        self.completed_member_id_var = tk.StringVar()
        tk.Entry(top, textvariable=self.completed_member_id_var).grid(row=0, column=1, padx=5)

        tk.Button(top, text="View Completed Membership Fees", command=self.show_completed_membership_fees).grid(row=0, column=2, padx=10)

        self.completed_tree_frame = tk.Frame(self.my_membership_completed_fees_tab)
        self.completed_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)




    def setup_alumni_tab(self):
        top = tk.Frame(self.alumni_tab)
        top.pack(pady=10)

        tk.Label(top, text="Organization:").grid(row=0, column=0)
        self.alumni_org_var = tk.StringVar()
        ttk.Combobox(top, textvariable=self.alumni_org_var, values=get_orgs()).grid(row=0, column=1, padx=5)

        tk.Label(top, text="Academic Year:").grid(row=0, column=2)
        self.alumni_yr_var = tk.StringVar()
        tk.Entry(top, textvariable=self.alumni_yr_var, width=10).grid(row=0, column=3, padx=5)

        tk.Label(top, text="Semester:").grid(row=0, column=4)
        self.alumni_sem_var = tk.StringVar()
        tk.Spinbox(top, from_=1, to=3, textvariable=self.alumni_sem_var, width=5).grid(row=0, column=5, padx=5)

        tk.Button(top, text="View Alumni", command=self.show_alumni_members).grid(row=0, column=6, padx=10)

        self.alumni_tree_frame = tk.Frame(self.alumni_tab)
        self.alumni_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def setup_roles_tab(self):
        filters = tk.Frame(self.roles_tab)
        filters.pack(pady=10)

        tk.Label(filters, text="Organization:").grid(row=0, column=0)
        self.roles_org_var = tk.StringVar()
        ttk.Combobox(filters, textvariable=self.roles_org_var, values=get_orgs()).grid(row=0, column=1, padx=5)

        tk.Label(filters, text="Role:").grid(row=0, column=2)
        self.roles_role_var = tk.StringVar()
        ttk.Combobox(filters, textvariable=self.roles_role_var, values=["President", "Vice President", "Secretary", "Treasurer"]).grid(row=0, column=3, padx=5)

        tk.Button(filters, text="Show Roles", command=self.show_org_roles).grid(row=0, column=4, padx=10)

        self.roles_tree_frame = tk.Frame(self.roles_tab)
        self.roles_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def setup_highest_debt_tab(self):
        controls = tk.Frame(self.highest_debt_frame)
        controls.pack(pady=10)

        tk.Label(controls, text="Organization:").grid(row=0, column=0)
        self.debt_org_var = tk.StringVar()
        ttk.Combobox(controls, textvariable=self.debt_org_var, values=get_orgs()).grid(row=0, column=1, padx=5)

        tk.Label(controls, text="Academic Year:").grid(row=0, column=2)
        self.debt_yr_var = tk.StringVar()
        tk.Entry(controls, textvariable=self.debt_yr_var, width=10).grid(row=0, column=3, padx=5)

        tk.Label(controls, text="Semester:").grid(row=0, column=4)
        self.debt_sem_var = tk.StringVar()
        tk.Spinbox(controls, from_=1, to=3, textvariable=self.debt_sem_var, width=5).grid(row=0, column=5)

        tk.Button(controls, text="Show Highest Debt", command=self.show_highest_debt).grid(row=0, column=6, padx=10)

        self.debt_tree_frame = tk.Frame(self.highest_debt_frame)
        self.debt_tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


    def setup_fee_summary_tab(self):
        controls = tk.Frame(self.fee_summary_frame)
        controls.pack(pady=10)

        tk.Label(controls, text="Organization:").grid(row=0, column=0, padx=5)
        self.summary_org_var = tk.StringVar()
        ttk.Combobox(controls, textvariable=self.summary_org_var, values=get_orgs()).grid(row=0, column=1, padx=5)

        tk.Button(controls, text="View Summary", command=self.view_fee_summary).grid(row=0, column=2, padx=10)

        self.summary_tree_frame = tk.Frame(self.fee_summary_frame)
        self.summary_tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


    def setup_stats_tab(self):
        controls = tk.Frame(self.stats_frame)
        controls.pack(pady=10)

        tk.Label(controls, text="Organization:").grid(row=0, column=0, padx=5)
        self.stats_org_var = tk.StringVar()
        ttk.Combobox(controls, textvariable=self.stats_org_var, values=get_orgs()).grid(row=0, column=1, padx=5)

        tk.Label(controls, text="Academic Year:").grid(row=0, column=2, padx=5)
        self.stats_acad_var = tk.StringVar()
        tk.Entry(controls, textvariable=self.stats_acad_var, width=10).grid(row=0, column=3, padx=5)

        tk.Label(controls, text="Semester:").grid(row=0, column=4, padx=5)
        self.stats_sem_var = tk.StringVar()
        tk.Spinbox(controls, from_=1, to=3, textvariable=self.stats_sem_var, width=5).grid(row=0, column=5, padx=5)

        tk.Button(controls, text="View Percentage", command=self.view_active_percentage).grid(row=0, column=6, padx=10)

        self.stats_tree_frame = tk.Frame(self.stats_frame)
        self.stats_tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)



    def setup_members_tab(self):
        tk.Label(self.members_frame, text="Select Student Organization:").pack(pady=2)
        self.org_var = tk.StringVar()
        self.org_dropdown = ttk.Combobox(self.members_frame, textvariable=self.org_var, values=get_orgs())
        self.org_dropdown.pack(pady=5)

        btns = tk.Frame(self.members_frame)
        btns.pack(pady=2)
        tk.Button(btns, text="Show Members", command=self.show_members).pack(side=tk.LEFT, padx=1)
        tk.Button(btns, text="Add Member", command=self.add_member).pack(side=tk.LEFT, padx=1)
        tk.Button(btns, text="Show Executives", command=self.show_executives).pack(side=tk.LEFT, padx=1)
        


        columns = ("ID", "Username", "Gender", "Batch", "Degree", "Role", "Status")
        self.members_tree = ttk.Treeview(self.members_frame, columns=columns, show="headings")
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=70)

        scrollbar = ttk.Scrollbar(self.members_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)

        # Create a frame to hold the Treeview and scrollbar
        tree_frame = tk.Frame(self.members_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=2)

        # Define columns
        columns = ("ID", "Username", "Gender", "Batch", "Degree", "Role", "Status")

        # Create the Treeview inside the tree_frame
        self.members_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Set up column headings and widths
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=100)  # Adjust width as needed

        # Add a scrollbar also inside tree_frame
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar
        self.members_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def setup_unpaid_tab(self):
        controls = tk.Frame(self.unpaid_frame)
        controls.pack(pady=10)

        tk.Label(controls, text="Organization:").grid(row=0, column=0)
        self.unpaid_org_var = tk.StringVar()
        ttk.Combobox(controls, textvariable=self.unpaid_org_var, values=get_orgs()).grid(row=0, column=1)

        tk.Label(controls, text="Academic Year:").grid(row=0, column=2)
        self.acad_yr_var = tk.StringVar()
        tk.Entry(controls, textvariable=self.acad_yr_var, width=10).grid(row=0, column=3)

        tk.Label(controls, text="Semester:").grid(row=1, column=0)
        self.semester_var = tk.StringVar()
        tk.Spinbox(controls, from_=1, to=3, textvariable=self.semester_var, width=5).grid(row=1, column=1)

        tk.Button(controls, text="Show Unpaid Fees", command=self.show_unpaid_fees).grid(row=1, column=2, columnspan=2)
        tk.Button(controls, text="Show Late Payments", command=self.show_late_payments).grid(row=2, column=0, columnspan=4, pady=5)


        self.unpaid_tree_frame = tk.Frame(self.unpaid_frame)
        self.unpaid_tree_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)


    def perform_delete_fee(self):
        fee_id = self.delete_fee_id_var.get().strip()
        if not fee_id.isdigit():
            messagebox.showerror("Invalid Input", "Fee ID must be a number.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Fee ID {fee_id}?")
        if not confirm:
            return

        try:
            success = delete_fee(int(fee_id))
            if success:
                messagebox.showinfo("Success", f"Fee ID {fee_id} successfully deleted.")
            else:
                messagebox.showwarning("Not Found", f"No fee found with ID {fee_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def perform_delete_member(self):
        member_id = self.delete_member_id_var.get().strip()
        if not member_id.isdigit():
            messagebox.showerror("Invalid Input", "Member ID must be a number.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete member ID {member_id}?")
        if not confirm:
            return

        try:
            success = delete_member(int(member_id))
            if success:
                messagebox.showinfo("Success", f"Member ID {member_id} successfully deleted.")
            else:
                messagebox.showwarning("Not Found", f"No member found with ID {member_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def perform_update_student_org_member(self):
        try:
            org_name = self.update_fields["Org Name"].get().strip()
            member_id = int(self.update_fields["Member ID"].get().strip())
            acad_yr = self.update_fields["Academic Year"].get().strip()
            semester = int(self.update_fields["Semester"].get().strip())
            role = self.update_fields["Role"].get().strip()
            status = self.update_fields["Status"].get().strip()
            is_executive = int(self.update_fields["Is Executive (1/0)"].get().strip())

            success = update_student_org_member(org_name, member_id, acad_yr, semester, role, status, is_executive)

            if success:
                messagebox.showinfo("Success", "Student organization member updated successfully.")
            else:
                messagebox.showwarning("No Match", "No record found to update.")
        except ValueError:
            messagebox.showerror("Input Error", "Please check your inputs. Make sure numeric fields are valid.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def perform_update_fee_status(self):
        try:
            member_id = int(self.fee_update_member_id_var.get().strip())
            fee_id = int(self.fee_update_fee_id_var.get().strip())
            status = self.fee_update_status_var.get().strip()
            date_str = self.fee_update_date_var.get().strip()

            payment_date = None
            if date_str:
                payment_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

            success = update_member_fee_status(member_id, fee_id, status, payment_date)
            if success:
                messagebox.showinfo("Success", f"Fee status updated for Member {member_id}, Fee {fee_id}.")
            else:
                messagebox.showwarning("Failed", "Update failed. Check if the member and fee IDs exist.")
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def perform_update_member(self):
        try:
            member_id = int(self.update_member_id_var.get().strip())
            username = self.update_username_var.get().strip()
            degree_program = self.update_degree_var.get().strip()

            if not (username and degree_program):
                messagebox.showwarning("Input Error", "All fields must be filled.")
                return

            success = update_member(member_id, username, degree_program)
            if success:
                messagebox.showinfo("Success", f"Member {member_id} successfully updated.")
            else:
                messagebox.showwarning("Not Found", f"No member found with ID {member_id}.")

        except ValueError:
            messagebox.showerror("Input Error", "Member ID must be a valid number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def show_members(self):
        org = self.org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Select an org.")
            return
        self.members_tree.delete(*self.members_tree.get_children())
        for m in get_members(org):
            self.members_tree.insert("", tk.END, values=m)

    def add_member(self):
        org = self.org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Select an org.")
            return
        add_member(org)
        self.show_members()

    def show_unpaid_fees(self):
        org = self.unpaid_org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Select an org.")
            return
        acad_yr = self.acad_yr_var.get().strip() or None
        semester = self.semester_var.get().strip() or None
        if semester:
            try:
                semester = int(semester)
            except ValueError:
                messagebox.showerror("Error", "Semester must be a number.")
                return
        try:
            data, columns = get_unpaid_members(org, acad_yr, semester)
            for widget in self.unpaid_tree_frame.winfo_children():
                widget.destroy()
            tree = ttk.Treeview(self.unpaid_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.title())
                tree.column(col, width=100)
            vsb = ttk.Scrollbar(self.unpaid_tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            for row in data:
                tree.insert("", tk.END, values=row)
            if data:
                total = sum(float(row[columns.index("amount")]) for row in data)
                messagebox.showinfo("Summary", f"{len(data)} fees. Total: ₱{total:.2f}")
            else:
                messagebox.showinfo("Info", "No unpaid fees found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_executives(self):
        org = self.org_var.get()
        if not org:
            messagebox.showwarning("Warning", "Select an org.")
            return

        acad_yr = simpledialog.askstring("Input", "Enter Academic Year (e.g. '24-25'):")
        if not acad_yr:
            messagebox.showerror("Error", "Academic year required.")
            return

        try:
            data, columns = get_executive_members(org, acad_yr)
            self.members_tree.delete(*self.members_tree.get_children())
            self.members_tree["columns"] = columns
            for col in columns:
                self.members_tree.heading(col, text=col)
                self.members_tree.column(col, width=100)
            for row in data:
                self.members_tree.insert("", tk.END, values=row)
            if not data:
                messagebox.showinfo("Info", "No executive members found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_org_roles(self):
        org = self.roles_org_var.get()
        role = self.roles_role_var.get()

        if not (org and role):
            messagebox.showwarning("Input Error", "Please select both organization and role.")
            return

        try:
            data, columns = get_org_roles(org, role)

            for widget in self.roles_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("No Results", f"No {role}s found for {org}.")
                return

            tree = ttk.Treeview(self.roles_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=120)
            vsb = ttk.Scrollbar(self.roles_tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def show_late_payments(self):
        org = self.unpaid_org_var.get()
        acad_yr = self.acad_yr_var.get().strip()
        semester = self.semester_var.get().strip()

        if not org or not acad_yr or not semester:
            messagebox.showwarning("Warning", "Fill in org, academic year, and semester.")
            return

        try:
            semester = int(semester)
        except ValueError:
            messagebox.showerror("Error", "Semester must be a number.")
            return

        try:
            data, columns = get_late_payments(org, acad_yr, semester)
            for widget in self.unpaid_tree_frame.winfo_children():
                widget.destroy()

            tree = ttk.Treeview(self.unpaid_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.title())
                tree.column(col, width=100)
            vsb = ttk.Scrollbar(self.unpaid_tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

            if data:
                total = sum(float(row[columns.index("amount")]) for row in data)
                messagebox.showinfo("Summary", f"{len(data)} late payments. Total: ₱{total:.2f}")
            else:
                messagebox.showinfo("Info", "No late payments found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_active_percentage(self):
        org = self.stats_org_var.get()
        acad = self.stats_acad_var.get()
        sem = self.stats_sem_var.get()

        if not org or not acad or not sem:
            messagebox.showwarning("Input Error", "Please provide all fields.")
            return

        try:
            sem = int(sem)
            result, columns = get_active_percentage(org, acad, sem)

            for widget in self.stats_tree_frame.winfo_children():
                widget.destroy()

            if not result:
                messagebox.showinfo("Info", "No data found for the selected inputs.")
                return

            tree = ttk.Treeview(self.stats_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=150)
            vsb = ttk.Scrollbar(self.stats_tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            tree.insert("", tk.END, values=result)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_fee_summary(self):
        org = self.summary_org_var.get()
        if not org:
            messagebox.showwarning("Input Error", "Please select an organization.")
            return

        try:
            data, columns = get_fee_summary_by_org(org)

            for widget in self.summary_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("Info", "No fee summary available.")
                return

            tree = ttk.Treeview(self.summary_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.title())
                tree.column(col, width=150)
            vsb = ttk.Scrollbar(self.summary_tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_highest_debt(self):
        org = self.debt_org_var.get()
        acad_yr = self.debt_yr_var.get().strip()
        semester = self.debt_sem_var.get().strip()

        if not (org and acad_yr and semester):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        try:
            semester = int(semester)
        except ValueError:
            messagebox.showerror("Error", "Semester must be a number.")
            return

        try:
            data, columns = get_highest_debt_members(org, acad_yr, semester)

            for widget in self.debt_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("Info", "No unpaid debts found.")
                return

            tree = ttk.Treeview(self.debt_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=120)
            vsb = ttk.Scrollbar(self.debt_tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

            max_amount = data[0][columns.index("amount")]
            messagebox.showinfo("Summary", f"Highest unpaid amount: ₱{max_amount:.2f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_alumni_members(self):
        org = self.alumni_org_var.get()
        acad_yr = self.alumni_yr_var.get().strip()
        sem = self.alumni_sem_var.get().strip()

        if not (org and acad_yr and sem):
            messagebox.showwarning("Input Error", "Please complete all fields.")
            return
        try:
            sem = int(sem)
        except ValueError:
            messagebox.showerror("Input Error", "Semester must be a number.")
            return

        try:
            data, columns = get_alumni_members(org, acad_yr, sem)

            for widget in self.alumni_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("No Results", f"No alumni found for {org} ({acad_yr} Sem {sem}).")
                return

            tree = ttk.Treeview(self.alumni_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=120)
            vsb = ttk.Scrollbar(self.alumni_tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_unpaid_membership_fees(self):
        member_id = self.unpaid_member_id_var.get().strip()

        if not member_id:
            messagebox.showwarning("Input Error", "Please enter a member ID.")
            return

        try:
            member_id = int(member_id)
        except ValueError:
            messagebox.showerror("Input Error", "Member ID must be a number.")
            return

        try:
            data, columns = get_unpaid_membership_fees(member_id)

            for widget in self.unpaid_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("No Results", f"No unpaid membership fees found for member ID {member_id}.")
                return

            tree = ttk.Treeview(self.unpaid_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=120)
            vsb = ttk.Scrollbar(self.unpaid_tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_completed_membership_fees(self):
        member_id = self.completed_member_id_var.get().strip()

        if not member_id:
            messagebox.showwarning("Input Error", "Please enter a member ID.")
            return

        try:
            member_id = int(member_id)
        except ValueError:
            messagebox.showerror("Input Error", "Member ID must be a number.")
            return

        try:
            data, columns = get_completed_membership_fees(member_id)

            for widget in self.completed_tree_frame.winfo_children():
                widget.destroy()

            if not data:
                messagebox.showinfo("No Results", f"No completed membership fees found for member ID {member_id}.")
                return

            tree = ttk.Treeview(self.completed_tree_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=120)
            vsb = ttk.Scrollbar(self.completed_tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            for row in data:
                tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
