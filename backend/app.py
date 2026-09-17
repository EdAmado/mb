import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from routes import api

def create_app():
    app = Flask(__name__)
    CORS(app) # Allows our Vue frontend to talk to the Flask backend
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fallback.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    
    db.init_app(app)
    
    with app.app_context():
        # Creates tables if they don't exist
        db.create_all()

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Welcome to mr-because API!"})

    # We will add our CRUD routes for questions here next!
    app.register_blueprint(api, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)