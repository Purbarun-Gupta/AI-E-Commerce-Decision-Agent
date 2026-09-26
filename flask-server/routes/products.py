from flask import Blueprint, request, jsonify

from db.connection import get_db
from db.models import Product


product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


# GET ALL PRODUCTS
@product_bp.route("/", methods=["GET"])
def get_products():

    db = next(get_db())

    try:
        products = db.query(Product).all()

        result = []

        for product in products:
            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "cost_price": product.cost_price
            })

        return jsonify(result)

    finally:
        db.close()


# GET ONE PRODUCT
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):

    db = next(get_db())

    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        return jsonify({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "cost_price": product.cost_price
        })

    finally:
        db.close()


# CREATE PRODUCT
@product_bp.route("/", methods=["POST"])
def create_product():

    db = next(get_db())

    try:
        data = request.get_json()

        product = Product(
            name=data["name"],
            category=data["category"],
            price=data["price"],
            cost_price=data["cost_price"]
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return jsonify({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "cost_price": product.cost_price
        }), 201

    finally:
        db.close()


# UPDATE PRODUCT
@product_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    db = next(get_db())

    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        data = request.get_json()

        product.name = data.get(
            "name",
            product.name
        )

        product.category = data.get(
            "category",
            product.category
        )

        product.price = data.get(
            "price",
            product.price
        )

        product.cost_price = data.get(
            "cost_price",
            product.cost_price
        )

        db.commit()
        db.refresh(product)

        return jsonify({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "cost_price": product.cost_price
        })

    finally:
        db.close()


# DELETE PRODUCT
@product_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    db = next(get_db())

    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        db.delete(product)
        db.commit()

        return jsonify({
            "message": "Product deleted successfully"
        })

    finally:
        db.close()