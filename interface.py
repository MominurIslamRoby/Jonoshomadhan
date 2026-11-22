import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path
from math import ceil

from storage import JSONStorage
from report_manager import ReportManager
from officer_manager import OfficerManager
from work_order_manager import WorkOrderManager


class JonoshomadhanApp:

    def __init__(self, root, issue_manager):
        self.root = root
        self.issue_manager = issue_manager
        self.report_manager = ReportManager(issue_manager)
        self.officer_manager = OfficerManager()
        self.work_order_manager = WorkOrderManager()

        self.root.title("JONOSHOMADHAN | Citizen Service Management")
        self.root.geometry("1480x900")
        self.root.minsize(1180, 760)
        self.root.configure(bg="#F3F6FA")

        self.asset_dir = Path(__file__).resolve().parent / "assets"
        self.logo_image = None
        self.app_icon = None

        self.load_brand_assets()

        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

        self.configure_styles()
        self.synchronize_issue_statuses()

        self.search_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="All Statuses")
        self.stat_labels = {}

        self.create_header()
        self.create_dashboard()
        self.create_request_section()
        self.refresh_table()


    def _load_scaled_image(self, image_path, max_width, max_height):
        image = tk.PhotoImage(file=str(image_path))

        scale_factor = max(
            1,
            ceil(image.width() / max_width),
            ceil(image.height() / max_height)
        )

        if scale_factor > 1:
            image = image.subsample(scale_factor, scale_factor)

        return image

    def load_brand_assets(self):
        logo_path = self.asset_dir / "jonoshomadhan_logo.png"
        icon_path = self.asset_dir / "jonoshomadhan_icon.png"

        try:
            if logo_path.exists():
                self.logo_image = self._load_scaled_image(
                    logo_path,
                    520,
                    92
                )

            if icon_path.exists():
                self.app_icon = self._load_scaled_image(
                    icon_path,
                    48,
                    48
                )
                self.root.iconphoto(True, self.app_icon)

            if not logo_path.exists():
                print(f"Brand logo not found: {logo_path}")

            if not icon_path.exists():
                print(f"Application icon not found: {icon_path}")

        except (tk.TclError, OSError) as error:
            messagebox.showwarning(
                "Brand Asset Warning",
                "Could not load one or more Jonoshomadhan brand assets.\n\n"
                f"{error}",
                parent=self.root
            )


    def configure_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#26364A",
            fieldbackground="#FFFFFF",
            rowheight=38,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#EAF0F7",
            foreground="#344B63",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(12, 10)
        )

        style.map(
            "Treeview",
            background=[("selected", "#DCEBFA")],
            foreground=[("selected", "#173B57")]
        )

        style.map(
            "Treeview.Heading",
            background=[("active", "#DCE6F0")]
        )

        style.configure(
            "TCombobox",
            padding=8,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 9)
        )

        style.configure(
            "TScrollbar",
            background="#D7E0EA",
            troughcolor="#F3F6FA",
            bordercolor="#F3F6FA",
            arrowcolor="#526579"
        )


    def synchronize_issue_statuses(self):
        status_map = {
            "Assigned": "Assigned",
            "Accepted": "In Progress",
            "In Progress": "In Progress",
            "Completed": "In Progress"
        }

        for order in self.work_order_manager.get_all_work_orders():
            verification = order.get(
                "verification_status",
                "Not Submitted"
            )

            if verification == "Verified":
                target_status = "Resolved"

            elif verification == "Rejected":
                target_status = "In Progress"

            else:
                target_status = status_map.get(
                    order.get("status")
                )

            if not target_status:
                continue

            issue = self.issue_manager.search_issue(
                order.get("issue_id", "")
            )

            if issue and issue.status != target_status:
                if not self.issue_manager.update_status(
                    issue.issue_id,
                    target_status
                ):
                    messagebox.showwarning(
                        "Synchronization Warning",
                        f"Could not synchronize complaint {issue.issue_id}. "
                        "Please check data/issues.json file permissions.",
                        parent=self.root
                    )

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    def create_header(self):
        header = tk.Frame(
            self.root,
            bg="#FFFFFF",
            height=112
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        # Explicit width prevents the logo container from collapsing
        # and clipping the image when geometry propagation is disabled.
        brand_area = tk.Frame(
            header,
            bg="#FFFFFF",
            width=560,
            height=100
        )

        brand_area.pack(side="left", padx=26, pady=6)
        brand_area.pack_propagate(False)

        if self.logo_image:
            tk.Label(
                brand_area,
                image=self.logo_image,
                bg="#FFFFFF",
                bd=0
            ).pack(
                side="left",
                anchor="center",
                padx=4,
                pady=3
            )

        else:
            tk.Label(
                brand_area,
                text="JONOSHOMADHAN",
                font=("Segoe UI", 22, "bold"),
                fg="#102F49",
                bg="#FFFFFF"
            ).pack(
                side="left",
                expand=True,
                anchor="w"
            )

        right_area = tk.Frame(
            header,
            bg="#FFFFFF"
        )

        right_area.pack(
            side="right",
            padx=32,
            pady=28
        )

        tk.Label(
            right_area,
            text="ADMINISTRATION CONSOLE",
            font=("Segoe UI", 9, "bold"),
            fg="#173B57",
            bg="#FFFFFF"
        ).pack(anchor="e")

        tk.Label(
            right_area,
            text=date.today().strftime("%A, %d %B %Y"),
            font=("Segoe UI", 10),
            fg="#718096",
            bg="#FFFFFF"
        ).pack(anchor="e", pady=(5, 0))

        tk.Frame(
            self.root,
            bg="#079C91",
            height=4
        ).pack(fill="x")


    def create_vector_icon(
        self,
        parent,
        icon_name,
        color,
        background="#FFFFFF",
        size=28
    ):
        canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg=background,
            highlightthickness=0,
            bd=0
        )

        center = size / 2
        stroke = max(1.7, size / 15)

        left = size * 0.25
        right = size * 0.75
        top = size * 0.18
        bottom = size * 0.82

        if icon_name == "document":
            canvas.create_rectangle(
                left + 2,
                top,
                right - 2,
                bottom,
                outline=color,
                width=stroke
            )

            canvas.create_line(
                left + 6,
                size * 0.40,
                right - 6,
                size * 0.40,
                fill=color,
                width=stroke
            )

            canvas.create_line(
                left + 6,
                size * 0.54,
                right - 6,
                size * 0.54,
                fill=color,
                width=stroke
            )

            canvas.create_line(
                left + 6,
                size * 0.68,
                size * 0.56,
                size * 0.68,
                fill=color,
                width=stroke
            )

        elif icon_name == "check":
            canvas.create_oval(
                left,
                top,
                right,
                bottom,
                outline=color,
                width=stroke
            )

            canvas.create_line(
                size * 0.34,
                size * 0.51,
                size * 0.46,
                size * 0.63,
                size * 0.68,
                size * 0.38,
                fill=color,
                width=stroke + 0.5,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )

        elif icon_name == "clock":
            canvas.create_oval(
                left,
                top,
                right,
                bottom,
                outline=color,
                width=stroke
            )

            canvas.create_line(
                center,
                size * 0.31,
                center,
                center,
                fill=color,
                width=stroke + 0.2,
                capstyle=tk.ROUND
            )

            canvas.create_line(
                center,
                center,
                size * 0.64,
                size * 0.60,
                fill=color,
                width=stroke + 0.2,
                capstyle=tk.ROUND
            )

        elif icon_name == "percent":
            canvas.create_line(
                size * 0.34,
                size * 0.68,
                size * 0.66,
                size * 0.32,
                fill=color,
                width=stroke + 0.2,
                capstyle=tk.ROUND
            )

            canvas.create_oval(
                size * 0.23,
                size * 0.22,
                size * 0.43,
                size * 0.42,
                outline=color,
                width=stroke
            )

            canvas.create_oval(
                size * 0.57,
                size * 0.58,
                size * 0.77,
                size * 0.78,
                outline=color,
                width=stroke
            )

        elif icon_name == "search":
            canvas.create_oval(
                size * 0.22,
                size * 0.20,
                size * 0.59,
                size * 0.57,
                outline=color,
                width=stroke
            )

            canvas.create_line(
                size * 0.53,
                size * 0.53,
                size * 0.78,
                size * 0.78,
                fill=color,
                width=stroke + 0.2,
                capstyle=tk.ROUND
            )

        elif icon_name == "refresh":
            canvas.create_arc(
                size * 0.20,
                size * 0.20,
                size * 0.80,
                size * 0.80,
                start=35,
                extent=285,
                style=tk.ARC,
                outline=color,
                width=stroke
            )

            canvas.create_line(
                size * 0.69,
                size * 0.20,
                size * 0.79,
                size * 0.22,
                size * 0.77,
                size * 0.33,
                fill=color,
                width=stroke,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )

        return canvas

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------

    def create_dashboard(self):
        self.dashboard = tk.Frame(
            self.root,
            bg="#F3F6FA"
        )

        self.dashboard.pack(
            fill="x",
            padx=30,
            pady=(14, 12)
        )

        intro = tk.Frame(
            self.dashboard,
            bg="#F3F6FA"
        )

        intro.pack(
            fill="x",
            pady=(0, 9)
        )

        tk.Label(
            intro,
            text="Overview",
            font=("Segoe UI", 17, "bold"),
            fg="#183B56",
            bg="#F3F6FA"
        ).pack(side="left")

        tk.Label(
            intro,
            text="Live summary of citizen service requests",
            font=("Segoe UI", 9),
            fg="#718096",
            bg="#F3F6FA"
        ).pack(
            side="left",
            padx=12,
            pady=(5, 0)
        )

        cards = [
            ("TOTAL REQUESTS", "total", "#2867A5", "document"),
            ("RESOLVED", "resolved", "#15966D", "check"),
            ("PENDING", "pending", "#D18A24", "clock"),
            ("RESOLUTION RATE", "resolution_percentage", "#7656C8", "percent")
        ]

        for title, key, accent, icon_name in cards:
            card = tk.Frame(
                self.dashboard,
                bg="#FFFFFF",
                highlightbackground="#E2E9F1",
                highlightthickness=1
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 13)
            )

            tk.Frame(
                card,
                bg=accent,
                width=5
            ).pack(side="left", fill="y")

            content = tk.Frame(
                card,
                bg="#FFFFFF"
            )

            content.pack(
                side="left",
                fill="both",
                expand=True,
                padx=17,
                pady=10
            )

            top = tk.Frame(
                content,
                bg="#FFFFFF"
            )

            top.pack(fill="x")

            tk.Label(
                top,
                text=title,
                font=("Segoe UI", 9, "bold"),
                fg="#78889A",
                bg="#FFFFFF"
            ).pack(side="left")

            self.create_vector_icon(
                top,
                icon_name,
                accent,
                background="#F3F7FB",
                size=34
            ).pack(side="right")

            value_label = tk.Label(
                content,
                text="0",
                font=("Segoe UI", 27, "bold"),
                fg="#183B56",
                bg="#FFFFFF"
            )

            value_label.pack(
                anchor="w",
                pady=(7, 0)
            )

            self.stat_labels[key] = value_label

        self.update_dashboard()

    def update_dashboard(self):
        summary = self.issue_manager.generate_summary()

        for key, label in self.stat_labels.items():
            value = summary.get(key, 0)

            if key == "resolution_percentage":
                value = f"{value}%"

            label.config(text=str(value))


    def create_request_section(self):
        section = tk.Frame(
            self.root,
            bg="#F3F6FA"
        )

        section.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 14)
        )

        title_row = tk.Frame(
            section,
            bg="#F3F6FA"
        )

        title_row.pack(
            fill="x",
            pady=(0, 8)
        )

        title_group = tk.Frame(
            title_row,
            bg="#F3F6FA"
        )

        title_group.pack(side="left")

        tk.Label(
            title_group,
            text="Service Requests",
            font=("Segoe UI", 18, "bold"),
            fg="#183B56",
            bg="#F3F6FA"
        ).pack(anchor="w")

        tk.Label(
            title_group,
            text="Review, assign and track citizen-reported issues",
            font=("Segoe UI", 9),
            fg="#718096",
            bg="#F3F6FA"
        ).pack(anchor="w", pady=(2, 0))

        toolbar = tk.Frame(
            section,
            bg="#FFFFFF",
            highlightbackground="#E2E9F1",
            highlightthickness=1
        )

        toolbar.pack(
            fill="x",
            pady=(0, 8)
        )

        search_area = tk.Frame(
            toolbar,
            bg="#FFFFFF"
        )

        search_area.pack(
            side="left",
            padx=13,
            pady=11
        )

        search_shell = tk.Frame(
            search_area,
            bg="#F6F8FB",
            highlightbackground="#DCE4ED",
            highlightthickness=1
        )

        search_shell.pack(side="left")

        self.create_vector_icon(
            search_shell,
            "search",
            "#7890A6",
            background="#F6F8FB",
            size=30
        ).pack(
            side="left",
            padx=(7, 1)
        )

        search_entry = tk.Entry(
            search_shell,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=28,
            relief="flat",
            bd=0,
            bg="#F6F8FB",
            fg="#26364A",
            insertbackground="#26364A"
        )

        search_entry.pack(
            side="left",
            ipady=10,
            padx=(2, 10)
        )

        search_entry.bind(
            "<Return>",
            lambda event: self.search_issues()
        )

        self.create_action_button(
            search_area,
            "Search",
            self.search_issues,
            "#173B57"
        ).pack(
            side="left",
            padx=(8, 5)
        )

        self.create_action_button(
            search_area,
            "Clear",
            self.clear_search,
            "#E9EEF4",
            "#40546A"
        ).pack(side="left")

        action_area = tk.Frame(
            toolbar,
            bg="#FFFFFF"
        )

        action_area.pack(
            side="right",
            padx=10,
            pady=11
        )

        self.create_action_button(
            action_area,
            "New Request",
            self.open_add_request_form,
            "#2469A6"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_area,
            "Analytics",
            self.view_analytics,
            "#7656C8"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_area,
            "Work Orders",
            self.view_work_orders,
            "#137D78"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_area,
            "Export",
            self.export_csv,
            "#526477"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_area,
            "Refresh",
            self.refresh_table,
            "#E9EEF4",
            "#40546A"
        ).pack(
            side="left",
            padx=(4, 2)
        )

        footer = tk.Frame(
            section,
            bg="#F3F6FA"
        )

        footer.pack(
            fill="x",
            pady=(6, 0)
        )

        tk.Label(
            footer,
            text="SELECT A REQUEST TO VIEW DETAILS OR TAKE ACTION",
            font=("Segoe UI", 8, "bold"),
            fg="#8291A1",
            bg="#F3F6FA"
        ).pack(
            side="left",
            pady=8
        )

        # Status filter placed between the instruction and action buttons.
        filter_area = tk.Frame(
            footer,
            bg="#F3F6FA"
        )

        filter_area.pack(
            side="left",
            padx=(24, 10),
            pady=3
        )

        tk.Label(
            filter_area,
            text="FILTER BY STATUS",
            font=("Segoe UI", 8, "bold"),
            fg="#718096",
            bg="#F3F6FA"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        status_options = ["All Statuses"] + list(
            self.issue_manager.STATUSES
        )

        self.status_filter_combo = ttk.Combobox(
            filter_area,
            textvariable=self.status_filter_var,
            values=status_options,
            state="readonly",
            width=19,
            font=("Segoe UI", 9)
        )

        self.status_filter_combo.pack(side="left")
        self.status_filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.search_issues()
        )

        action_group = tk.Frame(
            footer,
            bg="#F3F6FA"
        )

        action_group.pack(side="right")

        self.create_action_button(
            action_group,
            "View Details",
            self.view_selected_issue,
            "#526477"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_group,
            "Edit Request",
            self.edit_selected_issue,
            "#2469A6"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_group,
            "Manage Assignment",
            self.manage_assignment,
            "#16805D"
        ).pack(side="left", padx=4)

        self.create_action_button(
            action_group,
            "Delete",
            self.delete_selected_issue,
            "#B64242"
        ).pack(side="left", padx=4)

        table_card = tk.Frame(
            section,
            bg="#FFFFFF",
            highlightbackground="#E0E7EF",
            highlightthickness=1
        )

        table_card.pack(
            fill="both",
            expand=True
        )

        table_heading = tk.Frame(
            table_card,
            bg="#FFFFFF"
        )

        table_heading.pack(
            fill="x",
            padx=17,
            pady=(9, 6)
        )

        tk.Label(
            table_heading,
            text="REQUEST REGISTER",
            font=("Segoe UI", 9, "bold"),
            fg="#526477",
            bg="#FFFFFF"
        ).pack(side="left")

        self.record_count_label = tk.Label(
            table_heading,
            text="0 RECORDS",
            font=("Segoe UI", 8, "bold"),
            fg="#718096",
            bg="#FFFFFF"
        )

        self.record_count_label.pack(side="right")

        table_frame = tk.Frame(
            table_card,
            bg="#FFFFFF"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8)
        )

        columns = (
            "ID",
            "Category",
            "Location",
            "Ward",
            "Department",
            "Officer",
            "Status"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        widths = {
            "ID": 115,
            "Category": 175,
            "Location": 220,
            "Ward": 75,
            "Department": 220,
            "Officer": 175,
            "Status": 140
        }

        for column in columns:
            self.table.heading(
                column,
                text=column.upper()
            )

            self.table.column(
                column,
                width=widths[column],
                minwidth=65,
                anchor="center",
                stretch=True
            )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.table.tag_configure(
            "evenrow",
            background="#FFFFFF"
        )

        self.table.tag_configure(
            "oddrow",
            background="#F6F9FC"
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.table.bind(
            "<Double-1>",
            lambda event: self.view_selected_issue()
        )

    # ---------------------------------------------------------
    # BUTTONS AND COLORS
    # ---------------------------------------------------------

    def create_action_button(
        self,
        parent,
        text,
        command,
        background,
        foreground="#FFFFFF",
        width=None
    ):
        options = {
            "text": text,
            "command": command,
            "bg": background,
            "fg": foreground,
            "activebackground": background,
            "activeforeground": foreground,
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 13,
            "pady": 10,
            "cursor": "hand2",
            "highlightthickness": 0
        }

        if width is not None:
            options["width"] = width

        button = tk.Button(
            parent,
            **options
        )

        hover_background = self.blend_color(
            background,
            "#FFFFFF",
            0.12
        )

        button.bind(
            "<Enter>",
            lambda event: button.config(
                bg=hover_background
            )
        )

        button.bind(
            "<Leave>",
            lambda event: button.config(
                bg=background
            )
        )

        return button

    def blend_color(self, first, second, amount):
        first = first.lstrip("#")
        second = second.lstrip("#")

        first_rgb = tuple(
            int(first[index:index + 2], 16)
            for index in (0, 2, 4)
        )

        second_rgb = tuple(
            int(second[index:index + 2], 16)
            for index in (0, 2, 4)
        )

        blended = tuple(
            round(a + (b - a) * amount)
            for a, b in zip(first_rgb, second_rgb)
        )

        return "#" + "".join(
            f"{value:02X}"
            for value in blended
        )


    def insert_issue_row(self, issue):
        row_index = len(
            self.table.get_children()
        )

        self.table.insert(
            "",
            "end",
            values=(
                issue.issue_id,
                issue.category,
                issue.location,
                issue.ward_number,
                issue.department,
                self.get_officer_name(
                    issue.assigned_officer_id
                ),
                issue.status
            ),
            tags=(
                "evenrow" if row_index % 2 == 0 else "oddrow",
            )
        )

    def refresh_table(self):
        # Refresh clears the text search but preserves the selected status filter.
        self.search_var.set("")
        self.apply_request_filters()
        self.update_dashboard()

    def search_issues(self):
        # Search and status filtering are applied together.
        self.apply_request_filters()

    def apply_request_filters(self):
        keyword = self.search_var.get().strip().lower()
        selected_status = self.status_filter_var.get()

        self.table.delete(
            *self.table.get_children()
        )

        visible_count = 0

        for issue in self.issue_manager.view_issues():
            if (
                selected_status != "All Statuses"
                and issue.status != selected_status
            ):
                continue

            searchable_values = [
                issue.issue_id,
                issue.category,
                issue.location,
                str(issue.ward_number),
                issue.department,
                self.get_officer_name(
                    issue.assigned_officer_id
                ),
                issue.status
            ]

            if keyword and not any(
                keyword in str(value).lower()
                for value in searchable_values
            ):
                continue

            self.insert_issue_row(issue)
            visible_count += 1

        if hasattr(self, "record_count_label"):
            if selected_status == "All Statuses" and not keyword:
                count_text = f"{visible_count} RECORDS"
            else:
                count_text = f"{visible_count} MATCHING RECORDS"

            self.record_count_label.config(
                text=count_text
            )

    def clear_search(self):
        self.search_var.set("")
        self.apply_request_filters()

    def get_selected_issue(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a service request first.",
                parent=self.root
            )
            return None

        values = self.table.item(
            selected[0],
            "values"
        )

        return self.issue_manager.search_issue(
            values[0]
        )


    def view_selected_issue(self):
        issue = self.get_selected_issue()

        if issue is None:
            return

        details = (
            f"Request ID: {issue.issue_id}\n\n"
            f"Corporation: {issue.corporation_id}\n"
            f"Ward Number: {issue.ward_number}\n"
            f"Category: {issue.category}\n"
            f"Location: {issue.location}\n\n"
            f"Description:\n{issue.description}\n\n"
            f"Submission Date: {issue.submission_date}\n"
            f"Department: {issue.department}\n"
            f"Status: {issue.status}"
        )

        messagebox.showinfo(
            "Request Details",
            details,
            parent=self.root
        )

    # ---------------------------------------------------------
    # EDIT REQUEST
    # ---------------------------------------------------------

    def edit_selected_issue(self):
        issue = self.get_selected_issue()

        if issue is None:
            return

        form = tk.Toplevel(self.root)
        form.title("Edit Service Request")
        form.geometry("520x470")
        form.resizable(False, False)
        form.configure(bg="#F4F7FB")
        form.transient(self.root)
        form.grab_set()

        tk.Label(
            form,
            text=f"Edit Request: {issue.issue_id}",
            font=("Segoe UI", 16, "bold"),
            fg="#173B57",
            bg="#F4F7FB"
        ).pack(pady=15)

        fields = tk.Frame(
            form,
            bg="#F4F7FB"
        )

        fields.pack(
            fill="both",
            padx=30
        )

        tk.Label(
            fields,
            text="Category",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        category_var = tk.StringVar(
            value=issue.category
        )

        ttk.Combobox(
            fields,
            textvariable=category_var,
            values=self.issue_manager.CATEGORIES,
            state="readonly"
        ).pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Location",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        location_entry = tk.Entry(
            fields,
            font=("Segoe UI", 11)
        )

        location_entry.insert(
            0,
            issue.location
        )

        location_entry.pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Description",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        description_text = tk.Text(
            fields,
            height=6,
            font=("Segoe UI", 10),
            wrap="word"
        )

        description_text.insert(
            "1.0",
            issue.description
        )

        description_text.pack(
            fill="x",
            pady=(4, 15)
        )

        def save_changes():
            success = self.issue_manager.update_issue(
                issue.issue_id,
                category_var.get(),
                location_entry.get(),
                description_text.get(
                    "1.0",
                    "end"
                ).strip()
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    "Request updated successfully.",
                    parent=form
                )

                form.destroy()
                self.refresh_table()

            else:
                messagebox.showerror(
                    "Error",
                    "Unable to update request.",
                    parent=form
                )

        tk.Button(
            form,
            text="Save Changes",
            command=save_changes,
            bg="#2563A6",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=8
        ).pack(pady=10)



    def load_departments(self, corporation_id):
        storage = JSONStorage(
            "data/departments.json"
        )

        records = storage.load_data()

        return [
            department
            for department in records
            if isinstance(department, dict)
            and department.get("corporation_id") == corporation_id
            and department.get("department_id")
            and department.get("name")
        ]

    def get_officer_name(self, officer_id):
        if not officer_id:
            return "Not Assigned"

        officer = self.officer_manager.search_officer(
            officer_id
        )

        return (
            officer["name"]
            if officer
            else officer_id
        )


    def manage_assignment(self):
        issue = self.get_selected_issue()

        if issue is None:
            return

        try:
            departments = self.load_departments(
                issue.corporation_id
            )

        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror(
                "Department Error",
                str(error),
                parent=self.root
            )
            return

        if not departments:
            messagebox.showwarning(
                "No Departments",
                "No departments are available for this corporation.",
                parent=self.root
            )
            return

        form = tk.Toplevel(self.root)
        form.title("Manage Request Assignment")
        form.geometry("520x450")
        form.resizable(False, False)
        form.configure(bg="#F4F7FB")
        form.transient(self.root)
        form.grab_set()

        tk.Label(
            form,
            text=f"Manage Request: {issue.issue_id}",
            font=("Segoe UI", 16, "bold"),
            fg="#173B57",
            bg="#F4F7FB"
        ).pack(pady=18)

        fields = tk.Frame(
            form,
            bg="#F4F7FB"
        )

        fields.pack(
            fill="x",
            padx=30
        )

        tk.Label(
            fields,
            text="Assign Department",
            font=("Segoe UI", 10, "bold"),
            bg="#F4F7FB"
        ).pack(anchor="w")

        department_by_name = {
            item["name"]: item
            for item in departments
        }

        department_names = list(
            department_by_name
        )

        current_department = issue.department

        if current_department not in department_by_name:
            current_department = department_names[0]

        department_var = tk.StringVar(
            value=current_department
        )

        department_combo = ttk.Combobox(
            fields,
            textvariable=department_var,
            values=department_names,
            state="readonly"
        )

        department_combo.pack(
            fill="x",
            pady=(5, 12)
        )

        tk.Label(
            fields,
            text="Assign Officer",
            font=("Segoe UI", 10, "bold"),
            bg="#F4F7FB"
        ).pack(anchor="w")

        officer_var = tk.StringVar()

        officer_combo = ttk.Combobox(
            fields,
            textvariable=officer_var,
            state="readonly"
        )

        officer_combo.pack(
            fill="x",
            pady=(5, 12)
        )

        officer_by_label = {}

        def update_officer_options(event=None):
            selected_department = department_by_name.get(
                department_var.get()
            )

            if not selected_department:
                officer_by_label.clear()
                officer_combo["values"] = []
                officer_var.set("")
                return

            officers = self.officer_manager.get_officers_by_department(
                selected_department["department_id"],
                issue.corporation_id
            )

            officer_by_label.clear()
            labels = []

            for officer in officers:
                label = (
                    f'{officer["name"]} '
                    f'({officer["officer_id"]})'
                )

                officer_by_label[label] = officer
                labels.append(label)

            officer_combo["values"] = labels

            current_officer = next(
                (
                    label
                    for label, officer in officer_by_label.items()
                    if officer["officer_id"] == issue.assigned_officer_id
                ),
                ""
            )

            officer_var.set(current_officer)

        department_combo.bind(
            "<<ComboboxSelected>>",
            update_officer_options
        )

        update_officer_options()

        tk.Label(
            fields,
            text="Request Status",
            font=("Segoe UI", 10, "bold"),
            bg="#F4F7FB"
        ).pack(anchor="w")

        status_var = tk.StringVar(
            value=issue.status
        )

        ttk.Combobox(
            fields,
            textvariable=status_var,
            values=self.issue_manager.STATUSES,
            state="readonly"
        ).pack(
            fill="x",
            pady=(5, 15)
        )

        def save_assignment():
            selected_department = department_by_name.get(
                department_var.get()
            )

            selected_officer = officer_by_label.get(
                officer_var.get()
            )

            if not selected_department:
                messagebox.showerror(
                    "Invalid Department",
                    "Please select a valid department.",
                    parent=form
                )
                return

            if not selected_officer:
                messagebox.showerror(
                    "Officer Required",
                    "Please select an officer from the selected department.",
                    parent=form
                )
                return

            if not self.issue_manager.assign_officer(
                issue.issue_id,
                selected_department["name"],
                selected_officer["officer_id"]
            ):
                messagebox.showerror(
                    "Assignment Failed",
                    "Could not save the department and officer assignment.",
                    parent=form
                )
                return

            work_order_success, work_order_result = (
                self.work_order_manager.create_work_order(issue)
            )

            if not work_order_success:
                messagebox.showerror(
                    "Work Order Error",
                    "Officer assignment was saved, but work order "
                    f"creation failed: {work_order_result}",
                    parent=form
                )

                self.refresh_table()
                return

            if status_var.get() != "Assigned":
                if not self.issue_manager.update_status(
                    issue.issue_id,
                    status_var.get()
                ):
                    messagebox.showerror(
                        "Status Update Failed",
                        "The assignment was saved, but the status "
                        "could not be updated.",
                        parent=form
                    )

                    self.refresh_table()
                    return

            self.synchronize_issue_statuses()

            messagebox.showinfo(
                "Success",
                f'Assigned to {selected_officer["name"]} successfully.',
                parent=form
            )

            form.destroy()
            self.refresh_table()

        tk.Button(
            form,
            text="Save Assignment",
            command=save_assignment,
            bg="#16805D",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8
        ).pack(pady=12)



    def view_work_orders(self):
        window = tk.Toplevel(self.root)
        window.title(
            "JONOSHOMADHAN | Work Order Management"
        )

        window.geometry("1280x720")
        window.minsize(980, 620)
        window.configure(bg="#F2F5F9")
        window.transient(self.root)
        window.update_idletasks()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        if screen_width >= 1100 and screen_height >= 700:
            window.state("zoomed")

        palette = {
            "navy": "#102F49",
            "navy_light": "#1B4565",
            "teal": "#15958E",
            "blue": "#2875B8",
            "purple": "#7654C8",
            "green": "#15966F",
            "amber": "#D58A24",
            "red": "#C84B50",
            "ink": "#20364B",
            "muted": "#718096",
            "line": "#E0E7EF",
            "surface": "#FFFFFF",
            "background": "#F2F5F9",
            "soft_blue": "#EAF2FA",
            "soft_green": "#E8F5EF",
            "soft_amber": "#FFF4E3",
            "soft_red": "#FCEBED"
        }

        style = ttk.Style(window)

        style.configure(
            "WorkOrder.Treeview",
            background="#FFFFFF",
            foreground=palette["ink"],
            fieldbackground="#FFFFFF",
            rowheight=43,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "WorkOrder.Treeview.Heading",
            background="#EAF0F7",
            foreground="#344B63",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(12, 13)
        )

        style.map(
            "WorkOrder.Treeview",
            background=[("selected", "#DCEBFA")],
            foreground=[("selected", palette["navy"])]
        )

        style.map(
            "WorkOrder.Treeview.Heading",
            background=[("active", "#DCE6F0")]
        )

        # Header

        header = tk.Frame(
            window,
            bg=palette["navy"],
            height=108
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(
            header,
            bg=palette["navy"]
        )

        brand.pack(
            side="left",
            padx=28,
            pady=19
        )

        mark = tk.Frame(
            brand,
            bg=palette["navy"],
            width=50,
            height=50
        )

        mark.pack(
            side="left",
            padx=(0, 13)
        )

        mark.pack_propagate(False)

        if self.app_icon:
            tk.Label(
                mark,
                image=self.app_icon,
                bg=palette["navy"],
                bd=0
            ).pack(expand=True)

        else:
            tk.Label(
                mark,
                text="J",
                font=("Segoe UI", 23, "bold"),
                fg="#FFFFFF",
                bg="#1E7890"
            ).pack(expand=True)

        brand_text = tk.Frame(
            brand,
            bg=palette["navy"]
        )

        brand_text.pack(
            side="left",
            anchor="center"
        )

        tk.Label(
            brand_text,
            text="WORK ORDER MANAGEMENT",
            font=("Segoe UI", 19, "bold"),
            fg="#FFFFFF",
            bg=palette["navy"]
        ).pack(anchor="w")

        tk.Label(
            brand_text,
            text="Monitor assignments, operational progress and completion verification",
            font=("Segoe UI", 9),
            fg="#B9CCDA",
            bg=palette["navy"]
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        header_right = tk.Frame(
            header,
            bg=palette["navy"]
        )

        header_right.pack(
            side="right",
            padx=28,
            pady=28
        )

        tk.Label(
            header_right,
            text="ADMINISTRATION CONSOLE",
            font=("Segoe UI", 9, "bold"),
            fg="#DCE8F0",
            bg=palette["navy"]
        ).pack(anchor="e")

        tk.Label(
            header_right,
            text=date.today().strftime("%d %B %Y"),
            font=("Segoe UI", 9),
            fg="#AFC3D2",
            bg=palette["navy"]
        ).pack(
            anchor="e",
            pady=(5, 0)
        )

        tk.Frame(
            window,
            bg="#20A6A0",
            height=4
        ).pack(fill="x")

        body = tk.Frame(
            window,
            bg=palette["background"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=26,
            pady=20
        )

        # Overview heading

        heading_row = tk.Frame(
            body,
            bg=palette["background"]
        )

        heading_row.pack(
            fill="x",
            pady=(0, 14)
        )

        tk.Label(
            heading_row,
            text="Operational Overview",
            font=("Segoe UI", 16, "bold"),
            fg=palette["navy"],
            bg=palette["background"]
        ).pack(side="left")

        tk.Label(
            heading_row,
            text="Live summary of assigned field activities",
            font=("Segoe UI", 9),
            fg=palette["muted"],
            bg=palette["background"]
        ).pack(
            side="left",
            padx=13,
            pady=(4, 0)
        )

        # Summary cards

        summary_frame = tk.Frame(
            body,
            bg=palette["background"]
        )

        summary_frame.pack(
            fill="x",
            pady=(0, 18)
        )

        orders = self.work_order_manager.get_all_work_orders()

        summary_values = {
            "total": len(orders),

            "progress": sum(
                1
                for item in orders
                if item.get("status") == "In Progress"
            ),

            "completed": sum(
                1
                for item in orders
                if item.get("status") == "Completed"
            ),

            "pending": sum(
                1
                for item in orders
                if item.get("verification_status") == "Pending"
            )
        }

        summary_definitions = [
            ("TOTAL WORK ORDERS", "total", palette["blue"], "document"),
            ("IN PROGRESS", "progress", palette["amber"], "clock"),
            ("COMPLETED", "completed", palette["green"], "check"),
            ("AWAITING REVIEW", "pending", palette["purple"], "document")
        ]

        summary_labels = {}

        for index, (label, key, accent, icon_name) in enumerate(
            summary_definitions
        ):
            card = tk.Frame(
                summary_frame,
                bg=palette["surface"],
                highlightthickness=1,
                highlightbackground=palette["line"]
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0 if index == 0 else 10, 0)
            )

            tk.Frame(
                card,
                bg=accent,
                width=4
            ).pack(
                side="left",
                fill="y"
            )

            content = tk.Frame(
                card,
                bg=palette["surface"]
            )

            content.pack(
                side="left",
                fill="both",
                expand=True,
                padx=16,
                pady=13
            )

            top = tk.Frame(
                content,
                bg=palette["surface"]
            )

            top.pack(fill="x")

            tk.Label(
                top,
                text=label,
                font=("Segoe UI", 8, "bold"),
                fg=palette["muted"],
                bg=palette["surface"]
            ).pack(
                side="left",
                anchor="w"
            )

            icon_holder = tk.Frame(
                top,
                bg="#F2F6FA",
                width=32,
                height=32
            )

            icon_holder.pack(side="right")
            icon_holder.pack_propagate(False)

            self.create_vector_icon(
                icon_holder,
                icon_name,
                accent,
                background="#F2F6FA",
                size=25
            ).pack(expand=True)

            value_label = tk.Label(
                content,
                text=str(summary_values[key]),
                font=("Segoe UI", 23, "bold"),
                fg=palette["navy"],
                bg=palette["surface"]
            )

            value_label.pack(
                anchor="w",
                pady=(5, 0)
            )

            summary_labels[key] = value_label

        # Toolbar

        toolbar = tk.Frame(
            body,
            bg=palette["surface"],
            highlightthickness=1,
            highlightbackground=palette["line"]
        )

        toolbar.pack(
            fill="x",
            pady=(0, 14)
        )

        search_area = tk.Frame(
            toolbar,
            bg=palette["surface"]
        )

        search_area.pack(
            side="left",
            padx=13,
            pady=11
        )

        search_box = tk.Frame(
            search_area,
            bg="#F5F8FB",
            highlightthickness=1,
            highlightbackground="#DCE5EE"
        )

        search_box.pack(side="left")

        self.create_vector_icon(
            search_box,
            "search",
            "#7890A7",
            background="#F5F8FB",
            size=25
        ).pack(
            side="left",
            padx=(9, 2),
            pady=5
        )

        search_var = tk.StringVar()

        search_entry = tk.Entry(
            search_box,
            textvariable=search_var,
            width=29,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            bg="#F5F8FB",
            fg=palette["ink"],
            insertbackground=palette["navy"]
        )

        search_entry.pack(
            side="left",
            padx=(2, 10),
            ipady=8
        )

        def action_button(
            parent,
            text,
            command,
            background,
            foreground="#FFFFFF"
        ):
            button = tk.Button(
                parent,
                text=text,
                command=command,
                bg=background,
                fg=foreground,
                activebackground=background,
                activeforeground=foreground,
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                bd=0,
                padx=15,
                pady=10,
                cursor="hand2"
            )

            button.bind(
                "<Enter>",
                lambda event: button.configure(
                    relief="solid",
                    bd=1
                )
            )

            button.bind(
                "<Leave>",
                lambda event: button.configure(
                    relief="flat",
                    bd=0
                )
            )

            return button

        # Work order table

        table_card = tk.Frame(
            body,
            bg=palette["surface"],
            highlightthickness=1,
            highlightbackground=palette["line"]
        )

        table_card.pack(
            fill="both",
            expand=True
        )

        table_heading = tk.Frame(
            table_card,
            bg=palette["surface"]
        )

        table_heading.pack(
            fill="x",
            padx=16,
            pady=(13, 10)
        )

        tk.Label(
            table_heading,
            text="WORK ORDER REGISTER",
            font=("Segoe UI", 9, "bold"),
            fg=palette["ink"],
            bg=palette["surface"]
        ).pack(side="left")

        record_count_var = tk.StringVar()

        tk.Label(
            table_heading,
            textvariable=record_count_var,
            font=("Segoe UI", 8, "bold"),
            fg=palette["muted"],
            bg=palette["surface"]
        ).pack(side="right")

        table_container = tk.Frame(
            table_card,
            bg=palette["surface"]
        )

        table_container.pack(
            fill="both",
            expand=True,
            padx=13,
            pady=(0, 13)
        )

        columns = (
            "Work Order ID",
            "Complaint ID",
            "Department",
            "Officer",
            "Work Status",
            "Verification"
        )

        table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="WorkOrder.Treeview"
        )

        widths = {
            "Work Order ID": 125,
            "Complaint ID": 115,
            "Department": 235,
            "Officer": 185,
            "Work Status": 145,
            "Verification": 155
        }

        for column in columns:
            table.heading(
                column,
                text=column.upper()
            )

            table.column(
                column,
                width=widths[column],
                minwidth=95,
                anchor="center",
                stretch=True
            )

        table.tag_configure(
            "even",
            background="#FFFFFF"
        )

        table.tag_configure(
            "odd",
            background="#F5F8FC"
        )

        vertical_scroll = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=table.yview
        )

        horizontal_scroll = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=table.xview
        )

        table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        table.grid(
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

        table_container.grid_rowconfigure(
            0,
            weight=1
        )

        table_container.grid_columnconfigure(
            0,
            weight=1
        )

        # Refresh summary

        def refresh_summary():
            orders = self.work_order_manager.get_all_work_orders()

            summary_values = {
                "total": len(orders),

                "progress": sum(
                    1
                    for item in orders
                    if item.get("status") == "In Progress"
                ),

                "completed": sum(
                    1
                    for item in orders
                    if item.get("status") == "Completed"
                ),

                "pending": sum(
                    1
                    for item in orders
                    if item.get("verification_status") == "Pending"
                )
            }

            for key, value in summary_values.items():
                summary_labels[key].configure(
                    text=str(value)
                )

        # Refresh work order table

        def refresh_work_order_table():
            query = search_var.get().strip().lower()

            table.delete(
                *table.get_children()
            )

            visible_count = 0

            for order in self.work_order_manager.get_all_work_orders():
                officer = self.officer_manager.search_officer(
                    order["officer_id"]
                )

                officer_name = (
                    officer["name"]
                    if officer
                    else order["officer_id"]
                )

                row_values = (
                    order["work_order_id"],
                    order["issue_id"],
                    order["department"],
                    officer_name,
                    order["status"],
                    order.get(
                        "verification_status",
                        "Not Submitted"
                    )
                )

                if query and not any(
                    query in str(value).lower()
                    for value in row_values
                ):
                    continue

                table.insert(
                    "",
                    "end",
                    values=row_values,
                    tags=(
                        "even" if visible_count % 2 == 0 else "odd",
                    )
                )

                visible_count += 1

            record_count_var.set(
                f"{visible_count} RECORDS"
            )

            refresh_summary()

        # Selected work order

        def get_selected_work_order():
            selected = table.selection()

            if not selected:
                messagebox.showwarning(
                    "No Selection",
                    "Select a work order from the register first.",
                    parent=window
                )
                return None

            values = table.item(
                selected[0],
                "values"
            )

            work_order = self.work_order_manager.get_work_order(
                values[0]
            )

            if work_order is None:
                messagebox.showerror(
                    "Record Not Found",
                    "The selected work order could not be found.",
                    parent=window
                )
                return None

            return work_order

        # Update work order status

        def update_selected_work_order():
            work_order = get_selected_work_order()

            if work_order is None:
                return

            if work_order.get("verification_status") == "Verified":
                messagebox.showwarning(
                    "Verified Work Order",
                    "A verified work order cannot be changed.",
                    parent=window
                )
                return

            update_window = tk.Toplevel(window)

            update_window.title(
                f"Update {work_order['work_order_id']}"
            )

            update_window.geometry("500x390")
            update_window.resizable(False, False)
            update_window.configure(
                bg=palette["background"]
            )

            update_window.transient(window)
            update_window.grab_set()

            dialog_header = tk.Frame(
                update_window,
                bg=palette["navy"],
                height=88
            )

            dialog_header.pack(fill="x")
            dialog_header.pack_propagate(False)

            tk.Label(
                dialog_header,
                text="UPDATE WORK ORDER",
                font=("Segoe UI", 15, "bold"),
                fg="#FFFFFF",
                bg=palette["navy"]
            ).pack(
                anchor="w",
                padx=25,
                pady=(19, 2)
            )

            tk.Label(
                dialog_header,
                text=(
                    f"{work_order['work_order_id']} | "
                    f"Complaint {work_order['issue_id']}"
                ),
                font=("Segoe UI", 9),
                fg="#B9CCDA",
                bg=palette["navy"]
            ).pack(
                anchor="w",
                padx=25
            )

            form = tk.Frame(
                update_window,
                bg=palette["surface"]
            )

            form.pack(
                fill="both",
                expand=True,
                padx=20,
                pady=20
            )

            tk.Label(
                form,
                text="Work status",
                font=("Segoe UI", 10, "bold"),
                fg=palette["ink"],
                bg=palette["surface"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(18, 6)
            )

            status_var = tk.StringVar(
                value=work_order["status"]
            )

            status_combo = ttk.Combobox(
                form,
                textvariable=status_var,
                values=self.work_order_manager.STATUSES,
                state="readonly",
                font=("Segoe UI", 10)
            )

            status_combo.pack(
                fill="x",
                padx=18,
                ipady=4
            )

            tk.Label(
                form,
                text="Changing the status updates the linked complaint automatically.",
                font=("Segoe UI", 8),
                fg=palette["muted"],
                bg=palette["surface"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 18)
            )

            def save_work_order_status():
                new_status = status_var.get()

                if not self.work_order_manager.update_work_order_status(
                    work_order["work_order_id"],
                    new_status
                ):
                    messagebox.showerror(
                        "Update Failed",
                        "Could not update the work order status.",
                        parent=update_window
                    )
                    return

                self.synchronize_issue_statuses()

                messagebox.showinfo(
                    "Saved",
                    "Work order status updated successfully.",
                    parent=update_window
                )

                update_window.destroy()
                refresh_work_order_table()
                self.refresh_table()

            button_row = tk.Frame(
                form,
                bg=palette["surface"]
            )

            button_row.pack(
                fill="x",
                padx=18,
                pady=(0, 15)
            )

            action_button(
                button_row,
                "Save Changes",
                save_work_order_status,
                palette["green"]
            ).pack(side="left")

            action_button(
                button_row,
                "Cancel",
                update_window.destroy,
                "#E9EEF4",
                palette["ink"]
            ).pack(
                side="left",
                padx=8
            )

        # Verify work order completion

        def verify_selected_work_order():
            work_order = get_selected_work_order()

            if work_order is None:
                return

            if work_order["status"] != "Completed":
                messagebox.showwarning(
                    "Work Not Completed",
                    "Only completed work orders can be submitted for verification.",
                    parent=window
                )
                return

            if work_order.get("verification_status") != "Pending":
                messagebox.showwarning(
                    "Verification Unavailable",
                    "This work order is not awaiting verification.",
                    parent=window
                )
                return

            verify_window = tk.Toplevel(window)

            verify_window.title(
                f"Verify {work_order['work_order_id']}"
            )

            verify_window.geometry("590x590")
            verify_window.minsize(540, 540)
            verify_window.configure(
                bg=palette["background"]
            )

            verify_window.transient(window)
            verify_window.grab_set()

            verify_header = tk.Frame(
                verify_window,
                bg=palette["navy"],
                height=105
            )

            verify_header.pack(fill="x")
            verify_header.pack_propagate(False)

            tk.Label(
                verify_header,
                text="COMPLETION VERIFICATION",
                font=("Segoe UI", 15, "bold"),
                fg="#FFFFFF",
                bg=palette["navy"]
            ).pack(
                anchor="w",
                padx=26,
                pady=(20, 4)
            )

            tk.Label(
                verify_header,
                text=(
                    f"{work_order['work_order_id']} | "
                    f"Complaint {work_order['issue_id']}"
                ),
                font=("Segoe UI", 9),
                fg="#B9CCDA",
                bg=palette["navy"]
            ).pack(
                anchor="w",
                padx=26
            )

            form = tk.Frame(
                verify_window,
                bg=palette["surface"]
            )

            form.pack(
                fill="both",
                expand=True,
                padx=20,
                pady=18
            )

            info_grid = tk.Frame(
                form,
                bg=palette["surface"]
            )

            info_grid.pack(
                fill="x",
                padx=20,
                pady=(18, 15)
            )

            info_items = [
                ("DEPARTMENT", work_order["department"]),
                (
                    "ASSIGNED OFFICER",
                    self.get_officer_name(
                        work_order["officer_id"]
                    )
                )
            ]

            for index, (label, value) in enumerate(info_items):
                cell = tk.Frame(
                    info_grid,
                    bg="#F5F8FB"
                )

                cell.grid(
                    row=0,
                    column=index,
                    sticky="nsew",
                    padx=(0 if index == 0 else 8, 0)
                )

                info_grid.grid_columnconfigure(
                    index,
                    weight=1
                )

                tk.Label(
                    cell,
                    text=label,
                    font=("Segoe UI", 8, "bold"),
                    fg=palette["muted"],
                    bg="#F5F8FB"
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(10, 3)
                )

                tk.Label(
                    cell,
                    text=value,
                    font=("Segoe UI", 9, "bold"),
                    fg=palette["ink"],
                    bg="#F5F8FB",
                    wraplength=220,
                    justify="left"
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(0, 10)
                )

            tk.Label(
                form,
                text="Verification decision",
                font=("Segoe UI", 10, "bold"),
                fg=palette["ink"],
                bg=palette["surface"]
            ).pack(
                anchor="w",
                padx=20,
                pady=(4, 8)
            )

            decision_var = tk.StringVar(
                value="Approve"
            )

            decision_area = tk.Frame(
                form,
                bg=palette["surface"]
            )

            decision_area.pack(
                fill="x",
                padx=20
            )

            ttk.Radiobutton(
                decision_area,
                text="Approve completion",
                variable=decision_var,
                value="Approve"
            ).pack(
                side="left",
                padx=(0, 22)
            )

            ttk.Radiobutton(
                decision_area,
                text="Reject completion",
                variable=decision_var,
                value="Reject"
            ).pack(side="left")

            tk.Label(
                form,
                text="Verification notes",
                font=("Segoe UI", 10, "bold"),
                fg=palette["ink"],
                bg=palette["surface"]
            ).pack(
                anchor="w",
                padx=20,
                pady=(18, 7)
            )

            notes_text = tk.Text(
                form,
                height=6,
                font=("Segoe UI", 10),
                wrap="word",
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground=palette["line"],
                highlightcolor=palette["blue"],
                padx=10,
                pady=9
            )

            notes_text.pack(
                fill="x",
                padx=20
            )

            tk.Label(
                form,
                text="A verification note is required for both approval and rejection.",
                font=("Segoe UI", 8),
                fg=palette["muted"],
                bg=palette["surface"]
            ).pack(
                anchor="w",
                padx=20,
                pady=(6, 14)
            )

            def save_verification():
                notes = notes_text.get(
                    "1.0",
                    "end"
                ).strip()

                if not notes:
                    messagebox.showerror(
                        "Notes Required",
                        "Enter verification notes before saving.",
                        parent=verify_window
                    )
                    return

                issue = self.issue_manager.search_issue(
                    work_order["issue_id"]
                )

                if issue is None:
                    messagebox.showerror(
                        "Complaint Not Found",
                        "The original complaint could not be found.",
                        parent=verify_window
                    )
                    return

                old_issue_status = issue.status
                approved = decision_var.get() == "Approve"

                target_issue_status = (
                    "Resolved"
                    if approved
                    else "In Progress"
                )

                if not self.issue_manager.update_status(
                    issue.issue_id,
                    target_issue_status
                ):
                    messagebox.showerror(
                        "Complaint Update Failed",
                        "The linked complaint status could not be saved.",
                        parent=verify_window
                    )
                    return

                success, result = self.work_order_manager.verify_work_order(
                    work_order["work_order_id"],
                    approved,
                    notes
                )

                if not success:
                    self.issue_manager.update_status(
                        issue.issue_id,
                        old_issue_status
                    )

                    messagebox.showerror(
                        "Verification Failed",
                        result,
                        parent=verify_window
                    )
                    return

                self.synchronize_issue_statuses()

                messagebox.showinfo(
                    "Verification Saved",
                    (
                        "Completion approved. The complaint is now Resolved."
                        if approved
                        else "Completion rejected. The work order has returned to In Progress."
                    ),
                    parent=verify_window
                )

                verify_window.destroy()
                refresh_work_order_table()
                self.refresh_table()

            button_row = tk.Frame(
                form,
                bg=palette["surface"]
            )

            button_row.pack(
                fill="x",
                padx=20,
                pady=(15, 18)
            )

            action_button(
                button_row,
                "Save Verification",
                save_verification,
                palette["green"]
            ).pack(side="left")

            action_button(
                button_row,
                "Cancel",
                verify_window.destroy,
                "#E9EEF4",
                palette["ink"]
            ).pack(
                side="left",
                padx=8
            )

        # Toolbar buttons

        action_button(
            search_area,
            "Search",
            refresh_work_order_table,
            palette["navy"]
        ).pack(
            side="left",
            padx=(9, 5)
        )

        action_button(
            search_area,
            "Clear",
            lambda: (
                search_var.set(""),
                refresh_work_order_table()
            ),
            "#E9EEF4",
            palette["ink"]
        ).pack(
            side="left",
            padx=3
        )

        search_entry.bind(
            "<Return>",
            lambda event: refresh_work_order_table()
        )

        action_area = tk.Frame(
            toolbar,
            bg=palette["surface"]
        )

        action_area.pack(
            side="right",
            padx=13,
            pady=11
        )

        action_button(
            action_area,
            "Update Status",
            update_selected_work_order,
            palette["green"]
        ).pack(
            side="left",
            padx=4
        )

        action_button(
            action_area,
            "Verify Completion",
            verify_selected_work_order,
            palette["blue"]
        ).pack(
            side="left",
            padx=4
        )

        action_button(
            action_area,
            "Refresh",
            refresh_work_order_table,
            "#E9EEF4",
            palette["ink"]
        ).pack(
            side="left",
            padx=4
        )

        action_button(
            action_area,
            "Close",
            window.destroy,
            palette["navy"]
        ).pack(
            side="left",
            padx=(4, 0)
        )

        refresh_work_order_table()
        search_entry.focus_set()


    def delete_selected_issue(self):
        issue = self.get_selected_issue()

        if issue is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete request {issue.issue_id}?",
            parent=self.root
        )

        if not confirm:
            return

        if self.issue_manager.delete_issue(issue.issue_id):
            messagebox.showinfo(
                "Success",
                "Request deleted successfully.",
                parent=self.root
            )

            self.refresh_table()

        else:
            messagebox.showerror(
                "Error",
                "Unable to delete the request.",
                parent=self.root
            )


    def open_add_request_form(self):
        form = tk.Toplevel(self.root)

        form.title("Add New Service Request")
        form.geometry("540x650")
        form.resizable(False, False)
        form.configure(bg="#F4F7FB")
        form.transient(self.root)
        form.grab_set()

        tk.Label(
            form,
            text="Submit a New Service Request",
            font=("Segoe UI", 17, "bold"),
            fg="#173B57",
            bg="#F4F7FB"
        ).pack(pady=18)

        fields = tk.Frame(
            form,
            bg="#F4F7FB"
        )

        fields.pack(
            fill="both",
            padx=30
        )

        tk.Label(
            fields,
            text="City Corporation",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        corporation_var = tk.StringVar(
            value="CC-001"
        )

        ttk.Combobox(
            fields,
            textvariable=corporation_var,
            values=[
                "CC-001",
                "CC-002",
                "CC-003",
                "CC-004",
                "CC-005"
            ],
            state="readonly"
        ).pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Ward Number",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        ward_entry = tk.Entry(
            fields,
            font=("Segoe UI", 11)
        )

        ward_entry.pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Issue Category",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        category_var = tk.StringVar()

        ttk.Combobox(
            fields,
            textvariable=category_var,
            values=self.issue_manager.CATEGORIES,
            state="readonly"
        ).pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Location",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        location_entry = tk.Entry(
            fields,
            font=("Segoe UI", 11)
        )

        location_entry.pack(
            fill="x",
            pady=(4, 12)
        )

        tk.Label(
            fields,
            text="Problem Description",
            bg="#F4F7FB",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        description_text = tk.Text(
            fields,
            height=5,
            font=("Segoe UI", 10),
            wrap="word"
        )

        description_text.pack(
            fill="x",
            pady=(4, 15)
        )

        def submit_request():
            try:
                ward_number = int(
                    ward_entry.get().strip()
                )

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid ward number.",
                    parent=form
                )
                return

            success, result = self.issue_manager.create_issue(
                corporation_id=corporation_var.get(),
                ward_number=ward_number,
                category=category_var.get(),
                location=location_entry.get(),
                description=description_text.get(
                    "1.0",
                    "end"
                ).strip(),
                submission_date=date.today().isoformat()
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Request submitted successfully!\n"
                    f"Request ID: {result}",
                    parent=form
                )

                form.destroy()
                self.refresh_table()

            else:
                messagebox.showerror(
                    "Submission Failed",
                    result,
                    parent=form
                )

        tk.Button(
            form,
            text="Submit Request",
            command=submit_request,
            bg="#16805D",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=9
        ).pack(pady=12)


    def view_analytics(self):
        report_text = self.report_manager.generate_report_text()

        window = tk.Toplevel(self.root)

        window.title(
            "Jonoshomadhan | Analytics Report"
        )

        window.geometry("820x720")
        window.configure(bg="#F4F7FB")
        window.transient(self.root)

        tk.Label(
            window,
            text="Service Request Analytics",
            font=("Segoe UI", 18, "bold"),
            fg="#173B57",
            bg="#F4F7FB"
        ).pack(pady=15)

        text_frame = tk.Frame(window)

        text_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        scrollbar = ttk.Scrollbar(text_frame)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        report_display = tk.Text(
            text_frame,
            font=("Consolas", 10),
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=15,
            pady=15
        )

        report_display.insert(
            "1.0",
            report_text
        )

        report_display.config(
            state="disabled"
        )

        report_display.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=report_display.yview
        )

        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg="#173B57",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=25,
            pady=7
        ).pack(pady=12)


    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Service Requests",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ],
            initialfile="jonoshomadhan_report.csv"
        )

        if not file_path:
            return

        success, result = self.report_manager.export_issues_csv(
            file_path
        )

        if success:
            messagebox.showinfo(
                "Export Successful",
                f"Service requests exported successfully.\n\n"
                f"File: {result}",
                parent=self.root
            )

        else:
            messagebox.showerror(
                "Export Failed",
                f"Could not export the CSV file.\n\n{result}",
                parent=self.root
            )


def launch_app(issue_manager):
    root = tk.Tk()

    JonoshomadhanApp(
        root,
        issue_manager
    )

    root.mainloop()