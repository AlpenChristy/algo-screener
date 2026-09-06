import sys
import os

# Add backend and app directory to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(backend_dir, "app")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.main import app
