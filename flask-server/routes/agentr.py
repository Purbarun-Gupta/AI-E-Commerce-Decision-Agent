
from flask import Blueprint, request, jsonify
from ai.agent import ask_agent
import time
import traceback

agent_bp = Blueprint(
    "agent",
    __name__,
    url_prefix="/api/agent"
)


@agent_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    question = data.get("question")

    if not question or not isinstance(question, str):
        return jsonify({
            "error": "question is required"
        }), 400

    try:
        start_time = time.time()
        print(f"[AGENT] Received question: {question}", flush=True)

        result = ask_agent(question)

        elapsed = time.time() - start_time
        print(
            f"[AGENT] ask_agent completed in {elapsed:.2f} seconds",
            flush=True
        )

        return jsonify(result)

    except Exception as e:
        import traceback

        print(f"[AGENT ERROR] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__
        }), 500
