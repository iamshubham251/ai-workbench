# Entry point — delegates to the application factory in app/main.py
# Run with: uvicorn main:app --reload
from app.main import app  # noqa: F401
