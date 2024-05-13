# Ananas Funeral Welfare System

A Django application designed to manage funeral welfare services for the Ananas community.

**Features**

* **Member Management:**
    * Register new members
    * Update member information
    * Track member contributions
* **Case Management:**
    * Create and track funeral cases
    * Associate contributions with specific cases
    * Monitor case progress
* **Reporting:**
    * Generate reports on member contributions:
        * By date range
        * By member type
        * etc.
    * View case details and associated contributions


**Installation**

1. **Prerequisites:**
    * Python 3.x ([https://www.python.org/downloads/](https://www.python.org/downloads/))
    * pip (usually included with Python installation)

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/Gitauwairimu/ananas.git



3. **Create a Virtual Environment (Recommended)::**

A virtual environment isolates project dependencies, preventing conflicts with system-wide packages. Here's an example using venv:
Bash

   ```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

```

Use code with caution.

Install Dependencies:
Bash


    pip install -r requirements.txt

Use code with caution.

Configure Local Settings:

Copy the example settings file and modify it with your database credentials and other environment-specific configurations:
Bash


cp settings.example.py local_settings.py

Use code with caution.

Important: Never commit local_settings.py to version control.

Database Migrations:
Bash

    python manage.py migrate

Use code with caution.

Run Development Server (Optional):
Bash


    python manage.py runserver

Use code with caution.

    This starts the Django development server at http://localhost:8000/ by default.

Usage

Detailed instructions on using the application's functionalities will likely be documented within the application code or separate documentation files. Consult those resources for specific usage guidelines.

Contributing

We welcome contributions from the community! If you'd like to contribute, please create a pull request following these steps:

    Fork the repository.
    Create a new branch for your changes.
    Implement your modifications.
    Commit your changes with descriptive commit messages.
    Create a pull request.

We'll review your contributions and provide feedback.

License

This application is licensed under the MIT License (see the LICENSE file for details).
