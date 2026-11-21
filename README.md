# Jonoshomadhan (জনসমাধান)

### A Multi-City Corporation Citizen Service Request and Work Order Management System

**Tagline:** নাগরিকের সমস্যা, সমাধানের অগ্রযাত্রা।

---

## 1. Project Overview

Jonoshomadhan is a Python-based desktop application designed to manage citizen service requests for City Corporations in Bangladesh.

The system allows citizens' reported problems to be recorded and managed. It helps administrators monitor requests, assign responsible departments, update request statuses, and generate analytical reports.

The project is developed as an academic prototype for the **Programming in Python** course. It demonstrates how Python programming concepts can be applied to solve a practical civic service management problem.

**Note:** Jonoshomadhan is an independent academic prototype and is not an officially endorsed or integrated government system.

## 2. Project Objectives

- Provide a centralized system for managing citizen service requests.
- Organize requests by City Corporation, ward, and issue category.
- Support department assignment and request status tracking.
- Maintain persistent records using JSON files.
- Generate analytical reports and export request data to CSV.

## 3. Key Features

### Request Management
- Create new citizen service requests.
- View all submitted requests.
- Search requests using their unique ID.
- Edit existing request information.
- Delete requests when necessary.

### Department Management
- Assign requests to responsible departments.
- Load department information from JSON data.
- Track assigned and unassigned requests.

### Status Management
- Submitted
- Under Review
- Assigned
- In Progress
- Resolved
- Rejected

### Analytics and Reporting
- Display total service requests.
- Calculate resolved and pending requests.
- Calculate the resolution percentage.
- Generate status-wise breakdowns.
- Generate category-wise breakdowns.
- Generate department-wise breakdowns.

### Data Management
- Store application data in JSON files.
- Load saved records when the application starts.
- Save changes for persistent data storage.
- Export request records to CSV format.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Tkinter | Graphical User Interface |
| JSON | Data storage and persistence |
| CSV | Report data export |
| datetime | Date and time handling |
| os and pathlib | File and directory management |

**Dependencies:** Python Standard Library only. No third-party packages are required.

## 5. Project Structure

```text
Jonoshomadhan/
│
├── data/
│   ├── corporations.json
│   ├── departments.json
│   └── issues.json
│
├── main.py
├── models.py
├── issue_manager.py
├── storage.py
├── interface.py
├── report_manager.py
├── .gitignore
└── README.md
```

### Main Modules

| File | Responsibility |
|---|---|
| `main.py` | Application entry point |
| `models.py` | Defines the CommunityIssue class |
| `issue_manager.py` | Handles request management and business logic |
| `storage.py` | Handles JSON file reading and writing |
| `interface.py` | Implements the Tkinter graphical interface |
| `report_manager.py` | Generates analytics and CSV reports |

## 6. Installation and Execution

### Prerequisites
- Python 3.10 or later
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
```

### Step 2: Navigate to the Project Directory

```bash
cd Jonoshomadhan
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

### Step 5: Run the Application

```bash
python main.py
```

The Jonoshomadhan desktop application will launch.

## 7. Data Storage

The application uses JSON files for local data persistence.

- `corporations.json` stores City Corporation information.
- `departments.json` stores department information.
- `issues.json` stores citizen service request records.

Changes made through the application are saved to the corresponding JSON file, allowing records to remain available after the application is closed.

## 8. Sample Issue Categories

- Waste Management
- Road Maintenance
- Drainage
- Street Lighting
- Public Facilities
- Other

## 9. Future Improvements

- Citizen registration and authentication.
- Separate administrative and departmental accounts.
- Real-time citizen request tracking.
- Notifications for request status changes.
- Interactive maps and location-based reporting.
- Database integration using PostgreSQL.
- Web and mobile application support.
- Deployment for multiple City Corporations.

## 10. Academic Information

**Project Name:** Jonoshomadhan (জনসমাধান)

**Course:** CSC 4162 – Programming in Python

**Semester:** Fall 2026–27

**Project Type:** Python Desktop Application

**Development Approach:** Object-Oriented Programming

---

*Jonoshomadhan — নাগরিকের সমস্যা, সমাধানের অগ্রযাত্রা।*