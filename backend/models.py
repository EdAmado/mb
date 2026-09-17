from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(50), nullable=False) 
    text = db.Column(db.String(500), nullable=True) 
    media_url = db.Column(db.String(500), nullable=True) 
    medley_urls = db.Column(db.Text, nullable=True) 
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # REMOVED base_points and time_limit from here
    options = db.relationship('Option', backref='question', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'question_type': self.question_type,
            'text': self.text,
            'media_url': self.media_url,
            'medley_urls': self.medley_urls,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'options': [opt.to_dict() for opt in self.options]
        }

class Option(db.Model):
    __tablename__ = 'options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(255), nullable=True)
    media_url = db.Column(db.String(500), nullable=True) 
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'media_url': self.media_url,
            'is_correct': self.is_correct
        }

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_points = db.Column(db.Integer, nullable=False, default=0)
    correct_questions = db.Column(db.Integer, nullable=False, default=0)
    
    # ADDED config to games
    time_limit = db.Column(db.Integer, nullable=False, default=10)
    base_points = db.Column(db.Integer, nullable=False, default=100)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'total_points': self.total_points,
            'correct_questions': self.correct_questions,
            'time_limit': self.time_limit,
            'base_points': self.base_points
        }