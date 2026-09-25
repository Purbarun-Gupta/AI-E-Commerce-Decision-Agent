from flask import Flask
from flask_cors import CORS

from db.connection import engine


app = Flask(__name__)

#frontend -> flask
CORS(app)


@app.route("/")
def home():
    return {
        "message": "AI E-Commerce Decision Agent API is running",
        "status": "success"
    }


@app.route("/health")
def health():
    try:
        # Test db connection
        with engine.connect() as connection:
            pass

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)