import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import hashlib
from datetime import datetime
from dotenv import load_dotenv
import os

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


load_dotenv()


# =========================================================
# DATABASE
# =========================================================

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="hauling_app",
        password=os.getenv("MYSQL_PASSWORD"),
        database="bbasic_hauling"
    )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()
root.title("Basic Hauling & Logistic Inc. - Encoding System")
root.geometry("1250x780")
root.minsize(1100, 700)


# =========================================================
# COLORS
# =========================================================

BG = "#f5f6f8"
WHITE = "#ffffff"
DARK = "#1f2937"
TEXT = "#111827"
MUTED = "#6b7280"
BORDER = "#d1d5db"
ACCENT = "#0f4c81"
DANGER = "#b91c1c"

root.configure(bg=BG)


# =========================================================
# LOGO
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "basic_hauling_logo.png")


# =========================================================
# STYLES
# =========================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass


style.configure(
    "TButton",
    font=("Segoe UI", 10),
    padding=(12, 7)
)

style.configure(
    "Primary.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(16, 9)
)

style.configure(
    "Danger.TButton",
    font=("Segoe UI", 10, "bold"),
    foreground=DANGER,
    padding=(12, 7)
)

style.configure(
    "TEntry",
    font=("Segoe UI", 10),
    padding=7
)

style.configure(
    "TCombobox",
    font=("Segoe UI", 10),
    padding=6
)

style.configure(
    "Treeview",
    font=("Segoe UI", 9),
    rowheight=30,
    background=WHITE,
    fieldbackground=WHITE,
    foreground=TEXT
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 9, "bold"),
    padding=8
)

style.map(
    "Treeview",
    background=[("selected", "#dbeafe")],
    foreground=[("selected", TEXT)]
)


# =========================================================
# GLOBAL STATE
# =========================================================

current_truck_id = None
current_plate = ""
truck_map = {}

login_logo_image = None
workspace_logo_image = None


# =========================================================
# HELPERS
# =========================================================

def load_logo(master, max_width=None):
    """Load the company logo. Returns None if the file is missing."""

    if not os.path.exists(LOGO_PATH):
        return None

    try:
        image = tk.PhotoImage(file=LOGO_PATH)

        if max_width and image.width() > max_width:
            factor = max(
                1,
                (image.width() + max_width - 1) // max_width
            )

            image = image.subsample(
                factor,
                factor
            )

        return image

    except tk.TclError:
        return None


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def show_error(title, message):
    messagebox.showerror(
        title,
        message
    )


# =========================================================
# LOGIN
# =========================================================

def show_login():
    global login_logo_image

    clear_window()

    root.geometry("1250x780")

    # -----------------------------------------------------
    # CENTER LOGIN CARD
    # -----------------------------------------------------

    outer = tk.Frame(
        root,
        bg=BG
    )

    outer.pack(
        fill="both",
        expand=True
    )

    card = tk.Frame(
        outer,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=430,
        height=510
    )

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    login_logo_image = load_logo(card)

    if login_logo_image:

        logo_label = tk.Label(
            card,
            image=login_logo_image,
            bg=WHITE,
            bd=0
        )

        logo_label.pack(
            pady=(25, 5)
        )

    else:

        tk.Label(
            card,
            text="BASIC",
            font=("Segoe UI", 28, "bold"),
            fg="#c00000",
            bg=WHITE
        ).pack(
            pady=(35, 5)
        )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    tk.Label(
        card,
        text="Basic Hauling & Logistic Inc.",
        font=("Segoe UI", 17, "bold"),
        fg=DARK,
        bg=WHITE
    ).pack()

    tk.Label(
        card,
        text="Fuel & Transportation Encoding System",
        font=("Segoe UI", 10),
        fg=MUTED,
        bg=WHITE
    ).pack(
        pady=(3, 28)
    )

    # -----------------------------------------------------
    # LOGIN FORM
    # -----------------------------------------------------

    form = tk.Frame(
        card,
        bg=WHITE
    )

    form.pack(
        fill="x",
        padx=55
    )

    tk.Label(
        form,
        text="Username",
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg=WHITE
    ).pack(
        anchor="w"
    )

    username_entry = ttk.Entry(form)

    username_entry.pack(
        fill="x",
        pady=(6, 16)
    )

    tk.Label(
        form,
        text="Password",
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg=WHITE
    ).pack(
        anchor="w"
    )

    password_entry = ttk.Entry(
        form,
        show="*"
    )

    password_entry.pack(
        fill="x",
        pady=(6, 24)
    )

    # -----------------------------------------------------
    # LOGIN FUNCTION
    # -----------------------------------------------------

    def login():

        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:

            show_error(
                "Login",
                "Please enter your username and password."
            )

            return

        password_hash = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username = %s
                AND password_hash = %s
                LIMIT 1
                """,
                (
                    username,
                    password_hash
                )
            )

            result = cursor.fetchone()

            if result:

                show_workspace()

            else:

                show_error(
                    "Login Failed",
                    "Invalid username or password."
                )

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # -----------------------------------------------------
    # LOGIN BUTTON
    # -----------------------------------------------------

    ttk.Button(
        form,
        text="LOGIN",
        style="Primary.TButton",
        command=login
    ).pack(
        fill="x"
    )

    tk.Label(
        card,
        text="",
        bg=WHITE
    ).pack()

    username_entry.focus_set()

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )


# =========================================================
# WORKSPACE
# =========================================================

def show_workspace():

    global current_truck_id
    global current_plate
    global workspace_logo_image

    clear_window()

    root.geometry("1250x780")

    # =====================================================
    # HEADER
    # =====================================================

    header = tk.Frame(
        root,
        bg=WHITE,
        height=92
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)

    title_frame = tk.Frame(
        header,
        bg=WHITE
    )

    title_frame.pack(
        side="left",
        fill="y",
        padx=28
    )

    tk.Label(
        title_frame,
        text="ENCODE RECORDS",
        font=("Segoe UI", 22, "bold"),
        fg=DARK,
        bg=WHITE
    ).pack(
        anchor="w",
        pady=(18, 0)
    )

    tk.Label(
        title_frame,
        text="Fuel and transportation record management",
        font=("Segoe UI", 9),
        fg=MUTED,
        bg=WHITE
    ).pack(
        anchor="w"
    )

    workspace_logo_image = load_logo(header)

    if workspace_logo_image:

        logo_label = tk.Label(
            header,
            image=workspace_logo_image,
            bg=WHITE,
            bd=0
        )

        logo_label.pack(
            side="right",
            padx=25
        )

    # =====================================================
    # CONTENT
    # =====================================================

    content = tk.Frame(
        root,
        bg=BG
    )

    content.pack(
        fill="both",
        expand=True,
        padx=22,
        pady=(12, 12)
    )

    # =====================================================
    # TRUCK / SEARCH BAR
    # =====================================================

    top_bar = tk.Frame(
        content,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    top_bar.pack(
        fill="x",
        pady=(0, 10)
    )

    # -----------------------------------------------------
    # TRUCK SECTION
    # -----------------------------------------------------

    truck_section = tk.Frame(
        top_bar,
        bg=WHITE
    )

    truck_section.pack(
        side="left",
        padx=14,
        pady=11
    )

    tk.Label(
        truck_section,
        text="TRUCK",
        font=("Segoe UI", 9, "bold"),
        fg=MUTED,
        bg=WHITE
    ).grid(
        row=0,
        column=0,
        sticky="w"
    )

    truck_var = tk.StringVar()

    truck_combo = ttk.Combobox(
        truck_section,
        textvariable=truck_var,
        state="readonly",
        width=19
    )

    truck_combo.grid(
        row=1,
        column=0,
        padx=(0, 8),
        pady=(4, 0)
    )

    ttk.Button(
        truck_section,
        text="Add Truck",
        command=lambda: add_truck()
    ).grid(
        row=1,
        column=1,
        padx=3,
        pady=(4, 0)
    )

    ttk.Button(
        truck_section,
        text="Edit Truck",
        command=lambda: edit_truck()
    ).grid(
        row=1,
        column=2,
        padx=3,
        pady=(4, 0)
    )

    ttk.Button(
        truck_section,
        text="Delete Truck",
        style="Danger.TButton",
        command=lambda: delete_truck()
    ).grid(
        row=1,
        column=3,
        padx=3,
        pady=(4, 0)
    )

    # -----------------------------------------------------
    # SEARCH SECTION
    # -----------------------------------------------------

    search_section = tk.Frame(
        top_bar,
        bg=WHITE
    )

    search_section.pack(
        side="right",
        padx=14,
        pady=11
    )

    tk.Label(
        search_section,
        text="SEARCH RECORDS",
        font=("Segoe UI", 9, "bold"),
        fg=MUTED,
        bg=WHITE
    ).grid(
        row=0,
        column=0,
        columnspan=4,
        sticky="w"
    )

    search_entry = ttk.Entry(
        search_section,
        width=31
    )

    search_entry.grid(
        row=1,
        column=0,
        padx=(0, 7),
        pady=(4, 0)
    )

    def perform_search():

        load_records(
            search_entry.get().strip()
        )

    ttk.Button(
        search_section,
        text="Search",
        command=perform_search
    ).grid(
        row=1,
        column=1,
        pady=(4, 0)
    )

    def clear_search():

        search_entry.delete(
            0,
            tk.END
        )

        load_records()

        search_entry.focus_set()

    ttk.Button(
        search_section,
        text="Clear",
        command=clear_search
    ).grid(
        row=1,
        column=2,
        padx=(6, 0),
        pady=(4, 0)
    )

    # Lambda is intentional because export_to_excel is
    # defined later inside show_workspace().
    ttk.Button(
        search_section,
        text="Export to Excel",
        command=lambda: export_to_excel()
    ).grid(
        row=1,
        column=3,
        padx=(6, 0),
        pady=(4, 0)
    )

    search_entry.bind(
        "<Return>",
        lambda event: perform_search()
    )

    # =====================================================
    # NEW RECORD FORM
    # =====================================================

    form_frame = tk.LabelFrame(
        content,
        text="  NEW RECORD  ",
        font=("Segoe UI", 10, "bold"),
        fg=DARK,
        bg=WHITE,
        bd=1,
        relief="solid",
        padx=14,
        pady=12
    )

    form_frame.pack(
        fill="x",
        pady=(0, 10)
    )

    date_var = tk.StringVar(
        value=datetime.now().strftime("%Y-%m-%d")
    )

    atw_var = tk.StringVar()
    destination_var = tk.StringVar()
    liters_var = tk.StringVar()
    amount_var = tk.StringVar()

    previous_odo_var = tk.StringVar(
        value="N/A"
    )

    current_odo_var = tk.StringVar()

    distance_var = tk.StringVar(
        value="N/A"
    )

    efficiency_var = tk.StringVar(
        value="N/A"
    )

    fields = [
        ("Date", date_var, 0),
        ("ATW Number", atw_var, 1),
        ("Destination", destination_var, 2),
        ("Liters", liters_var, 3),
        ("Total Amount", amount_var, 4),
        ("Previous ODO", previous_odo_var, 5),
        ("Current ODO", current_odo_var, 6),
    ]

    entries = {}

    for label_text, variable, column in fields:

        cell = tk.Frame(
            form_frame,
            bg=WHITE
        )

        cell.grid(
            row=0,
            column=column,
            padx=6,
            sticky="nsew"
        )

        tk.Label(
            cell,
            text=label_text,
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=WHITE
        ).pack(
            anchor="w"
        )

        entry = ttk.Entry(
            cell,
            textvariable=variable,
            width=16
        )

        if label_text == "Previous ODO":

            entry.configure(
                state="readonly"
            )

        entry.pack(
            fill="x",
            pady=(4, 0)
        )

        entries[label_text] = entry

        form_frame.grid_columnconfigure(
            column,
            weight=1
        )

    # -----------------------------------------------------
    # CALCULATED VALUES
    # -----------------------------------------------------

    calc_frame = tk.Frame(
        form_frame,
        bg="#f8fafc"
    )

    calc_frame.grid(
        row=1,
        column=0,
        columnspan=7,
        sticky="ew",
        padx=6,
        pady=(12, 0)
    )

    tk.Label(
        calc_frame,
        text="Distance",
        font=("Segoe UI", 8, "bold"),
        fg=MUTED,
        bg="#f8fafc"
    ).grid(
        row=0,
        column=0,
        padx=(10, 4),
        pady=8,
        sticky="w"
    )

    tk.Label(
        calc_frame,
        textvariable=distance_var,
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg="#f8fafc"
    ).grid(
        row=0,
        column=1,
        padx=(0, 30),
        pady=8,
        sticky="w"
    )

    tk.Label(
        calc_frame,
        text="Fuel Efficiency",
        font=("Segoe UI", 8, "bold"),
        fg=MUTED,
        bg="#f8fafc"
    ).grid(
        row=0,
        column=2,
        padx=(0, 4),
        pady=8,
        sticky="w"
    )

    tk.Label(
        calc_frame,
        textvariable=efficiency_var,
        font=("Segoe UI", 10, "bold"),
        fg=TEXT,
        bg="#f8fafc"
    ).grid(
        row=0,
        column=3,
        padx=(0, 10),
        pady=8,
        sticky="w"
    )

    # =====================================================
    # ODO CALCULATION
    # =====================================================

    def calculate_odo(*args):

        try:

            current_text = current_odo_var.get().strip()

            if not current_text:

                distance_var.set("N/A")
                efficiency_var.set("N/A")

                return

            current = float(
                current_text
            )

            previous_text = previous_odo_var.get().strip()

            if previous_text == "N/A" or not previous_text:

                distance_var.set("N/A")
                efficiency_var.set("N/A")

                return

            previous = float(
                previous_text
            )

            if current < previous:

                distance_var.set("Invalid ODO")
                efficiency_var.set("Invalid ODO")

                return

            distance = current - previous

            distance_var.set(
                f"{distance:,.2f}"
            )

            try:

                liters = float(
                    liters_var.get().strip()
                )

                if liters <= 0:

                    efficiency_var.set("N/A")

                else:

                    efficiency = distance / liters

                    efficiency_var.set(
                        f"{efficiency:,.2f} km/L"
                    )

            except ValueError:

                efficiency_var.set("N/A")

        except ValueError:

            distance_var.set("N/A")
            efficiency_var.set("N/A")

    current_odo_var.trace_add(
        "write",
        calculate_odo
    )

    liters_var.trace_add(
        "write",
        calculate_odo
    )

    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form():

        date_var.set(
            datetime.now().strftime("%Y-%m-%d")
        )

        atw_var.set("")
        destination_var.set("")
        liters_var.set("")
        amount_var.set("")
        current_odo_var.set("")

        distance_var.set("N/A")
        efficiency_var.set("N/A")

        refresh_previous_odo()

        entries["ATW Number"].focus_set()

    # =====================================================
    # SAVE RECORD
    # =====================================================

    def save_record():

        global current_truck_id

        if current_truck_id is None:

            show_error(
                "Save Record",
                "Please select a truck first."
            )

            return

        date_text = date_var.get().strip()
        atw = atw_var.get().strip()
        destination = destination_var.get().strip()
        liters_text = liters_var.get().strip()
        amount_text = amount_var.get().strip()
        current_odo_text = current_odo_var.get().strip()

        if not all([
            date_text,
            atw,
            destination,
            liters_text,
            amount_text,
            current_odo_text
        ]):

            show_error(
                "Save Record",
                "Please complete all required fields."
            )

            return

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        try:

            datetime.strptime(
                date_text,
                "%Y-%m-%d"
            )

        except ValueError:

            show_error(
                "Invalid Date",
                "Use the date format YYYY-MM-DD."
            )

            return

        # -------------------------------------------------
        # LITERS
        # -------------------------------------------------

        try:

            liters = float(
                liters_text
            )

            if liters <= 0:
                raise ValueError

        except ValueError:

            show_error(
                "Invalid Liters",
                "Please enter a valid liters value."
            )

            return

        # -------------------------------------------------
        # AMOUNT
        # -------------------------------------------------

        try:

            amount = float(
                amount_text
                .replace(",", "")
                .replace("₱", "")
                .strip()
            )

            if amount < 0:
                raise ValueError

        except ValueError:

            show_error(
                "Invalid Amount",
                "Please enter a valid total amount."
            )

            return

        # -------------------------------------------------
        # CURRENT ODO
        # -------------------------------------------------

        try:

            current_odo = float(
                current_odo_text
            )

        except ValueError:

            show_error(
                "Invalid ODO",
                "Please enter a valid Current ODO."
            )

            return

        previous_odo = get_previous_odo(
            current_truck_id
        )

        if (
            previous_odo is not None
            and current_odo < previous_odo
        ):

            show_error(
                "Invalid ODO",
                f"Current ODO cannot be lower than "
                f"Previous ODO ({previous_odo:,.2f})."
            )

            return

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                INSERT INTO truck_records
                (
                    truck_id,
                    atw_number,
                    date,
                    destination,
                    liters,
                    amount,
                    previous_odo,
                    current_odo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    current_truck_id,
                    atw,
                    date_text,
                    destination,
                    liters,
                    amount,
                    previous_odo,
                    current_odo
                )
            )

            db.commit()

            load_records()

            clear_form()

            # Keep newest saved record selected.
            if record_tree.get_children():

                first_item = (
                    record_tree.get_children()[0]
                )

                record_tree.selection_set(
                    first_item
                )

                record_tree.focus(
                    first_item
                )

                record_tree.see(
                    first_item
                )

        except mysql.connector.Error as err:

            if db:
                db.rollback()

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # ENTER KEY ENCODING
    # =====================================================

    encoding_order = [
        "ATW Number",
        "Destination",
        "Liters",
        "Total Amount",
        "Current ODO",
    ]

    def encoding_enter(event):

        widget = event.widget

        current_name = next(
            (
                name
                for name, entry in entries.items()
                if entry is widget
            ),
            None
        )

        if current_name not in encoding_order:
            return "break"

        index = encoding_order.index(
            current_name
        )

        # Shift + Enter = previous field
        if event.state & 0x0001:

            if index > 0:

                entries[
                    encoding_order[index - 1]
                ].focus_set()

            return "break"

        # Enter on Current ODO = save
        if index == len(encoding_order) - 1:

            save_record()

            return "break"

        # Normal Enter = next field
        entries[
            encoding_order[index + 1]
        ].focus_set()

        return "break"

    for name in encoding_order:

        entries[name].bind(
            "<Return>",
            encoding_enter
        )

        entries[name].bind(
            "<KP_Enter>",
            encoding_enter
        )

    # =====================================================
    # RECORDS TABLE
    # =====================================================

    table_frame = tk.Frame(
        content,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    table_frame.pack(
        fill="both",
        expand=True
    )

    table_title = tk.Frame(
        table_frame,
        bg=WHITE
    )

    table_title.pack(
        fill="x",
        padx=12,
        pady=(9, 5)
    )

    tk.Label(
        table_title,
        text="ENCODED RECORDS",
        font=("Segoe UI", 10, "bold"),
        fg=DARK,
        bg=WHITE
    ).pack(
        side="left"
    )

    tk.Label(
        table_title,
        text="Newest record appears first",
        font=("Segoe UI", 8),
        fg=MUTED,
        bg=WHITE
    ).pack(
        side="left",
        padx=12
    )

    tree_container = tk.Frame(
        table_frame,
        bg=WHITE
    )

    tree_container.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 10)
    )

    columns = (
        "number",
        "atw",
        "date",
        "destination",
        "liters",
        "amount",
        "previous_odo",
        "current_odo",
        "distance",
        "efficiency"
    )

    record_tree = ttk.Treeview(
        tree_container,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    headings = {
        "number": "#",
        "atw": "ATW Number",
        "date": "Date",
        "destination": "Destination",
        "liters": "Liters",
        "amount": "Total Amount",
        "previous_odo": "Previous ODO",
        "current_odo": "Current ODO",
        "distance": "Distance",
        "efficiency": "Fuel Efficiency"
    }

    widths = {
        "number": 45,
        "atw": 120,
        "date": 95,
        "destination": 190,
        "liters": 80,
        "amount": 105,
        "previous_odo": 105,
        "current_odo": 105,
        "distance": 95,
        "efficiency": 110
    }

    for column in columns:

        record_tree.heading(
            column,
            text=headings[column]
        )

        record_tree.column(
            column,
            width=widths[column],
            minwidth=widths[column],
            anchor="center"
        )

    record_tree.column(
        "destination",
        anchor="w"
    )

    vertical_scroll = ttk.Scrollbar(
        tree_container,
        orient="vertical",
        command=record_tree.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        tree_container,
        orient="horizontal",
        command=record_tree.xview
    )

    record_tree.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    record_tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    vertical_scroll.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    horizontal_scroll.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    tree_container.grid_rowconfigure(
        0,
        weight=1
    )

    tree_container.grid_columnconfigure(
        0,
        weight=1
    )

    record_tree.tag_configure(
        "even",
        background="#f9fafb"
    )

    record_tree.tag_configure(
        "odd",
        background="#ffffff"
    )

    # =====================================================
    # BOTTOM BAR
    # =====================================================

    bottom_bar = tk.Frame(
        content,
        bg=BG
    )

    bottom_bar.pack(
        fill="x",
        pady=(10, 0)
    )

    ttk.Button(
        bottom_bar,
        text="LOGOUT",
        command=show_login
    ).pack(
        side="right"
    )

    # =====================================================
    # DATABASE FUNCTIONS
    # =====================================================

    def get_previous_odo(truck_id):

        previous_odo = None

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT current_odo
                FROM truck_records
                WHERE truck_id = %s
                AND current_odo IS NOT NULL
                ORDER BY id DESC
                LIMIT 1
                """,
                (truck_id,)
            )

            result = cursor.fetchone()

            if result:

                previous_odo = float(
                    result[0]
                )

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

        return previous_odo

    # =====================================================
    # REFRESH PREVIOUS ODO
    # =====================================================

    def refresh_previous_odo():

        if current_truck_id is None:

            previous_odo_var.set(
                "N/A"
            )

        else:

            previous = get_previous_odo(
                current_truck_id
            )

            if previous is None:

                previous_odo_var.set(
                    "N/A"
                )

            else:

                previous_odo_var.set(
                    f"{previous:,.2f}"
                )

        calculate_odo()

    # =====================================================
    # LOAD RECORDS
    # =====================================================

    def load_records(search_text=""):

        for item in record_tree.get_children():

            record_tree.delete(
                item
            )

        if current_truck_id is None:
            return

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            if search_text:

                pattern = f"%{search_text}%"

                cursor.execute(
                    """
                    SELECT
                        id,
                        atw_number,
                        date,
                        destination,
                        liters,
                        amount,
                        previous_odo,
                        current_odo
                    FROM truck_records
                    WHERE truck_id = %s
                    AND (
                        atw_number LIKE %s
                        OR destination LIKE %s
                        OR CAST(date AS CHAR) LIKE %s
                    )
                    ORDER BY id DESC
                    """,
                    (
                        current_truck_id,
                        pattern,
                        pattern,
                        pattern
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        id,
                        atw_number,
                        date,
                        destination,
                        liters,
                        amount,
                        previous_odo,
                        current_odo
                    FROM truck_records
                    WHERE truck_id = %s
                    ORDER BY id DESC
                    """,
                    (current_truck_id,)
                )

            rows = cursor.fetchall()

            # -------------------------------------------------
            # NUMBERING
            # -------------------------------------------------
            # Oldest record = #1
            # Newest record = highest number

            display_rows = list(
                reversed(rows)
            )

            number_map = {}

            for index, row in enumerate(
                display_rows,
                start=1
            ):

                number_map[row[0]] = index

            # -------------------------------------------------
            # DISPLAY ROWS
            # -------------------------------------------------

            for row_index, row in enumerate(rows):

                record_id = row[0]
                atw = row[1]
                date_value = row[2]
                destination = row[3]

                liters = (
                    float(row[4])
                    if row[4] is not None
                    else 0
                )

                amount = (
                    float(row[5])
                    if row[5] is not None
                    else 0
                )

                previous = row[6]
                current = row[7]

                # Date
                if hasattr(
                    date_value,
                    "strftime"
                ):

                    date_display = (
                        date_value.strftime(
                            "%Y-%m-%d"
                        )
                    )

                else:

                    date_display = str(
                        date_value
                    )

                # Previous ODO
                previous_display = (
                    f"{float(previous):,.2f}"
                    if previous is not None
                    else "N/A"
                )

                # Current ODO
                current_display = (
                    f"{float(current):,.2f}"
                    if current is not None
                    else "N/A"
                )

                # Distance / Efficiency
                if (
                    previous is not None
                    and current is not None
                ):

                    distance = (
                        float(current)
                        - float(previous)
                    )

                    if distance >= 0:

                        distance_display = (
                            f"{distance:,.2f}"
                        )

                        if liters > 0:

                            efficiency_display = (
                                f"{distance / liters:,.2f} km/L"
                            )

                        else:

                            efficiency_display = "N/A"

                    else:

                        distance_display = "Invalid"
                        efficiency_display = "Invalid"

                else:

                    distance_display = "N/A"
                    efficiency_display = "N/A"

                values = (
                    number_map[record_id],
                    atw,
                    date_display,
                    destination,
                    f"{liters:,.2f}",
                    f"₱{amount:,.2f}",
                    previous_display,
                    current_display,
                    distance_display,
                    efficiency_display
                )

                tag = (
                    "even"
                    if row_index % 2 == 0
                    else "odd"
                )

                record_tree.insert(
                    "",
                    "end",
                    iid=str(record_id),
                    values=values,
                    tags=(tag,)
                )

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # EXPORT TO EXCEL
    # =====================================================

    def export_to_excel():

        if current_truck_id is None:

            show_error(
                "Export to Excel",
                "Please select a truck first."
            )

            return

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT
                    t.plate_number,
                    tr.atw_number,
                    tr.date,
                    tr.destination,
                    tr.liters,
                    tr.amount,
                    tr.previous_odo,
                    tr.current_odo
                FROM truck_records tr
                JOIN trucks t
                    ON tr.truck_id = t.id
                WHERE tr.truck_id = %s
                ORDER BY tr.id DESC
                """,
                (current_truck_id,)
            )

            records = cursor.fetchall()

            if not records:

                show_error(
                    "Export to Excel",
                    "There are no records to export for this truck."
                )

                return

            plate = records[0][0]

            # -------------------------------------------------
            # ASK WHERE TO SAVE
            # -------------------------------------------------

            file_path = filedialog.asksaveasfilename(
                title="Export to Excel",
                defaultextension=".xlsx",
                filetypes=[
                    (
                        "Excel Workbook",
                        "*.xlsx"
                    )
                ],
                initialfile=(
                    f"{plate}_transportation_records.xlsx"
                )
            )

            if not file_path:
                return

            # -------------------------------------------------
            # CREATE EXCEL WORKBOOK
            # -------------------------------------------------

            workbook = Workbook()

            worksheet = workbook.active

            worksheet.title = (
                "Transportation Records"
            )

            # -------------------------------------------------
            # HEADERS
            # -------------------------------------------------

            headers = [
                "Plate Number",
                "ATW Number",
                "Date",
                "Destination",
                "Liters",
                "Total Amount",
                "Previous ODO",
                "Current ODO",
                "Distance",
                "Fuel Efficiency"
            ]

            worksheet.append(
                headers
            )

            # Header formatting
            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True
                )

                cell.alignment = Alignment(
                    horizontal="center"
                )

            # -------------------------------------------------
            # ADD RECORDS
            # -------------------------------------------------

            for record in records:

                (
                    plate_number,
                    atw,
                    date_value,
                    destination,
                    liters,
                    amount,
                    previous_odo,
                    current_odo
                ) = record

                # Calculate distance
                if (
                    previous_odo is not None
                    and current_odo is not None
                ):

                    distance = (
                        float(current_odo)
                        - float(previous_odo)
                    )

                    if distance >= 0:

                        distance_display = distance

                        if (
                            liters
                            and float(liters) > 0
                        ):

                            efficiency = (
                                distance
                                / float(liters)
                            )

                        else:

                            efficiency = None

                    else:

                        distance_display = None
                        efficiency = None

                else:

                    distance_display = None
                    efficiency = None

                worksheet.append(
                    [
                        plate_number,
                        atw,
                        date_value,
                        destination,
                        (
                            float(liters)
                            if liters is not None
                            else 0
                        ),
                        (
                            float(amount)
                            if amount is not None
                            else 0
                        ),
                        (
                            float(previous_odo)
                            if previous_odo is not None
                            else None
                        ),
                        (
                            float(current_odo)
                            if current_odo is not None
                            else None
                        ),
                        distance_display,
                        efficiency
                    ]
                )

            # -------------------------------------------------
            # DATE FORMAT
            # -------------------------------------------------

            for cell in worksheet["C"][1:]:

                if cell.value:

                    cell.number_format = (
                        "yyyy-mm-dd"
                    )

            # -------------------------------------------------
            # NUMBER FORMATS
            # -------------------------------------------------

            # Liters
            for cell in worksheet["E"][1:]:

                cell.number_format = (
                    '#,##0.00'
                )

            # Total Amount
            for cell in worksheet["F"][1:]:

                cell.number_format = (
                    '₱#,##0.00'
                )

            # Previous ODO
            for cell in worksheet["G"][1:]:

                cell.number_format = (
                    '#,##0.00'
                )

            # Current ODO
            for cell in worksheet["H"][1:]:

                cell.number_format = (
                    '#,##0.00'
                )

            # Distance
            for cell in worksheet["I"][1:]:

                cell.number_format = (
                    '#,##0.00'
                )

            # Fuel Efficiency
            for cell in worksheet["J"][1:]:

                cell.number_format = (
                    '0.00'
                )

            # -------------------------------------------------
            # COLUMN WIDTHS
            # -------------------------------------------------

            for column in worksheet.columns:

                max_length = 0

                column_letter = (
                    column[0].column_letter
                )

                for cell in column:

                    if cell.value is not None:

                        max_length = max(
                            max_length,
                            len(str(cell.value))
                        )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max_length + 2,
                    40
                )

            # -------------------------------------------------
            # EXCEL USABILITY
            # -------------------------------------------------

            worksheet.freeze_panes = "A2"

            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            # -------------------------------------------------
            # SAVE
            # -------------------------------------------------

            workbook.save(
                file_path
            )

            messagebox.showinfo(
                "Export Complete",
                "Records successfully exported to:\n\n"
                f"{file_path}"
            )

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        except Exception as err:

            show_error(
                "Export Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # ADD TRUCK
    # =====================================================

    def add_truck():

        dialog = tk.Toplevel(root)

        dialog.title(
            "Add Trucks"
        )

        dialog.geometry(
            "390x210"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            root
        )

        dialog.grab_set()

        tk.Label(
            dialog,
            text="Add Trucks",
            font=("Segoe UI", 15, "bold")
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            dialog,
            text="Plate Number",
            font=("Segoe UI", 10)
        ).pack()

        plate_entry = ttk.Entry(
            dialog,
            width=32
        )

        plate_entry.pack(
            pady=7
        )

        plate_entry.focus_set()

        def save_truck():

            plate = (
                plate_entry
                .get()
                .strip()
                .upper()
            )

            if not plate:

                show_error(
                    "Add Truck",
                    "Please enter a plate number."
                )

                plate_entry.focus_set()

                return

            db = None
            cursor = None

            try:

                db = connect_database()
                cursor = db.cursor()

                cursor.execute(
                    """
                    INSERT INTO trucks
                    (plate_number)
                    VALUES (%s)
                    """,
                    (plate,)
                )

                db.commit()

                load_trucks(
                    select_plate=plate
                )

                # Keep dialog open for fast encoding
                plate_entry.delete(
                    0,
                    tk.END
                )

                plate_entry.focus_set()

            except mysql.connector.IntegrityError:

                show_error(
                    "Add Truck",
                    "That plate number already exists."
                )

                plate_entry.focus_set()

            except mysql.connector.Error as err:

                show_error(
                    "Database Error",
                    str(err)
                )

                plate_entry.focus_set()

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()

        ttk.Button(
            dialog,
            text="ADD TRUCK",
            style="Primary.TButton",
            command=save_truck
        ).pack(
            pady=12
        )

        plate_entry.bind(
            "<Return>",
            lambda event: save_truck()
        )

    # =====================================================
    # EDIT TRUCK
    # =====================================================

    def edit_truck():

        global current_truck_id

        if current_truck_id is None:

            show_error(
                "Edit Truck",
                "Please select a truck."
            )

            return

        dialog = tk.Toplevel(root)

        dialog.title(
            "Edit Truck"
        )

        dialog.geometry(
            "390x190"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            root
        )

        dialog.grab_set()

        tk.Label(
            dialog,
            text="Edit Truck",
            font=("Segoe UI", 15, "bold")
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            dialog,
            text="Plate Number",
            font=("Segoe UI", 10)
        ).pack()

        plate_entry = ttk.Entry(
            dialog,
            width=32
        )

        plate_entry.insert(
            0,
            current_plate
        )

        plate_entry.pack(
            pady=7
        )

        plate_entry.focus_set()

        plate_entry.select_range(
            0,
            "end"
        )

        def save_edit():

            global current_plate

            plate = (
                plate_entry
                .get()
                .strip()
                .upper()
            )

            if not plate:

                show_error(
                    "Edit Truck",
                    "Please enter a plate number."
                )

                return

            db = None
            cursor = None

            try:

                db = connect_database()
                cursor = db.cursor()

                cursor.execute(
                    """
                    UPDATE trucks
                    SET plate_number = %s
                    WHERE id = %s
                    """,
                    (
                        plate,
                        current_truck_id
                    )
                )

                db.commit()

                dialog.destroy()

                current_plate = plate

                load_trucks(
                    select_plate=plate
                )

            except mysql.connector.IntegrityError:

                show_error(
                    "Edit Truck",
                    "That plate number already exists."
                )

            except mysql.connector.Error as err:

                show_error(
                    "Database Error",
                    str(err)
                )

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()

        ttk.Button(
            dialog,
            text="SAVE CHANGES",
            style="Primary.TButton",
            command=save_edit
        ).pack(
            pady=12
        )

        plate_entry.bind(
            "<Return>",
            lambda event: save_edit()
        )

    # =====================================================
    # DELETE TRUCK
    # =====================================================

    def delete_truck():

        global current_truck_id
        global current_plate

        if current_truck_id is None:

            show_error(
                "Delete Truck",
                "Please select a truck."
            )

            return

        if not messagebox.askyesno(
            "Delete Truck",
            f"Delete truck {current_plate} "
            f"and all of its records?"
        ):

            return

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                DELETE FROM truck_records
                WHERE truck_id = %s
                """,
                (current_truck_id,)
            )

            cursor.execute(
                """
                DELETE FROM trucks
                WHERE id = %s
                """,
                (current_truck_id,)
            )

            db.commit()

            current_truck_id = None
            current_plate = ""

            load_trucks()

        except mysql.connector.Error as err:

            if db:
                db.rollback()

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # LOAD TRUCKS
    # =====================================================

    def load_trucks(select_plate=None):

        global current_truck_id
        global current_plate
        global truck_map

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    plate_number
                FROM trucks
                ORDER BY plate_number ASC
                """
            )

            rows = cursor.fetchall()

            truck_map = {
                plate: truck_id
                for truck_id, plate in rows
            }

            plates = [
                plate
                for _, plate in rows
            ]

            truck_combo["values"] = plates

            if not plates:

                current_truck_id = None
                current_plate = ""

                truck_var.set("")

                clear_form()

                load_records()

                return

            target = (
                select_plate
                if select_plate in plates
                else plates[0]
            )

            truck_var.set(
                target
            )

            current_plate = target

            current_truck_id = (
                truck_map[target]
            )

            clear_form()

            load_records()

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # CHANGE TRUCK
    # =====================================================

    def change_truck(event=None):

        global current_truck_id
        global current_plate

        plate = (
            truck_var
            .get()
            .strip()
        )

        if not plate:

            current_truck_id = None
            current_plate = ""

            clear_form()
            load_records()

            return

        current_plate = plate

        current_truck_id = (
            truck_map.get(plate)
        )

        clear_form()
        load_records()

    truck_combo.bind(
        "<<ComboboxSelected>>",
        change_truck
    )

    # =====================================================
    # EDIT RECORD
    # =====================================================

    def edit_record():

        global current_truck_id

        selected = record_tree.selection()

        if not selected:

            show_error(
                "Edit Record",
                "Please select a record from the table."
            )

            return

        record_id = int(
            selected[0]
        )

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT
                    atw_number,
                    date,
                    destination,
                    liters,
                    amount,
                    current_odo
                FROM truck_records
                WHERE id = %s
                AND truck_id = %s
                """,
                (
                    record_id,
                    current_truck_id
                )
            )

            record = cursor.fetchone()

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

            return

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

        if not record:

            show_error(
                "Edit Record",
                "Record not found."
            )

            return

        # -------------------------------------------------
        # EDIT WINDOW
        # -------------------------------------------------

        dialog = tk.Toplevel(root)

        dialog.title(
            "Edit Record"
        )

        dialog.geometry(
            "520x520"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            root
        )

        dialog.grab_set()

        tk.Label(
            dialog,
            text="Edit Record",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=(18, 4)
        )

        tk.Label(
            dialog,
            text=f"Truck: {current_plate}",
            font=("Segoe UI", 9),
            fg=MUTED
        ).pack(
            pady=(0, 15)
        )

        form = tk.Frame(
            dialog
        )

        form.pack(
            fill="x",
            padx=45
        )

        # -------------------------------------------------
        # EDIT VARIABLES
        # -------------------------------------------------

        edit_date = tk.StringVar(
            value=(
                record[1].strftime("%Y-%m-%d")
                if hasattr(
                    record[1],
                    "strftime"
                )
                else str(record[1])
            )
        )

        edit_atw = tk.StringVar(
            value=str(record[0])
        )

        edit_destination = tk.StringVar(
            value=str(record[2])
        )

        edit_liters = tk.StringVar(
            value=str(record[3])
        )

        edit_amount = tk.StringVar(
            value=str(record[4])
        )

        edit_current_odo = tk.StringVar(
            value=str(record[5])
        )

        edit_previous_odo = None

        # -------------------------------------------------
        # FIND PREVIOUS ODO
        # -------------------------------------------------

        db2 = None
        cursor2 = None

        try:

            db2 = connect_database()
            cursor2 = db2.cursor()

            cursor2.execute(
                """
                SELECT current_odo
                FROM truck_records
                WHERE truck_id = %s
                AND id < %s
                AND current_odo IS NOT NULL
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    current_truck_id,
                    record_id
                )
            )

            result = cursor2.fetchone()

            if result:

                edit_previous_odo = float(
                    result[0]
                )

        except mysql.connector.Error as err:

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor2:
                cursor2.close()

            if db2:
                db2.close()

        edit_distance = tk.StringVar(
            value="N/A"
        )

        edit_efficiency = tk.StringVar(
            value="N/A"
        )

        edit_fields = [
            ("Date", edit_date),
            ("ATW Number", edit_atw),
            ("Destination", edit_destination),
            ("Liters", edit_liters),
            ("Total Amount", edit_amount),
        ]

        edit_entries = {}

        for row_index, (
            label_text,
            variable
        ) in enumerate(edit_fields):

            tk.Label(
                form,
                text=label_text,
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=row_index,
                column=0,
                sticky="w",
                pady=6
            )

            entry = ttk.Entry(
                form,
                textvariable=variable,
                width=38
            )

            entry.grid(
                row=row_index,
                column=1,
                sticky="ew",
                pady=6
            )

            edit_entries[
                label_text
            ] = entry

        previous_display = (
            f"{edit_previous_odo:,.2f}"
            if edit_previous_odo is not None
            else "N/A"
        )

        tk.Label(
            form,
            text="Previous ODO",
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=5,
            column=0,
            sticky="w",
            pady=6
        )

        tk.Label(
            form,
            text=previous_display,
            font=("Segoe UI", 10, "bold"),
            fg=ACCENT
        ).grid(
            row=5,
            column=1,
            sticky="w",
            pady=6
        )

        tk.Label(
            form,
            text="Current ODO",
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=6
        )

        ttk.Entry(
            form,
            textvariable=edit_current_odo,
            width=38
        ).grid(
            row=6,
            column=1,
            sticky="ew",
            pady=6
        )

        # -------------------------------------------------
        # EDIT CALCULATIONS
        # -------------------------------------------------

        calc = tk.Frame(
            form,
            bg="#f8fafc"
        )

        calc.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 5)
        )

        tk.Label(
            calc,
            text="Distance:",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fafc"
        ).grid(
            row=0,
            column=0,
            padx=(10, 4),
            pady=9
        )

        tk.Label(
            calc,
            textvariable=edit_distance,
            font=("Segoe UI", 9),
            bg="#f8fafc"
        ).grid(
            row=0,
            column=1,
            padx=(0, 25),
            pady=9
        )

        tk.Label(
            calc,
            text="Fuel Efficiency:",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fafc"
        ).grid(
            row=0,
            column=2,
            padx=(0, 4),
            pady=9
        )

        tk.Label(
            calc,
            textvariable=edit_efficiency,
            font=("Segoe UI", 9),
            bg="#f8fafc"
        ).grid(
            row=0,
            column=3,
            padx=(0, 10),
            pady=9
        )

        def calculate_edit():

            try:

                current = float(
                    edit_current_odo
                    .get()
                    .strip()
                )

                if edit_previous_odo is None:

                    edit_distance.set(
                        "N/A"
                    )

                    edit_efficiency.set(
                        "N/A"
                    )

                    return

                if current < edit_previous_odo:

                    edit_distance.set(
                        "Invalid ODO"
                    )

                    edit_efficiency.set(
                        "Invalid ODO"
                    )

                    return

                distance = (
                    current
                    - edit_previous_odo
                )

                edit_distance.set(
                    f"{distance:,.2f}"
                )

                liters = float(
                    edit_liters
                    .get()
                    .strip()
                )

                if liters > 0:

                    edit_efficiency.set(
                        f"{distance / liters:,.2f} km/L"
                    )

                else:

                    edit_efficiency.set(
                        "N/A"
                    )

            except ValueError:

                edit_distance.set(
                    "N/A"
                )

                edit_efficiency.set(
                    "N/A"
                )

        edit_current_odo.trace_add(
            "write",
            lambda *args: calculate_edit()
        )

        edit_liters.trace_add(
            "write",
            lambda *args: calculate_edit()
        )

        # -------------------------------------------------
        # UPDATE RECORD
        # -------------------------------------------------

        def update_record():

            date_text = (
                edit_date
                .get()
                .strip()
            )

            atw = (
                edit_atw
                .get()
                .strip()
            )

            destination = (
                edit_destination
                .get()
                .strip()
            )

            liters_text = (
                edit_liters
                .get()
                .strip()
            )

            amount_text = (
                edit_amount
                .get()
                .strip()
            )

            current_odo_text = (
                edit_current_odo
                .get()
                .strip()
            )

            if not all([
                date_text,
                atw,
                destination,
                liters_text,
                amount_text,
                current_odo_text
            ]):

                show_error(
                    "Edit Record",
                    "Please complete all required fields."
                )

                return

            # Date
            try:

                datetime.strptime(
                    date_text,
                    "%Y-%m-%d"
                )

            except ValueError:

                show_error(
                    "Invalid Date",
                    "Use the date format YYYY-MM-DD."
                )

                return

            # Liters
            try:

                liters = float(
                    liters_text
                )

                if liters <= 0:
                    raise ValueError

            except ValueError:

                show_error(
                    "Invalid Liters",
                    "Please enter a valid liters value."
                )

                return

            # Amount
            try:

                amount = float(
                    amount_text
                    .replace(",", "")
                    .replace("₱", "")
                    .strip()
                )

                if amount < 0:
                    raise ValueError

            except ValueError:

                show_error(
                    "Invalid Amount",
                    "Please enter a valid total amount."
                )

                return

            # Current ODO
            try:

                current_odo = float(
                    current_odo_text
                )

            except ValueError:

                show_error(
                    "Invalid ODO",
                    "Please enter a valid Current ODO."
                )

                return

            if (
                edit_previous_odo is not None
                and current_odo < edit_previous_odo
            ):

                show_error(
                    "Invalid ODO",
                    f"Current ODO cannot be lower "
                    f"than Previous ODO "
                    f"({edit_previous_odo:,.2f})."
                )

                return

            db3 = None
            cursor3 = None

            try:

                db3 = connect_database()
                cursor3 = db3.cursor()

                cursor3.execute(
                    """
                    UPDATE truck_records
                    SET
                        atw_number = %s,
                        date = %s,
                        destination = %s,
                        liters = %s,
                        amount = %s,
                        current_odo = %s
                    WHERE id = %s
                    AND truck_id = %s
                    """,
                    (
                        atw,
                        date_text,
                        destination,
                        liters,
                        amount,
                        current_odo,
                        record_id,
                        current_truck_id
                    )
                )

                db3.commit()

                dialog.destroy()

                load_records(
                    search_entry.get().strip()
                )

                refresh_previous_odo()

            except mysql.connector.Error as err:

                if db3:
                    db3.rollback()

                show_error(
                    "Database Error",
                    str(err)
                )

            finally:

                if cursor3:
                    cursor3.close()

                if db3:
                    db3.close()

        ttk.Button(
            dialog,
            text="SAVE CHANGES",
            style="Primary.TButton",
            command=update_record
        ).pack(
            pady=(15, 8)
        )

        ttk.Button(
            dialog,
            text="CANCEL",
            command=dialog.destroy
        ).pack()

        calculate_edit()

    # =====================================================
    # DELETE RECORD
    # =====================================================

    def delete_record():

        global current_truck_id

        selected = record_tree.selection()

        if not selected:

            show_error(
                "Delete Record",
                "Please select a record from the table."
            )

            return

        record_id = int(
            selected[0]
        )

        if not messagebox.askyesno(
            "Delete Record",
            "Delete the selected record?"
        ):

            return

        db = None
        cursor = None

        try:

            db = connect_database()
            cursor = db.cursor()

            cursor.execute(
                """
                DELETE FROM truck_records
                WHERE id = %s
                AND truck_id = %s
                """,
                (
                    record_id,
                    current_truck_id
                )
            )

            db.commit()

            load_records(
                search_entry.get().strip()
            )

            refresh_previous_odo()

        except mysql.connector.Error as err:

            if db:
                db.rollback()

            show_error(
                "Database Error",
                str(err)
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    # =====================================================
    # RIGHT-CLICK RECORD MENU
    # =====================================================

    record_menu = tk.Menu(
        root,
        tearoff=0
    )

    record_menu.add_command(
        label="Edit Record",
        command=edit_record
    )

    record_menu.add_command(
        label="Delete Record",
        command=delete_record
    )

    def show_record_menu(event):

        row_id = record_tree.identify_row(
            event.y
        )

        # Do nothing on empty space.
        if not row_id:
            return

        # Select right-clicked row.
        record_tree.selection_set(
            row_id
        )

        record_tree.focus(
            row_id
        )

        try:

            record_menu.tk_popup(
                event.x_root,
                event.y_root
            )

        finally:

            record_menu.grab_release()

    record_tree.bind(
        "<Button-3>",
        show_record_menu
    )

    # =====================================================
    # INITIAL DATA LOAD
    # =====================================================

    load_trucks()


# =========================================================
# START APPLICATION
# =========================================================

show_login()

root.mainloop()