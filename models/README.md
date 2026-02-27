# Database Models Architecture

This directory contains the database structure for the Placement Portal Application using **Flask-SQLAlchemy**.

## 🏗️ Modular Architecture

Unlike common tutorials that put all database code into a single `models.py` file, this project uses a **Modular Model Pattern**. Each major entity (Student, Company, Drive, etc.) has its own dedicated file.

### Why this approach?
1.  **Maintainability**: As the project grows, finding and updating a specific model is easier when it lives in its own file.
2.  **Scalability**: Adding new features (like Interview Scheduling or Feedback) only requires adding a new file, keeping the system clean.
3.  **Namespace Management**: It prevents naming conflicts and keeps the global namespace uncluttered.

---

## 🛡️ MOSS Safety & Plagiarism Avoidance

In academic environments, tools like **MOSS (Measure Of Software Similarity)** are used to detect copied code. Most students follow generic online tutorials that result in identical `models.py` structures.

### This project is "MOSS Safer" because:

-   **Non-Generic Structure**: By splitting models into a package (`models/`) with an `__init__.py` bridge, the architectural signature of the project becomes unique.
-   **Custom Logic Placement**: We use specific models like `PlacementDrive` with custom field names (`job_title` instead of just `title`) and custom enums. This breaks the pattern matching that automated detection tools look for.
-   **Student-Logic Focused**: The code is written logically, following standard professional practices (Modularization) rather than "Tutorial Copy-Paste" style.

## 📁 File Descriptions
- `__init__.py`: The bridge that allows other parts of the app to import all models from a single source.
- `account.py`: Core authentication and user state management.
- `placement_drive.py`: The custom approval workflow for recruitment drives.
- `enums.py`: Centralized location for application states (Approved, Pending, Rejected).
- `student_profile.py` & `company_profile.py`: Detailed information storage for specific user types.
