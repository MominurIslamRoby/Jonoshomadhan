from models import CommunityIssue


class IssueManager:
    STATUSES = (
        "Submitted",
        "Under Review",
        "Assigned",
        "In Progress",
        "Resolved",
        "Rejected"
    )

    CATEGORIES = (
        "Waste Management",
        "Road Maintenance",
        "Drainage",
        "Street Lighting",
        "Public Facilities",
        "Other"
    )

    def __init__(self, storage):
        self.storage = storage
        self.issues = []
        self.load_issues()

    def load_issues(self):
        records = self.storage.load_data()
        self.issues = []

        for record in records:
            try:
                issue = CommunityIssue.from_dict(record)
                self.issues.append(issue)
            except (KeyError, TypeError, ValueError):
                print("Warning: An invalid request record was skipped.")

    def save_issues(self):
        records = [issue.to_dict() for issue in self.issues]
        return self.storage.save_data(records)

    def generate_issue_id(self):
        numbers = []

        for issue in self.issues:
            try:
                numbers.append(int(issue.issue_id.split("-")[1]))
            except (ValueError, IndexError):
                continue

        return f"JS-{max(numbers, default=1000) + 1}"

    def add_issue(self, issue):
        existing_ids = {item.issue_id for item in self.issues}

        if issue.issue_id in existing_ids:
            return False

        self.issues.append(issue)

        if self.save_issues():
            return True

        self.issues.remove(issue)
        return False

    def create_issue(
        self,
        corporation_id,
        ward_number,
        category,
        location,
        description,
        submission_date
    ):
        if not all([
            corporation_id,
            category,
            isinstance(location, str) and location.strip(),
            isinstance(description, str) and description.strip()
        ]):
            return False, "All fields are required."

        if category not in self.CATEGORIES:
            return False, "Please select a valid issue category."

        if not isinstance(ward_number, int) or ward_number < 1:
            return False, "Ward number must be a positive integer."

        issue = CommunityIssue(
            issue_id=self.generate_issue_id(),
            corporation_id=corporation_id,
            ward_number=ward_number,
            category=category,
            location=location.strip(),
            description=description.strip(),
            submission_date=submission_date
        )

        if self.add_issue(issue):
            return True, issue.issue_id

        return False, "Could not save the request. Please try again."

    def view_issues(self):
        return self.issues

    def search_issue(self, issue_id):
        if not isinstance(issue_id, str):
            return None

        for issue in self.issues:
            if issue.issue_id.lower() == issue_id.strip().lower():
                return issue

        return None

    def update_issue(self, issue_id, category, location, description):
        issue = self.search_issue(issue_id)

        if issue is None:
            return False

        if (
            category not in self.CATEGORIES
            or not isinstance(location, str)
            or not location.strip()
            or not isinstance(description, str)
            or not description.strip()
        ):
            return False

        old_values = (issue.category, issue.location, issue.description)
        issue.update_details(category, location.strip(), description.strip())

        if self.save_issues():
            return True

        issue.update_details(*old_values)
        return False

    def delete_issue(self, issue_id):
        issue = self.search_issue(issue_id)

        if issue is None:
            return False

        self.issues.remove(issue)

        if self.save_issues():
            return True

        self.issues.append(issue)
        return False

    def assign_department(self, issue_id, department):
        issue = self.search_issue(issue_id)

        if issue is None or not isinstance(department, str) or not department.strip():
            return False

        old_values = (issue.department, issue.status)
        issue.assign_department(department.strip())
        issue.update_status("Assigned")

        if self.save_issues():
            return True

        issue.assign_department(old_values[0])
        issue.update_status(old_values[1])
        return False

    def assign_officer(self, issue_id, department, officer_id):
        issue = self.search_issue(issue_id)

        if (
            issue is None
            or not isinstance(department, str)
            or not department.strip()
            or not isinstance(officer_id, str)
            or not officer_id.strip()
        ):
            return False

        old_values = (
            issue.department,
            issue.assigned_officer_id,
            issue.status
        )

        issue.assign_department(department.strip())
        issue.assign_officer(officer_id.strip())
        issue.update_status("Assigned")

        if self.save_issues():
            return True

        issue.assign_department(old_values[0])
        issue.assign_officer(old_values[1])
        issue.update_status(old_values[2])
        return False

    def update_status(self, issue_id, new_status):
        issue = self.search_issue(issue_id)

        if issue is None or new_status not in self.STATUSES:
            return False

        old_status = issue.status
        issue.update_status(new_status)

        if self.save_issues():
            return True

        issue.update_status(old_status)
        return False

    def generate_summary(self):
        total = len(self.issues)
        status_counts = {}
        category_counts = {}
        department_counts = {}

        for issue in self.issues:
            status_counts[issue.status] = status_counts.get(issue.status, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
            department_counts[issue.department] = department_counts.get(issue.department, 0) + 1

        resolved = status_counts.get("Resolved", 0)
        pending = total - resolved - status_counts.get("Rejected", 0)
        resolution_percentage = (resolved / total) * 100 if total else 0

        return {
            "total": total,
            "resolved": resolved,
            "pending": pending,
            "resolution_percentage": round(resolution_percentage, 2),
            "status_counts": status_counts,
            "category_counts": category_counts,
            "department_counts": department_counts
        }
