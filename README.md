# FarmConn

Welcome to FarmConn! This repository contains both the backend server and the frontend application for the FarmConn platform.
## Project Structure
*   `FarmConn/`: The backend application built with Flask (Python).

## Getting Started
Follow these instructions to set up and run the project locally.
### Prerequisites
*   **Python 3.8+**
*   **Git**
---
### Setup (Flask)
The backend handles the API, database connectivity, and can also serve server-side rendered templates.
1.  **Navigate to the backend directory:**
    ```bash
    cd FarmConn
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    *   **Mac/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Database Setup:**
    Initialize the database and apply migrations.
    ```bash
    flask db upgrade
    ```
    *Note: If you run into issues, you may need to initialize the db first with `flask db init` and `flask db migrate`.*
6.  **Run the Server:**
    ```bash
    python run.py
    ```
    The backend will start at `http://127.0.0.1:5000`.
---

## Troubleshooting
*   **Missing `.env`**: You may need to create a `.env` file in the `FarmConn` directory with your configuration (Secret Key, Database URI, Mail settings). Check `config.py` or ask the project lead for the required variables.
*   **Port Conflicts**: If port 5000 are in use, you can change them in `run.py` respectively.
