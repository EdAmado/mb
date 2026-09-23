<template>
    <div class="max-w-4xl mx-auto p-4 sm:p-6 text-gray-200 min-h-screen flex flex-col justify-center">

        <!-- CANCELLATION NOTICE MODAL / BANNER -->
        <transition name="fade">
            <div v-if="cancellationMessage"
                class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div
                    class="bg-gray-800 border border-red-500/50 rounded-2xl p-6 max-w-md w-full shadow-2xl text-center">
                    <div
                        class="w-16 h-16 bg-red-900/50 border border-red-500/40 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
                        🛑
                    </div>
                    <h3 class="text-2xl font-bold text-white mb-2">Lobby Cancelled</h3>
                    <p class="text-gray-300 text-sm mb-6">{{ cancellationMessage }}</p>
                    <button @click="returnHome"
                        class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition shadow-lg text-center cursor-pointer">
                        Return to Home
                    </button>
                </div>
            </div>
        </transition>

        <!-- TOP BAR -->
        <div class="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
            <div class="flex items-center space-x-3">
                <h1 class="text-2xl sm:text-3xl font-extrabold text-blue-400">Game Lobby</h1>
                <span
                    class="px-2.5 py-1 rounded-full text-xs font-bold bg-green-900/70 border border-green-600 text-green-300 flex items-center gap-1.5 animate-pulse">
                    <span class="w-2 h-2 rounded-full bg-green-400"></span>
                    Waiting for players
                </span>
            </div>

            <!-- Role Badge -->
            <span class="px-3 py-1 rounded-lg text-xs font-bold border"
                :class="isAdmin ? 'bg-yellow-900/40 border-yellow-500/50 text-yellow-300' : 'bg-gray-800 border-gray-700 text-gray-300'">
                {{ isAdmin ? '👑 Admin (Host)' : '🎮 Player' }}
            </span>
        </div>

        <!-- MAIN LOBBY CONTENT -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- PLAYERS LIST CARD -->
            <div
                class="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-bold text-white flex items-center gap-2">
                            <span>👥</span> Players ({{ lobby.players ? lobby.players.length : 0 }})
                        </h2>
                    </div>

                    <!-- Players list -->
                    <div class="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
                        <div v-for="player in lobby.players" :key="player.id"
                            class="flex items-center justify-between p-3 rounded-xl border transition"
                            :class="player.id === playerId ? 'bg-gray-900/90 border-blue-500/60 ring-1 ring-blue-500/30' : 'bg-gray-900/50 border-gray-700/60'">

                            <div class="flex items-center space-x-3 min-w-0">
                                <div class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0"
                                    :class="player.is_admin ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40' : 'bg-blue-500/20 text-blue-300 border border-blue-500/40'">
                                    {{ player.is_admin ? '👑' : player.name.charAt(0).toUpperCase() }}
                                </div>

                                <div class="min-w-0">
                                    <div class="flex items-center gap-2">
                                        <span class="font-bold text-sm text-gray-100 truncate block">
                                            {{ player.name }}
                                        </span>
                                        <span v-if="player.id === playerId"
                                            class="text-xs text-blue-400 font-semibold">(You)</span>
                                    </div>
                                    <span v-if="player.is_admin" class="text-xs text-yellow-400/80 font-medium">Host /
                                        Admin</span>
                                </div>
                            </div>

                            <!-- Edit Name Button (Only for current player) -->
                            <div v-if="player.id === playerId" class="flex-shrink-0">
                                <button v-if="!isEditingName" @click="startEditName(player.name)" type="button"
                                    class="text-xs px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-blue-300 rounded border border-gray-600 transition flex items-center gap-1 cursor-pointer"
                                    title="Edit your nickname">
                                    <span>✏️</span> Edit
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Inline Nickname Edit Modal / Form -->
                    <div v-if="isEditingName" class="mt-4 p-3 bg-gray-900 rounded-xl border border-blue-500/60">
                        <label class="block text-xs font-semibold text-blue-300 mb-1.5">Change Your Nickname</label>
                        <div class="flex gap-2">
                            <input type="text" v-model="editedName" maxlength="20"
                                class="flex-1 p-2 bg-gray-800 rounded-lg border border-gray-600 focus:border-blue-500 outline-none text-white text-sm"
                                placeholder="Enter nickname" @keyup.enter="saveNickname" autofocus />
                            <button @click="saveNickname" type="button"
                                class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition cursor-pointer">
                                Save
                            </button>
                            <button @click="isEditingName = false" type="button"
                                class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-xs font-medium transition cursor-pointer">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Footer Leave button for regular player -->
                <div v-if="!isAdmin" class="mt-6 pt-4 border-t border-gray-700/60">
                    <button @click="leaveLobby" type="button"
                        class="w-full py-2.5 bg-gray-700 hover:bg-red-900/60 text-gray-300 hover:text-red-200 rounded-xl font-semibold text-sm transition border border-gray-600 hover:border-red-500/50 flex items-center justify-center gap-2 cursor-pointer">
                        <span>🚪</span> Leave Lobby
                    </button>
                </div>
            </div>

            <!-- RIGHT COLUMN: SETTINGS & CONTROLS -->
            <div class="space-y-6">

                <!-- QUESTION DATASET POOL WARNING FOR ADMIN -->
                <div v-if="isAdmin && lobby.unlocked_questions_count !== undefined && lobby.unlocked_questions_count < 30"
                    class="p-4 bg-amber-950/60 border border-amber-500/60 rounded-2xl shadow-xl">
                    <div class="flex items-start gap-3">
                        <span class="text-2xl shrink-0">⚠️</span>
                        <div class="flex-1">
                            <h4 class="text-sm font-bold text-amber-300">Dataset Question Shortage</h4>
                            <p class="text-xs text-amber-200/90 mt-0.5 leading-relaxed">
                                The dataset has only <strong class="text-white">{{ lobby.unlocked_questions_count
                                }}</strong> of {{ lobby.total_questions_count || 45 }} questions unlocked (30 needed
                                for a match).
                            </p>
                            <button @click="unlockAllQuestions" type="button" :disabled="isUnlocking"
                                class="mt-2.5 px-3 py-1.5 bg-amber-600 hover:bg-amber-500 disabled:bg-gray-700 text-gray-950 hover:text-white rounded-lg font-bold text-xs transition shadow flex items-center gap-1.5 cursor-pointer">
                                <span v-if="isUnlocking"
                                    class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
                                <span>🔓 Unlock All Questions</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ADMIN SETTINGS CARD (Only shown to Admin) -->
                <div v-if="isAdmin" class="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <span>⚙️</span> Game Settings
                    </h2>

                    <div class="space-y-4">
                        <div>
                            <div class="flex justify-between items-center mb-1.5">
                                <label class="text-sm font-medium text-gray-300">Time per question (seconds)</label>
                                <span class="text-blue-400 font-mono font-bold">{{ localSettings.time_limit }}s</span>
                            </div>
                            <input type="range" v-model.number="localSettings.time_limit" @change="broadcastSettings"
                                min="5" max="60" step="1"
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
                                <span class="text-yellow-400 font-mono font-bold">{{ localSettings.base_points }}
                                    pts</span>
                            </div>
                            <input type="number" v-model.number="localSettings.base_points" @change="broadcastSettings"
                                min="10" max="1000" step="10"
                                class="w-full p-2.5 bg-gray-900 rounded-lg border border-gray-600 focus:border-blue-500 text-white outline-none font-mono text-sm" />
                        </div>

                        <div class="pt-2 border-t border-gray-700/60">
                            <div
                                class="flex items-center justify-between p-3 bg-gray-900/80 rounded-xl border border-gray-700">
                                <div class="pr-2">
                                    <label class="text-sm font-semibold text-gray-200 block">Lock chosen
                                        questions</label>
                                    <span class="text-xs text-gray-400">Guarantees next game only picks fresh
                                        questions</span>
                                </div>
                                <input type="checkbox" v-model="localSettings.lock_chosen_questions"
                                    @change="broadcastSettings"
                                    class="w-5 h-5 rounded accent-blue-600 cursor-pointer" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- PLAYER READ-ONLY SETTINGS SUMMARY (For non-admin) -->
                <div v-else class="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <span>⚙️</span> Match Settings
                    </h2>
                    <div class="grid grid-cols-2 gap-3">
                        <div class="bg-gray-900/80 p-3 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Time Per Question</span>
                            <div class="text-xl font-extrabold text-blue-400 font-mono mt-1">
                                {{ lobby.settings ? lobby.settings.time_limit : 10 }}s
                            </div>
                        </div>
                        <div class="bg-gray-900/80 p-3 rounded-xl border border-gray-700 text-center">
                            <span class="text-xs text-gray-400 uppercase font-semibold">Base Points</span>
                            <div class="text-xl font-extrabold text-yellow-400 font-mono mt-1">
                                {{ lobby.settings ? lobby.settings.base_points : 100 }} pts
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ACTION BUTTONS CARD -->
                <div class="bg-gray-800 p-5 sm:p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <!-- ADMIN ACTIONS -->
                    <div v-if="isAdmin" class="space-y-3">
                        <button @click="startGame" type="button" :disabled="nonAdminPlayersCount < 1"
                            :class="nonAdminPlayersCount < 1
                                ? 'bg-gray-700 text-gray-400 cursor-not-allowed border border-gray-600'
                                : 'bg-green-600 hover:bg-green-500 text-white shadow-lg hover:shadow-green-500/20 cursor-pointer'"
                            class="w-full py-4 rounded-xl text-lg font-bold transition text-center flex items-center justify-center gap-2">
                            <span>🚀</span> Start Game
                        </button>
                        <p v-if="nonAdminPlayersCount < 1" class="text-xs text-amber-400/90 text-center font-medium">
                            At least 1 player must join before starting the game
                        </p>

                        <button @click="cancelLobby" type="button"
                            class="w-full py-3 bg-red-900/40 hover:bg-red-800/80 text-red-300 hover:text-white rounded-xl font-bold transition border border-red-700/60 text-center flex items-center justify-center gap-2 cursor-pointer">
                            <span>✕</span> Cancel Lobby
                        </button>
                    </div>

                    <!-- PLAYER WAITING VIEW -->
                    <div v-else class="text-center py-4 space-y-3">
                        <div
                            class="w-10 h-10 border-3 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto">
                        </div>
                        <p class="text-sm font-semibold text-gray-300">
                            Waiting for the admin (<span class="text-blue-300">{{ lobby.admin_name || 'Host' }}</span>)
                            to start the game...
                        </p>
                    </div>
                </div>

            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import socket from '../socket'

const router = useRouter()

const playerId = ref(sessionStorage.getItem('player_id'))
const playerToken = ref(sessionStorage.getItem('player_token'))
const isAdmin = ref(sessionStorage.getItem('is_admin') === 'true')

const nonAdminPlayersCount = computed(() => {
    return (lobby.value.players || []).filter(p => !p.is_admin).length
})

const lobby = ref({
    is_active: false,
    status: 'lobby',
    admin_id: null,
    admin_name: 'Admin',
    players: [],
    settings: { time_limit: 10, base_points: 100 }
})

const localSettings = ref({
    time_limit: 15,
    base_points: 100,
    lock_chosen_questions: true
})

const cancellationMessage = ref('')
const isEditingName = ref(false)
const editedName = ref('')
const isUnlocking = ref(false)

onMounted(() => {
    // If not joined, redirect home
    if (!playerId.value || !playerToken.value) {
        router.push('/')
        return
    }

    // Join lobby room in Socket.IO
    socket.emit('join_lobby_room')

    // Listeners
    socket.on('lobby_state', handleLobbyUpdate)
    socket.on('lobby_updated', handleLobbyUpdate)
    socket.on('lobby_cancelled', handleLobbyCancelled)
    socket.on('game_started', handleGameStarted)
})

onUnmounted(() => {
    socket.off('lobby_state', handleLobbyUpdate)
    socket.off('lobby_updated', handleLobbyUpdate)
    socket.off('lobby_cancelled', handleLobbyCancelled)
    socket.off('game_started', handleGameStarted)
})

const handleLobbyUpdate = (data) => {
    if (!data || !data.is_active) {
        handleLobbyCancelled({ message: 'The lobby is no longer active.' })
        return
    }

    lobby.value = data
    if (data.settings) {
        if (data.settings.time_limit !== undefined) localSettings.value.time_limit = data.settings.time_limit
        if (data.settings.base_points !== undefined) localSettings.value.base_points = data.settings.base_points
        if (data.settings.lock_chosen_questions !== undefined) localSettings.value.lock_chosen_questions = data.settings.lock_chosen_questions
    }
}

const unlockAllQuestions = async () => {
    isUnlocking.value = true
    try {
        const res = await fetch('/api/questions/unlock-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: playerToken.value })
        })
        const data = await res.json()
        if (data && data.success) {
            if (data.lobby) {
                handleLobbyUpdate(data.lobby)
            }
            socket.emit('get_lobby_state')
        } else {
            socket.emit('unlock_all_questions', { token: playerToken.value }, (socketRes) => {
                if (socketRes && socketRes.success && socketRes.lobby) {
                    handleLobbyUpdate(socketRes.lobby)
                }
            })
        }
    } catch (e) {
        console.error('Error unlocking questions:', e)
        socket.emit('unlock_all_questions', { token: playerToken.value }, (socketRes) => {
            if (socketRes && socketRes.success && socketRes.lobby) {
                handleLobbyUpdate(socketRes.lobby)
            }
        })
    } finally {
        isUnlocking.value = false
    }
}

const handleLobbyCancelled = (data) => {
    cancellationMessage.value = data && data.message ? data.message : 'The lobby was cancelled.'
    sessionStorage.removeItem('player_id')
    sessionStorage.removeItem('player_token')
    sessionStorage.removeItem('is_admin')
}

const returnHome = () => {
    cancellationMessage.value = ''
    router.push('/')
}

const startEditName = (currentName) => {
    editedName.value = currentName
    isEditingName.value = true
}

const saveNickname = () => {
    if (!editedName.value.trim()) return
    socket.emit('update_nickname', {
        player_id: playerId.value,
        token: playerToken.value,
        nickname: editedName.value.trim()
    }, (res) => {
        if (res && res.success) {
            isEditingName.value = false
        }
    })
}

const broadcastSettings = () => {
    if (!isAdmin.value) return
    socket.emit('update_settings', {
        token: playerToken.value,
        settings: {
            time_limit: localSettings.value.time_limit,
            base_points: localSettings.value.base_points,
            lock_chosen_questions: localSettings.value.lock_chosen_questions
        }
    })
}

const cancelLobby = () => {
    if (!confirm('Are you sure you want to cancel the lobby? All players will be returned to the home screen.')) return
    socket.emit('cancel_lobby', { token: playerToken.value }, (res) => {
        if (res && res.success) {
            sessionStorage.removeItem('player_id')
            sessionStorage.removeItem('player_token')
            sessionStorage.removeItem('is_admin')
            router.push('/')
        }
    })
}

const leaveLobby = () => {
    socket.emit('leave_lobby', {
        player_id: playerId.value,
        token: playerToken.value
    }, () => {
        sessionStorage.removeItem('player_id')
        sessionStorage.removeItem('player_token')
        sessionStorage.removeItem('is_admin')
        router.push('/')
    })
}

const handleGameStarted = () => {
    router.push('/game')
}

const startGame = () => {
    if (nonAdminPlayersCount.value < 1) {
        alert("Cannot start game without at least one player.")
        return
    }
    socket.emit('start_game', { token: playerToken.value }, (res) => {
        if (res && res.success) {
            router.push('/game')
        } else {
            alert(res && res.error ? res.error : "Failed to start game.")
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
