import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db
from routes import api
from lobby import lobby_manager

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

def create_app():
    app = Flask(__name__)
    CORS(app)  # Allows our Vue frontend to talk to the Flask backend
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fallback.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    
    db.init_app(app)
    socketio.init_app(app)
    
    with app.app_context():
        # Creates tables if they don't exist
        db.create_all()

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Welcome to mr-because API!"})

    app.register_blueprint(api, url_prefix='/api')

    # --- REST LOBBY STATUS ENDPOINT ---
    @app.route('/api/lobby/status', methods=['GET'])
    def get_lobby_status():
        state = lobby_manager.get_public_state()
        return jsonify(state), 200

    # --- SOCKET.IO EVENT HANDLERS ---
    @socketio.on('connect')
    def handle_connect():
        # Automatically subscribe client to global updates (for landing page)
        join_room('global')

    @socketio.on('join_lobby_room')
    def handle_join_lobby_room():
        join_room('lobby')
        emit('lobby_state', lobby_manager.get_public_state())

    @socketio.on('get_lobby_state')
    def handle_get_state():
        state = lobby_manager.get_public_state()
        emit('lobby_state', state)
        return state

    @socketio.on('open_lobby')
    def handle_open_lobby(data=None):
        data = data or {}
        admin_name = data.get('admin_name', 'Admin')
        admin_player, error = lobby_manager.open_lobby(admin_name)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='global')
        socketio.emit('lobby_updated', state, to='lobby')
        return {
            "success": True,
            "player": admin_player,
            "token": admin_player['token'],
            "lobby": state
        }

    @socketio.on('join_lobby')
    def handle_join_lobby(data=None):
        data = data or {}
        nickname = data.get('nickname', '')
        player, error = lobby_manager.join_lobby(nickname)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='global')
        socketio.emit('lobby_updated', state, to='lobby')
        return {
            "success": True,
            "player": player,
            "token": player['token'],
            "lobby": state
        }

    @socketio.on('update_nickname')
    def handle_update_nickname(data=None):
        data = data or {}
        player_id = data.get('player_id')
        token = data.get('token')
        new_name = data.get('nickname')
        player, error = lobby_manager.update_nickname(player_id, token, new_name)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True, "player": player, "lobby": state}

    @socketio.on('update_settings')
    def handle_update_settings(data=None):
        data = data or {}
        token = data.get('token')
        settings, error = lobby_manager.update_settings(token, data.get('settings', {}))
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True, "settings": settings, "lobby": state}

    @socketio.on('start_game')
    def handle_start_game(data=None):
        data = data or {}
        token = data.get('token')
        success, error = lobby_manager.start_game(token, db_session=db.session)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('game_started', state, to='lobby')
        socketio.emit('lobby_updated', state, to='global')
        return {"success": True, "lobby": state}

    @socketio.on('admin_advance_guide')
    def handle_advance_guide(data=None):
        data = data or {}
        token = data.get('token')
        success, error = lobby_manager.advance_guide(token)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('guide_updated', state, to='lobby')
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True, "lobby": state}

    @socketio.on('admin_advance')
    def handle_admin_advance(data=None):
        data = data or {}
        token = data.get('token')
        success, error = lobby_manager.advance_game(token)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True, "lobby": state}

    @socketio.on('end_question_timer')
    def handle_end_question_timer(data=None):
        lobby_manager.end_question_timer()
        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True, "lobby": state}

    @socketio.on('submit_answer')
    def handle_submit_answer(data=None):
        data = data or {}
        player_id = data.get('player_id')
        token = data.get('token')
        letter = data.get('letter')
        success, error = lobby_manager.submit_answer(player_id, token, letter)
        if error:
            return {"success": False, "error": error}

        state = lobby_manager.get_public_state()
        socketio.emit('lobby_updated', state, to='lobby')
        return {"success": True}

    @socketio.on('get_scoreboard')
    def handle_get_scoreboard(data=None):
        data = data or {}
        token = data.get('token')
        res = lobby_manager.get_scoreboard(token)
        return {"success": True, "data": res}

    @socketio.on('cancel_lobby')
    def handle_cancel_lobby(data=None):
        data = data or {}
        token = data.get('token')
        success, error = lobby_manager.cancel_lobby(token)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        # Broadcast lobby_cancelled so all players in lobby redirect home
        socketio.emit('lobby_cancelled', {"message": "The lobby has been cancelled by the admin."}, to='lobby')
        # Broadcast lobby_updated to global so landing page changes to "Open game"
        socketio.emit('lobby_updated', state, to='global')
        return {"success": True}

    @socketio.on('leave_lobby')
    def handle_leave_lobby(data=None):
        data = data or {}
        player_id = data.get('player_id')
        token = data.get('token')
        success, error, was_cancelled = lobby_manager.leave_lobby(player_id, token)
        if error:
            return {"success": False, "error": error}
        
        state = lobby_manager.get_public_state()
        if was_cancelled:
            socketio.emit('lobby_cancelled', {"message": "The admin left and the lobby was cancelled."}, to='lobby')
            socketio.emit('lobby_updated', state, to='global')
        else:
            socketio.emit('lobby_updated', state, to='lobby')
            socketio.emit('lobby_updated', state, to='global')
        return {"success": True}

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)