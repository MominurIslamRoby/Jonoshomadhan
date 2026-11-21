class CommunityIssue:
    def __init__(
        self,
        issue_id,
        corporation_id,
        ward_number,
        category,
        location,
        description,
        submission_date,
        department="Not Assigned",
        status="Submitted",
        assigned_officer_id=None
    ):
        self.issue_id = issue_id
        self.corporation_id = corporation_id
        self.ward_number = ward_number
        self.category = category
        self.location = location
        self.description = description
        self.submission_date = submission_date
        self.department = department
        self.status = status
        self.assigned_officer_id = assigned_officer_id

    def update_status(self, new_status):
        self.status = new_status

    def assign_department(self, department):
        self.department = department

    def assign_officer(self, officer_id):
        self.assigned_officer_id = officer_id

    def update_details(self, category, location, description):
        self.category = category
        self.location = location
        self.description = description

    def to_dict(self):
        return {
            "issue_id": self.issue_id,
            "corporation_id": self.corporation_id,
            "ward_number": self.ward_number,
            "category": self.category,
            "location": self.location,
            "description": self.description,
            "submission_date": self.submission_date,
            "department": self.department,
            "status": self.status,
            "assigned_officer_id": self.assigned_officer_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            issue_id=data["issue_id"],
            corporation_id=data["corporation_id"],
            ward_number=data["ward_number"],
            category=data["category"],
            location=data["location"],
            description=data["description"],
            submission_date=data["submission_date"],
            department=data.get("department", "Not Assigned"),
            status=data.get("status", "Submitted"),
            assigned_officer_id=data.get("assigned_officer_id")
        )
