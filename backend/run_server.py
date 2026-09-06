import uvicorn
import os
import sys

if __name__ == "__main__":
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
