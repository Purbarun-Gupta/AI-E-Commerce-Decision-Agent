from flask import Flask
from flask_cors import CORS

from db.connection import engine

from routes.products import product_bp
from routes.customer import customer_bp
from routes.orders import order_bp
from routes.inventory import inventory_bp
from routes.analytics import analytics_bp

app = Flask(__name__)

#products
app.register_blueprint(product_bp)
#customer
app.register_blueprint(customer_bp)
#orders
app.register_blueprint(order_bp)
#inventory
app.register_blueprint(inventory_bp)
#analysis
app.register_blueprint(analytics_bp)

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