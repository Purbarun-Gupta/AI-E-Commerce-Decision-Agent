from flask import Blueprint, request, jsonify
from datetime import date

from db.connection import get_db
from db.models import Inventory, Product


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory"
)


# =========================================================
# GET ALL INVENTORY
# =========================================================

@inventory_bp.route("/", methods=["GET"])
def get_inventory():

    db = next(get_db())

    try:

        inventory = db.query(Inventory).all()

        result = []

        for item in inventory:

            result.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": (
                    item.product.name
                    if item.product
                    else None
                ),
                "current_stock": item.current_stock,
                "reorder_level": item.reorder_level,
                "last_updated": (
                    item.last_updated.isoformat()
                    if item.last_updated
                    else None
                )
            })

        return jsonify(result)

    finally:
        db.close()


# =========================================================
# GET INVENTORY FOR ONE PRODUCT
# =========================================================

@inventory_bp.route("/<int:product_id>", methods=["GET"])
def get_product_inventory(product_id):

    db = next(get_db())

    try:

        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()

        if not inventory:

            return jsonify({
                "error": "Inventory record not found"
            }), 404

        return jsonify({
            "id": inventory.id,
            "product_id": inventory.product_id,
            "product_name": (
                inventory.product.name
                if inventory.product
                else None
            ),
            "current_stock": inventory.current_stock,
            "reorder_level": inventory.reorder_level,
            "last_updated": (
                inventory.last_updated.isoformat()
                if inventory.last_updated
                else None
            )
        })

    finally:
        db.close()


# =========================================================
# CREATE INVENTORY
# =========================================================

@inventory_bp.route("/", methods=["POST"])
def create_inventory():

    db = next(get_db())

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "Request body is required"
            }), 400


        # -------------------------------------------------
        # Validate product_id
        # -------------------------------------------------

        product_id = data.get("product_id")

        if not product_id:

            return jsonify({
                "error": "product_id is required"
            }), 400


        # -------------------------------------------------
        # Check product exists
        # -------------------------------------------------

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:

            return jsonify({
                "error": "Product not found"
            }), 404


        # -------------------------------------------------
        # Check inventory already exists
        # -------------------------------------------------

        existing_inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()

        if existing_inventory:

            return jsonify({
                "error": "Inventory already exists for this product"
            }), 409


        # -------------------------------------------------
        # Create inventory
        # -------------------------------------------------

        current_stock = data.get("current_stock", 0)
        reorder_level = data.get("reorder_level", 10)

        if current_stock < 0:

            return jsonify({
                "error": "current_stock cannot be negative"
            }), 400

        if reorder_level < 0:

            return jsonify({
                "error": "reorder_level cannot be negative"
            }), 400


        inventory = Inventory(
            product_id=product_id,
            current_stock=current_stock,
            reorder_level=reorder_level,
            last_updated=date.today()
        )

        db.add(inventory)

        db.commit()

        db.refresh(inventory)


        return jsonify({

            "message": "Inventory created successfully",

            "inventory": {
                "id": inventory.id,
                "product_id": inventory.product_id,
                "product_name": product.name,
                "current_stock": inventory.current_stock,
                "reorder_level": inventory.reorder_level,
                "last_updated": inventory.last_updated.isoformat()
            }

        }), 201


    except Exception as e:

        db.rollback()

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        db.close()


# =========================================================
# UPDATE INVENTORY
# =========================================================

@inventory_bp.route("/<int:product_id>", methods=["PUT"])
def update_inventory(product_id):

    db = next(get_db())

    try:

        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()

        if not inventory:

            return jsonify({
                "error": "Inventory record not found"
            }), 404


        data = request.get_json()

        if "current_stock" in data:

            if data["current_stock"] < 0:

                return jsonify({
                    "error": "current_stock cannot be negative"
                }), 400

            inventory.current_stock = data["current_stock"]


        if "reorder_level" in data:

            if data["reorder_level"] < 0:

                return jsonify({
                    "error": "reorder_level cannot be negative"
                }), 400

            inventory.reorder_level = data["reorder_level"]


        inventory.last_updated = date.today()

        db.commit()

        db.refresh(inventory)


        return jsonify({

            "message": "Inventory updated successfully",

            "inventory": {
                "id": inventory.id,
                "product_id": inventory.product_id,
                "current_stock": inventory.current_stock,
                "reorder_level": inventory.reorder_level,
                "last_updated": inventory.last_updated.isoformat()
            }

        })


    except Exception as e:

        db.rollback()

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        db.close()