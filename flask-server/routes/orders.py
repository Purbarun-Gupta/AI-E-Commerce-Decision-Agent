from flask import Blueprint, request, jsonify
from datetime import date

from db.connection import get_db
from db.models import Order, OrderItem, Customer, Product, Inventory


order_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/orders"
)

# GET ALL ORDERS

@order_bp.route("/", methods=["GET"])
def get_orders():

    db = next(get_db())

    try:
        orders = db.query(Order).all()

        result = []

        for order in orders:

            result.append({
                "id": order.id,
                "customer_id": order.customer_id,
                "customer_name": (
                    order.customer.name
                    if order.customer
                    else None
                ),
                "order_date": (
                    order.order_date.isoformat()
                    if order.order_date
                    else None
                ),
                "total_amount": order.total_amount,
                "status": order.status
            })

        return jsonify(result)

    finally:
        db.close()

# GET SINGLE ORDER

@order_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):

    db = next(get_db())

    try:

        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        items = []

        for item in order.items:

            items.append({
                "product_id": item.product_id,
                "product_name": (
                    item.product.name
                    if item.product
                    else None
                ),
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.quantity * item.unit_price
            })

        return jsonify({
            "id": order.id,
            "customer_id": order.customer_id,
            "customer_name": (
                order.customer.name
                if order.customer
                else None
            ),
            "order_date": (
                order.order_date.isoformat()
                if order.order_date
                else None
            ),
            "total_amount": order.total_amount,
            "status": order.status,
            "items": items
        })

    finally:
        db.close()

# CREATE ORDER

@order_bp.route("/", methods=["POST"])
def create_order():

    db = next(get_db())

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        if not data.get("customer_id"):
            return jsonify({
                "error": "customer_id is required"
            }), 400

        if not data.get("items"):
            return jsonify({
                "error": "At least one order item is required"
            }), 400


       
        # 2. Check customer exists
       

        customer = db.query(Customer).filter(
            Customer.id == data["customer_id"]
        ).first()

        if not customer:
            return jsonify({
                "error": "Customer not found"
            }), 404


       
        # 3. Convert order date
       

        try:

            if data.get("order_date"):
                order_date = date.fromisoformat(
                    data["order_date"]
                )
            else:
                order_date = date.today()

        except ValueError:

            return jsonify({
                "error": "order_date must be in YYYY-MM-DD format"
            }), 400


       
        # 4. Process all products
       

        order_items_data = []

        total_amount = 0

        for item in data["items"]:

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            # Validate product_id
            if not product_id:
                return jsonify({
                    "error": "product_id is required for every item"
                }), 400

            # Validate quantity
            if not quantity or quantity <= 0:
                return jsonify({
                    "error": "quantity must be greater than 0"
                }), 400


            
            # Check product exists
            

            product = db.query(Product).filter(
                Product.id == product_id
            ).first()

            if not product:
                return jsonify({
                    "error": f"Product {product_id} not found"
                }), 404


            
            # Check inventory exists
            

            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id
            ).first()

            if not inventory:
                return jsonify({
                    "error": (
                        f"Inventory record not found "
                        f"for product {product_id}"
                    )
                }), 404


            
            # Check stock
            

            if inventory.current_stock < quantity:

                return jsonify({
                    "error": (
                        f"Insufficient stock for "
                        f"product {product.name}. "
                        f"Available: {inventory.current_stock}, "
                        f"Requested: {quantity}"
                    )
                }), 400


            
            # Calculate subtotal
            

            unit_price = product.price

            subtotal = quantity * unit_price

            total_amount += subtotal


            # Store temporarily
            order_items_data.append({
                "product": product,
                "inventory": inventory,
                "quantity": quantity,
                "unit_price": unit_price
            })


       
        # 5. Create Order
       

        order = Order(
            customer_id=data["customer_id"],
            order_date=order_date,
            total_amount=total_amount,
            status=data.get("status", "Completed")
        )

        db.add(order)

        # Generate order.id
        db.flush()


       
        # 6. Create Order Items
       

        for item in order_items_data:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product"].id,
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )

            db.add(order_item)


            
            # Reduce inventory
            

            item["inventory"].current_stock -= item["quantity"]
            item["inventory"].last_updated = date.today()


       
        # 7. Commit transaction
       

        db.commit()

        db.refresh(order)


       
        # 8. Response
       

        return jsonify({

            "message": "Order created successfully",

            "order": {
                "id": order.id,
                "customer_id": order.customer_id,
                "order_date": order.order_date.isoformat(),
                "total_amount": order.total_amount,
                "status": order.status
            }

        }), 201


    except Exception as e:

        db.rollback()

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        db.close()