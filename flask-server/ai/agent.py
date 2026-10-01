from services.analytics_service import (
    get_total_revenue,
    get_total_orders,
    get_average_order_value,
    get_top_products,
    get_low_stock_products,
    get_product_profit,
    get_category_sales
)

from ai.gemini import generate_response


def get_business_data():

    return {
        "total_revenue": get_total_revenue(),

        "total_orders": get_total_orders(),

        "average_order_value": get_average_order_value(),

        "top_products": get_top_products(),

        "low_stock_products": get_low_stock_products(),

        "product_profit": get_product_profit(),

        "category_sales": get_category_sales()
    }


def build_prompt(question, business_data):

    return f"""
You are an AI E-Commerce Decision Agent.

You help a business owner understand their e-commerce
business and make data-driven decisions.

You have access to the following CURRENT BUSINESS DATA:

TOTAL REVENUE:
{business_data["total_revenue"]}

TOTAL ORDERS:
{business_data["total_orders"]}

AVERAGE ORDER VALUE:
{business_data["average_order_value"]}

TOP PRODUCTS:
{business_data["top_products"]}

LOW STOCK PRODUCTS:
{business_data["low_stock_products"]}

PRODUCT PROFIT:
{business_data["product_profit"]}

CATEGORY SALES:
{business_data["category_sales"]}


USER QUESTION:
{question}


INSTRUCTIONS:

1. Use the provided business data as the source of truth.
2. Do not invent business numbers.
3. Do not claim that something is happening unless the
   provided data supports it.
4. Explain the important evidence behind your conclusion.
5. Give practical business recommendations.
6. If the data is insufficient to answer the question,
   clearly say what information is missing.
7. Keep the response concise but useful.

Respond in this structure:

KEY FINDING:
Explain the main finding.

EVIDENCE:
Mention the relevant business data.

RECOMMENDED ACTION:
Give a practical action the business could consider.

REASON:
Explain why the action follows from the data.
"""


def ask_agent(question):

    business_data = get_business_data()

    prompt = build_prompt(
        question,
        business_data
    )

    answer = generate_response(prompt)

    return {
        "question": question,
        "answer": answer,
        "business_data": business_data
    }