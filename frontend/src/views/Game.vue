<template>
    <div class="min-h-screen text-gray-200 flex flex-col justify-center px-4 py-8 relative select-none">

        <!-- FLOATING SCORE DELTA NOTIFICATION -->
        <transition name="fade-up">
            <div v-if="scoreDeltaNotification"
                class="fixed top-20 right-8 z-50 pointer-events-none font-extrabold text-2xl px-4 py-2 rounded-xl shadow-2xl border"
                :class="scoreDeltaNotification.points >= 0 ? 'bg-green-950/90 border-green-500 text-green-300' : 'bg-red-950/90 border-red-500 text-red-300'">
                {{ scoreDeltaNotification.points >= 0 ? `+${scoreDeltaNotification.points}` :
                    scoreDeltaNotification.points }} pts
            </div>
        </transition>

        <!-- SCORE MODAL (TRIGGERED BY 'V' OR CLICK) -->
        <transition name="fade">
            <div v-if="showScoreModal" @click.self="showScoreModal = false"
                class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full shadow-2xl relative">
                    <button @click="showScoreModal = false"
                        class="absolute top-4 right-4 text-gray-400 hover:text-white text-xl">✕</button>

                    <h3 class="text-2xl font-bold text-yellow-400 mb-6 flex items-center gap-2">
                        <span>🏆</span> Score & Match Stats
                    </h3>

                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div class="bg-gray-900 p-4 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Current Score</span>
                            <div class="text-3xl font-extrabold mt-1"
                                :class="score < 0 ? 'text-red-400' : 'text-yellow-400'">{{ score }}</div>
                        </div>
                        <div class="bg-gray-900 p-4 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Accuracy</span>
                            <div class="text-3xl font-extrabold text-blue-400 mt-1">
                                {{ answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0 }}%
                            </div>
                        </div>
                    </div>

                    <div
                        class="space-y-2.5 text-sm bg-gray-900/60 p-4 rounded-xl border border-gray-700/60 mb-6 font-medium">
                        <div class="flex justify-between">
                            <span class="text-gray-400">Questions Progress:</span>
                            <span class="text-white">{{ currentIndex + 1 }} / {{ gameQuestions.length }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">Correct Answers:</span>
                            <span class="text-green-400 font-bold">{{ correctCount }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">Wrong Answers:</span>
                            <span class="text-red-400 font-bold">{{ answeredCount - correctCount }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">Current Phase:</span>
                            <span class="text-blue-300 font-semibold">{{ currentPhaseTitle }}</span>
                        </div>
                    </div>

                    <button @click="showScoreModal = false"
                        class="w-full py-3 bg-gray-700 hover:bg-gray-600 rounded-xl font-bold transition text-center">
                        Back to Game <kbd class="ml-2 bg-gray-600 px-1.5 py-0.5 rounded text-xs text-gray-300">V</kbd>
                    </button>
                </div>
            </div>
        </transition>

        <!-- 1. LOADING SCREEN (AUTO-STARTS MATCH) -->
        <div v-if="gameState === 'start'" class="max-w-md mx-auto text-center py-20 space-y-6">
            <h1 class="text-6xl font-extrabold text-blue-400 tracking-tight">mr-because</h1>
            <div class="flex justify-center items-center py-4">
                <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin">
                </div>
            </div>
            <p class="text-gray-400 font-mono text-sm">Preparing match...</p>
        </div>

        <!-- 2. FULLSCREEN ROUND INTRO SCREEN -->
        <div v-else-if="gameState === 'round_intro'"
            class="fixed inset-0 z-40 bg-gray-950 flex flex-col items-center justify-center p-6 text-center">

            <!-- Wrong Round Flashy Intro -->
            <div v-if="roundIntroType === 'wrong'" class="max-w-2xl space-y-6 animate-pulse-glow">
                <div class="text-7xl animate-bounce">⚡</div>
                <div
                    class="inline-block px-4 py-1.5 bg-red-900/80 border border-red-500 rounded-full text-red-300 font-mono text-sm tracking-widest uppercase font-bold">
                    Rapid Fire Round
                </div>
                <h1
                    class="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-orange-400 to-yellow-400">
                    WRONG ROUND
                </h1>
                <p class="text-2xl text-gray-200 font-semibold">
                    Find the <span class="text-red-400 underline decoration-wavy">FALSE</span> option!
                </p>
                <div
                    class="bg-gray-900/80 p-5 rounded-2xl border border-red-900/60 text-gray-300 space-y-2 max-w-md mx-auto text-sm">
                    <p>🔥 <strong>8 Questions back-to-back</strong></p>
                    <p>⏱️ <strong>5 Seconds</strong> per question (No pauses!)</p>
                    <p>⚡ The faster you pick the false one, the more points you gain!</p>
                </div>
                <div class="text-4xl font-mono font-bold text-orange-400">
                    Starting in {{ roundIntroCountdown }}s...
                </div>
            </div>

            <!-- Generic Round 1 or Round 3 Intro -->
            <div v-else class="max-w-lg space-y-6">
                <div class="text-6xl">🚀</div>
                <h2 class="text-5xl font-extrabold text-blue-400">
                    {{ roundIntroTitle }}
                </h2>
                <p class="text-xl text-gray-300">
                    {{ roundIntroSubtitle }}
                </p>
                <div class="text-3xl font-mono font-bold text-blue-300">
                    Starting in {{ roundIntroCountdown }}s...
                </div>
            </div>
        </div>

        <!-- 3. MUSIC TEASER & AUDIO PLAYBACK INTRO -->
        <div v-else-if="gameState === 'music_intro' || gameState === 'music_playing'"
            class="max-w-2xl mx-auto bg-gray-900/90 border border-purple-600/60 p-10 rounded-3xl text-center shadow-2xl relative overflow-hidden">

            <div
                class="absolute -top-12 -right-12 w-48 h-48 bg-purple-600/20 rounded-full blur-3xl pointer-events-none">
            </div>

            <!-- Floating instruments teaser animation -->
            <div class="flex justify-center items-center gap-4 text-4xl mb-6 animate-float">
                <span>🎸</span><span>🎹</span><span>🎷</span><span>🎺</span><span>🎻</span>
            </div>

            <span
                class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-purple-900 text-purple-200 border border-purple-500">
                Listening Challenge
            </span>

            <h2 class="text-4xl font-extrabold text-white mt-4 mb-2">Music Round</h2>

            <!-- Music Phase 1: 3-Second Countdown -->
            <div v-if="gameState === 'music_intro'" class="py-8 space-y-4">
                <p class="text-gray-300 text-lg">
                    Listen closely! You will only hear the audio track <strong>ONCE</strong>.
                </p>
                <div class="text-6xl font-extrabold text-purple-400 font-mono animate-scale-pop">
                    {{ musicCountdown }}
                </div>
                <p class="text-sm text-gray-400">Audio begins playing in {{ musicCountdown }} seconds...</p>
            </div>

            <!-- Music Phase 2: Playing audio track (Question/options hidden!) -->
            <div v-else-if="gameState === 'music_playing'" class="py-8 space-y-6">
                <div class="relative flex justify-center items-center">
                    <div
                        class="w-32 h-32 rounded-full border-4 border-purple-500 border-dashed animate-spin-slow flex items-center justify-center bg-gray-950">
                        <span class="text-4xl">🎵</span>
                    </div>
                </div>

                <!-- Animated sound bars -->
                <div class="flex justify-center items-end gap-1.5 h-12">
                    <span v-for="n in 12" :key="n" class="w-2 bg-purple-500 rounded-full animate-sound-bar"
                        :style="{ animationDelay: `${(n * 0.15)}s`, height: `${20 + ((n * 17) % 35)}px` }"></span>
                </div>

                <div class="space-y-2">
                    <p class="text-xl font-bold text-purple-300">Listening Window</p>
                    <div class="text-5xl font-extrabold text-purple-400 font-mono animate-pulse">
                        {{ audioPlaybackTimeLeft }}s
                    </div>
                    <p class="text-xs text-gray-400">Audio plays for a maximum of 10 seconds. The question will unlock
                        automatically.</p>
                </div>
            </div>
        </div>

        <!-- 4. GHOST QUESTION REVEAL SCREEN -->
        <div v-else-if="gameState === 'ghost_reveal'"
            class="max-w-2xl mx-auto bg-purple-950/90 border-2 border-purple-500 p-8 rounded-3xl text-center shadow-2xl space-y-6 animate-pulse-glow">
            <div class="text-7xl animate-float-ghost">👻</div>
            <h2 class="text-4xl font-extrabold text-purple-300">GHOST QUESTION REVEALED!</h2>

            <div v-if="ghostSurvived" class="bg-green-950/80 border border-green-500 p-5 rounded-2xl space-y-2">
                <p class="text-2xl font-bold text-green-300">🎉 YOU SURVIVED!</p>
                <p class="text-sm text-gray-200">
                    You resisted clicking! All options were completely <strong>FALSE</strong>.
                </p>
                <p class="text-xl font-bold text-yellow-400">+{{ gameBasePoints }} Points Awarded!</p>
            </div>
            <div v-else class="bg-red-950/80 border border-red-500 p-5 rounded-2xl space-y-2">
                <p class="text-2xl font-bold text-red-300">💥 TRAPPED BY THE GHOST!</p>
                <p class="text-sm text-gray-200">
                    You selected an option, but in a Ghost Question, <strong>all options are false</strong>!
                </p>
                <p class="text-xl font-bold text-red-400">{{ lastScoreDelta }} Points</p>
            </div>

            <p class="text-xs text-purple-300 animate-pulse font-mono">Press 'B' to continue to the next
                question</p>
        </div>

        <!-- 5. ACTIVE GAMEPLAY (SPLIT SCREEN LAYOUT IF QUESTION MEDIA EXISTS) -->
        <div v-else-if="gameState === 'playing' || gameState === 'review' || gameState === 'wrong_auto_next'"
            class="max-w-6xl mx-auto w-full">

            <div class="grid grid-cols-1 gap-6 items-start"
                :class="hasQuestionImage ? 'lg:grid-cols-12' : hasOptionImages ? 'max-w-5xl mx-auto' : 'max-w-4xl mx-auto'">

                <!-- LEFT MAIN PANEL: QUESTION, TIMER, OPTIONS -->
                <div class="bg-gray-800 p-6 md:p-8 rounded-2xl shadow-2xl border border-gray-700 relative"
                    :class="hasQuestionImage ? 'lg:col-span-7' : 'w-full'">

                    <!-- Top HUD -->
                    <div
                        class="flex justify-between items-center mb-6 text-gray-400 font-bold border-b border-gray-700 pb-4 text-sm md:text-base">
                        <div class="flex items-center gap-2">
                            <span>Question {{ currentIndex + 1 }} / {{ gameQuestions.length }}</span>
                            <span class="text-xs px-2 py-0.5 rounded-full font-mono font-semibold"
                                :class="isWrongRound ? 'bg-red-950 text-red-400 border border-red-700' : 'bg-gray-900 text-gray-400 border border-gray-700'">
                                {{ currentPhaseTitle }}
                            </span>
                        </div>
                        <div class="text-xl font-mono" :class="score < 0 ? 'text-red-400' : 'text-yellow-400'">Score: {{
                            score }}</div>
                    </div>

                    <!-- Question Type Badge (Stealth Ghost: displays as normal basic round!) -->
                    <div class="text-center mb-4">
                        <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest"
                            :class="displayedTypeBadge.class">
                            {{ displayedTypeBadge.label }}
                        </span>
                    </div>

                    <!-- Question Text -->
                    <h2 class="text-2xl md:text-3xl font-extrabold text-center text-white mb-6 leading-snug">
                        {{ currentQuestion.text }}
                    </h2>

                    <!-- Timer Bar -->
                    <div class="w-full bg-gray-900 rounded-full h-3.5 mb-3 overflow-hidden border border-gray-700/60">
                        <div class="h-full transition-all duration-75 ease-linear rounded-full"
                            :class="timeLeft <= 3 ? 'bg-red-500' : isWrongRound ? 'bg-orange-500' : 'bg-blue-500'"
                            :style="{ width: timerPercentage + '%' }"></div>
                    </div>
                    <div class="text-center text-xl font-mono font-bold mb-6"
                        :class="timeLeft <= 2 ? 'text-red-400 animate-ping' : timeLeft <= 3 ? 'text-red-400' : 'text-gray-300'">
                        {{ timeLeft }}s
                    </div>

                    <!-- Options Grid: Visual Image Cards if options have images -->
                    <div v-if="hasOptionImages" class="grid gap-4"
                        :class="hasQuestionImage ? 'grid-cols-2' : currentQuestion.options.length <= 2 ? 'grid-cols-2 max-w-lg mx-auto' : currentQuestion.options.length <= 4 ? 'grid-cols-2 sm:grid-cols-4' : 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-5'">

                        <button v-for="opt in currentQuestion.options" :key="opt.id" @click="selectOption(opt)"
                            :disabled="gameState !== 'playing'"
                            class="rounded-2xl border-2 overflow-hidden transition-all duration-200 flex flex-col group text-left relative focus:outline-none"
                            :class="getOptionClass(opt)">

                            <!-- Option Image Cover -->
                            <div
                                class="w-full h-36 sm:h-44 bg-gray-950 flex items-center justify-center overflow-hidden relative">
                                <img v-if="opt.media_url" :src="getMediaUrl(opt.media_url)" :alt="opt.text"
                                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                                <div v-else class="text-3xl text-gray-600">🖼️</div>
                            </div>

                            <!-- Option Text Label -->
                            <div class="p-3 text-center w-full font-bold text-sm sm:text-base truncate">
                                {{ opt.text }}
                            </div>
                        </button>
                    </div>

                    <!-- Options Grid: Standard Text Buttons when options have NO images -->
                    <div v-else class="grid grid-cols-1 gap-3.5"
                        :class="currentQuestion.options && currentQuestion.options.length > 2 ? 'sm:grid-cols-2' : 'grid-cols-1'">

                        <button v-for="opt in currentQuestion.options" :key="opt.id" @click="selectOption(opt)"
                            :disabled="gameState !== 'playing'"
                            class="p-4 rounded-xl text-base md:text-lg font-bold transition-all border-2 flex items-center justify-between text-left gap-3 relative overflow-hidden"
                            :class="getOptionClass(opt)">
                            <span class="flex-1">{{ opt.text }}</span>
                        </button>
                    </div>

                    <!-- Wrong Round Auto-Advancing Indicator -->
                    <div v-if="gameState === 'wrong_auto_next'"
                        class="mt-4 text-center text-sm text-orange-400 font-mono animate-pulse">
                        Next question incoming...
                    </div>
                </div>

                <!-- RIGHT SIDE PANEL: QUESTION MEDIA (ONLY FOR THE QUESTION'S OWN IMAGE) -->
                <div v-if="hasQuestionImage"
                    class="lg:col-span-5 bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-700 space-y-4">
                    <h4 class="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <span>🖼️</span> Question Media
                    </h4>

                    <!-- Question Image -->
                    <div
                        class="rounded-xl overflow-hidden border border-gray-700 bg-gray-950 flex justify-center items-center p-2">
                        <img :src="getMediaUrl(currentQuestion.media_url)" alt="Question Media"
                            class="max-h-80 w-auto object-contain rounded-lg shadow-md" />
                    </div>
                </div>

            </div>
        </div>

        <!-- 6. GAME OVER SCREEN -->
        <div v-else-if="gameState === 'gameover'"
            class="max-w-2xl mx-auto text-center bg-gray-800 p-10 rounded-3xl border border-gray-700 shadow-2xl space-y-6">

            <div class="text-6xl">🏁</div>
            <h1 class="text-5xl font-extrabold text-blue-400 tracking-tight">Match Complete!</h1>

            <div class="bg-gray-900/90 p-6 rounded-2xl border border-gray-700 space-y-4">
                <div class="text-sm uppercase tracking-widest text-gray-400 font-bold">Final Score</div>
                <div class="text-6xl font-extrabold font-mono" :class="score < 0 ? 'text-red-400' : 'text-yellow-400'">
                    {{ score }}</div>

                <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-800">
                    <div>
                        <span class="text-xs text-gray-400 uppercase">Correct Answers</span>
                        <div class="text-2xl font-bold text-green-400 mt-1">{{ correctCount }} / {{
                            gameQuestions.length
                            }}</div>
                    </div>
                    <div>
                        <span class="text-xs text-gray-400 uppercase">Accuracy</span>
                        <div class="text-2xl font-bold text-blue-400 mt-1">
                            {{ gameQuestions.length > 0 ? Math.round((correctCount / gameQuestions.length) *
                                100) : 0
                            }}%
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-center gap-4 pt-2">
                <button @click="resetToStart"
                    class="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold text-lg transition shadow-lg hover:scale-105">
                    Play Again
                </button>
                <router-link to="/"
                    class="px-6 py-3.5 bg-gray-700 hover:bg-gray-600 rounded-xl font-bold text-lg transition hover:scale-105">
                    Back to Menu
                </router-link>
            </div>
        </div>

        <!-- 7. FLOATING BOTTOM-RIGHT ACTION BAR ('V' SCORE, 'B' NEXT) -->
        <transition name="fade">
            <div v-if="showBottomActionBar"
                class="fixed bottom-6 right-6 z-40 flex items-center space-x-3 bg-gray-900/95 border border-gray-700 px-4 py-3 rounded-2xl shadow-2xl backdrop-blur-md">

                <button @click="showScoreModal = true" type="button"
                    class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-yellow-400 font-bold rounded-xl border border-gray-700 text-sm flex items-center gap-2 transition hover:scale-105"
                    title="View current score (Press 'V')">
                    <kbd class="bg-gray-700 px-1.5 py-0.5 rounded text-xs text-white border border-gray-600">V</kbd>
                    <span>View Score</span>
                </button>

                <button @click="proceedToNext" type="button"
                    class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-sm flex items-center gap-2 shadow-lg shadow-blue-600/30 transition hover:scale-105"
                    title="Proceed to next question (Press 'B')">
                    <span>{{ isLastQuestionOfMatch ? 'Finish Match' : 'Next Question' }}</span>
                    <kbd class="bg-blue-700 px-1.5 py-0.5 rounded text-xs text-blue-100 border border-blue-500">B</kbd>
                </button>
            </div>
        </transition>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const API_BASE = 'http://localhost:5000'
const route = useRoute()

// Base settings from landing page route query
const gameTimeLimit = computed(() => {
    const val = parseInt(route.query.time_limit)
    return isNaN(val) || val <= 0 ? 10 : val
})

const gameBasePoints = computed(() => {
    const val = parseInt(route.query.base_points)
    return isNaN(val) || val <= 0 ? 100 : val
})

// Master Question List & Sampled 20 questions
const rawPoolQuestions = ref([])
const gameQuestions = ref([])

// Game State Machine
// 'start' | 'round_intro' | 'music_intro' | 'music_playing' | 'playing' | 'ghost_reveal' | 'review' | 'wrong_auto_next' | 'gameover'
const gameState = ref('start')
const currentIndex = ref(0)
const score = ref(0)
const correctCount = ref(0)
const answeredCount = ref(0)

// High-resolution active question runtime state
const timeLeft = ref(0)
const timeLeftMs = ref(0)
const questionStartTime = ref(0)
const questionTotalMs = ref(10000)
const activeQuestionTimeLimit = ref(10)
const timerInterval = ref(null)
const selectedOptionId = ref(null)
const ghostSurvived = ref(false)
const lastScoreDelta = ref(0)
const scoreDeltaNotification = ref(null)
let deltaTimeout = null

// Modals & Keyboard Controls
const showScoreModal = ref(false)

// Round intro animation state
const roundIntroType = ref('')
const roundIntroTitle = ref('')
const roundIntroSubtitle = ref('')
const roundIntroCountdown = ref(3)
let roundIntroTimer = null

// Music round intro & Audio state
const musicCountdown = ref(3)
const audioPlaybackTimeLeft = ref(10)
let musicCountdownTimer = null
let audioPlaybackTimer = null
let currentAudio = null
let audioSafetyTimer = null

const currentQuestion = computed(() => gameQuestions.value[currentIndex.value] || {})

// Round phase detection
// Questions 0..6: Round 1 (7 questions)
// Questions 7..14: Round 2 (8 wrong questions)
// Questions 15..19: Round 3 (5 final questions)
const isWrongRound = computed(() => currentIndex.value >= 7 && currentIndex.value <= 14)
const isLastWrongQuestion = computed(() => currentIndex.value === 14)
const isLastQuestionOfMatch = computed(() => currentIndex.value === gameQuestions.value.length - 1)

const currentPhaseTitle = computed(() => {
    if (currentIndex.value < 7) return 'Round 1'
    if (currentIndex.value <= 14) return 'Wrong Round'
    return 'Final Round'
})

// Stealth Ghost: Mask ghost questions during gameplay as normal round
const displayedTypeBadge = computed(() => {
    const q = currentQuestion.value
    if (q.question_type === 'ghost') {
        // Disguised as normal round!
        return {
            label: `${currentPhaseTitle.value.toUpperCase()} QUESTION`,
            class: 'bg-blue-900 text-blue-200 border border-blue-500'
        }
    }
    if (q.question_type === 'wrong') {
        return {
            label: 'FIND THE FALSE ONE',
            class: 'bg-red-900 text-red-200 border border-red-500 animate-pulse'
        }
    }
    if (q.question_type === 'music_single') {
        return {
            label: 'MUSIC ROUND',
            class: 'bg-purple-900 text-purple-200 border border-purple-500'
        }
    }
    return {
        label: `${currentPhaseTitle.value.toUpperCase()} QUESTION`,
        class: 'bg-blue-900 text-blue-200 border border-blue-500'
    }
})

// Media detection: Question Image is dedicated to side panel, Option Images are rendered as answer cards
const hasQuestionImage = computed(() => {
    const q = currentQuestion.value
    return Boolean(q.media_url && q.question_type !== 'music_single')
})

const hasOptionImages = computed(() => {
    return Boolean(currentQuestion.value.options && currentQuestion.value.options.some(o => !!o.media_url))
})

// Progress percentage (high-resolution smooth bar)
const timerPercentage = computed(() => {
    if (!questionTotalMs.value) return 100
    return Math.max(0, Math.min(100, (timeLeftMs.value / questionTotalMs.value) * 100))
})

// Bottom-right action bar display rule:
// In review state for Round 1 & Round 3, or after the 8th question of Wrong round!
const showBottomActionBar = computed(() => {
    if (gameState.value === 'ghost_reveal') return true
    if (gameState.value === 'review') return true
    return false
})

const getMediaUrl = (url) => {
    if (!url) return ''
    return url.startsWith('http') ? url : `${API_BASE}${url}`
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeyPress)
    await fetchPoolQuestions()
    if (rawPoolQuestions.value.length > 0) {
        startGame()
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyPress)
    stopCurrentAudio()
    clearInterval(timerInterval.value)
    clearInterval(roundIntroTimer)
    clearInterval(musicCountdownTimer)
    clearInterval(audioPlaybackTimer)
    clearTimeout(deltaTimeout)
})

// --- POOL SAMPLING (20 QUESTIONS) ---
const fetchPoolQuestions = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/questions?active_only=true`)
        rawPoolQuestions.value = await res.json()
    } catch (err) {
        console.error("Error fetching question pool:", err)
    }
}

const shuffleArray = (array) => {
    const arr = [...array]
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr
}

const build20QuestionMatch = () => {
    const pool = rawPoolQuestions.value

    // 1. Exactly 8 Wrong questions
    const wrongPool = pool.filter(q => q.question_type === 'wrong').sort(() => Math.random() - 0.5)
    const selectedWrongs = wrongPool.slice(0, 8)

    // 2. Exactly 1 Ghost question
    const ghostPool = pool.filter(q => q.question_type === 'ghost').sort(() => Math.random() - 0.5)
    const selectedGhosts = ghostPool.slice(0, 1)

    // 3. 1 or 2 Music questions
    const musicPool = pool.filter(q => q.question_type === 'music_single').sort(() => Math.random() - 0.5)
    const musicCount = Math.min(musicPool.length, Math.random() > 0.5 ? 2 : 1)
    const selectedMusics = musicPool.slice(0, musicCount)

    // 4. Fill remaining up to 12 non-wrong questions with Basic
    const neededBasics = 20 - selectedWrongs.length - selectedGhosts.length - selectedMusics.length
    const basicPool = pool.filter(q => q.question_type === 'basic').sort(() => Math.random() - 0.5)
    const selectedBasics = basicPool.slice(0, neededBasics)

    // Mix non-wrong questions randomly
    const nonWrongMixed = [...selectedGhosts, ...selectedMusics, ...selectedBasics].sort(() => Math.random() - 0.5)

    // Partition into 3 rounds:
    // Round 1: 7 questions
    const round1 = nonWrongMixed.slice(0, 7)
    // Round 2: 8 wrong questions
    const round2 = selectedWrongs
    // Round 3: remaining 5 questions
    const round3 = nonWrongMixed.slice(7)

    // Randomize option order for all questions so the correct option is not in a fixed position
    gameQuestions.value = [...round1, ...round2, ...round3].map(q => ({
        ...q,
        options: shuffleArray(q.options || [])
    }))
}

// --- GAME FLOW CONTROLLER ---
const startGame = () => {
    if (rawPoolQuestions.value.length === 0) {
        alert("No active questions available! Please activate some questions in the Admin panel.")
        return
    }

    build20QuestionMatch()
    score.value = 0
    correctCount.value = 0
    answeredCount.value = 0
    currentIndex.value = 0

    // Begin with Round 1 intro
    triggerRoundIntro('round1')
}

const triggerRoundIntro = (type) => {
    gameState.value = 'round_intro'
    roundIntroType.value = type
    roundIntroCountdown.value = 3

    if (type === 'wrong') {
        roundIntroTitle.value = 'WRONG ROUND'
        roundIntroSubtitle.value = 'Find the FALSE option!'
    } else if (type === 'round3') {
        roundIntroTitle.value = 'FINAL ROUND'
        roundIntroSubtitle.value = '5 Questions to decide your final score!'
    } else {
        roundIntroTitle.value = 'ROUND 1'
        roundIntroSubtitle.value = '7 General Knowledge Questions'
    }

    clearInterval(roundIntroTimer)
    roundIntroTimer = setInterval(() => {
        roundIntroCountdown.value--
        if (roundIntroCountdown.value <= 0) {
            clearInterval(roundIntroTimer)
            prepareCurrentQuestion()
        }
    }, 1000)
}

const stopCurrentAudio = () => {
    clearTimeout(audioSafetyTimer)
    audioSafetyTimer = null
    clearInterval(audioPlaybackTimer)
    audioPlaybackTimer = null
    if (currentAudio) {
        try {
            currentAudio.pause()
            currentAudio.currentTime = 0
            currentAudio.onended = null
            currentAudio.onerror = null
        } catch (e) {
            console.warn("Error stopping audio:", e)
        }
        currentAudio = null
    }
}

const prepareCurrentQuestion = () => {
    stopCurrentAudio()
    selectedOptionId.value = null
    ghostSurvived.value = false

    const q = currentQuestion.value

    // If Music question: trigger 3-second instrument countdown then audio
    if (q.question_type === 'music_single') {
        gameState.value = 'music_intro'
        musicCountdown.value = 3

        // Preload audio during countdown
        if (q.media_url) {
            const audioUrl = getMediaUrl(q.media_url)
            currentAudio = new Audio(audioUrl)
            currentAudio.preload = 'auto'
            currentAudio.onended = () => {
                onMusicAudioEnded()
            }
            currentAudio.onerror = (e) => {
                console.warn("Audio loading error, proceeding to question:", e)
                onMusicAudioEnded()
            }
        }

        clearInterval(musicCountdownTimer)
        musicCountdownTimer = setInterval(() => {
            musicCountdown.value--
            if (musicCountdown.value <= 0) {
                clearInterval(musicCountdownTimer)
                playMusicTrack()
            }
        }, 1000)
        return
    }

    // Normal or Wrong question: start countdown immediately
    startActiveQuestionTimer()
}

const playMusicTrack = () => {
    gameState.value = 'music_playing'
    audioPlaybackTimeLeft.value = 10

    if (currentAudio) {
        clearTimeout(audioSafetyTimer)
        clearInterval(audioPlaybackTimer)

        audioSafetyTimer = setTimeout(() => {
            console.warn("Audio safety timeout reached (12s limit)")
            onMusicAudioEnded()
        }, 12000)

        currentAudio.currentTime = 0
        const playPromise = currentAudio.play()
        if (playPromise !== undefined) {
            playPromise.catch(e => {
                console.warn("Audio autoplay blocked or error, proceeding to question:", e)
                onMusicAudioEnded()
            })
        }

        // Strict 10-second listening window
        audioPlaybackTimer = setInterval(() => {
            audioPlaybackTimeLeft.value--
            if (audioPlaybackTimeLeft.value <= 0) {
                clearInterval(audioPlaybackTimer)
                onMusicAudioEnded()
            }
        }, 1000)
    } else {
        setTimeout(onMusicAudioEnded, 2000)
    }
}

const onMusicAudioEnded = () => {
    stopCurrentAudio()
    startActiveQuestionTimer()
}

const startActiveQuestionTimer = () => {
    gameState.value = 'playing'
    stopCurrentAudio()

    // Static 5s for Wrong round, user-chosen gameTimeLimit for others
    const durationSec = isWrongRound.value ? 5 : gameTimeLimit.value
    activeQuestionTimeLimit.value = durationSec
    questionTotalMs.value = durationSec * 1000
    timeLeftMs.value = questionTotalMs.value
    timeLeft.value = durationSec
    questionStartTime.value = Date.now()

    clearInterval(timerInterval.value)
    timerInterval.value = setInterval(() => {
        const elapsed = Date.now() - questionStartTime.value
        const remaining = Math.max(0, questionTotalMs.value - elapsed)
        timeLeftMs.value = remaining
        timeLeft.value = Math.ceil(remaining / 1000)

        if (remaining <= 0) {
            clearInterval(timerInterval.value)
            handleTimeUp()
        }
    }, 25)
}

// --- OPTION SELECTION & SCORING ---
const selectOption = (opt) => {
    if (gameState.value !== 'playing' || timeLeftMs.value <= 0) return

    clearInterval(timerInterval.value)
    selectedOptionId.value = opt.id
    answeredCount.value++

    const qType = currentQuestion.value.question_type
    let isWinning = false

    if (qType === 'wrong') {
        isWinning = (opt.is_correct === false) // Winning in Wrong round means picking the false option
    } else if (qType === 'ghost') {
        isWinning = false // Any click in ghost round is a loss!
    } else {
        isWinning = (opt.is_correct === true)
    }

    // Exact percentage of timer remaining
    const elapsedMs = Date.now() - questionStartTime.value
    const remainingMs = Math.max(0, questionTotalMs.value - elapsedMs)
    const remainingRatio = Math.max(0.01, Math.min(1.0, remainingMs / questionTotalMs.value))
    const remainingPercentage = Math.round(remainingRatio * 100)

    // Score points: percentage of base points (e.g. 87% timer = 87% base points)
    const pointsMagnitude = Math.max(1, Math.round(gameBasePoints.value * (remainingPercentage / 100)))
    let delta = 0

    if (isWinning) {
        delta = pointsMagnitude
        score.value += delta
        correctCount.value++
    } else {
        delta = -pointsMagnitude
        score.value += delta // Score can go negative!
    }

    lastScoreDelta.value = delta
    triggerScoreDeltaNotification(delta)

    handleQuestionResolution()
}

const handleTimeUp = () => {
    clearInterval(timerInterval.value)
    timeLeftMs.value = 0
    timeLeft.value = 0
    answeredCount.value++

    const qType = currentQuestion.value.question_type

    // Ghost survival check: If timer ran out and player did not click anything, they WIN!
    if (qType === 'ghost' && !selectedOptionId.value) {
        ghostSurvived.value = true
        correctCount.value++
        const delta = gameBasePoints.value
        score.value += delta
        lastScoreDelta.value = delta
        triggerScoreDeltaNotification(delta)
    } else {
        // No option picked on time: 0 points
        lastScoreDelta.value = 0
    }

    handleQuestionResolution()
}

const handleQuestionResolution = () => {
    const qType = currentQuestion.value.question_type

    // 1. Ghost Round: Reveal animation
    if (qType === 'ghost') {
        gameState.value = 'ghost_reveal'
        return
    }

    // 2. Wrong Round Blitz: Wavy animation on correct choice, auto-advancing
    if (isWrongRound.value) {
        if (!isLastWrongQuestion.value) {
            // Auto advance after wavy animation (900ms)
            gameState.value = 'wrong_auto_next'
            setTimeout(() => {
                currentIndex.value++
                prepareCurrentQuestion()
            }, 900)
            return
        } else {
            // 8th wrong question finished: show review state with [V] and [B]
            gameState.value = 'review'
            return
        }
    }

    // 3. Normal / Music questions: Review state with bottom-right action bar
    gameState.value = 'review'
}

const triggerScoreDeltaNotification = (delta) => {
    scoreDeltaNotification.value = { points: delta }
    clearTimeout(deltaTimeout)
    deltaTimeout = setTimeout(() => {
        scoreDeltaNotification.value = null
    }, 1500)
}

// --- PROCEEDING & TRANSITIONS ---
const proceedToNext = () => {
    stopCurrentAudio()
    showScoreModal.value = false

    // Check if moving to the next question or ending game
    if (currentIndex.value + 1 < gameQuestions.value.length) {
        currentIndex.value++

        // Check if entering Wrong Round (index 7)
        if (currentIndex.value === 7) {
            triggerRoundIntro('wrong')
        }
        // Check if entering Final Round (index 15)
        else if (currentIndex.value === 15) {
            triggerRoundIntro('round3')
        }
        else {
            prepareCurrentQuestion()
        }
    } else {
        endGame()
    }
}

const handleKeyPress = (e) => {
    const key = e.key.toLowerCase()

    // 'V' toggles Score Modal
    if (key === 'v') {
        showScoreModal.value = !showScoreModal.value
    }

    // 'B' proceeds if in review or ghost_reveal state
    if (key === 'b' && (gameState.value === 'review' || gameState.value === 'ghost_reveal')) {
        proceedToNext()
    }
}

const endGame = async () => {
    stopCurrentAudio()
    gameState.value = 'gameover'
    // Persist final session to PostgreSQL
    try {
        await fetch(`${API_BASE}/api/games`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                total_points: score.value,
                correct_questions: correctCount.value,
                time_limit: gameTimeLimit.value,
                base_points: gameBasePoints.value
            })
        })
    } catch (err) {
        console.error("Failed to save game session:", err)
    }
}

const resetToStart = async () => {
    stopCurrentAudio()
    gameState.value = 'start'
    await fetchPoolQuestions()
    if (rawPoolQuestions.value.length > 0) {
        startGame()
    }
}

// --- DYNAMIC OPTION STYLING & WAVY EFFECT ---
const getOptionClass = (opt) => {
    const state = gameState.value
    const isAnswered = state === 'review' || state === 'ghost_reveal' || state === 'wrong_auto_next'

    if (!isAnswered) {
        return 'bg-gray-700/80 hover:bg-gray-600/90 border-gray-600 hover:border-blue-400 cursor-pointer text-gray-100 hover:scale-[1.01]'
    }

    const isSelected = selectedOptionId.value === opt.id
    const qType = currentQuestion.value.question_type

    // In Wrong round: the correct answer is opt.is_correct === false!
    let shouldBeHighlightedAsRight = false
    if (qType === 'wrong') {
        shouldBeHighlightedAsRight = (opt.is_correct === false)
    } else if (qType === 'ghost') {
        shouldBeHighlightedAsRight = false // All were false in ghost round
    } else {
        shouldBeHighlightedAsRight = opt.is_correct
    }

    // In Wrong round during wavy phase: apply wavy animation!
    if (state === 'wrong_auto_next' && shouldBeHighlightedAsRight) {
        return 'bg-green-600 text-white border-green-400 animate-wavy-correct shadow-xl'
    }

    if (shouldBeHighlightedAsRight) {
        return isSelected
            ? 'bg-green-600 border-green-400 text-white scale-[1.02] shadow-lg ring-2 ring-green-400/50'
            : 'bg-green-950 border-green-600 text-green-200'
    } else {
        return isSelected
            ? 'bg-red-600 border-red-400 text-white ring-2 ring-red-400/50'
            : 'bg-gray-900/60 border-gray-800 text-gray-500 opacity-40'
    }
}
</script>

<style scoped>
/* Keyframe for wavy animation on correct choice in Wrong round */
@keyframes wavy-correct {
    0% {
        transform: scale(1) rotate(0deg);
    }

    15% {
        transform: scale(1.06) rotate(-3deg);
    }

    30% {
        transform: scale(1.08) rotate(3deg);
    }

    45% {
        transform: scale(1.06) rotate(-2deg);
    }

    60% {
        transform: scale(1.04) rotate(2deg);
    }

    75% {
        transform: scale(1.02) rotate(-1deg);
    }

    100% {
        transform: scale(1) rotate(0deg);
    }
}

.animate-wavy-correct {
    animation: wavy-correct 0.8s ease-in-out infinite;
}

/* Floating Ghost Animation */
@keyframes float-ghost {

    0%,
    100% {
        transform: translateY(0) scale(1);
    }

    50% {
        transform: translateY(-16px) scale(1.08);
    }
}

.animate-float-ghost {
    animation: float-ghost 2s ease-in-out infinite;
}

/* Sound bar equalizer animation */
@keyframes sound-bar {

    0%,
    100% {
        transform: scaleY(0.3);
    }

    50% {
        transform: scaleY(1);
    }
}

.animate-sound-bar {
    animation: sound-bar 0.6s ease-in-out infinite alternate;
    transform-origin: bottom;
}

/* Slow vinyl spinning */
@keyframes spin-slow {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.animate-spin-slow {
    animation: spin-slow 8s linear infinite;
}

/* Scale pop countdown */
@keyframes scale-pop {
    0% {
        transform: scale(0.5);
        opacity: 0;
    }

    50% {
        transform: scale(1.2);
    }

    100% {
        transform: scale(1);
        opacity: 1;
    }
}

.animate-scale-pop {
    animation: scale-pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Pulse glow for wrong round */
@keyframes pulse-glow {

    0%,
    100% {
        filter: drop-shadow(0 0 15px rgba(239, 68, 68, 0.4));
    }

    50% {
        filter: drop-shadow(0 0 35px rgba(249, 115, 22, 0.8));
    }
}

.animate-pulse-glow {
    animation: pulse-glow 2s ease-in-out infinite;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.fade-up-enter-active,
.fade-up-leave-active {
    transition: all 0.35s ease-out;
}

.fade-up-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.fade-up-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}
</style>