from flask import Blueprint, request, jsonify

from ai.agent import ask_agent


agent_bp = Blueprint(
    "agent",
    __name__,
    url_prefix="/api/agent"
)


@agent_bp.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "question is required"
        }), 400

    try:

        result = ask_agent(question)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500