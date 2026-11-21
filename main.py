
from storage import JSONStorage
from issue_manager import IssueManager
from interface import launch_app


def main():
    """Start the Jonoshomadhan application."""

    # Initialize JSON storage
    storage = JSONStorage("data/issues.json")

    # Initialize request management system
    issue_manager = IssueManager(storage)

    # Launch the Tkinter graphical interface
    launch_app(issue_manager)


if __name__ == "__main__":
    main()
