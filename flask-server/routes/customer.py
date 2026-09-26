from flask import Blueprint, request, jsonify
from datetime import date

from db.connection import get_db
from db.models import Customer


customer_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers"
)

# GET ALL CUSTOMERS

@customer_bp.route("/", methods=["GET"])
def get_customers():

    db = next(get_db())

    try:
        customers = db.query(Customer).all()

        result = []

        for customer in customers:
            result.append({
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "location": customer.location,
                "registration_date": (
                    customer.registration_date.isoformat()
                    if customer.registration_date
                    else None
                )
            })

        return jsonify(result)

    finally:
        db.close()


# GET ONE CUSTOMER

@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):

    db = next(get_db())

    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id
        ).first()

        if not customer:
            return jsonify({
                "error": "Customer not found"
            }), 404

        return jsonify({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "location": customer.location,
            "registration_date": (
                customer.registration_date.isoformat()
                if customer.registration_date
                else None
            )
        })

    finally:
        db.close()

# CREATE CUSTOMER

@customer_bp.route("/", methods=["POST"])
def create_customer():

    db = next(get_db())

    try:
        data = request.get_json()

        # Check required fields
        if not data.get("name") or not data.get("email"):
            return jsonify({
                "error": "name and email are required"
            }), 400

        # Check if email already exists
        existing_customer = db.query(Customer).filter(
            Customer.email == data["email"]
        ).first()

        if existing_customer:
            return jsonify({
                "error": "Customer with this email already exists"
            }), 409

        # Convert string date to Python date object
        registration_date = None

        if data.get("registration_date"):
            registration_date = date.fromisoformat(
                data["registration_date"]
            )

        customer = Customer(
            name=data["name"],
            email=data["email"],
            location=data.get("location"),
            registration_date=registration_date
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return jsonify({
            "message": "Customer created successfully",
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "location": customer.location,
                "registration_date": (
                    customer.registration_date.isoformat()
                    if customer.registration_date
                    else None
                )
            }
        }), 201

    except ValueError:

        db.rollback()

        return jsonify({
            "error": "registration_date must be in YYYY-MM-DD format"
        }), 400

    except Exception as e:

        db.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        db.close()