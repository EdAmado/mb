import uuid
import time
import random
from datetime import datetime

class LobbyManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.is_active = False
        self.status = None  # 'lobby', 'guide', 'in_game'
        self.guide_step = 0
        self.admin_id = None
        self.admin_token = None
        self.admin_name = "Admin"
        self.players = {}  # player_id -> dict
        self.settings = {
            "time_limit": 15,
            "base_points": 100
        }
        self.created_at = None

        # Game Match State
        self.match_questions = []  # Exactly 30 questions
        self.question_index = 0    # 0 to 29
        self.question_phase = 'intro'  # 'intro', 'ladder', 'ended', 'round_points', 'last_5_warning', 'finished'
        self.round_started_at = None
        self.current_round_answers = {}  # player_id -> { letter, time_left, time_ratio, timestamp }
        self.player_scores = {}  # player_id -> int
        self.round_deltas = {}  # player_id -> { player_id, name, letter, is_correct, delta, score }

    def open_lobby(self, admin_name=None):
        if self.is_active:
            return None, "A game lobby is already active."

        self.reset()
        self.is_active = True
        self.status = 'lobby'
        self.created_at = datetime.utcnow().isoformat() + 'Z'

        admin_id = uuid.uuid4().hex[:8]
        admin_token = uuid.uuid4().hex
        self.admin_id = admin_id
        self.admin_token = admin_token
        self.admin_name = admin_name.strip() if admin_name and admin_name.strip() else "Admin"

        admin_player = {
            "id": admin_id,
            "name": self.admin_name,
            "is_admin": True,
            "token": admin_token,
            "joined_at": self.created_at
        }
        self.players[admin_id] = admin_player
        self.player_scores[admin_id] = 0
        return admin_player, None

    def join_lobby(self, nickname):
        if not self.is_active:
            return None, "No active game lobby found."
        if self.status != 'lobby':
            return None, "Game is already in progress."

        name = nickname.strip() if nickname else ""
        if not name:
            return None, "Nickname is required."

        player_id = uuid.uuid4().hex[:8]
        player_token = uuid.uuid4().hex
        joined_at = datetime.utcnow().isoformat() + 'Z'

        player = {
            "id": player_id,
            "name": name,
            "is_admin": False,
            "token": player_token,
            "joined_at": joined_at
        }
        self.players[player_id] = player
        self.player_scores[player_id] = 0
        return player, None

    def update_nickname(self, player_id, token, new_name):
        player = self.players.get(player_id)
        if not player or player.get('token') != token:
            return None, "Unauthorized."

        clean_name = new_name.strip() if new_name else ""
        if not clean_name:
            return None, "Nickname cannot be empty."

        player['name'] = clean_name
        if player['is_admin']:
            self.admin_name = clean_name
        return player, None

    def update_settings(self, token, settings_data):
        if not self.is_active or self.admin_token != token:
            return None, "Unauthorized: only the admin can change game settings."

        if 'time_limit' in settings_data:
            try:
                val = int(settings_data['time_limit'])
                if 5 <= val <= 60:
                    self.settings['time_limit'] = val
            except (ValueError, TypeError):
                pass

        if 'base_points' in settings_data:
            try:
                val = int(settings_data['base_points'])
                if 10 <= val <= 1000:
                    self.settings['base_points'] = val
            except (ValueError, TypeError):
                pass

        return self.settings, None

    def leave_lobby(self, player_id, token):
        if not self.is_active:
            return True, None, False
        player = self.players.get(player_id)
        if not player or player.get('token') != token:
            return False, "Unauthorized.", False

        if player.get('is_admin'):
            self.reset()
            return True, None, True  # was_cancelled = True

        del self.players[player_id]
        if player_id in self.player_scores:
            del self.player_scores[player_id]
        return True, None, False

    def cancel_lobby(self, token):
        if not self.is_active:
            return False, "No active lobby."
        if self.admin_token != token:
            return False, "Unauthorized: only the admin can cancel the lobby."

        self.reset()
        return True, None

    def load_match_questions(self, db_session):
        """Builds a curated list of exactly 30 questions from active questions."""
        from models import Question
        all_active = db_session.query(Question).filter_by(is_active=True).all()

        ghost_pool = [q for q in all_active if q.question_type == 'ghost']
        music_pool = [q for q in all_active if q.question_type == 'music_single']
        wrong_pool = [q for q in all_active if q.question_type == 'wrong']
        basic_pool = [q for q in all_active if q.question_type == 'basic']

        random.shuffle(ghost_pool)
        random.shuffle(music_pool)
        random.shuffle(wrong_pool)
        random.shuffle(basic_pool)

        # Select target counts: 1 ghost, 1 music, up to 14 wrong, remaining basic to reach 30
        selected = []
        if ghost_pool:
            selected.append(ghost_pool.pop(0))
        if music_pool:
            selected.append(music_pool.pop(0))

        # Take up to 14 wrong questions
        wrong_take = min(14, len(wrong_pool))
        selected.extend(wrong_pool[:wrong_take])

        # Fill the remainder up to 30 with basic questions
        needed = 30 - len(selected)
        basic_take = min(needed, len(basic_pool))
        selected.extend(basic_pool[:basic_take])

        # If still under 30 (e.g. if DB had fewer), fill with any remaining wrong or active
        if len(selected) < 30:
            remaining = [q for q in all_active if q not in selected]
            random.shuffle(remaining)
            selected.extend(remaining[:30 - len(selected)])

        # Shuffle the final 30 questions
        random.shuffle(selected)
        if len(selected) > 30:
            selected = selected[:30]

        letters = ['A', 'B', 'C', 'D', 'E']
        prepared_questions = []

        for q in selected:
            # Shuffle options so correct answer is not in static index 0
            opts = list(q.options)
            random.shuffle(opts)

            options_data = []
            winning_letter = None

            for idx, opt in enumerate(opts):
                letter = letters[idx] if idx < len(letters) else f'OPT_{idx}'
                is_correct = bool(opt.is_correct)
                options_data.append({
                    'letter': letter,
                    'id': opt.id,
                    'text': opt.text,
                    'media_url': opt.media_url,
                    'is_correct': is_correct
                })

                # Determine winning option letter for question type
                if q.question_type == 'wrong':
                    # In wrong round, picking the FALSE option is winning
                    if not is_correct:
                        winning_letter = letter
                elif q.question_type == 'ghost':
                    # All options false, no winning letter
                    winning_letter = None
                else:
                    # Basic & music_single: True is winning
                    if is_correct:
                        winning_letter = letter

            prepared_questions.append({
                'id': q.id,
                'question_type': q.question_type,
                'text': q.text,
                'media_url': q.media_url,
                'medley_urls': q.medley_urls,
                'options': options_data,
                'valid_letters': [o['letter'] for o in options_data],
                'winning_letter': winning_letter
            })

        self.match_questions = prepared_questions
        return self.match_questions

    def start_game(self, token, db_session=None):
        if not self.is_active:
            return False, "No active lobby."
        if self.admin_token != token:
            return False, "Unauthorized: only the admin can start the game."

        non_admin_players = [p for p in self.players.values() if not p.get('is_admin')]
        if len(non_admin_players) < 1:
            return False, "Cannot start game without at least one player."

        if db_session:
            self.load_match_questions(db_session)

        # Reset scores
        self.player_scores = {pid: 0 for pid in self.players}
        self.status = 'guide'
        self.guide_step = 0
        self.question_index = 0
        self.question_phase = 'intro'
        self.current_round_answers = {}
        self.round_deltas = {}
        return True, None

    def advance_guide(self, token):
        if not self.is_active:
            return False, "No active game."
        if self.admin_token != token:
            return False, "Unauthorized: only the admin can advance the game."

        if self.status == 'guide':
            self.guide_step += 1
            if self.guide_step > 3:
                # Transition to Question 1 Intro!
                self.status = 'in_game'
                self.question_index = 0
                self.question_phase = 'intro'
                self.current_round_answers = {}
                self.round_deltas = {}

        return True, None

    def advance_game(self, token):
        """Admin advances through the wait states."""
        if not self.is_active:
            return False, "No active game."
        if self.admin_token != token:
            return False, "Unauthorized: only the admin can advance the game."

        if self.status == 'guide':
            return self.advance_guide(token)

        if self.status != 'in_game':
            return False, "Game not active."

        # State machine for question progression:
        if self.question_phase == 'intro':
            # Reveal ladder animation and start 15s answering timer
            self.question_phase = 'ladder'
            self.round_started_at = time.time()
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        elif self.question_phase == 'ladder':
            # Admin forced end or timer expired
            self._evaluate_round()
            self.question_phase = 'ended'
            return True, None

        elif self.question_phase == 'ended':
            # If last question of the match finished
            if self.question_index >= len(self.match_questions) - 1:
                self.question_phase = 'finished'
                return True, None

            # If during the last 5 questions (Q26-30, indices 25 to 29):
            # No round points view! Advance directly to next question intro.
            if self.question_index >= 25:
                self.question_index += 1
                self.question_phase = 'intro'
                self.current_round_answers = {}
                self.round_deltas = {}
                return True, None

            # For questions 0 to 24 (Q1 to Q25): show round points view
            self.question_phase = 'round_points'
            return True, None

        elif self.question_phase == 'round_points':
            # If we just viewed round points for Question 25 (index 24):
            # Show the "Last 5 Questions" suspense warning screen!
            if self.question_index == 24:
                self.question_phase = 'last_5_warning'
                return True, None

            # Advance to next question intro
            self.question_index += 1
            self.question_phase = 'intro'
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        elif self.question_phase == 'last_5_warning':
            # Move from warning screen to Question 26 (index 25) intro
            self.question_index = 25
            self.question_phase = 'intro'
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        return True, None

    def end_question_timer(self):
        """Called when 15s timer expires to transition from ladder to ended."""
        if self.status == 'in_game' and self.question_phase == 'ladder':
            self._evaluate_round()
            self.question_phase = 'ended'
            return True
        return False

    def _evaluate_round(self):
        """Calculates points gained or lost based on speed and accuracy."""
        if not self.match_questions or self.question_index >= len(self.match_questions):
            return

        q = self.match_questions[self.question_index]
        q_type = q['question_type']
        base_points = int(self.settings.get('base_points', 100))
        options_by_letter = {opt['letter']: opt for opt in q['options']}

        for pid, player in self.players.items():
            if player.get('is_admin'):
                # Admin does not participate in scoring
                continue

            ans = self.current_round_answers.get(pid)
            if ans:
                letter = ans['letter']
                ratio = ans['time_ratio']
                opt = options_by_letter.get(letter)

                is_correct = False
                if q_type == 'wrong':
                    # Picking FALSE option is correct
                    is_correct = bool(opt and not opt['is_correct'])
                elif q_type == 'ghost':
                    # Any tap in ghost round is wrong
                    is_correct = False
                else:
                    # Basic & music_single
                    is_correct = bool(opt and opt['is_correct'])

                delta = max(1, round(base_points * ratio))
                points_delta = delta if is_correct else -delta

                self.player_scores[pid] = self.player_scores.get(pid, 0) + points_delta
                self.round_deltas[pid] = {
                    'player_id': pid,
                    'name': player['name'],
                    'letter': letter,
                    'is_correct': is_correct,
                    'delta': points_delta,
                    'score': self.player_scores[pid]
                }
            else:
                # Player did not answer before 15s timer expired
                if q_type == 'ghost':
                    # Ghost trap survived! Full base points awarded
                    points_delta = base_points
                    self.player_scores[pid] = self.player_scores.get(pid, 0) + points_delta
                    self.round_deltas[pid] = {
                        'player_id': pid,
                        'name': player['name'],
                        'letter': None,
                        'is_correct': True,
                        'delta': points_delta,
                        'score': self.player_scores[pid],
                        'survived_ghost': True
                    }
                else:
                    self.round_deltas[pid] = {
                        'player_id': pid,
                        'name': player['name'],
                        'letter': None,
                        'is_correct': None,
                        'delta': 0,
                        'score': self.player_scores.get(pid, 0)
                    }

    def submit_answer(self, player_id, token, letter):
        """Records a player's single answer lock-in during the 15s window."""
        if not self.is_active or self.status != 'in_game':
            return False, "No active question in progress."

        if self.question_phase != 'ladder':
            return False, "Question is not currently accepting answers."

        player = self.players.get(player_id)
        if not player or player.get('token') != token:
            return False, "Unauthorized."

        if player_id in self.current_round_answers:
            return False, "Answer already submitted."

        q = self.match_questions[self.question_index]
        if letter not in q['valid_letters']:
            return False, "Invalid option letter."

        elapsed = time.time() - (self.round_started_at or time.time())
        time_left = max(0.0, 15.0 - elapsed)
        time_ratio = max(0.01, min(1.0, time_left / 15.0))

        self.current_round_answers[player_id] = {
            'letter': letter,
            'time_left': round(time_left, 2),
            'time_ratio': time_ratio,
            'timestamp': time.time()
        }
        return True, None

    def get_scoreboard(self, token):
        """Returns leaderboard if allowed; blocks during question and during last 5 questions."""
        if not self.is_active or self.status != 'in_game':
            return {"allowed": False, "reason": "No active match."}

        # 1. Blocked during active 15s question ladder
        if self.question_phase == 'ladder':
            return {"allowed": False, "reason": "Scoreboard cannot be viewed during a question."}

        # 2. Blocked during last 5 questions (Q26-30, indices >= 25) and last 5 warning screen
        if self.question_index >= 25 or self.question_phase == 'last_5_warning':
            return {"allowed": False, "reason": "Scoreboard is hidden for the final 5 questions."}

        # Build sorted leaderboard
        ranked = [
            {
                "id": pid,
                "name": p["name"],
                "score": self.player_scores.get(pid, 0)
            }
            for pid, p in self.players.items()
            if not p["is_admin"]
        ]
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return {"allowed": True, "leaderboard": ranked}

    def get_public_state(self):
        if not self.is_active:
            return {
                "is_active": False,
                "status": None,
                "players": [],
                "settings": self.settings,
                "guide_step": 0
            }

        sanitized_players = [
            {
                "id": p["id"],
                "name": p["name"],
                "is_admin": p["is_admin"],
                "joined_at": p["joined_at"],
                "has_answered": p["id"] in self.current_round_answers
            }
            for p in self.players.values()
        ]

        state = {
            "is_active": True,
            "status": self.status,
            "admin_id": self.admin_id,
            "admin_name": self.admin_name,
            "players": sanitized_players,
            "settings": self.settings,
            "created_at": self.created_at,
            "guide_step": self.guide_step
        }

        if self.status == 'in_game' and self.match_questions:
            q_idx = self.question_index
            q = self.match_questions[q_idx] if q_idx < len(self.match_questions) else None

            # Prepare sanitized question representation
            question_data = None
            if q:
                # In intro: options are hidden
                if self.question_phase == 'intro':
                    options_sanitized = []
                # In ladder: options revealed without is_correct
                elif self.question_phase == 'ladder':
                    options_sanitized = [
                        {
                            "letter": opt["letter"],
                            "text": opt["text"],
                            "media_url": opt["media_url"]
                        }
                        for opt in q["options"]
                    ]
                # In ended or round_points: full options with correctness
                else:
                    options_sanitized = [
                        {
                            "letter": opt["letter"],
                            "text": opt["text"],
                            "media_url": opt["media_url"],
                            "is_correct": opt["is_correct"]
                        }
                        for opt in q["options"]
                    ]

                question_data = {
                    "id": q["id"],
                    "question_type": q["question_type"],
                    "text": q["text"],
                    "media_url": q["media_url"],
                    "medley_urls": q["medley_urls"],
                    "options": options_sanitized,
                    "valid_letters": q["valid_letters"],
                    "winning_letter": q["winning_letter"] if self.question_phase in ['ended', 'round_points', 'finished'] else None
                }

            state.update({
                "question_index": self.question_index,
                "total_questions": len(self.match_questions),
                "question_phase": self.question_phase,
                "question": question_data,
                "round_started_at": self.round_started_at,
                "round_time_limit": 15,
                "answered_player_ids": list(self.current_round_answers.keys()),
                "round_deltas": self.round_deltas if self.question_phase in ['ended', 'round_points', 'finished'] else {},
                "is_last_5": bool(self.question_index >= 25),
                "can_view_scoreboard": bool(self.question_phase != 'ladder' and self.question_index < 25 and self.question_phase != 'last_5_warning')
            })

            if self.question_phase == 'finished':
                # Final leaderboard
                final_ranked = [
                    {
                        "id": pid,
                        "name": p["name"],
                        "score": self.player_scores.get(pid, 0)
                    }
                    for pid, p in self.players.items()
                    if not p["is_admin"]
                ]
                final_ranked.sort(key=lambda x: x["score"], reverse=True)
                state["final_leaderboard"] = final_ranked

        return state

lobby_manager = LobbyManager()
