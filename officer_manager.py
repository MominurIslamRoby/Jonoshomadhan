
from storage import JSONStorage


class OfficerManager:
    """Manages department officers and officer assignments."""

    def __init__(self):
        self.storage = JSONStorage("data/officers.json")
        self.officers = []
        self.load_officers()

    def load_officers(self):
        """Load officer records from JSON storage."""
        records = self.storage.load_data()
        self.officers = []

        for record in records:
            try:
                required_fields = (
                    "officer_id",
                    "name",
                    "department_id",
                    "corporation_id",
                    "designation"
                )

                if not all(record.get(field) for field in required_fields):
                    continue

                self.officers.append(record)

            except (AttributeError, TypeError):
                print("Warning: An invalid officer record was skipped.")

    def get_all_officers(self):
        """Return all valid officer records."""
        return self.officers

    def get_officers_by_department(self, department_id, corporation_id):
        """Return officers belonging to a specific department and corporation."""
        return [
            officer
            for officer in self.officers
            if officer["department_id"] == department_id
            and officer["corporation_id"] == corporation_id
        ]

    def search_officer(self, officer_id):
        """Find an officer using their unique ID."""
        for officer in self.officers:
            if officer["officer_id"].lower() == officer_id.lower():
                return officer

        return None
