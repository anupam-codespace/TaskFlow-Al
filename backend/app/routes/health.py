"""
app/routes/health.py — Health check endpoint.

Always returns 200 with service status. Used by monitoring tools and
deployment platforms to verify the API is reachable and the DB is connected.
"""

from flask import Blueprint, jsonify, current_app
from app import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health

    Returns 200 with DB connectivity status.
    Never raises — always returns a structured response for observability.
    """
    db_ok = False
    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        current_app.logger.error("DB health check failed: %s", exc)

    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "version": "1.0.0",
    }), 200 if db_ok else 503
