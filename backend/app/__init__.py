from flask import Flask
from flask_cors import CORS
from .routes.ai_routes import ai_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    return app 