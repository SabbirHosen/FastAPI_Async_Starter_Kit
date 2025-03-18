# FastAPI Async Starter Kit

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A production-ready FastAPI starter template with async SQLAlchemy, PostgreSQL, Alembic migrations, and JWT
authentication. Designed for scalability and maintainability.

## Features

- 🚀 **FastAPI** - Modern, fast (high-performance) web framework
- 🐘 **PostgreSQL** - Robust relational database support
- 🔐 **JWT Authentication** - Secure token-based authentication
- 🧩 **Modular Architecture** - Well-organized project structure
- 🛠️ **Alembic Migrations** - Database schema version control
- ⚡ **Async SQLAlchemy** - High-performance database operations
- 📄 **Pagination** - Built-in pagination with metadata
- 🔧 **Environment Configuration** - Easy environment management
- 🛡️ **Security** - Password hashing, CORS, and more

## Project Structure

fastapi-async-starter/  
├── app/  
│ ├── core/ # Core configurations and utilities  
│ ├── crud/ # Database operations  
│ ├── db/ # Database models and session  
│ ├── schemas/ # Pydantic models  
│ ├── api/ # API endpoints  
│ └── main.py # Application entry point  
├── alembic/ # Database migrations  
├── tests/ # Test cases  
├── .env # Environment variables  
├── requirements.txt # Project dependencies  
├── alembic.ini # Alembic configuration  
└── README.md # Project documentation

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-async-starter.git
   cd fastapi-async-starter
   ```
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
    ```bash
   pip install -r requirements.txt
   ```
4. Copy the example.env to the .env file and update the variables
    ```bash
    cp example.env .env
    ```
5. Set up PostgreSQL:
    - Create a new database
    - Update the `DB_URL` in `.env` with your credentials

6. Run migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

### Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- FastAPI documentation
- SQLAlchemy documentation
- Alembic documentation


### Additional Files

1. **LICENSE** (MIT License):
```text
MIT License

Copyright (c) [2025] [Sabbir Hosen]

Permission is hereby granted...
```