import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag import ask_rag

from services.analytics_service import (
    get_total_revenue,
    get_total_orders,
    get_average_order_value,
    get_top_products,
    get_low_stock_products,
    get_product_profit,
    get_product_performance,
    get_total_profit,
    get_profit_margin,
    get_category_sales,
    get_inventory_risk,
    get_sales_trends,
    get_customer_metrics
)

from ai.gemini import generate_response


def get_business_data():

    return {
        "total_revenue": get_total_revenue(),

        "total_orders": get_total_orders(),

        "average_order_value": get_average_order_value(),

        "total_profit": get_total_profit(),

        "profit_margin": get_profit_margin(),

        "top_products": get_top_products(),

        "low_stock_products": get_low_stock_products(),

        "inventory_risk": get_inventory_risk(),

        "product_profit": get_product_profit(),

        "product_performance": get_product_performance(),

        "category_sales": get_category_sales(),

        "sales_trends": get_sales_trends(),

        "customer_metrics": get_customer_metrics()
    }


def build_prompt(question, business_data):

    # RAG-only question
    if not business_data:
        return f"""
You are an AI E-Commerce Decision Agent.

You help a business owner understand e-commerce
policies, procedures, guidelines, and documented
operational information.

For this question, use the provided knowledge base
as the source of truth.

Do not invent information.

========================
USER QUESTION
========================

{question}

========================
INSTRUCTIONS
========================

1. Answer the question using the knowledge base.

2. Do not invent policies, rules, dates, conditions,
   or procedures.

3. If the knowledge base does not contain enough
   information to answer the question, clearly say
   that the information was not found.

4. Keep the response concise but useful.

5. Distinguish documented information from your
   own interpretation.

Respond using this structure:

KEY FINDING:
Explain the answer.

EVIDENCE:
Mention the relevant information from the knowledge base.

RECOMMENDED ACTION:
Give a practical action if applicable.

REASON:
Explain why the action follows from the documented information.
"""

    # DATABASE / BOTH question
    return f"""
You are an AI E-Commerce Decision Agent.

You help a business owner understand their e-commerce
business and make data-driven decisions.

You have access to the following CURRENT BUSINESS DATA.

IMPORTANT:
The business data below comes directly from the analytics
engine and should be treated as the source of truth.

Do not invent or modify business numbers.

========================
BUSINESS OVERVIEW
========================

TOTAL REVENUE:
{business_data["total_revenue"]}

TOTAL ORDERS:
{business_data["total_orders"]}

AVERAGE ORDER VALUE:
{business_data["average_order_value"]}

TOTAL PROFIT:
{business_data["total_profit"]}

OVERALL PROFIT MARGIN:
{business_data["profit_margin"]}%


========================
PRODUCT ANALYTICS
========================

TOP PRODUCTS:
{business_data["top_products"]}

PRODUCT PROFIT:
{business_data["product_profit"]}

PRODUCT PERFORMANCE:
{business_data["product_performance"]}


========================
INVENTORY ANALYTICS
========================

LOW STOCK PRODUCTS:
{business_data["low_stock_products"]}

INVENTORY RISK:
{business_data["inventory_risk"]}


========================
SALES ANALYTICS
========================

CATEGORY SALES:
{business_data["category_sales"]}

SALES TRENDS:
{business_data["sales_trends"]}


========================
CUSTOMER ANALYTICS
========================

CUSTOMER METRICS:
{business_data["customer_metrics"]}


========================
USER QUESTION
========================

{question}


========================
INSTRUCTIONS
========================

1. Use the provided business data as the source of truth.

2. Do not invent business numbers.

3. Do not claim that something is happening unless the
   provided data supports it.

4. When making a recommendation, explain the relevant
   evidence from the business data.

5. Distinguish between:
   - observed facts from the database
   - your interpretation of those facts
   - recommended actions

6. If the available data is insufficient to answer the
   question, clearly state what information is missing.

7. Do not expose internal implementation details such as
   database queries or Python code.

8. Keep the response concise but useful.

9. When discussing profitability, consider both:
   - total profit
   - profit margin

10. When discussing products, consider both:
    - sales volume
    - profitability

11. When discussing inventory, use the provided inventory
    risk levels rather than inventing new risk categories.

12. When discussing trends, use the provided sales trend data.

13. Do not assume that correlation proves causation.

Respond using this structure:

KEY FINDING:
Explain the main finding.

EVIDENCE:
Mention the relevant business data supporting it.

RECOMMENDED ACTION:
Give a practical business action that could be considered.

REASON:
Explain why the action follows from the available data.
"""

def route_question(question):
    question_lower = question.lower()

    rag_keywords = [
        "policy",
        "policies",
        "return",
        "returns",
        "refund",
        "refunds",
        "cancel",
        "cancellation",
        "warranty",
        "shipping",
        "delivery",
        "terms",
        "condition",
        "conditions",
        "procedure",
        "procedures",
        "guideline",
        "guidelines"
    ]

    database_keywords = [
        "revenue",
        "sales",
        "profit",
        "margin",
        "total orders",
        "number of orders",
        "inventory",
        "stock",
        "customer",
        "customers",
        "units sold",
        "performance",
        "performing",
        "trend",
        "trends",
        "category sales",
        "top products",
        "products",
        "low stock",
        "profit margin",
        "average order value",
        "aov"
    ]

    needs_rag = any(
        keyword in question_lower
        for keyword in rag_keywords
    )

    needs_database = any(
        keyword in question_lower
        for keyword in database_keywords
    )

    if needs_rag and needs_database:
        return "BOTH"

    if needs_rag:
        return "RAG"

    return "DATABASE"


import time




def get_knowledge(question):
    try:
        result = ask_rag(question, k=4)

        if not isinstance(result, dict):
            raise TypeError(
                f"ask_rag returned {type(result).__name__}, expected dict"
            )

        answer = result.get("answer", "")
        sources = result.get("sources", [])

        if not isinstance(answer, str):
            answer = str(answer) if answer is not None else ""

        if not isinstance(sources, list):
            sources = []

        return {
            "answer": answer.strip(),
            "sources": sources
        }

    except Exception as e:
        print(f"[RAG ERROR] {e}", flush=True)
        raise

def ask_agent(question):
    import time

    total_start = time.perf_counter()

    route = route_question(question)
    business_data = None
    knowledge = None

    if route in ["DATABASE", "BOTH"]:
        start = time.perf_counter()
        business_data = get_business_data()
        print(
            f"[TIMING] get_business_data: "
            f"{time.perf_counter() - start:.2f}s",
            flush=True,
        )

    if route in ["RAG", "BOTH"]:
        start = time.perf_counter()
        knowledge = get_knowledge(question)
        print(
            f"[TIMING] get_knowledge: "
            f"{time.perf_counter() - start:.2f}s",
            flush=True,
        )

    if business_data is None:
        business_data = {}

    start = time.perf_counter()
    prompt = build_prompt(question, business_data)

    if knowledge is not None:
        prompt += f"""
KNOWLEDGE BASE ANSWER:
{knowledge["answer"]}
KNOWLEDGE BASE SOURCES:
{knowledge["sources"]}
IMPORTANT: use knowledge base for policies and DB for current business numbers.
"""

    print(
        f"[TIMING] prompt construction: "
        f"{time.perf_counter() - start:.2f}s",
        flush=True,
    )
    print(f"[TIMING] prompt characters: {len(prompt)}", flush=True)

    start = time.perf_counter()
    answer = generate_response(prompt)
    print(
        f"[TIMING] generate_response: "
        f"{time.perf_counter() - start:.2f}s",
        flush=True,
    )

    print(
        f"[TIMING] TOTAL: {time.perf_counter() - total_start:.2f}s",
        flush=True,
    )

    return {
        "question": question,
        "route": route,
        "answer": answer,
        "business_data": business_data,
        "knowledge": knowledge,
    }
