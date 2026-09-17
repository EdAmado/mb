<template>
    <div class="flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <div class="text-center mb-10">
            <h1 class="text-6xl font-extrabold tracking-tight text-blue-400 mb-2">mr-because</h1>
            <p class="text-gray-400 text-lg">Configure your match settings and test your knowledge</p>
        </div>

        <!-- GAME CONFIGURATION CARD -->
        <div class="w-full max-w-md bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-2xl mb-8">
            <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>⚙️</span> Game Settings
            </h2>

            <div class="space-y-4">
                <div>
                    <div class="flex justify-between items-center mb-1.5">
                        <label class="text-sm font-medium text-gray-300">Time per question (seconds)</label>
                        <span class="text-blue-400 font-mono font-bold">{{ timeLimit }}s</span>
                    </div>
                    <input type="range" v-model.number="timeLimit" min="5" max="60" step="1"
                        class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500" />
                    <div class="flex justify-between text-xs text-gray-500 mt-1 font-mono">
                        <span>5s</span>
                        <span>10s</span>
                        <span>30s</span>
                        <span>60s</span>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between items-center mb-1.5">
                        <label class="text-sm font-medium text-gray-300">Base points per question</label>
                        <span class="text-yellow-400 font-mono font-bold">{{ basePoints }} pts</span>
                    </div>
                    <input type="number" v-model.number="basePoints" min="10" max="1000" step="10"
                        class="w-full p-2.5 bg-gray-900 rounded-lg border border-gray-600 focus:border-blue-500 text-white outline-none font-mono" />
                </div>
            </div>
        </div>

        <!-- ACTIONS -->
        <div class="flex flex-col sm:flex-row gap-3 w-full max-w-md">
            <button @click="startGame"
                class="flex-1 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xl font-bold transition-all shadow-lg hover:shadow-blue-500/30 text-center">
                Start Game
            </button>

            <button @click="openHistoryModal"
                class="py-4 px-5 bg-gray-800 hover:bg-gray-700 text-yellow-400 border border-gray-700 hover:border-yellow-500/50 rounded-xl text-lg font-bold transition-all shadow-lg text-center flex items-center justify-center gap-2"
                title="View past recorded games">
                <span>📜</span> History
            </button>

            <router-link to="/admin"
                class="py-4 px-5 bg-gray-700 hover:bg-gray-600 text-white rounded-xl text-lg font-bold transition-all shadow-lg text-center flex items-center justify-center">
                Questions
            </router-link>
        </div>

        <!-- GAME HISTORY MODAL -->
        <transition name="fade">
            <div v-if="showHistoryModal" @click.self="showHistoryModal = false"
                class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div
                    class="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-2xl w-full shadow-2xl relative max-h-[90vh] flex flex-col">
                    <button @click="showHistoryModal = false"
                        class="absolute top-4 right-4 text-gray-400 hover:text-white text-xl">✕</button>

                    <h3 class="text-2xl font-bold text-yellow-400 mb-4 flex items-center gap-2">
                        <span>📜</span> Recorded Game History
                    </h3>

                    <!-- Quick Summary Stats -->
                    <div v-if="pastGames.length > 0" class="grid grid-cols-3 gap-3 mb-5">
                        <div class="bg-gray-900/80 p-3 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Total Matches</span>
                            <div class="text-2xl font-extrabold text-blue-400 mt-0.5">{{ pastGames.length }}</div>
                        </div>
                        <div class="bg-gray-900/80 p-3 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Best Score</span>
                            <div class="text-2xl font-extrabold mt-0.5"
                                :class="bestScore < 0 ? 'text-red-400' : 'text-yellow-400'">
                                {{ bestScore }}
                            </div>
                        </div>
                        <div class="bg-gray-900/80 p-3 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Avg Score</span>
                            <div class="text-2xl font-extrabold mt-0.5"
                                :class="averageScore < 0 ? 'text-red-400' : 'text-green-400'">
                                {{ averageScore }}
                            </div>
                        </div>
                    </div>

                    <!-- Games List / Table -->
                    <div class="overflow-y-auto flex-1 pr-1 border border-gray-700/60 rounded-xl bg-gray-900/50">
                        <div v-if="isLoadingHistory" class="p-8 text-center text-gray-400">
                            <div
                                class="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-2">
                            </div>
                            Loading past games...
                        </div>

                        <div v-else-if="pastGames.length === 0" class="p-10 text-center text-gray-400">
                            <span class="text-4xl block mb-2">🎮</span>
                            <p class="font-semibold text-gray-300">No recorded games yet!</p>
                            <p class="text-xs text-gray-500 mt-1">Play a match to see your score and accuracy history
                                here.</p>
                        </div>

                        <table v-else class="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr
                                    class="bg-gray-900 text-gray-400 border-b border-gray-800 select-none text-xs uppercase">
                                    <th class="p-3">Date</th>
                                    <th class="p-3 text-center">Score</th>
                                    <th class="p-3 text-center">Correct</th>
                                    <th class="p-3 text-right">Settings</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-800">
                                <tr v-for="g in pastGames" :key="g.id" class="hover:bg-gray-800/60 transition">
                                    <td class="p-3 font-mono text-gray-300 text-xs">
                                        {{ formatDate(g.timestamp) }}
                                    </td>
                                    <td class="p-3 text-center font-extrabold font-mono text-base"
                                        :class="g.total_points < 0 ? 'text-red-400' : 'text-yellow-400'">
                                        {{ g.total_points }}
                                    </td>
                                    <td class="p-3 text-center">
                                        <span class="text-green-400 font-bold font-mono">{{ g.correct_questions
                                            }}</span>
                                        <span class="text-gray-500 font-mono text-xs"> / 20</span>
                                    </td>
                                    <td class="p-3 text-right text-xs text-gray-400 font-mono">
                                        {{ g.time_limit }}s • {{ g.base_points }}pts
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <button @click="showHistoryModal = false"
                        class="mt-4 w-full py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-bold transition text-center text-sm">
                        Close
                    </button>
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const API_BASE = 'http://localhost:5000'
const router = useRouter()

const timeLimit = ref(10)
const basePoints = ref(100)

const showHistoryModal = ref(false)
const isLoadingHistory = ref(false)
const pastGames = ref([])

const openHistoryModal = async () => {
    showHistoryModal.value = true
    isLoadingHistory.value = true
    try {
        const res = await fetch(`${API_BASE}/api/games`)
        if (res.ok) {
            pastGames.value = await res.json()
        }
    } catch (err) {
        console.error("Failed to load past games:", err)
    } finally {
        isLoadingHistory.value = false
    }
}

const bestScore = computed(() => {
    if (pastGames.value.length === 0) return 0
    return Math.max(...pastGames.value.map(g => g.total_points))
})

const averageScore = computed(() => {
    if (pastGames.value.length === 0) return 0
    const total = pastGames.value.reduce((acc, g) => acc + g.total_points, 0)
    return Math.round(total / pastGames.value.length)
})

const formatDate = (isoString) => {
    if (!isoString) return '-'
    const d = new Date(isoString)
    return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const startGame = () => {
    router.push({
        path: '/game',
        query: {
            time_limit: timeLimit.value || 10,
            base_points: basePoints.value || 100
        }
    })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>