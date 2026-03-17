"""Development entry point: python run.py"""

from app import create_app
from app import scheduler

app = create_app()
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
