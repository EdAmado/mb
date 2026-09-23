import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from models import db, Question, Option, GameSession

api = Blueprint('api', __name__)

# --- AUTHENTICATION ---
@api.route('/auth/verify', methods=['POST'])
def verify_admin_password():
    data = request.json or {}
    password = data.get('password', '')
    expected_password = os.getenv('ADMIN_PASSWORD', 'admin')
    
    if password and password == expected_password:
        return jsonify({"success": True, "message": "Authenticated"}), 200
    
    return jsonify({"error": "Invalid password"}), 401

# --- MEDIA UPLOADS ---
@api.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Generate unique filename to avoid collisions
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    upload_path = current_app.config['UPLOAD_FOLDER']
    file.save(os.path.join(upload_path, filename))
    
    return jsonify({"url": f"/api/uploads/{filename}"}), 201

@api.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def validate_question_data(data):
    question_type = data.get('question_type')
    if not question_type:
        return "question_type is required"
    
    options = data.get('options', [])
    if not isinstance(options, list) or len(options) < 2 or len(options) > 5:
        return "Question must have between 2 and 5 options"
    
    # If one option has an image, others need them aswell.
    has_image = [bool(opt.get('media_url')) for opt in options]
    if any(has_image) and not all(has_image):
        return "If one option has an image, all options must have an image"
    
    # There can only be one correct option (not counting ghost)
    correct_count = sum(1 for opt in options if opt.get('is_correct'))
    if question_type == 'ghost':
        if correct_count > 0:
            return "Ghost questions cannot have any correct options"
    else:
        if correct_count != 1:
            return "There must be exactly one correct option"
            
    return None

# --- QUESTIONS CRUD ---
@api.route('/questions', methods=['GET'])
def get_questions():
    query = Question.query
    if request.args.get('active_only') == 'true':
        query = query.filter_by(is_active=True)
    questions = query.order_by(Question.created_at.desc()).all()
    return jsonify([q.to_dict() for q in questions]), 200

@api.route('/questions', methods=['POST'])
def create_question():
    data = request.json or {}
    
    error = validate_question_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    new_question = Question(
        question_type=data.get('question_type'),
        text=data.get('text'),
        media_url=data.get('media_url') or None,
        medley_urls=data.get('medley_urls'),
        is_active=data.get('is_active', True)
    )
    db.session.add(new_question)
    db.session.flush() # Get the new_question.id before committing
    
    options_data = data.get('options', [])
    for opt in options_data:
        new_option = Option(
            question_id=new_question.id,
            text=opt.get('text'),
            media_url=opt.get('media_url') or None,
            is_correct=bool(opt.get('is_correct', False))
        )
        db.session.add(new_option)
        
    db.session.commit()
    return jsonify(new_question.to_dict()), 201

@api.route('/questions/<int:id>', methods=['PUT'])
def update_question(id):
    question = Question.query.get_or_404(id)
    data = request.json or {}
    
    error = validate_question_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    question.question_type = data.get('question_type')
    question.text = data.get('text')
    question.media_url = data.get('media_url') or None
    question.medley_urls = data.get('medley_urls')
    if 'is_active' in data:
        question.is_active = bool(data['is_active'])
    
    # Replace options
    Option.query.filter_by(question_id=question.id).delete()
    options_data = data.get('options', [])
    for opt in options_data:
        new_option = Option(
            question_id=question.id,
            text=opt.get('text'),
            media_url=opt.get('media_url') or None,
            is_correct=bool(opt.get('is_correct', False))
        )
        db.session.add(new_option)
        
    db.session.commit()
    return jsonify(question.to_dict()), 200

@api.route('/questions/<int:id>/toggle-lock', methods=['PATCH'])
def toggle_question_lock(id):
    question = Question.query.get_or_404(id)
    question.is_active = not question.is_active
    db.session.commit()
    return jsonify(question.to_dict()), 200

@api.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return '', 204

@api.route('/questions/unlock-all', methods=['POST', 'PATCH'])
def unlock_all_questions():
    Question.query.update({Question.is_active: True})
    db.session.commit()
    from lobby import lobby_manager
    state = lobby_manager.get_public_state()
    return jsonify({"success": True, "message": "All questions unlocked", "lobby": state}), 200

# --- GAME SESSIONS ---
@api.route('/games', methods=['GET'])
def get_games():
    games = GameSession.query.order_by(GameSession.timestamp.desc()).all()
    return jsonify([g.to_dict() for g in games]), 200

@api.route('/games', methods=['POST'])
def save_game():
    data = request.json or {}
    new_game = GameSession(
        total_points=data.get('total_points', 0),
        correct_questions=data.get('correct_questions', 0),
        time_limit=data.get('time_limit', 10),
        base_points=data.get('base_points', 100)
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify(new_game.to_dict()), 201