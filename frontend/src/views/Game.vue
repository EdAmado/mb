<template>
    <div class="min-h-screen bg-gray-950 text-gray-100 select-none">

        <!-- CONFETTI CANVAS ON FINISH -->
        <canvas ref="confettiCanvasRef" class="fixed inset-0 pointer-events-none z-50 w-full h-full"></canvas>

        <!-- CANCELLATION NOTICE MODAL (FOR PLAYERS AND ADMIN) -->
        <transition name="fade">
            <div v-if="cancellationNotice"
                class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-gray-800 border border-red-500/50 rounded-2xl p-6 max-w-md w-full shadow-2xl text-center">
                    <div class="w-16 h-16 bg-red-900/50 border border-red-500/40 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
                        🛑
                    </div>
                    <h3 class="text-2xl font-bold text-white mb-2">Game Cancelled</h3>
                    <p class="text-gray-300 text-sm mb-6">{{ cancellationNotice }}</p>
                    <button @click="returnHome"
                        class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition shadow-lg text-center cursor-pointer">
                        Return to Home
                    </button>
                </div>
            </div>
        </transition>

        <!-- ADMIN CANCEL GAME CONFIRMATION MODAL (TRIGGERED BY ESCAPE KEY) -->
        <transition name="fade">
            <div v-if="showCancelConfirmModal && isAdmin" @click.self="showCancelConfirmModal = false"
                class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full shadow-2xl text-center relative">
                    <button @click="showCancelConfirmModal = false"
                        class="absolute top-4 right-4 text-gray-400 hover:text-white text-xl cursor-pointer">✕</button>

                    <div class="w-14 h-14 bg-red-900/40 border border-red-500/40 rounded-2xl flex items-center justify-center text-2xl mx-auto mb-4">
                        ⚠️
                    </div>
                    <h3 class="text-2xl font-bold text-white mb-2">Cancel Game?</h3>
                    <p class="text-gray-300 text-sm mb-6">
                        Are you sure you want to cancel the match? All players will be returned to the home screen.
                    </p>

                    <div class="flex gap-3">
                        <button @click="confirmCancelGame" type="button"
                            class="flex-1 py-3 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold transition shadow-lg cursor-pointer">
                            Yes, Cancel
                        </button>
                        <button @click="showCancelConfirmModal = false" type="button"
                            class="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-xl font-semibold transition cursor-pointer">
                            Resume
                        </button>
                    </div>
                </div>
            </div>
        </transition>

        <!-- TOTAL SCOREBOARD MODAL (TOGGLED BY ADMIN PRESSING KEY 'V') -->
        <transition name="fade">
            <div v-if="showScoreboardModal && isAdmin" @click.self="showScoreboardModal = false"
                class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-gray-900 border border-yellow-500/40 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl relative">
                    <button @click="showScoreboardModal = false"
                        class="absolute top-5 right-5 text-gray-400 hover:text-white text-xl cursor-pointer">✕</button>

                    <div class="flex items-center gap-3 mb-6">
                        <span class="w-12 h-12 rounded-2xl bg-yellow-500/20 border border-yellow-500/40 text-yellow-400 flex items-center justify-center text-2xl">
                            🏆
                        </span>
                        <div>
                            <h3 class="text-2xl font-black text-white">Current Standings</h3>
                            <p class="text-xs text-gray-400">Total leaderboard ranking</p>
                        </div>
                    </div>

                    <div v-if="scoreboardList.length === 0" class="text-center py-8 text-gray-400 text-sm">
                        No scores recorded yet.
                    </div>

                    <div v-else class="space-y-2.5 max-h-96 overflow-y-auto pr-1">
                        <div v-for="(p, idx) in scoreboardList" :key="p.id"
                            class="flex items-center justify-between p-3.5 rounded-2xl border transition"
                            :class="idx === 0
                                ? 'bg-yellow-950/40 border-yellow-500/50 shadow-md shadow-yellow-900/20'
                                : idx === 1
                                    ? 'bg-gray-800/80 border-gray-600'
                                    : idx === 2
                                        ? 'bg-amber-950/30 border-amber-700/50'
                                        : 'bg-gray-800/40 border-gray-800'">
                            <div class="flex items-center gap-3">
                                <span class="w-7 h-7 rounded-xl font-black text-xs flex items-center justify-center"
                                    :class="idx === 0
                                        ? 'bg-yellow-500 text-gray-950'
                                        : idx === 1
                                            ? 'bg-gray-300 text-gray-950'
                                            : idx === 2
                                                ? 'bg-amber-600 text-white'
                                                : 'bg-gray-700 text-gray-300'">
                                    {{ idx + 1 }}
                                </span>
                                <span class="font-bold text-sm text-gray-200 truncate max-w-[200px]">
                                    {{ p.name }}
                                </span>
                            </div>
                            <span class="font-mono font-extrabold text-base"
                                :class="p.score >= 0 ? 'text-yellow-400' : 'text-red-400'">
                                {{ p.score }} pts
                            </span>
                        </div>
                    </div>

                    <div class="mt-6 text-center text-xs text-gray-500 font-mono">
                        Press <kbd class="bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700 text-gray-300">V</kbd> again or <kbd class="bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700 text-gray-300">Esc</kbd> to close
                    </div>
                </div>
            </div>
        </transition>

        <!-- ========================================================================= -->
        <!-- 1. PLAYER VIEW: PERMANENT RESPONSIVE MOBILE CONTROLLER (OPTIONS A, B, C, D, E) -->
        <!-- ========================================================================= -->
        <div v-if="!isAdmin" class="min-h-screen flex flex-col justify-between p-3.5 sm:p-5 max-w-lg mx-auto">

            <!-- PLAYER HEADER -->
            <header class="flex justify-between items-center bg-gray-900/90 border border-gray-800 rounded-2xl px-4 py-3 shadow-lg">
                <div class="flex items-center space-x-2.5">
                    <span class="w-9 h-9 rounded-full bg-blue-600/30 border border-blue-500/40 text-blue-300 font-extrabold text-sm flex items-center justify-center">
                        {{ playerName.charAt(0).toUpperCase() }}
                    </span>
                    <span class="font-bold text-sm text-gray-200 truncate max-w-[140px] sm:max-w-[200px]">
                        {{ playerName }}
                    </span>
                </div>

                <div class="flex items-center space-x-2">
                    <span class="px-3 py-1 rounded-full text-xs font-semibold border"
                        :class="playerStatusBadgeClass">
                        {{ playerStatusText }}
                    </span>
                </div>
            </header>

            <!-- CONTROLLER BUTTONS: A, B, C, D, E (ALWAYS VISIBLE THROUGHOUT THE GAME) -->
            <main class="my-auto py-3">
                <div class="text-center mb-3.5">
                    <p class="text-xs sm:text-sm font-semibold tracking-wide"
                        :class="isAnsweringActive ? 'text-yellow-300 animate-pulse' : 'text-gray-400'">
                        {{ playerPromptText }}
                    </p>
                    <div v-if="selectedOptionLetter" class="mt-1">
                        <span class="inline-block px-3 py-0.5 rounded-full text-xs font-black bg-blue-900/60 border border-blue-400 text-blue-200">
                            🔒 Locked in: Option {{ selectedOptionLetter }}
                        </span>
                    </div>
                </div>

                <!-- Grid of 5 Choices: 2x2 + 1 bottom centered -->
                <div class="grid grid-cols-2 gap-3 sm:gap-4">

                    <!-- Option A -->
                    <button type="button"
                        @click="handlePlayerSelect('A')"
                        :disabled="!isOptionClickable('A')"
                        class="h-24 sm:h-32 rounded-2xl border-2 transition-all duration-150 flex flex-col items-center justify-center relative overflow-hidden select-none"
                        :class="getOptionBtnClass('A', 'red')">
                        <span class="text-3xl sm:text-4xl font-black tracking-wider">A</span>
                        <span class="text-[10px] sm:text-xs uppercase tracking-widest font-bold opacity-80 mt-1">
                            {{ selectedOptionLetter === 'A' ? 'Selected' : 'Option A' }}
                        </span>
                    </button>

                    <!-- Option B -->
                    <button type="button"
                        @click="handlePlayerSelect('B')"
                        :disabled="!isOptionClickable('B')"
                        class="h-24 sm:h-32 rounded-2xl border-2 transition-all duration-150 flex flex-col items-center justify-center relative overflow-hidden select-none"
                        :class="getOptionBtnClass('B', 'blue')">
                        <span class="text-3xl sm:text-4xl font-black tracking-wider">B</span>
                        <span class="text-[10px] sm:text-xs uppercase tracking-widest font-bold opacity-80 mt-1">
                            {{ selectedOptionLetter === 'B' ? 'Selected' : 'Option B' }}
                        </span>
                    </button>

                    <!-- Option C -->
                    <button type="button"
                        @click="handlePlayerSelect('C')"
                        :disabled="!isOptionClickable('C')"
                        class="h-24 sm:h-32 rounded-2xl border-2 transition-all duration-150 flex flex-col items-center justify-center relative overflow-hidden select-none"
                        :class="getOptionBtnClass('C', 'amber')">
                        <span class="text-3xl sm:text-4xl font-black tracking-wider">C</span>
                        <span class="text-[10px] sm:text-xs uppercase tracking-widest font-bold opacity-80 mt-1">
                            {{ selectedOptionLetter === 'C' ? 'Selected' : 'Option C' }}
                        </span>
                    </button>

                    <!-- Option D -->
                    <button type="button"
                        @click="handlePlayerSelect('D')"
                        :disabled="!isOptionClickable('D')"
                        class="h-24 sm:h-32 rounded-2xl border-2 transition-all duration-150 flex flex-col items-center justify-center relative overflow-hidden select-none"
                        :class="getOptionBtnClass('D', 'emerald')">
                        <span class="text-3xl sm:text-4xl font-black tracking-wider">D</span>
                        <span class="text-[10px] sm:text-xs uppercase tracking-widest font-bold opacity-80 mt-1">
                            {{ selectedOptionLetter === 'D' ? 'Selected' : 'Option D' }}
                        </span>
                    </button>

                    <!-- Option E (Spans full width on bottom) -->
                    <button type="button"
                        @click="handlePlayerSelect('E')"
                        :disabled="!isOptionClickable('E')"
                        class="col-span-2 h-20 sm:h-28 rounded-2xl border-2 transition-all duration-150 flex flex-col items-center justify-center relative overflow-hidden select-none"
                        :class="getOptionBtnClass('E', 'purple')">
                        <span class="text-3xl sm:text-4xl font-black tracking-wider">E</span>
                        <span class="text-[10px] sm:text-xs uppercase tracking-widest font-bold opacity-80 mt-0.5">
                            {{ selectedOptionLetter === 'E' ? 'Selected' : 'Option E' }}
                        </span>
                    </button>
                </div>
            </main>

            <!-- FOOTER INFO -->
            <footer class="text-center py-2">
                <span class="text-xs text-gray-500 font-mono">
                    mr-because • Connected
                </span>
            </footer>
        </div>


        <!-- ========================================================================= -->
        <!-- 2. ADMIN (HOST) VIEW: IMMERSIVE FULL-SCREEN GAME BOARD                     -->
        <!-- Header and Footer are completely removed as requested                     -->
        <!-- ========================================================================= -->
        <div v-else @click="handleAdminScreenClick" class="min-h-screen flex flex-col justify-center p-6 sm:p-10 max-w-5xl mx-auto cursor-pointer select-none relative">

            <!-- AUDIO PLAYER FOR MUSIC QUESTIONS -->
            <audio ref="audioPlayerRef" :src="currentMusicAudioUrl" preload="auto"></audio>

            <!-- MAIN VIEW CONTAINER -->
            <main class="w-full my-auto">

                <!-- ============================================================ -->
                <!-- A. GUIDE WALKTHROUGH VIEW                                    -->
                <!-- ONLY shows the part being showcased, NOT the upcoming parts  -->
                <!-- ============================================================ -->
                <div v-if="gameStatus === 'guide'">
                    <div class="text-center mb-8">
                        <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-blue-900/60 text-blue-300 border border-blue-600/60 inline-block mb-3">
                            Interactive Game Guide
                        </span>
                        <h2 class="text-3xl sm:text-4xl font-extrabold text-white">
                            {{ currentGuideTitle }}
                        </h2>
                        <p class="text-gray-400 text-sm mt-1 max-w-xl mx-auto">
                            {{ currentGuideDescription }}
                        </p>
                    </div>

                    <!-- STEP 0: SHOWCASE QUESTION AREA ONLY -->
                    <div v-if="guideStep === 0"
                        class="p-6 sm:p-10 rounded-3xl bg-blue-950/40 border-2 border-blue-400 ring-4 ring-blue-500/20 shadow-2xl transition-all duration-300">
                        <div class="flex justify-between items-center text-xs text-blue-300 font-mono mb-4">
                            <span>Question 1 / 30 • General Knowledge</span>
                            <span>15s</span>
                        </div>
                        <h3 class="text-2xl sm:text-4xl font-extrabold text-white text-center py-6">
                            "What is the capital city of Australia?"
                        </h3>
                        <div class="mt-4 text-center">
                            <span class="inline-block px-4 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-blue-900/80 text-blue-200 border border-blue-500 animate-pulse">
                                📍 [Question Area] Question text, category, and round number appear here.
                            </span>
                        </div>
                    </div>

                    <!-- STEP 1: SHOWCASE OPTIONS AREA ONLY -->
                    <div v-else-if="guideStep === 1"
                        class="p-6 sm:p-8 rounded-3xl bg-blue-950/40 border-2 border-blue-400 ring-4 ring-blue-500/20 shadow-2xl transition-all duration-300">
                        <div class="text-xs font-bold text-blue-300 uppercase tracking-wider mb-4 flex items-center justify-between">
                            <span>Choices (Correspond to Player Controllers)</span>
                            <span class="text-blue-300 font-bold text-xs animate-pulse">📍 [Options Area]</span>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div class="p-4 bg-red-950/40 border border-red-500/50 rounded-2xl flex items-center gap-3">
                                <span class="w-8 h-8 rounded-xl bg-red-600 text-white font-extrabold text-sm flex items-center justify-center">A</span>
                                <span class="text-base font-semibold text-gray-200">Sydney</span>
                            </div>
                            <div class="p-4 bg-blue-950/40 border border-blue-500/50 rounded-2xl flex items-center gap-3">
                                <span class="w-8 h-8 rounded-xl bg-blue-600 text-white font-extrabold text-sm flex items-center justify-center">B</span>
                                <span class="text-base font-semibold text-gray-200">Melbourne</span>
                            </div>
                            <div class="p-4 bg-amber-950/40 border border-amber-500/50 rounded-2xl flex items-center gap-3">
                                <span class="w-8 h-8 rounded-xl bg-amber-600 text-white font-extrabold text-sm flex items-center justify-center">C</span>
                                <span class="text-base font-semibold text-gray-200">Canberra</span>
                            </div>
                            <div class="p-4 bg-emerald-950/40 border border-emerald-500/50 rounded-2xl flex items-center gap-3">
                                <span class="w-8 h-8 rounded-xl bg-emerald-600 text-white font-extrabold text-sm flex items-center justify-center">D</span>
                                <span class="text-base font-semibold text-gray-200">Brisbane</span>
                            </div>
                            <div class="p-4 bg-purple-950/40 border border-purple-500/50 rounded-2xl flex items-center gap-3 sm:col-span-2">
                                <span class="w-8 h-8 rounded-xl bg-purple-600 text-white font-extrabold text-sm flex items-center justify-center">E</span>
                                <span class="text-base font-semibold text-gray-200">Perth</span>
                            </div>
                        </div>
                        <p class="text-center text-xs text-blue-200 mt-4">
                            Players select letter A, B, C, D, or E on their mobile screens.
                        </p>
                    </div>

                    <!-- STEP 2: SHOWCASE IMAGES & MEDIA ONLY -->
                    <div v-else-if="guideStep === 2"
                        class="p-6 sm:p-8 rounded-3xl bg-blue-950/40 border-2 border-blue-400 ring-4 ring-blue-500/20 shadow-2xl transition-all duration-300">
                        <div class="text-xs font-bold text-blue-300 uppercase tracking-wider mb-4 flex items-center justify-between">
                            <span>Question Visual Assets & Audio Clues</span>
                            <span class="text-blue-300 font-bold text-xs animate-pulse">📍 [Media Area]</span>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div class="h-48 rounded-2xl bg-gray-950 border border-gray-700 flex flex-col items-center justify-center p-4 text-center">
                                <span class="text-5xl mb-2">🖼️</span>
                                <h4 class="font-bold text-sm text-gray-200 mb-1">Visual Clues & Images</h4>
                                <p class="text-xs text-gray-400">Photos, maps, and artwork display here</p>
                            </div>
                            <div class="h-48 rounded-2xl bg-purple-950/40 border border-purple-500/50 flex flex-col items-center justify-center p-4 text-center">
                                <span class="text-5xl mb-2">🎵</span>
                                <h4 class="font-bold text-sm text-purple-200 mb-1">Music Track Visualizer</h4>
                                <p class="text-xs text-gray-400 mb-3">Audio challenges play track automatically</p>
                                <div class="w-3/4 bg-gray-800 h-2 rounded-full overflow-hidden">
                                    <div class="bg-purple-400 h-full w-2/3 animate-pulse"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- STEP 3: SHOWCASE QUESTION TYPES ONLY -->
                    <div v-else-if="guideStep >= 3"
                        class="p-6 sm:p-8 rounded-3xl bg-blue-950/40 border-2 border-blue-400 ring-4 ring-blue-500/20 shadow-2xl transition-all duration-300">
                        <div class="text-center mb-6">
                            <span class="inline-block px-3 py-1 rounded-lg text-xs font-bold bg-blue-900/80 text-blue-200 border border-blue-500 animate-pulse">
                                📍 [Question Types] The 4 distinct game modes in mr-because
                            </span>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="p-4 bg-gray-800 border border-blue-500/40 rounded-2xl">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-2xl">🎯</span>
                                    <h4 class="font-bold text-base text-blue-300">Basic</h4>
                                </div>
                                <p class="text-xs text-gray-400 leading-relaxed">
                                    Standard trivia. Pick the 1 single correct option out of the choices.
                                </p>
                            </div>
                            <div class="p-4 bg-gray-800 border border-red-500/40 rounded-2xl">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-2xl">⚡</span>
                                    <h4 class="font-bold text-base text-red-300">Wrong Round</h4>
                                </div>
                                <p class="text-xs text-gray-400 leading-relaxed">
                                    Rapid fire! Find the 1 <strong>FALSE</strong> option among true options.
                                </p>
                            </div>
                            <div class="p-4 bg-gray-800 border border-purple-500/40 rounded-2xl">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-2xl">👻</span>
                                    <h4 class="font-bold text-base text-purple-300">Ghost Trap</h4>
                                </div>
                                <p class="text-xs text-gray-400 leading-relaxed">
                                    Trap question! All options are FALSE. Don't answer to avoid point loss.
                                </p>
                            </div>
                            <div class="p-4 bg-gray-800 border border-yellow-500/40 rounded-2xl">
                                <div class="flex items-center gap-2 mb-2">
                                    <span class="text-2xl">🎵</span>
                                    <h4 class="font-bold text-base text-yellow-300">Music</h4>
                                </div>
                                <p class="text-xs text-gray-400 leading-relaxed">
                                    Audio listening challenge. Listen to the track and pick the matching title/artist.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>


                <!-- ============================================================ -->
                <!-- B. QUESTION INTRO / LADDER / ENDED VIEW                      -->
                <!-- Options are non-clickable on host board                      -->
                <!-- ============================================================ -->
                <div v-else-if="gameStatus === 'in_game' && currentQuestion && ['intro', 'ladder', 'ended'].includes(questionPhase)">

                    <!-- 15S COUNTDOWN TIMER BAR (SHOWN DURING LADDER PHASE) -->
                    <div v-if="questionPhase === 'ladder'" class="mb-5 bg-gray-900 border border-gray-800 rounded-2xl p-3 shadow-lg">
                        <div class="flex justify-between items-center mb-2 px-1">
                            <span class="text-xs font-bold uppercase tracking-wider text-yellow-400 flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping"></span>
                                Answering Window
                            </span>
                            <span class="font-mono text-xl sm:text-2xl font-black"
                                :class="timerSeconds <= 5 ? 'text-red-400 animate-pulse' : 'text-yellow-400'">
                                {{ timerSeconds }}s
                            </span>
                        </div>
                        <div class="w-full bg-gray-800 h-3 rounded-full overflow-hidden">
                            <div class="h-full transition-all duration-100 ease-linear rounded-full"
                                :class="timerSeconds <= 5 ? 'bg-red-500' : 'bg-gradient-to-r from-yellow-500 to-amber-500'"
                                :style="{ width: `${timerPercentage}%` }">
                            </div>
                        </div>
                        <div class="flex justify-between items-center text-xs text-gray-400 mt-2 px-1">
                            <span>Speed multiplier: {{ Math.round(timerPercentage) }}% points</span>
                            <span>{{ answeredPlayersCount }} of {{ nonAdminPlayersCount }} answered</span>
                        </div>
                    </div>

                    <!-- QUESTION CARD -->
                    <div class="bg-gray-900/90 border border-gray-800 rounded-3xl p-6 sm:p-8 shadow-2xl mb-6 relative overflow-hidden">

                        <!-- TYPE & ROUND HEADER -->
                        <div class="flex flex-wrap justify-between items-center gap-2 mb-4">
                            <div class="flex items-center gap-2">
                                <span class="px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider border shadow-sm"
                                    :class="questionTypeBadgeClass">
                                    {{ questionTypeLabel }}
                                </span>
                                <span v-if="isLastFiveMatch" class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-red-950 border border-red-500/60 text-red-300">
                                    🔒 Final 5 Round
                                </span>
                            </div>

                            <div class="flex items-center gap-4 text-xs font-mono text-gray-400">
                                <span>Question <strong class="text-yellow-400">{{ currentQuestionIndex + 1 }}</strong> / <strong>{{ totalQuestionsCount }}</strong></span>
                                <span>Base: <strong class="text-yellow-400">{{ basePoints }} pts</strong></span>
                            </div>
                        </div>

                        <!-- QUESTION TEXT -->
                        <h3 class="text-2xl sm:text-3xl lg:text-4xl font-black text-white text-center py-3 leading-snug">
                            {{ currentQuestion.text }}
                        </h3>

                        <!-- MEDIA DISPLAY (IMAGE / AUDIO VISUALIZER) -->
                        <div v-if="currentQuestion.media_url" class="mt-4 max-w-md mx-auto">
                            <!-- Image Display -->
                            <div v-if="isImageMedia(currentQuestion.media_url)"
                                class="rounded-2xl overflow-hidden border border-gray-700 bg-gray-950 max-h-64 flex items-center justify-center shadow-lg">
                                <img :src="currentQuestion.media_url" alt="Question visual clue"
                                    class="max-h-64 w-auto object-contain" />
                            </div>

                            <!-- Music Audio Visualizer -->
                            <div v-else-if="currentQuestion.question_type === 'music_single'"
                                class="p-4 bg-purple-950/40 border border-purple-500/50 rounded-2xl flex items-center gap-4">
                                <span class="text-3xl animate-bounce">🎵</span>
                                <div class="flex-1 min-w-0">
                                    <div class="text-xs font-bold text-purple-300 uppercase tracking-wider mb-1">
                                        Music Listening Challenge
                                    </div>
                                    <div class="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
                                        <div class="bg-purple-400 h-full w-full animate-pulse"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- OPTIONS SECTION -->
                    <!-- 1. INTRO WAIT STATE: OPTIONS HIDDEN / PLACEHOLDER -->
                    <div v-if="questionPhase === 'intro'"
                        class="p-8 rounded-3xl bg-gray-900/50 border border-dashed border-gray-800 text-center">
                        <div class="w-12 h-12 rounded-2xl bg-blue-900/30 border border-blue-500/30 text-blue-400 flex items-center justify-center text-xl mx-auto mb-3 animate-pulse">
                            👁️
                        </div>
                        <h4 class="text-lg font-bold text-gray-300">Options are Concealed</h4>
                        <p class="text-xs text-gray-400 mt-1 max-w-md mx-auto">
                            Players are viewing question on the screen. Advance to reveal options and start the 15-second timer.
                        </p>
                    </div>

                    <!-- 2. LADDER ANIMATION & ENDED OPTIONS DISPLAY (NON-CLICKABLE ON HOST BOARD) -->
                    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                        <div v-for="(opt, idx) in currentQuestionOptions" :key="opt.letter"
                            @click.stop
                            class="p-4 rounded-2xl border-2 flex items-center gap-3.5 transition-all duration-300 cursor-default select-none pointer-events-auto"
                            :class="[
                                questionPhase === 'ladder' ? `ladder-item ladder-item-${idx}` : '',
                                getBoardOptionClass(opt)
                            ]">
                            <!-- Letter Badge -->
                            <span class="w-9 h-9 rounded-xl font-black text-sm flex items-center justify-center shrink-0 shadow-md"
                                :class="getBoardOptionBadgeClass(opt)">
                                {{ opt.letter }}
                            </span>

                            <!-- Option Text -->
                            <span class="text-base sm:text-lg font-bold flex-1"
                                :class="getBoardOptionTextClass(opt)">
                                {{ opt.text }}
                            </span>

                            <!-- Reveal Badge (Only in 'ended' phase) -->
                            <span v-if="questionPhase === 'ended' && opt.letter === currentWinningLetter"
                                class="px-2.5 py-1 rounded-lg text-xs font-black bg-green-500 text-gray-950 uppercase tracking-wider shrink-0 shadow-md">
                                ✓ Correct
                            </span>
                            <span v-else-if="questionPhase === 'ended' && currentQuestion.question_type === 'wrong' && opt.is_correct === false"
                                class="px-2.5 py-1 rounded-lg text-xs font-black bg-green-500 text-gray-950 uppercase tracking-wider shrink-0 shadow-md">
                                ✓ FALSE (Winner)
                            </span>
                        </div>
                    </div>

                    <!-- GHOST REVEAL BANNER IN 'ENDED' PHASE -->
                    <div v-if="questionPhase === 'ended' && currentQuestion.question_type === 'ghost'"
                        class="mt-4 p-4 rounded-2xl bg-purple-950/60 border border-purple-500/60 text-center animate-pulse">
                        <span class="text-2xl mr-2">👻</span>
                        <strong class="text-purple-300 font-bold">Ghost Trap Revealed!</strong>
                        <span class="text-xs text-purple-200 ml-2">All options were false! Players who did not answer earned full points!</span>
                    </div>
                </div>


                <!-- ============================================================ -->
                <!-- C. ROUND POINTS SUMMARY VIEW (AFTER QUESTIONS 1-25)          -->
                <!-- ============================================================ -->
                <div v-else-if="gameStatus === 'in_game' && questionPhase === 'round_points'">
                    <div class="text-center mb-6">
                        <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-yellow-900/60 text-yellow-300 border border-yellow-600/60 inline-block mb-3">
                            Question {{ (currentQuestionIndex !== null ? currentQuestionIndex + 1 : 1) }} Points
                        </span>
                        <h2 class="text-3xl sm:text-4xl font-black text-white">
                            Round Points Awarded
                        </h2>
                        <p class="text-gray-400 text-xs sm:text-sm mt-1">
                            Points gained or lost based on response speed and accuracy.
                        </p>
                    </div>

                    <div class="bg-gray-900/90 border border-gray-800 rounded-3xl p-6 sm:p-8 shadow-2xl max-w-2xl mx-auto">
                        <div v-if="Object.keys(roundDeltas).length === 0" class="text-center py-8 text-gray-400 text-sm">
                            No answers registered for this round.
                        </div>

                        <div v-else class="space-y-3">
                            <div v-for="(res, pid) in roundDeltas" :key="pid"
                                class="p-4 rounded-2xl border flex items-center justify-between transition"
                                :class="res.delta > 0
                                    ? 'bg-green-950/30 border-green-500/50'
                                    : res.delta < 0
                                        ? 'bg-red-950/30 border-red-500/50'
                                        : 'bg-gray-800/40 border-gray-700/60'">

                                <div class="flex items-center gap-3">
                                    <span class="w-10 h-10 rounded-xl font-black text-sm flex items-center justify-center"
                                        :class="res.delta > 0
                                            ? 'bg-green-600 text-white'
                                            : res.delta < 0
                                                ? 'bg-red-600 text-white'
                                                : 'bg-gray-700 text-gray-300'">
                                        {{ res.delta > 0 ? '✓' : res.delta < 0 ? '✗' : '—' }}
                                    </span>

                                    <div>
                                        <h4 class="font-bold text-base text-white">{{ res.name }}</h4>
                                        <p class="text-xs text-gray-400">
                                            <span v-if="res.letter">Chose Option <strong>{{ res.letter }}</strong></span>
                                            <span v-else-if="res.survived_ghost">👻 Survived Ghost Trap!</span>
                                            <span v-else>No answer</span>
                                        </p>
                                    </div>
                                </div>

                                <div class="text-right">
                                    <div class="font-mono font-black text-lg"
                                        :class="res.delta > 0 ? 'text-green-400' : res.delta < 0 ? 'text-red-400' : 'text-gray-400'">
                                        {{ res.delta > 0 ? `+${res.delta}` : res.delta }} pts
                                    </div>
                                    <div class="text-[11px] font-mono text-gray-400">
                                        Total: <strong class="text-yellow-400">{{ res.score }} pts</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>


                <!-- ============================================================ -->
                <!-- D. LAST 5 QUESTIONS WARNING SCREEN                           -->
                <!-- ============================================================ -->
                <div v-else-if="gameStatus === 'in_game' && questionPhase === 'last_5_warning'">
                    <div class="bg-gradient-to-b from-red-950/70 via-gray-900 to-gray-950 border-2 border-red-500/60 rounded-3xl p-8 sm:p-12 shadow-2xl text-center max-w-2xl mx-auto relative overflow-hidden">
                        <div class="w-20 h-20 rounded-3xl bg-red-900/60 border border-red-500 text-red-300 flex items-center justify-center text-4xl mx-auto mb-6 animate-pulse">
                            🔥
                        </div>

                        <span class="px-3.5 py-1 rounded-full text-xs font-black uppercase tracking-widest bg-red-900/80 text-red-200 border border-red-500 inline-block mb-4">
                            Critical Alert
                        </span>

                        <h2 class="text-3xl sm:text-5xl font-black text-white mb-4 tracking-tight">
                            FINAL 5 QUESTIONS
                        </h2>

                        <p class="text-gray-300 text-sm sm:text-base leading-relaxed max-w-lg mx-auto mb-6">
                            From this point forward, the scoreboard and round points are <strong>completely locked and hidden</strong> until the final grand reveal!
                        </p>

                        <div class="p-4 rounded-2xl bg-gray-950/80 border border-red-900/60 inline-flex items-center gap-2 text-xs font-mono text-red-300">
                            <span>🔒</span> Scoreboard lookup is disabled for the remainder of the match.
                        </div>
                    </div>
                </div>


                <!-- ============================================================ -->
                <!-- E. GRAND FINALE / PODIUM VIEW (AFTER QUESTION 30)           -->
                <!-- ============================================================ -->
                <div v-else-if="gameStatus === 'in_game' && questionPhase === 'finished'">
                    <div class="text-center mb-8">
                        <span class="px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest bg-yellow-500 text-gray-950 inline-block mb-3 shadow-lg">
                            Match Complete
                        </span>
                        <h2 class="text-4xl sm:text-5xl font-black text-white">
                            Grand Finale Podium
                        </h2>
                        <p class="text-gray-400 text-sm mt-1">Final rankings and champions</p>
                    </div>

                    <!-- PODIUM DISPLAY -->
                    <div class="grid grid-cols-3 gap-3 sm:gap-4 max-w-2xl mx-auto items-end mb-8 pt-6">

                        <!-- 2ND PLACE -->
                        <div v-if="finalLeaderboard[1]"
                            class="bg-gray-900/90 border border-gray-600 rounded-3xl p-4 text-center h-48 sm:h-56 flex flex-col justify-between shadow-xl">
                            <div>
                                <span class="text-3xl">🥈</span>
                                <h4 class="font-extrabold text-sm sm:text-base text-gray-200 truncate mt-1">
                                    {{ finalLeaderboard[1].name }}
                                </h4>
                            </div>
                            <div>
                                <span class="text-xl sm:text-2xl font-black text-gray-300 font-mono">
                                    {{ finalLeaderboard[1].score }} pts
                                </span>
                                <div class="text-[10px] text-gray-500 uppercase font-bold mt-0.5">2nd Place</div>
                            </div>
                        </div>
                        <div v-else class="h-48"></div>

                        <!-- 1ST PLACE -->
                        <div v-if="finalLeaderboard[0]"
                            class="bg-yellow-950/40 border-2 border-yellow-400 rounded-3xl p-5 text-center h-60 sm:h-72 flex flex-col justify-between shadow-2xl relative">
                            <span class="absolute -top-4 left-1/2 -translate-x-1/2 text-2xl">👑</span>
                            <div>
                                <span class="text-4xl">🥇</span>
                                <h4 class="font-black text-base sm:text-lg text-yellow-300 truncate mt-1">
                                    {{ finalLeaderboard[0].name }}
                                </h4>
                            </div>
                            <div>
                                <span class="text-2xl sm:text-3xl font-black text-yellow-400 font-mono">
                                    {{ finalLeaderboard[0].score }} pts
                                </span>
                                <div class="text-xs text-yellow-500/80 uppercase font-black tracking-widest mt-1">Champion</div>
                            </div>
                        </div>
                        <div v-else class="h-60"></div>

                        <!-- 3RD PLACE -->
                        <div v-if="finalLeaderboard[2]"
                            class="bg-amber-950/30 border border-amber-700/60 rounded-3xl p-4 text-center h-40 sm:h-48 flex flex-col justify-between shadow-xl">
                            <div>
                                <span class="text-3xl">🥉</span>
                                <h4 class="font-extrabold text-sm sm:text-base text-gray-200 truncate mt-1">
                                    {{ finalLeaderboard[2].name }}
                                </h4>
                            </div>
                            <div>
                                <span class="text-lg sm:text-xl font-black text-amber-300 font-mono">
                                    {{ finalLeaderboard[2].score }} pts
                                </span>
                                <div class="text-[10px] text-amber-500 uppercase font-bold mt-0.5">3rd Place</div>
                            </div>
                        </div>
                        <div v-else class="h-40"></div>
                    </div>

                    <!-- RETURN HOME BUTTON -->
                    <div class="text-center">
                        <button @click.stop="confirmCancelGame" type="button"
                            class="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black transition shadow-xl cursor-pointer">
                            Return to Landing Page
                        </button>
                    </div>
                </div>

            </main>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import socket from '../socket'

const router = useRouter()

// Player Credentials
const playerId = ref(sessionStorage.getItem('player_id'))
const playerToken = ref(sessionStorage.getItem('player_token'))
const isAdmin = ref(sessionStorage.getItem('is_admin') === 'true')
const playerName = ref('Player')

// Lobby / Game State
const gameStatus = ref('guide') // 'guide', 'in_game'
const guideStep = ref(0)
const questionPhase = ref('intro') // 'intro', 'ladder', 'ended', 'round_points', 'last_5_warning', 'finished'
const currentQuestionIndex = ref(0)
const totalQuestionsCount = ref(30)
const currentQuestion = ref(null)
const playersList = ref([])
const roundDeltas = ref({})
const finalLeaderboard = ref([])

// Player Answering
const selectedOptionLetter = ref(null) // 'A', 'B', 'C', 'D', 'E'
const answeredPlayerIds = ref([])

// 15-second Timer
const timerSeconds = ref(15)
const timerPercentage = ref(100)
let timerInterval = null
let lastTickedSecond = null

// Modals
const showCancelConfirmModal = ref(false)
const showScoreboardModal = ref(false)
const scoreboardList = ref([])
const cancellationNotice = ref('')

// Audio & Confetti Refs
const audioPlayerRef = ref(null)
const confettiCanvasRef = ref(null)
let audioCtx = null

// Config Settings
const basePoints = ref(100)

// Guide Info
const guideStepsInfo = [
    {
        title: "1. Question Area",
        description: "Where question text, round title, and timer appear."
    },
    {
        title: "2. Options Area",
        description: "Where choices A, B, C, D, E are revealed for players to choose."
    },
    {
        title: "3. Images & Media",
        description: "Visual assets, clues, and audio challenge controls appear here."
    },
    {
        title: "4. Question Types",
        description: "Overview of Basic, Wrong (find false), Ghost (all false), and Music questions."
    }
]

// Computed Helpers
const currentGuideTitle = computed(() => {
    return guideStepsInfo[Math.min(guideStep.value, guideStepsInfo.length - 1)].title
})

const currentGuideDescription = computed(() => {
    return guideStepsInfo[Math.min(guideStep.value, guideStepsInfo.length - 1)].description
})

const isLastFiveMatch = computed(() => {
    return currentQuestionIndex.value >= 25
})

const canViewScoreboard = computed(() => {
    return (
        gameStatus.value === 'in_game' &&
        questionPhase.value !== 'ladder' &&
        currentQuestionIndex.value < 25 &&
        questionPhase.value !== 'last_5_warning'
    )
})

const currentWinningLetter = computed(() => {
    return currentQuestion.value ? currentQuestion.value.winning_letter : null
})

const currentQuestionOptions = computed(() => {
    return currentQuestion.value ? currentQuestion.value.options : []
})

const currentMusicAudioUrl = computed(() => {
    if (currentQuestion.value && currentQuestion.value.question_type === 'music_single' && currentQuestion.value.media_url) {
        return currentQuestion.value.media_url
    }
    return ''
})

const nonAdminPlayersCount = computed(() => {
    return playersList.value.filter(p => !p.is_admin).length
})

const answeredPlayersCount = computed(() => {
    return answeredPlayerIds.value.length
})

const questionTypeLabel = computed(() => {
    if (!currentQuestion.value) return 'Question'
    const t = currentQuestion.value.question_type
    if (t === 'wrong') return '⚡ Wrong Round (Find False!)'
    if (t === 'ghost') return '👻 Ghost Trap'
    if (t === 'music_single') return '🎵 Music Track'
    return '🎯 Basic Trivia'
})

const questionTypeBadgeClass = computed(() => {
    if (!currentQuestion.value) return 'bg-gray-800 text-gray-300 border-gray-700'
    const t = currentQuestion.value.question_type
    if (t === 'wrong') return 'bg-red-950 text-red-300 border-red-500'
    if (t === 'ghost') return 'bg-purple-950 text-purple-300 border-purple-500'
    if (t === 'music_single') return 'bg-yellow-950 text-yellow-300 border-yellow-500'
    return 'bg-blue-950 text-blue-300 border-blue-500'
})

// Player Status & Prompts
const isAnsweringActive = computed(() => {
    return gameStatus.value === 'in_game' && questionPhase.value === 'ladder'
})

const playerStatusText = computed(() => {
    if (gameStatus.value === 'guide') return 'Guide in Progress'
    if (questionPhase.value === 'intro') return 'Round Starting'
    if (questionPhase.value === 'ladder') {
        return selectedOptionLetter.value ? 'Answer Locked' : 'Choose Now (15s)'
    }
    if (questionPhase.value === 'ended') return 'Round Ended'
    if (questionPhase.value === 'round_points') return 'Points Review'
    if (questionPhase.value === 'last_5_warning') return 'Final 5 Round'
    if (questionPhase.value === 'finished') return 'Game Over'
    return 'Playing'
})

const playerStatusBadgeClass = computed(() => {
    if (isAnsweringActive.value) {
        return selectedOptionLetter.value
            ? 'bg-blue-900/60 border-blue-500 text-blue-300'
            : 'bg-yellow-900/60 border-yellow-500 text-yellow-300 animate-pulse'
    }
    return 'bg-gray-800 border-gray-700 text-gray-400'
})

const playerPromptText = computed(() => {
    if (gameStatus.value === 'guide') {
        return 'Follow the guide on the host board...'
    }
    if (questionPhase.value === 'intro') {
        return 'Look at the main board • Waiting for choices...'
    }
    if (questionPhase.value === 'ladder') {
        return selectedOptionLetter.value
            ? 'Your choice is locked in. Waiting for round end...'
            : '⚡ Tap your answer now!'
    }
    if (questionPhase.value === 'ended') {
        return 'Time is up! Look at the main board for results.'
    }
    if (questionPhase.value === 'round_points') {
        return 'Round points shown on host board.'
    }
    if (questionPhase.value === 'last_5_warning') {
        return 'Final 5 Questions starting...'
    }
    return 'Look at the main board'
})

// Player Option Button State
const isOptionClickable = (letter) => {
    if (!isAnsweringActive.value) return false
    if (selectedOptionLetter.value !== null) return false
    if (currentQuestion.value && currentQuestion.value.valid_letters) {
        return currentQuestion.value.valid_letters.includes(letter)
    }
    return true
}

const getOptionBtnClass = (letter, colorName) => {
    const isSelected = selectedOptionLetter.value === letter
    const isClickable = isOptionClickable(letter)

    // Base color themes
    const themes = {
        red: {
            active: 'bg-red-600 hover:bg-red-500 border-red-400 text-white shadow-lg shadow-red-900/50 cursor-pointer active:scale-95',
            inactive: 'bg-red-950/30 border-red-900/40 text-red-500/60 cursor-default opacity-70',
            selected: 'bg-red-600 border-white text-white ring-4 ring-red-400/60 scale-102 shadow-2xl shadow-red-600/60'
        },
        blue: {
            active: 'bg-blue-600 hover:bg-blue-500 border-blue-400 text-white shadow-lg shadow-blue-900/50 cursor-pointer active:scale-95',
            inactive: 'bg-blue-950/30 border-blue-900/40 text-blue-500/60 cursor-default opacity-70',
            selected: 'bg-blue-600 border-white text-white ring-4 ring-blue-400/60 scale-102 shadow-2xl shadow-blue-600/60'
        },
        amber: {
            active: 'bg-amber-600 hover:bg-amber-500 border-amber-400 text-white shadow-lg shadow-amber-900/50 cursor-pointer active:scale-95',
            inactive: 'bg-amber-950/30 border-amber-900/40 text-amber-500/60 cursor-default opacity-70',
            selected: 'bg-amber-600 border-white text-white ring-4 ring-amber-400/60 scale-102 shadow-2xl shadow-amber-600/60'
        },
        emerald: {
            active: 'bg-emerald-600 hover:bg-emerald-500 border-emerald-400 text-white shadow-lg shadow-emerald-900/50 cursor-pointer active:scale-95',
            inactive: 'bg-emerald-950/30 border-emerald-900/40 text-emerald-500/60 cursor-default opacity-70',
            selected: 'bg-emerald-600 border-white text-white ring-4 ring-emerald-400/60 scale-102 shadow-2xl shadow-emerald-600/60'
        },
        purple: {
            active: 'bg-purple-600 hover:bg-purple-500 border-purple-400 text-white shadow-lg shadow-purple-900/50 cursor-pointer active:scale-95',
            inactive: 'bg-purple-950/30 border-purple-900/40 text-purple-500/60 cursor-default opacity-70',
            selected: 'bg-purple-600 border-white text-white ring-4 ring-purple-400/60 scale-102 shadow-2xl shadow-purple-600/60'
        }
    }

    const t = themes[colorName] || themes.blue
    if (isSelected) return t.selected
    if (isClickable) return t.active
    return t.inactive
}

// Host Board Option Styling (Non-clickable, no hover)
const getBoardOptionClass = (opt) => {
    if (questionPhase.value === 'ended') {
        const isWinning = opt.letter === currentWinningLetter.value ||
            (currentQuestion.value && currentQuestion.value.question_type === 'wrong' && opt.is_correct === false)

        if (isWinning) {
            return 'bg-green-950/80 border-green-400 ring-4 ring-green-500/40 shadow-xl scale-[1.02]'
        }
        return 'bg-gray-900/40 border-gray-800 opacity-50'
    }

    // During Ladder phase
    const colors = {
        A: 'bg-red-950/30 border-red-500/40',
        B: 'bg-blue-950/30 border-blue-500/40',
        C: 'bg-amber-950/30 border-amber-500/40',
        D: 'bg-emerald-950/30 border-emerald-500/40',
        E: 'bg-purple-950/30 border-purple-500/40'
    }
    return colors[opt.letter] || 'bg-gray-800/60 border-gray-700'
}

const getBoardOptionBadgeClass = (opt) => {
    const badges = {
        A: 'bg-red-600 text-white',
        B: 'bg-blue-600 text-white',
        C: 'bg-amber-600 text-white',
        D: 'bg-emerald-600 text-white',
        E: 'bg-purple-600 text-white'
    }
    return badges[opt.letter] || 'bg-gray-700 text-gray-200'
}

const getBoardOptionTextClass = (opt) => {
    if (questionPhase.value === 'ended') {
        const isWinning = opt.letter === currentWinningLetter.value ||
            (currentQuestion.value && currentQuestion.value.question_type === 'wrong' && opt.is_correct === false)
        return isWinning ? 'text-green-300' : 'text-gray-400'
    }
    return 'text-gray-100'
}

const isImageMedia = (url) => {
    if (!url) return false
    return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url)
}

// Web Audio API Tick Sound Generator (Plays on 5s, 4s, 3s, 2s, 1s)
const getAudioContext = () => {
    if (!audioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext
        if (AudioContextClass) {
            audioCtx = new AudioContextClass()
        }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume().catch(() => {})
    }
    return audioCtx
}

const playTickSound = (sec) => {
    try {
        const ctx = getAudioContext()
        if (!ctx) return

        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.connect(gain)
        gain.connect(ctx.destination)

        // Rising pitch as time runs out (5 -> 810Hz, 1 -> 1050Hz)
        const baseFreq = 750 + (6 - sec) * 60
        osc.type = 'sine'
        osc.frequency.setValueAtTime(baseFreq, ctx.currentTime)

        gain.gain.setValueAtTime(0.35, ctx.currentTime)
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08)

        osc.start(ctx.currentTime)
        osc.stop(ctx.currentTime + 0.08)
    } catch (e) {
        // Audio synthesis unavailable
    }
}

// Lifecycle Hooks
onMounted(() => {
    if (!playerId.value || !playerToken.value) {
        router.push('/')
        return
    }

    // Join room & fetch initial state
    socket.emit('join_lobby_room')
    socket.emit('get_lobby_state')

    // Socket Listeners
    socket.on('lobby_state', handleStateUpdate)
    socket.on('lobby_updated', handleStateUpdate)
    socket.on('guide_updated', handleStateUpdate)
    socket.on('game_started', handleStateUpdate)
    socket.on('lobby_cancelled', handleLobbyCancelled)

    // Keyboard navigation
    window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
    socket.off('lobby_state', handleStateUpdate)
    socket.off('lobby_updated', handleStateUpdate)
    socket.off('guide_updated', handleStateUpdate)
    socket.off('game_started', handleStateUpdate)
    socket.off('lobby_cancelled', handleLobbyCancelled)
    window.removeEventListener('keydown', handleKeyDown)
    stopTimer()
    stopAudio()
})

// Timer Management
const startTimer = (durationSeconds = 15) => {
    stopTimer()
    lastTickedSecond = null
    timerSeconds.value = durationSeconds
    timerPercentage.value = 100

    const startTime = Date.now()
    const totalMs = durationSeconds * 1000

    timerInterval = setInterval(() => {
        const elapsed = Date.now() - startTime
        const remaining = Math.max(0, totalMs - elapsed)
        const remainingSec = Math.ceil(remaining / 1000)
        timerSeconds.value = remainingSec
        timerPercentage.value = Math.max(0, (remaining / totalMs) * 100)

        // Tick sound on the last 5 seconds of the question
        if (remainingSec <= 5 && remainingSec >= 1 && lastTickedSecond !== remainingSec) {
            lastTickedSecond = remainingSec
            playTickSound(remainingSec)
        }

        if (remaining <= 0) {
            stopTimer()
            if (isAdmin.value) {
                socket.emit('end_question_timer')
            }
        }
    }, 50)
}

const stopTimer = () => {
    if (timerInterval) {
        clearInterval(timerInterval)
        timerInterval = null
    }
    lastTickedSecond = null
}

// Audio Control
const playAudio = () => {
    if (audioPlayerRef.value && currentMusicAudioUrl.value) {
        audioPlayerRef.value.currentTime = 0
        audioPlayerRef.value.play().catch(() => {})
    }
}

const stopAudio = () => {
    if (audioPlayerRef.value) {
        audioPlayerRef.value.pause()
        audioPlayerRef.value.currentTime = 0
    }
}

// State Update Handler
const handleStateUpdate = (state) => {
    if (!state || !state.is_active) {
        handleLobbyCancelled({ message: 'The match has concluded or was cancelled.' })
        return
    }

    gameStatus.value = state.status || 'guide'

    if (state.guide_step !== undefined) {
        guideStep.value = state.guide_step
    }

    if (state.players) {
        playersList.value = state.players
        const me = state.players.find(p => p.id === playerId.value)
        if (me) {
            playerName.value = me.name
        }
    }

    if (state.settings && state.settings.base_points) {
        basePoints.value = state.settings.base_points
    }

    // In-Game updates
    if (state.status === 'in_game') {
        const prevPhase = questionPhase.value
        const prevIndex = currentQuestionIndex.value

        currentQuestionIndex.value = state.question_index !== undefined ? state.question_index : 0
        totalQuestionsCount.value = state.total_questions || 30
        questionPhase.value = state.question_phase || 'intro'
        currentQuestion.value = state.question || null
        answeredPlayerIds.value = state.answered_player_ids || []
        roundDeltas.value = state.round_deltas || {}

        if (state.final_leaderboard) {
            finalLeaderboard.value = state.final_leaderboard
        }

        // New question or phase reset: clear player answer
        if (currentQuestionIndex.value !== prevIndex || questionPhase.value === 'intro') {
            selectedOptionLetter.value = null
            stopAudio()
            stopTimer()
        }

        // Phase transitioned to 'ladder': start timer and music
        if (questionPhase.value === 'ladder' && prevPhase !== 'ladder') {
            startTimer(15)
            if (currentQuestion.value && currentQuestion.value.question_type === 'music_single') {
                playAudio()
            }
        }

        // Phase ended: stop timer and audio
        if (questionPhase.value === 'ended' || questionPhase.value === 'round_points') {
            stopTimer()
            stopAudio()
        }

        // Finished: trigger confetti
        if (questionPhase.value === 'finished' && prevPhase !== 'finished') {
            triggerConfetti()
        }
    }
}

// Player Action: Tap Option A, B, C, D, or E
const handlePlayerSelect = (letter) => {
    if (!isOptionClickable(letter)) return

    // Single tap is locked in immediately without confirmation
    selectedOptionLetter.value = letter

    socket.emit('submit_answer', {
        player_id: playerId.value,
        token: playerToken.value,
        letter: letter
    }, (res) => {
        if (!res || !res.success) {
            // Revert if error
            selectedOptionLetter.value = null
        }
    })
}

// Admin Action: Advance Game via Space, Enter, or Click
const handleAdminScreenClick = () => {
    if (isAdmin.value && !showCancelConfirmModal.value && !showScoreboardModal.value) {
        // Prevent accidental clicks from skipping the 15-second answering window!
        if (gameStatus.value === 'in_game' && questionPhase.value === 'ladder') {
            return
        }
        advanceGame()
    }
}

const advanceGame = () => {
    if (!isAdmin.value) return
    socket.emit('admin_advance', { token: playerToken.value }, (res) => {
        if (res && res.success && res.lobby) {
            handleStateUpdate(res.lobby)
        }
    })
}

// Keyboard Listener
const handleKeyDown = (e) => {
    // 1. ESCAPE: Toggle Cancel Game Modal
    if (e.key === 'Escape') {
        if (showScoreboardModal.value) {
            showScoreboardModal.value = false
            return
        }
        if (isAdmin.value) {
            showCancelConfirmModal.value = !showCancelConfirmModal.value
        }
        return
    }

    // 2. 'V' / 'v': Toggle Total Scoreboard Modal (Only for Admin when allowed)
    if (isAdmin.value && (e.key === 'v' || e.key === 'V')) {
        if (showScoreboardModal.value) {
            showScoreboardModal.value = false
            return
        }

        if (canViewScoreboard.value) {
            fetchAndShowScoreboard()
        }
        return
    }

    // 3. SPACE / ENTER: Host Advance
    if (isAdmin.value && (e.key === ' ' || e.key === 'Enter')) {
        e.preventDefault()
        if (!showCancelConfirmModal.value && !showScoreboardModal.value) {
            // Do not advance during ladder via keypress
            if (gameStatus.value === 'in_game' && questionPhase.value === 'ladder') {
                return
            }
            advanceGame()
        }
    }
}

// Fetch Scoreboard Modal Data
const fetchAndShowScoreboard = () => {
    socket.emit('get_scoreboard', { token: playerToken.value }, (res) => {
        if (res && res.success && res.data && res.data.allowed) {
            scoreboardList.value = res.data.leaderboard || []
            showScoreboardModal.value = true
        }
    })
}

// Confirm Cancel Game
const confirmCancelGame = () => {
    socket.emit('cancel_lobby', { token: playerToken.value }, (res) => {
        showCancelConfirmModal.value = false
        if (res && res.success) {
            sessionStorage.removeItem('player_id')
            sessionStorage.removeItem('player_token')
            sessionStorage.removeItem('is_admin')
            router.push('/')
        }
    })
}

const handleLobbyCancelled = (data) => {
    cancellationNotice.value = data && data.message ? data.message : 'The match was ended by the admin.'
    sessionStorage.removeItem('player_id')
    sessionStorage.removeItem('player_token')
    sessionStorage.removeItem('is_admin')
}

const returnHome = () => {
    cancellationNotice.value = ''
    router.push('/')
}

// Confetti Effect for Podium
const triggerConfetti = () => {
    const canvas = confettiCanvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles = []
    const colors = ['#f59e0b', '#3b82f6', '#ef4444', '#10b981', '#8b5cf6', '#ec4899']

    for (let i = 0; i < 120; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            size: Math.random() * 8 + 4,
            speedY: Math.random() * 4 + 2,
            speedX: (Math.random() - 0.5) * 3,
            color: colors[Math.floor(Math.random() * colors.length)],
            rotation: Math.random() * 360,
            rotSpeed: (Math.random() - 0.5) * 10
        })
    }

    let animId = null
    const render = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        particles.forEach(p => {
            p.y += p.speedY
            p.x += p.speedX
            p.rotation += p.rotSpeed
            ctx.save()
            ctx.translate(p.x, p.y)
            ctx.rotate((p.rotation * Math.PI) / 180)
            ctx.fillStyle = p.color
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size)
            ctx.restore()
        })

        if (particles.some(p => p.y < canvas.height)) {
            animId = requestAnimationFrame(render)
        }
    }
    render()
}
</script>

<style scoped>
/* Staggered Ladder Cascade Animation */
@keyframes ladderDrop {
    0% {
        opacity: 0;
        transform: translateY(-24px) scale(0.97);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.ladder-item {
    animation: ladderDrop 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

.ladder-item-0 { animation-delay: 0.05s; }
.ladder-item-1 { animation-delay: 0.18s; }
.ladder-item-2 { animation-delay: 0.31s; }
.ladder-item-3 { animation-delay: 0.44s; }
.ladder-item-4 { animation-delay: 0.57s; }

/* Transitions */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>