
import csv
import os
from datetime import datetime


class ReportManager:
    """Generates reports and exports service request data."""

    def __init__(self, issue_manager):
        self.issue_manager = issue_manager

    def generate_report(self):
        """Generate a complete summary report."""

        summary = self.issue_manager.generate_summary()
        issues = self.issue_manager.view_issues()

        report = {
            "generated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "total_requests": summary["total"],
            "resolved_requests": summary["resolved"],
            "pending_requests": summary["pending"],
            "resolution_rate": summary["resolution_percentage"],
            "status_breakdown": summary["status_counts"],
            "category_breakdown": summary["category_counts"],
            "department_breakdown": summary["department_counts"],
            "total_categories": len(summary["category_counts"]),
            "total_departments": len(summary["department_counts"]),
            "issue_records": len(issues)
        }

        return report

    def generate_report_text(self):
        """Convert the report into readable text."""

        report = self.generate_report()

        lines = [
            "JONOSHOMADHAN",
            "CITIZEN SERVICE REQUEST REPORT",
            "=" * 45,
            f"Generated At: {report['generated_at']}",
            "",
            "GENERAL STATISTICS",
            "-" * 45,
            f"Total Requests: {report['total_requests']}",
            f"Resolved Requests: {report['resolved_requests']}",
            f"Pending Requests: {report['pending_requests']}",
            f"Resolution Rate: {report['resolution_rate']}%",
            "",
            "STATUS BREAKDOWN",
            "-" * 45
        ]

        for status, count in report["status_breakdown"].items():
            lines.append(f"{status}: {count}")

        lines.extend([
            "",
            "CATEGORY BREAKDOWN",
            "-" * 45
        ])

        for category, count in report["category_breakdown"].items():
            lines.append(f"{category}: {count}")

        lines.extend([
            "",
            "DEPARTMENT BREAKDOWN",
            "-" * 45
        ])

        for department, count in report["department_breakdown"].items():
            lines.append(f"{department}: {count}")

        lines.extend([
            "",
            "=" * 45,
            "End of Report"
        ])

        return "\n".join(lines)

    def export_issues_csv(self, file_path):
        """Export all service requests to a CSV file."""

        issues = self.issue_manager.view_issues()

        fieldnames = [
            "issue_id",
            "corporation_id",
            "ward_number",
            "category",
            "location",
            "description",
            "submission_date",
            "department",
            "status"
        ]

        try:
            directory = os.path.dirname(file_path)

            if directory:
                os.makedirs(directory, exist_ok=True)

            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as csv_file:

                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=fieldnames
                )

                writer.writeheader()

                for issue in issues:
                    writer.writerow({
                        "issue_id": issue.issue_id,
                        "corporation_id": issue.corporation_id,
                        "ward_number": issue.ward_number,
                        "category": issue.category,
                        "location": issue.location,
                        "description": issue.description,
                        "submission_date": issue.submission_date,
                        "department": issue.department,
                        "status": issue.status
                    })

            return True, file_path

        except (OSError, PermissionError, ValueError) as error:
            return False, str(error)
