<template>
    <div class="flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <div class="text-center mb-10">
            <h1 class="text-5xl sm:text-6xl font-extrabold tracking-tight text-blue-400 mb-2">mr-because</h1>
            <p class="text-gray-400 text-base sm:text-lg">Host or join a multiplayer trivia match and test your knowledge</p>
        </div>

        <!-- ACTIONS -->
        <div class="flex flex-col sm:flex-row gap-3 w-full max-w-md">

            <!-- NO GAME ACTIVE: OPEN GAME (BECOME ADMIN) -->
            <button v-if="!lobbyState.is_active" @click="handleOpenGame" :disabled="isActionLoading"
                class="flex-1 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-xl text-xl font-bold transition-all shadow-lg hover:shadow-blue-500/30 text-center flex items-center justify-center gap-2 cursor-pointer">
                <span v-if="isActionLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                <span>{{ isActionLoading ? 'Opening...' : 'Open game' }}</span>
            </button>

            <!-- GAME ACTIVE (LOBBY): JOIN GAME -->
            <button v-else-if="lobbyState.status === 'lobby'" @click="showJoinModal = true"
                class="flex-1 py-4 bg-green-600 hover:bg-green-500 text-white rounded-xl text-xl font-bold transition-all shadow-lg hover:shadow-green-500/30 text-center flex items-center justify-center gap-2 cursor-pointer animate-pulse">
                <span>Join game</span>
            </button>

            <!-- GAME IN PROGRESS -->
            <button v-else disabled
                class="flex-1 py-4 bg-gray-700 text-gray-400 rounded-xl text-lg font-bold text-center cursor-not-allowed">
                Game in Progress
            </button>

            <!-- HISTORY BUTTON -->
            <button @click="openHistoryModal"
                class="py-4 px-5 bg-gray-800 hover:bg-gray-700 text-yellow-400 border border-gray-700 hover:border-yellow-500/50 rounded-xl text-lg font-bold transition-all shadow-lg text-center flex items-center justify-center gap-2 cursor-pointer"
                title="View past recorded games">
                <span>📜</span> History
            </button>

            <!-- QUESTIONS BUTTON (PASSWORD PROTECTED) -->
            <router-link to="/admin"
                class="py-4 px-5 bg-gray-700 hover:bg-gray-600 text-white rounded-xl text-lg font-bold transition-all shadow-lg text-center flex items-center justify-center">
                Questions
            </router-link>
        </div>

        <!-- ACTIVE LOBBY NOTIFICATION BADGE -->
        <div v-if="lobbyState.is_active && lobbyState.status === 'lobby'" class="mt-4 text-xs text-green-400 font-medium flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-green-400 animate-ping"></span>
            A lobby is currently open with {{ lobbyState.players ? lobbyState.players.length : 1 }} player(s).
        </div>

        <!-- JOIN NICKNAME MODAL -->
        <transition name="fade">
            <div v-if="showJoinModal" @click.self="showJoinModal = false"
                class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full shadow-2xl relative">
                    <button @click="showJoinModal = false"
                        class="absolute top-4 right-4 text-gray-400 hover:text-white text-xl">✕</button>

                    <h3 class="text-2xl font-bold text-green-400 mb-2 flex items-center gap-2">
                        <span>🎮</span> Join Game Lobby
                    </h3>
                    <p class="text-gray-400 text-sm mb-5">Enter your nickname to join the active match lobby.</p>

                    <div v-if="joinError" class="mb-4 p-3 bg-red-900/60 border border-red-500 rounded-lg text-red-200 text-sm">
                        {{ joinError }}
                    </div>

                    <form @submit.prevent="handleJoinGame" class="space-y-4">
                        <input
                            type="text"
                            v-model="joinNickname"
                            placeholder="Your Nickname (e.g. Maverick)"
                            maxlength="20"
                            class="w-full p-3 bg-gray-900 rounded-xl border border-gray-600 focus:border-green-500 outline-none text-white text-base"
                            autofocus
                        />

                        <button
                            type="submit"
                            :disabled="isActionLoading || !joinNickname.trim()"
                            class="w-full py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl font-bold transition shadow-lg text-center flex items-center justify-center gap-2 cursor-pointer"
                        >
                            <span v-if="isActionLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                            <span>{{ isActionLoading ? 'Joining...' : 'Join Lobby' }}</span>
                        </button>
                    </form>
                </div>
            </div>
        </transition>

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
                            <p class="text-xs text-gray-500 mt-1">Play a match to see your score and accuracy history here.</p>
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
                                        <span class="text-green-400 font-bold font-mono">{{ g.correct_questions }}</span>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import socket from '../socket'

const API_BASE = ''
const router = useRouter()

const lobbyState = ref({
    is_active: false,
    status: null,
    players: []
})

const isActionLoading = ref(false)
const showJoinModal = ref(false)
const joinNickname = ref('')
const joinError = ref('')

// History Modal State
const showHistoryModal = ref(false)
const isLoadingHistory = ref(false)
const pastGames = ref([])

onMounted(() => {
    fetchLobbyStatus()

    socket.on('lobby_updated', updateLobbyState)
    socket.on('lobby_cancelled', () => {
        lobbyState.value = { is_active: false, status: null, players: [] }
    })
})

onUnmounted(() => {
    socket.off('lobby_updated', updateLobbyState)
    socket.off('lobby_cancelled')
})

const updateLobbyState = (data) => {
    if (data) {
        lobbyState.value = data
    }
}

const fetchLobbyStatus = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/lobby/status`)
        if (res.ok) {
            lobbyState.value = await res.json()
        }
    } catch (err) {
        console.error("Failed to load lobby status:", err)
    }
}

const handleOpenGame = () => {
    isActionLoading.value = true
    socket.emit('open_lobby', { admin_name: 'Admin' }, (res) => {
        isActionLoading.value = false
        if (res && res.success) {
            sessionStorage.setItem('player_id', res.player.id)
            sessionStorage.setItem('player_token', res.token)
            sessionStorage.setItem('is_admin', 'true')
            router.push('/lobby')
        } else {
            alert(res && res.error ? res.error : "Failed to open lobby.")
            fetchLobbyStatus()
        }
    })
}

const handleJoinGame = () => {
    const name = joinNickname.value.trim()
    if (!name) return

    isActionLoading.value = true
    joinError.value = ''

    socket.emit('join_lobby', { nickname: name }, (res) => {
        isActionLoading.value = false
        if (res && res.success) {
            sessionStorage.setItem('player_id', res.player.id)
            sessionStorage.setItem('player_token', res.token)
            sessionStorage.setItem('is_admin', 'false')
            showJoinModal.value = false
            router.push('/lobby')
        } else {
            joinError.value = res && res.error ? res.error : "Failed to join lobby."
            fetchLobbyStatus()
        }
    })
}

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