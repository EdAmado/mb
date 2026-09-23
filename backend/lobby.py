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
            "base_points": 100,
            "lock_chosen_questions": True
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
        self.wrong_block_deltas = {}  # Cumulative points gained/lost during wrong questions block
        self.round_points_type = 'standard'  # 'standard' | 'wrong_block'
        self.final_countdown_label = ""

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

        if 'lock_chosen_questions' in settings_data:
            self.settings['lock_chosen_questions'] = bool(settings_data['lock_chosen_questions'])

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

    def is_first_wrong_question(self, index):
        if index < 0 or index >= len(self.match_questions):
            return False
        curr_q = self.match_questions[index]
        if curr_q['question_type'] != 'wrong':
            return False
        if index == 0:
            return True
        prev_q = self.match_questions[index - 1]
        return prev_q['question_type'] != 'wrong'

    def is_audio_question(self, index):
        if index < 0 or index >= len(self.match_questions):
            return False
        return self.match_questions[index]['question_type'] == 'music_single'

    def _get_final_countdown_label(self, index):
        labels = {
            25: "5 Questions Remaining",
            26: "4 Questions Remaining",
            27: "3 Questions Remaining",
            28: "2 Questions Remaining",
            29: "Final Question"
        }
        return labels.get(index, "Final Question")

    def load_match_questions(self, db_session):
        """Builds a curated list of exactly 30 questions from active questions.
        Guarantees:
        1. Final 5 questions (indices 25-29) are strictly 'basic' questions.
        2. All 'wrong' questions are grouped consecutively in one block.
        3. Includes 1 ghost and 1 music question.
        4. Intelligently locks questions if lock_chosen_questions is enabled,
           preserving at least one question of each specialty type for subsequent matches.
        """
        random.seed()
        from models import Question
        all_active = db_session.query(Question).filter_by(is_active=True).all()
        if len(all_active) < 30:
            return False, f"Not enough unlocked questions in dataset: only {len(all_active)} available (30 needed). Please unlock questions in Admin or click 'Unlock All Questions'."

        ghost_pool = [q for q in all_active if q.question_type == 'ghost']
        music_pool = [q for q in all_active if q.question_type == 'music_single']
        wrong_pool = [q for q in all_active if q.question_type == 'wrong']
        basic_pool = [q for q in all_active if q.question_type == 'basic']

        random.shuffle(ghost_pool)
        random.shuffle(music_pool)
        random.shuffle(wrong_pool)
        random.shuffle(basic_pool)

        # 1. Final 5 MUST be basic questions
        final_5 = []
        while len(final_5) < 5 and basic_pool:
            final_5.append(basic_pool.pop(0))
        random.shuffle(final_5)

        # 2. For the first 25 questions:
        selected_ghost = [ghost_pool.pop(0)] if ghost_pool else []
        selected_music = [music_pool.pop(0)] if music_pool else []

        # Take up to 12 wrong questions and keep them grouped
        wrong_take = min(12, len(wrong_pool))
        selected_wrong = wrong_pool[:wrong_take]
        random.shuffle(selected_wrong)

        # Remaining needed for first 25
        needed_basic = 25 - (len(selected_ghost) + len(selected_music) + len(selected_wrong))
        basic_take = min(needed_basic, len(basic_pool))
        selected_first_25_basic = basic_pool[:basic_take]
        basic_pool = basic_pool[basic_take:]

        deficit = 25 - (len(selected_ghost) + len(selected_music) + len(selected_wrong) + len(selected_first_25_basic))
        if deficit > 0 and len(wrong_pool) > wrong_take:
            extra_wrong = wrong_pool[wrong_take:wrong_take + deficit]
            selected_wrong.extend(extra_wrong)

        standard_first = selected_ghost + selected_music + selected_first_25_basic
        random.shuffle(standard_first)

        # Place the consecutive block of wrong questions in a randomized position among standard questions
        insert_idx = random.randint(1, max(1, len(standard_first) - 1)) if len(standard_first) > 1 else len(standard_first) // 2
        first_25 = standard_first[:insert_idx] + selected_wrong + standard_first[insert_idx:]

        # If still under 25, fill with any leftover questions
        if len(first_25) < 25:
            used_ids = set(q.id for q in first_25 + final_5)
            leftover = [q for q in all_active if q.id not in used_ids]
            random.shuffle(leftover)
            first_25.extend(leftover[:25 - len(first_25)])

        # Assemble match: first 25 + final 5
        selected = first_25[:25] + final_5

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

        # Intelligent locking if setting is True
        if self.settings.get('lock_chosen_questions', True):
            active_ghost_count = len([q for q in all_active if q.question_type == 'ghost'])
            active_music_count = len([q for q in all_active if q.question_type == 'music_single'])
            active_wrong_count = len([q for q in all_active if q.question_type == 'wrong'])

            for q in selected:
                if q.question_type == 'ghost':
                    if active_ghost_count > 1:
                        q.is_active = False
                        active_ghost_count -= 1
                elif q.question_type == 'music_single':
                    if active_music_count > 1:
                        q.is_active = False
                        active_music_count -= 1
                elif q.question_type == 'wrong':
                    if active_wrong_count > 1:
                        q.is_active = False
                        active_wrong_count -= 1
                else:
                    q.is_active = False

            try:
                db_session.commit()
            except Exception:
                db_session.rollback()

        self.match_questions = prepared_questions
        return True, None

    def start_game(self, token, db_session=None):
        if not self.is_active:
            return False, "No active lobby."
        if self.admin_token != token:
            return False, "Unauthorized: only the admin can start the game."

        non_admin_players = [p for p in self.players.values() if not p.get('is_admin')]
        if len(non_admin_players) < 1:
            return False, "Cannot start game without at least one player."

        if db_session:
            success, err = self.load_match_questions(db_session)
            if not success:
                return False, err

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
                # Transition to in_game!
                self.status = 'in_game'
                self.question_index = 0
                self.current_round_answers = {}
                self.round_deltas = {}

                # Check if Question 0 has a special intro
                if self.is_first_wrong_question(0):
                    self.question_phase = 'wrong_round_intro'
                elif self.is_audio_question(0):
                    self.question_phase = 'audio_intro'
                else:
                    self.question_phase = 'intro'

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

        # 1. WRONG ROUND INTRO -> advance into first wrong question
        if self.question_phase == 'wrong_round_intro':
            self.question_phase = 'ladder'
            self.round_started_at = time.time()
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        # 2. AUDIO QUESTION INTRO -> advance into audio question intro (5s countdown -> audio)
        elif self.question_phase == 'audio_intro':
            self.question_phase = 'intro'
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        # 3. INTRO -> advance to ladder (reveals options & starts timer)
        elif self.question_phase == 'intro':
            self.question_phase = 'ladder'
            self.round_started_at = time.time()
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        # 4. LADDER -> evaluates round upon timeout or manual advance
        elif self.question_phase == 'ladder':
            self._evaluate_round()
            self.question_phase = 'ended'
            return True, None

        # 5. ENDED -> determines next step depending on question type / position
        elif self.question_phase == 'ended':
            if self.question_index >= len(self.match_questions) - 1:
                self.question_phase = 'finished'
                return True, None

            curr_q = self.match_questions[self.question_index]

            # If current question is part of the rapid-fire wrong questions block:
            if curr_q['question_type'] == 'wrong':
                next_idx = self.question_index + 1
                next_q = self.match_questions[next_idx] if next_idx < len(self.match_questions) else None

                # If the next question is also a wrong question, jump straight into ladder:
                if next_q and next_q['question_type'] == 'wrong':
                    self.question_index = next_idx
                    self.question_phase = 'ladder'
                    self.round_started_at = time.time()
                    self.current_round_answers = {}
                    self.round_deltas = {}
                    return True, None
                else:
                    # Wrong questions block has finished! Transition to round points summary with cumulative deltas
                    self.question_phase = 'round_points'
                    self.round_points_type = 'wrong_block'
                    self.round_deltas = {}
                    for pid, pdata in self.wrong_block_deltas.items():
                        self.round_deltas[pid] = {
                            'player_id': pid,
                            'name': pdata['name'],
                            'letter': None,
                            'is_correct': pdata['delta'] > 0,
                            'delta': pdata['delta'],
                            'duration': None,
                            'score': self.player_scores.get(pid, 0)
                        }
                    return True, None

            # If in the final 5 questions (Q26-30, indices 25 to 29):
            if self.question_index >= 25:
                next_idx = self.question_index + 1
                if next_idx >= len(self.match_questions):
                    self.question_phase = 'finished'
                    return True, None

                self.question_index = next_idx
                self.question_phase = 'final_countdown'
                self.final_countdown_label = self._get_final_countdown_label(next_idx)
                return True, None

            # Standard questions (0 to 24): show round points view
            self.question_phase = 'round_points'
            self.round_points_type = 'standard'
            return True, None

        # 6. ROUND POINTS -> advances to next question or last_5_warning
        elif self.question_phase == 'round_points':
            self.round_points_type = 'standard'
            if self.question_index == 24:
                self.question_phase = 'last_5_warning'
                return True, None

            next_idx = self.question_index + 1
            if next_idx >= len(self.match_questions):
                self.question_phase = 'finished'
                return True, None

            self.question_index = next_idx
            self.current_round_answers = {}
            self.round_deltas = {}

            if self.is_first_wrong_question(next_idx):
                self.question_phase = 'wrong_round_intro'
                self.wrong_block_deltas = {}
            elif self.is_audio_question(next_idx):
                self.question_phase = 'audio_intro'
            else:
                self.question_phase = 'intro'
            return True, None

        # 7. LAST 5 WARNING -> advances to Final Fifth interstitial
        elif self.question_phase == 'last_5_warning':
            self.question_index = 25
            self.question_phase = 'final_countdown'
            self.final_countdown_label = 'Final Fifth'
            self.current_round_answers = {}
            self.round_deltas = {}
            return True, None

        # 8. FINAL COUNTDOWN INTERSTITIAL -> advances into that final question intro
        elif self.question_phase == 'final_countdown':
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
                    'duration': ans.get('duration', 0.0),
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
                        'duration': None,
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
                        'duration': None,
                        'score': self.player_scores.get(pid, 0)
                    }

        # For wrong questions, accumulate points gained or lost into wrong_block_deltas
        if q_type == 'wrong':
            for pid, player in self.players.items():
                if player.get('is_admin'):
                    continue
                if pid not in self.wrong_block_deltas:
                    self.wrong_block_deltas[pid] = {
                        'player_id': pid,
                        'name': player['name'],
                        'delta': 0
                    }
                delta_for_q = self.round_deltas.get(pid, {}).get('delta', 0)
                self.wrong_block_deltas[pid]['delta'] += delta_for_q

    def submit_answer(self, player_id, token, letter):
        """Records a player's single answer lock-in during the answering window."""
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

        total_window = 5.0 if q['question_type'] == 'wrong' else 15.0
        elapsed = time.time() - (self.round_started_at or time.time())
        duration = round(elapsed, 2)
        time_left = max(0.0, total_window - elapsed)
        time_ratio = max(0.01, min(1.0, time_left / total_window))

        self.current_round_answers[player_id] = {
            'letter': letter,
            'time_left': round(time_left, 2),
            'time_ratio': time_ratio,
            'duration': duration,
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
        if self.question_index >= 25 or self.question_phase in ['last_5_warning', 'final_countdown']:
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

    def get_public_state(self, *args, **kwargs):
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

        try:
            from models import Question
            state["total_questions_count"] = Question.query.count()
            state["unlocked_questions_count"] = Question.query.filter_by(is_active=True).count()
        except Exception:
            pass

        if self.status == 'in_game' and self.match_questions:
            q_idx = self.question_index
            q = self.match_questions[q_idx] if q_idx < len(self.match_questions) else None

            # Prepare sanitized question representation
            question_data = None
            if q:
                # Mask ghost as basic until revealed in ended/round_points/finished
                reported_type = q["question_type"]
                if reported_type == 'ghost' and self.question_phase not in ['ended', 'round_points', 'finished']:
                    reported_type = 'basic'

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
                    "question_type": reported_type,
                    "actual_type": q["question_type"] if self.question_phase in ['ended', 'round_points', 'finished'] else None,
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
                "round_points_type": self.round_points_type,
                "final_countdown_label": self.final_countdown_label,
                "question": question_data,
                "round_started_at": self.round_started_at,
                "round_time_limit": 15,
                "answered_player_ids": list(self.current_round_answers.keys()),
                "round_deltas": self.round_deltas if self.question_phase in ['ended', 'round_points', 'finished'] else {},
                "is_last_5": bool(self.question_index >= 25),
                "can_view_scoreboard": bool(self.question_phase != 'ladder' and self.question_index < 25 and self.question_phase not in ['last_5_warning', 'final_countdown'])
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
