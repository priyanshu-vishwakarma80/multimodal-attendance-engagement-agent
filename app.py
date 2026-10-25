"""
Multimodal Attendance & Engagement Agent
Main Flask Application Entry Point.
"""

import sys
import logging
from flask import Flask, jsonify
from config import Config
from utils.storage_utils import init_db
from routes.view_routes import view_bp
from routes.api_routes import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory for Flask gateway."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize local SQLite storage
    init_db()
    logger.info("Database initialized successfully.")

    # Register Blueprints
    app.register_blueprint(view_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error occurred", "status": 500}), 500

    return app

app = create_app()

if __name__ == "__main__":
    print("=" * 65)
    print(" Multimodal Attendance & Engagement Agent - Server Starting")
    print(f" Web Dashboard: http://localhost:{Config.PORT}")
    print(f" Offline Privacy Mode: {Config.PRIVACY_OFFLINE_MODE}")
    print(f" Gemini GenAI: {'Enabled' if Config.GEMINI_API_KEY else 'Local Offline Heuristics'}")
    print("=" * 65)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
