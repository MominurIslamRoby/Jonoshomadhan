
import json
from pathlib import Path


class JSONStorage:
    """Handles saving and loading application data using JSON."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def load_data(self):
        """Load records from a JSON file."""

        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

                if not content:
                    return []

                data = json.loads(content)

                if not isinstance(data, list):
                    print("Warning: JSON data must be a list.")
                    return []

                if not all(isinstance(item, dict) for item in data):
                    print("Warning: Invalid record found in JSON file.")
                    return []

                return data

        except json.JSONDecodeError:
            print("Warning: JSON file contains invalid data.")
            return []

        except OSError as error:
            print(f"File reading error: {error}")
            return []

    def save_data(self, data):
        """Save records to a JSON file."""

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            return True

        except (OSError, TypeError, ValueError) as error:
            print(f"File saving error: {error}")
            return False
