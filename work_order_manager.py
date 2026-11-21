
from datetime import datetime
from storage import JSONStorage


class WorkOrderManager:
    STATUSES = (
        "Assigned",
        "Accepted",
        "In Progress",
        "Completed"
    )

    VERIFICATION_STATUSES = (
        "Not Submitted",
        "Pending",
        "Verified",
        "Rejected"
    )

    def __init__(self):
        self.storage = JSONStorage("data/work_orders.json")
        self.work_orders = []
        self.load_work_orders()

    def load_work_orders(self):
        records = self.storage.load_data()
        self.work_orders = []

        for record in records:
            try:
                required_fields = (
                    "work_order_id",
                    "issue_id",
                    "corporation_id",
                    "department",
                    "officer_id",
                    "status",
                    "created_at"
                )

                if all(record.get(field) for field in required_fields):
                    record.setdefault("verification_status", "Not Submitted")
                    record.setdefault("verification_notes", "")
                    record.setdefault("verified_at", None)
                    record.setdefault("updated_at", record["created_at"])
                    self.work_orders.append(record)

            except (AttributeError, TypeError):
                print("Warning: An invalid work order was skipped.")

    def save_work_orders(self):
        return self.storage.save_data(self.work_orders)

    def generate_work_order_id(self):
        numbers = []

        for order in self.work_orders:
            try:
                number = int(order["work_order_id"].split("-")[1])
                numbers.append(number)
            except (ValueError, IndexError, KeyError):
                continue

        return f"WO-{max(numbers, default=1000) + 1}"

    def create_work_order(self, issue):
        if not issue.assigned_officer_id:
            return False, "Please assign an officer first."

        existing = self.get_work_order_by_issue(issue.issue_id)

        if existing:
            if existing["status"] != "Assigned":
                return False, "A work order already exists for this request."

            old_department = existing["department"]
            old_officer = existing["officer_id"]

            existing["department"] = issue.department
            existing["officer_id"] = issue.assigned_officer_id

            if self.save_work_orders():
                return True, existing["work_order_id"]

            existing["department"] = old_department
            existing["officer_id"] = old_officer
            return False, "Could not update the work order."

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        work_order = {
            "work_order_id": self.generate_work_order_id(),
            "issue_id": issue.issue_id,
            "corporation_id": issue.corporation_id,
            "department": issue.department,
            "officer_id": issue.assigned_officer_id,
            "status": "Assigned",
            "verification_status": "Not Submitted",
            "verification_notes": "",
            "verified_at": None,
            "created_at": now,
            "updated_at": now
        }

        self.work_orders.append(work_order)

        if self.save_work_orders():
            return True, work_order["work_order_id"]

        self.work_orders.remove(work_order)
        return False, "Could not save the work order."

    def get_all_work_orders(self):
        return self.work_orders

    def get_work_order(self, work_order_id):
        if not isinstance(work_order_id, str):
            return None

        for order in self.work_orders:
            if order["work_order_id"].lower() == work_order_id.strip().lower():
                return order

        return None

    def get_work_order_by_issue(self, issue_id):
        if not isinstance(issue_id, str):
            return None

        for order in self.work_orders:
            if order["issue_id"].lower() == issue_id.strip().lower():
                return order

        return None

    def update_work_order_status(self, work_order_id, new_status):
        order = self.get_work_order(work_order_id)

        if order is None or new_status not in self.STATUSES:
            return False

        if order.get("verification_status") == "Verified":
            return False

        old_status = order["status"]
        old_updated_at = order["updated_at"]
        old_verification = order.get("verification_status", "Not Submitted")
        old_notes = order.get("verification_notes", "")

        order["status"] = new_status
        order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if new_status == "Completed":
            order["verification_status"] = "Pending"
            order["verification_notes"] = ""
        elif new_status == "In Progress":
            order["verification_status"] = "Not Submitted"
            order["verification_notes"] = ""

        if self.save_work_orders():
            return True

        order["status"] = old_status
        order["updated_at"] = old_updated_at
        order["verification_status"] = old_verification
        order["verification_notes"] = old_notes
        return False

    def verify_work_order(self, work_order_id, approved, notes):
        order = self.get_work_order(work_order_id)

        if order is None:
            return False, "Work order not found."

        if order["status"] != "Completed":
            return False, "Only completed work orders can be verified."

        if order.get("verification_status") != "Pending":
            return False, "This work order is not awaiting verification."

        if not isinstance(notes, str) or not notes.strip():
            return False, "Verification notes are required."

        old_values = (
            order.get("verification_status"),
            order.get("verification_notes"),
            order.get("verified_at"),
            order["status"],
            order["updated_at"]
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if approved:
            order["verification_status"] = "Verified"
        else:
            order["verification_status"] = "Rejected"
            order["status"] = "In Progress"

        order["verification_notes"] = notes.strip()
        order["verified_at"] = now
        order["updated_at"] = now

        if self.save_work_orders():
            return True, "Work order verification saved successfully."

        order["verification_status"] = old_values[0]
        order["verification_notes"] = old_values[1]
        order["verified_at"] = old_values[2]
        order["status"] = old_values[3]
        order["updated_at"] = old_values[4]

        return False, "Could not save the verification."
