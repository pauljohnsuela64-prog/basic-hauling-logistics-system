# Basic Hauling Logistics System

A Python and MySQL-based logistics management system designed to record, manage, and monitor transportation records.

This project was developed as a BSIT portfolio project to practice Python programming, MySQL database management, CRUD operations, and building a simple desktop-based management system.

## Features

* 🚚 Add and manage truck information
* 📝 Add transportation records
* 🔍 Search transportation records
* 📋 View existing records
* ✏️ Update records
* 🗑️ Delete records
* 📊 Manage transportation data using MySQL
* 🖥️ User-friendly Python application interface

## Technologies Used

* **Python** — Application development and system logic
* **MySQL** — Database management
* **mysql-connector-python** — Python-to-MySQL connection
* **python-dotenv** — Secure environment variable management
* **Git & GitHub** — Version control and project hosting

## Database

The system uses a MySQL database to store and manage logistics information.

Example transportation information includes:

* Date of transportation
* Place of transportation
* Liters
* Price
* Previous ODO
* Current ODO
* Truck information

## Project Structure

```text
basic-hauling-logistics-system/
│
├── app.py          # Main application
├── database.py     # Database connection and database functions
├── .gitignore      # Files excluded from Git
└── README.md       # Project documentation
```

## How to Run

### 1. Install Python

Make sure Python is installed on your computer.

### 2. Install the required Python packages

```bash
pip install mysql-connector-python python-dotenv
```

### 3. Set up MySQL

Create the required MySQL database and tables used by the application.

The database name used by this project is:

```text
bbasic_hauling
```

### 4. Configure the environment file

Create a `.env` file in the project folder and add your MySQL password:

```text
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
```

**Do not upload your `.env` file to GitHub.** It contains sensitive database credentials and is excluded using `.gitignore`.

### 5. Run the application

From the project folder, run:

```bash
python app.py
```

## What I Learned

Through this project, I practiced:

* Python programming
* MySQL database management
* Connecting Python applications to MySQL
* CRUD operations
* Organizing application code
* Using environment variables to protect sensitive information
* Git and GitHub version control
* Troubleshooting programming and database errors

## Screenshots

### Main Application

![Main Application](Login.jpg)

## Future Improvements  

Possible future improvements include:

* User login and authentication
* Dashboard with statistics
* Reports and data export
* Improved user interface
* Automated calculations and summaries
* Better database validation
* Additional logistics management features

## Author

**Paul John Suela**

BSIT Student
ICCT Colleges
