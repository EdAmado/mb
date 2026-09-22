<template>
    <div class="max-w-6xl mx-auto p-4 sm:p-6 text-gray-200">
        <!-- PASSWORD LOCK SCREEN -->
        <div v-if="!isAuthenticated" class="min-h-[75vh] flex items-center justify-center px-4">
            <div class="bg-gray-800 p-8 rounded-2xl border border-gray-700 shadow-2xl max-w-md w-full text-center">
                <div class="w-16 h-16 bg-blue-900/50 border border-blue-500/40 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-5 shadow-inner">
                    🔒
                </div>
                
                <h2 class="text-2xl font-bold text-white mb-2">Restricted Access</h2>
                <p class="text-gray-400 text-sm mb-6">Enter the password to access and manage questions.</p>
                
                <div v-if="authError" class="mb-4 p-3 bg-red-900/60 border border-red-500 rounded-lg text-red-200 text-sm flex items-center justify-between">
                    <span>{{ authError }}</span>
                    <button @click="authError = ''" type="button" class="text-red-300 font-bold ml-2">✕</button>
                </div>

                <form @submit.prevent="handleUnlock" class="space-y-4">
                    <input
                        type="password"
                        v-model="passwordInput"
                        placeholder="Enter password"
                        autocomplete="current-password"
                        class="w-full p-3 bg-gray-900 rounded-xl border border-gray-600 focus:border-blue-500 outline-none text-white text-center font-mono placeholder-gray-500 text-base transition"
                        autofocus
                    />
                    
                    <button
                        type="submit"
                        :disabled="isCheckingPassword"
                        class="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-xl font-bold transition shadow-lg hover:shadow-blue-500/20 text-center flex items-center justify-center gap-2 cursor-pointer"
                    >
                        <span v-if="isCheckingPassword" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        <span>{{ isCheckingPassword ? 'Verifying...' : 'Unlock' }}</span>
                    </button>
                </form>

                <div class="mt-6 pt-6 border-t border-gray-700/60">
                    <router-link to="/" class="text-sm text-gray-400 hover:text-white transition flex items-center justify-center gap-1.5 font-medium">
                        ← Back to Home
                    </router-link>
                </div>
            </div>
        </div>

        <!-- MAIN QUESTIONS MANAGEMENT CONTENT -->
        <div v-else>
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 sm:mb-8 border-b border-gray-700 pb-4">
                <h1 class="text-2xl sm:text-3xl font-bold text-blue-400">Questions Management</h1>
                <div class="flex items-center space-x-3 self-end sm:self-auto">
                    <button @click="handleLock" type="button"
                        class="px-3.5 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-300 rounded font-medium transition flex items-center gap-1.5 text-sm cursor-pointer"
                        title="Lock and require password again">
                        <span>🔒</span> Lock
                    </button>
                    <router-link to="/" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded font-medium transition text-sm">
                        Back to Home
                    </router-link>
                </div>
            </div>

        <!-- ADD / EDIT QUESTION FORM -->
        <div id="question-form" class="bg-gray-800 p-4 sm:p-6 rounded-lg shadow-lg mb-8 sm:mb-10 border"
            :class="editingQuestionId ? 'border-blue-500 ring-1 ring-blue-500/50' : 'border-gray-700'">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
                <div class="flex items-center space-x-3">
                    <h2 class="text-xl sm:text-2xl font-semibold text-white">
                        {{ editingQuestionId ? `Edit Question #${editingQuestionId}` : 'Add New Question' }}
                    </h2>
                    <span v-if="editingQuestionId"
                        class="px-2.5 py-0.5 rounded text-xs font-bold bg-blue-900 text-blue-300 border border-blue-600">
                        Editing Mode
                    </span>
                </div>
                <div class="flex items-center space-x-3 self-end sm:self-auto">
                    <!-- Form Lock Toggle -->
                    <button type="button" @click="form.is_active = !form.is_active"
                        class="px-3 py-1 rounded text-xs font-bold border transition flex items-center space-x-1.5"
                        :class="form.is_active ? 'bg-green-900/60 border-green-600 text-green-300' : 'bg-gray-700 border-gray-600 text-gray-400'"
                        :title="form.is_active ? 'Available in game pool' : 'Locked (excluded from game pool)'">
                        <span>{{ form.is_active ? '🔓 Pool: Active' : '🔒 Pool: Locked' }}</span>
                    </button>

                    <button v-if="editingQuestionId" @click="cancelEdit"
                        class="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-sm rounded font-medium transition">
                        Cancel Edit
                    </button>
                </div>
            </div>

            <!-- Error Banner -->
            <div v-if="formError"
                class="mb-4 p-3 bg-red-900/60 border border-red-500 rounded text-red-200 text-sm flex justify-between items-center">
                <span>{{ formError }}</span>
                <button @click="formError = ''" class="text-red-300 font-bold ml-4">✕</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm mb-1 text-gray-400 font-medium">Question Type</label>
                    <select v-model="form.question_type" @change="handleTypeChange"
                        class="w-full p-2 bg-gray-900 rounded border border-gray-600 focus:border-blue-500 outline-none">
                        <option value="basic">Basic</option>
                        <option value="wrong">Wrong (Find the false one)</option>
                        <option value="ghost">Ghost (Skip, all false)</option>
                        <option value="music_single">Music (Single Track)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-sm mb-1 text-gray-400 font-medium">Question Text / Title</label>
                    <input type="text" v-model="form.text"
                        class="w-full p-2 bg-gray-900 rounded border border-gray-600 focus:border-blue-500 outline-none"
                        placeholder="e.g. What is the capital of France?" />
                </div>
            </div>

            <!-- Question Media Upload -->
            <!-- Music track for music_single -->
            <div v-if="form.question_type === 'music_single'"
                class="mb-4 p-4 bg-gray-900/70 rounded border border-gray-700">
                <label class="block text-sm mb-1 text-blue-300 font-medium">Upload Audio Track</label>
                <div class="flex items-center space-x-3">
                    <input type="file" ref="questionFileInput" @change="uploadQuestionMedia" accept="audio/*"
                        class="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer" />
                    <button v-if="form.media_url" @click="removeQuestionMedia" type="button"
                        class="text-xs text-red-400 hover:text-red-300 underline font-semibold">
                        Remove Audio
                    </button>
                </div>
                <div v-if="form.media_url" class="mt-2">
                    <audio :src="getMediaUrl(form.media_url)" controls class="h-8 max-w-md"></audio>
                </div>
            </div>

            <!-- Image for question (non-music) -->
            <div v-else class="mb-4 p-4 bg-gray-900/70 rounded border border-gray-700">
                <label class="block text-sm mb-1 text-blue-300 font-medium">Question Image (Optional)</label>
                <div class="flex items-center space-x-3">
                    <input type="file" ref="questionFileInput" @change="uploadQuestionMedia" accept="image/*"
                        class="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer" />
                    <button v-if="form.media_url" @click="removeQuestionMedia" type="button"
                        class="text-xs text-red-400 hover:text-red-300 underline font-semibold">
                        Remove Image
                    </button>
                </div>
                <div v-if="form.media_url" class="mt-2 flex items-center space-x-3">
                    <img :src="getMediaUrl(form.media_url)" alt="Question Image Preview"
                        class="h-20 w-auto rounded border border-gray-600 object-cover" />
                    <span class="text-xs text-green-400">Image attached</span>
                </div>
            </div>

            <!-- OPTIONS SECTION -->
            <div class="mt-6 border-t border-gray-700 pt-4">
                <div class="flex justify-between items-center mb-2">
                    <div>
                        <h3 class="text-xl font-semibold text-white">Options</h3>
                        <p class="text-xs text-gray-400 mt-0.5">
                            Must have between 2 and 5 options. If one option has an image, all must have an image.
                            <span v-if="form.question_type === 'ghost'" class="text-purple-300 font-semibold">(Ghost
                                questions have no correct option)</span>
                            <span v-else class="text-blue-300 font-semibold">(Select exactly 1 correct option)</span>
                        </p>
                    </div>
                    <button @click="addOption" v-if="form.options.length < 5" type="button"
                        class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded text-sm font-semibold transition">
                        + Add Option
                    </button>
                </div>

                <div class="space-y-3 mt-4">
                    <div v-for="(opt, index) in form.options" :key="index"
                        class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 bg-gray-900 p-3 rounded border border-gray-700">

                        <!-- Option number and text -->
                        <div class="flex items-center space-x-2 flex-1 min-w-0">
                            <span class="text-xs font-mono text-gray-500 w-4 text-center flex-shrink-0">{{ index + 1 }}</span>
                            <input type="text" v-model="opt.text" placeholder="Option text"
                                class="flex-1 p-2 bg-gray-800 rounded border border-gray-600 focus:border-blue-500 outline-none text-sm min-w-0" />
                        </div>

                        <!-- Upload Image + Correct toggle + Delete button -->
                        <div class="flex items-center space-x-2 flex-1 min-w-0 pl-6 sm:pl-0">
                            <!-- Upload Image for Option -->
                            <div class="flex-1 flex items-center space-x-2 min-w-0">
                                <input type="file" :ref="el => setOptionFileInput(el, index)"
                                    @change="e => uploadOptionMedia(e, index)" accept="image/*"
                                    class="text-xs text-gray-400 file:mr-2 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-medium file:bg-gray-700 file:text-gray-200 hover:file:bg-gray-600 cursor-pointer w-full" />
                                <div v-if="opt.media_url" class="flex items-center space-x-1 flex-shrink-0">
                                    <img :src="getMediaUrl(opt.media_url)" alt="Option Preview"
                                        class="h-9 w-9 rounded object-cover border border-gray-600" />
                                    <button @click="removeOptionMedia(index)" type="button"
                                        class="text-red-400 hover:text-red-300 text-xs p-1"
                                        title="Remove option image">✕</button>
                                </div>
                            </div>

                            <!-- Mark Correct (Single selection for non-ghost, disabled for ghost) -->
                            <div class="w-20 sm:w-24 flex items-center justify-center flex-shrink-0">
                                <span v-if="form.question_type === 'ghost'" class="text-xs text-purple-400 italic">
                                    All False
                                </span>
                                <label v-else class="flex items-center space-x-1.5 cursor-pointer select-none">
                                    <input type="radio" :name="'correct-option'" :checked="opt.is_correct"
                                        @change="setCorrectOption(index)"
                                        class="w-4 h-4 text-blue-600 focus:ring-0 cursor-pointer" />
                                    <span class="text-xs sm:text-sm font-medium"
                                        :class="opt.is_correct ? 'text-green-400 font-bold' : 'text-gray-400'">
                                        Correct
                                    </span>
                                </label>
                            </div>

                            <!-- Reserved Space for 'X' delete button (Always w-8 even if length <= 2) -->
                            <div class="w-8 flex items-center justify-center flex-shrink-0">
                                <button @click="removeOption(index)" v-if="form.options.length > 2" type="button"
                                    class="text-red-400 hover:text-red-300 hover:bg-red-900/40 p-1 rounded font-bold transition"
                                    title="Remove Option">
                                    ✕
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <button @click="saveQuestion" type="button"
                class="mt-6 w-full py-3 rounded-lg font-bold text-lg shadow-lg transition"
                :class="editingQuestionId ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-green-600 hover:bg-green-500 text-white'">
                {{ editingQuestionId ? 'Update Question' : 'Save Question' }}
            </button>
        </div>

        <!-- SEARCH BAR & SORT CONTROLS -->
        <div
            class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between mb-6 bg-gray-900/80 p-4 rounded-xl border border-gray-800 shadow-md">
            <div class="relative flex-1 max-w-lg">
                <span
                    class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 text-sm">
                    🔍
                </span>
                <input type="text" v-model="searchQuery" @input="handleSearchInput" placeholder="Search question"
                    class="w-full pl-10 pr-10 py-2.5 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 text-sm text-gray-200 outline-none transition placeholder-gray-500" />
                <button v-if="searchQuery" @click="clearSearch" type="button"
                    class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-xs text-gray-400 hover:text-white"
                    title="Clear search">
                    ✕
                </button>
            </div>

            <div class="flex items-center space-x-3 self-end sm:self-auto">
                <span v-if="isSearching" class="text-xs text-blue-400 animate-pulse font-medium">
                    Filtering...
                </span>
                <span v-else-if="debouncedSearchQuery" class="text-xs text-gray-400">
                    Matches: <strong class="text-blue-300">{{ totalMatchingQuestions }}</strong>
                </span>

                <!-- Sort Toggle Button -->
                <button @click="toggleSortOrder" type="button"
                    class="px-3.5 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs font-semibold text-gray-300 flex items-center space-x-1.5 transition flex-shrink-0"
                    title="Toggle table sort order by date">
                    <span>Sort:</span>
                    <span class="text-blue-400 font-bold">{{ sortOrder === 'desc' ? 'Most Recent ↓' : 'Oldest First ↑'
                        }}</span>
                </button>
            </div>
        </div>

        <!-- QUESTIONS TABLES (Grouped by Type) -->
        <div v-for="(group, type) in groupedQuestions" :key="type" class="mb-10">
            <div class="flex justify-between items-center border-b border-gray-700 pb-2 mb-3">
                <h3 class="text-2xl font-bold capitalize text-blue-300">
                    {{ type.replace('_', ' ') }} Questions
                </h3>
                <span class="text-xs font-semibold px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                    {{ group.length }} {{ group.length === 1 ? 'question' : 'questions' }}
                </span>
            </div>

            <div v-if="group.length === 0"
                class="text-gray-500 italic py-4 bg-gray-900/30 rounded-lg text-center border border-gray-800/50">
                No questions found.
            </div>

            <div v-else class="overflow-x-auto">
                <table
                    class="w-full text-left border-collapse bg-gray-900/50 rounded-lg overflow-hidden border border-gray-800">
                    <thead>
                        <tr class="bg-gray-800 text-gray-300 text-xs sm:text-sm select-none">
                            <th class="p-2.5 sm:p-3 text-center w-px whitespace-nowrap" title="Availability in game pool">Pool</th>
                            <th class="p-2.5 sm:p-3">Question</th>
                            <th class="p-2.5 sm:p-3 w-px whitespace-nowrap">Created</th>
                            <th class="p-2.5 sm:p-3 text-center w-px whitespace-nowrap">Options</th>
                            <th class="p-2.5 sm:p-3 text-center w-px whitespace-nowrap">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800 text-xs sm:text-sm">
                        <tr v-for="q in group" :key="q.id" class="hover:bg-gray-800/40 transition">

                            <!-- Lock / Game Pool Toggle (Minimum Width) -->
                            <td class="p-2.5 sm:p-3 text-center w-px whitespace-nowrap">
                                <button @click="toggleLock(q)" type="button"
                                    class="p-1 rounded text-base sm:text-lg transition hover:scale-125 focus:outline-none"
                                    :title="q.is_active ? 'In game pool. Click to lock (exclude from game).' : 'Locked (excluded from game). Click to unlock.'">
                                    {{ q.is_active ? '🔓' : '🔒' }}
                                </button>
                            </td>

                            <!-- Question Text (Flexible / Maximum Width) -->
                            <td class="p-2.5 sm:p-3 max-w-0" :title="q.text || '(No text)'">
                                <span class="truncate block font-medium text-gray-200">
                                    {{ q.text || '(No text)' }}
                                </span>
                            </td>

                            <!-- Created Timestamp (Minimum Width) -->
                            <td class="p-2.5 sm:p-3 text-xs font-mono text-gray-400 w-px whitespace-nowrap">
                                {{ formatDate(q.created_at) }}
                            </td>

                            <!-- Number of Options (Minimum Width) -->
                            <td class="p-2.5 sm:p-3 text-center font-mono text-gray-300 w-px whitespace-nowrap">
                                {{ q.options ? q.options.length : 0 }}
                            </td>

                            <!-- Actions (Minimum Width) -->
                            <td class="p-2.5 sm:p-3 text-center w-px whitespace-nowrap">
                                <div class="flex items-center justify-center space-x-1">
                                    <!-- Pencil icon to edit -->
                                    <button @click="startEdit(q)"
                                        class="p-1 text-blue-400 hover:text-blue-200 hover:bg-blue-900/40 rounded transition"
                                        title="Edit question">
                                        ✏️
                                    </button>
                                    <!-- Delete icon -->
                                    <button @click="deleteQuestion(q.id)"
                                        class="p-1 text-red-400 hover:text-red-200 hover:bg-red-900/40 rounded transition"
                                        title="Delete question">
                                        🗑️
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = '/api'
const SERVER_BASE = ''
const questions = ref([])
const editingQuestionId = ref(null)
const formError = ref('')

// Authentication state
const isAuthenticated = ref(sessionStorage.getItem('admin_authenticated') === 'true')
const passwordInput = ref('')
const authError = ref('')
const isCheckingPassword = ref(false)

const handleUnlock = async () => {
    if (!passwordInput.value) {
        authError.value = 'Please enter the password.'
        return
    }
    authError.value = ''
    isCheckingPassword.value = true
    try {
        const res = await fetch(`${API_BASE}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: passwordInput.value })
        })
        if (res.ok) {
            isAuthenticated.value = true
            sessionStorage.setItem('admin_authenticated', 'true')
            passwordInput.value = ''
            await fetchQuestions()
        } else {
            const data = await res.json().catch(() => ({}))
            authError.value = data.error || 'Incorrect password. Access denied.'
        }
    } catch (err) {
        authError.value = 'Unable to verify password. Please try again.'
    } finally {
        isCheckingPassword.value = false
    }
}

const handleLock = () => {
    isAuthenticated.value = false
    sessionStorage.removeItem('admin_authenticated')
    questions.value = []
    passwordInput.value = ''
    authError.value = ''
}

// Native file input DOM refs
const questionFileInput = ref(null)
const optionFileInputs = ref([])

const setOptionFileInput = (el, index) => {
    if (el) {
        optionFileInputs.value[index] = el
    }
}

// Search & Sort state
const searchQuery = ref('')
const debouncedSearchQuery = ref('')
const isSearching = ref(false)
let searchTimer = null
const sortOrder = ref('desc') // 'desc' = most recent first, 'asc' = oldest first

const defaultForm = () => ({
    question_type: 'basic',
    text: '',
    media_url: '',
    is_active: true,
    options: [
        { text: '', media_url: '', is_correct: true },
        { text: '', media_url: '', is_correct: false }
    ]
})

const form = ref(defaultForm())

const getMediaUrl = (url) => {
    if (!url) return ''
    return url.startsWith('http') ? url : `${SERVER_BASE}${url}`
}

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

// Search debouncing (1000ms)
const handleSearchInput = () => {
    isSearching.value = true
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
        debouncedSearchQuery.value = searchQuery.value.trim().toLowerCase()
        isSearching.value = false
    }, 1000)
}

const clearSearch = () => {
    searchQuery.value = ''
    debouncedSearchQuery.value = ''
    isSearching.value = false
    clearTimeout(searchTimer)
}

const toggleSortOrder = () => {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

// Filtered and Sorted Questions
const filteredQuestions = computed(() => {
    let list = [...questions.value]

    // Filter by text search
    if (debouncedSearchQuery.value) {
        list = list.filter(q => q.text && q.text.toLowerCase().includes(debouncedSearchQuery.value))
    }

    // Sort by created_at
    list.sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime()
        const dateB = new Date(b.created_at || 0).getTime()
        return sortOrder.value === 'desc' ? dateB - dateA : dateA - dateB
    })

    return list
})

const totalMatchingQuestions = computed(() => filteredQuestions.value.length)

// Group questions for the tables
const groupedQuestions = computed(() => {
    const groups = { basic: [], wrong: [], ghost: [], music_single: [] }
    filteredQuestions.value.forEach(q => {
        if (groups[q.question_type]) {
            groups[q.question_type].push(q)
        }
    })
    return groups
})

onMounted(() => {
    if (isAuthenticated.value) {
        fetchQuestions()
    }
})

const fetchQuestions = async () => {
    try {
        const res = await fetch(`${API_BASE}/questions`)
        questions.value = await res.json()
    } catch (error) {
        console.error("Error fetching questions", error)
    }
}

const handleTypeChange = () => {
    if (form.value.question_type === 'ghost') {
        form.value.options.forEach(opt => {
            opt.is_correct = false
        })
    } else {
        const hasCorrect = form.value.options.some(opt => opt.is_correct)
        if (!hasCorrect && form.value.options.length > 0) {
            form.value.options[0].is_correct = true
        }
    }
}

const setCorrectOption = (selectedIndex) => {
    form.value.options.forEach((opt, idx) => {
        opt.is_correct = (idx === selectedIndex)
    })
}

// Option array management
const addOption = () => {
    if (form.value.options.length < 5) {
        const shouldBeCorrect = form.value.question_type !== 'ghost' && !form.value.options.some(o => o.is_correct)
        form.value.options.push({ text: '', media_url: '', is_correct: shouldBeCorrect })
    }
}

const removeOption = (index) => {
    if (form.value.options.length > 2) {
        const wasCorrect = form.value.options[index].is_correct
        form.value.options.splice(index, 1)
        optionFileInputs.value.splice(index, 1)
        if (wasCorrect && form.value.question_type !== 'ghost' && form.value.options.length > 0) {
            form.value.options[0].is_correct = true
        }
    }
}

// File Upload helper
const uploadFile = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData })
    const data = await res.json()
    return data.url
}

const uploadQuestionMedia = async (event) => {
    const file = event.target.files[0]
    if (file) {
        try {
            const url = await uploadFile(file)
            form.value.media_url = url
        } catch (err) {
            formError.value = "Failed to upload file."
            if (questionFileInput.value) questionFileInput.value.value = ''
        }
    }
}

const removeQuestionMedia = () => {
    form.value.media_url = ''
    if (questionFileInput.value) {
        questionFileInput.value.value = ''
    }
}

const uploadOptionMedia = async (event, index) => {
    const file = event.target.files[0]
    if (file) {
        try {
            const url = await uploadFile(file)
            form.value.options[index].media_url = url
        } catch (err) {
            formError.value = "Failed to upload option image."
            if (optionFileInputs.value[index]) optionFileInputs.value[index].value = ''
        }
    }
}

const removeOptionMedia = (index) => {
    form.value.options[index].media_url = ''
    if (optionFileInputs.value[index]) {
        optionFileInputs.value[index].value = ''
    }
}

const clearAllFileInputs = () => {
    if (questionFileInput.value) {
        questionFileInput.value.value = ''
    }
    optionFileInputs.value.forEach(input => {
        if (input) input.value = ''
    })
}

// Quick toggle lock in table
const toggleLock = async (q) => {
    const oldState = q.is_active
    q.is_active = !q.is_active
    try {
        const res = await fetch(`${API_BASE}/questions/${q.id}/toggle-lock`, { method: 'PATCH' })
        if (!res.ok) {
            q.is_active = oldState
        }
    } catch (err) {
        q.is_active = oldState
        console.error("Error toggling lock:", err)
    }
}

const startEdit = (q) => {
    formError.value = ''
    clearAllFileInputs()
    editingQuestionId.value = q.id
    form.value = {
        question_type: q.question_type,
        text: q.text || '',
        media_url: q.media_url || '',
        is_active: q.is_active !== false,
        options: q.options.map(opt => ({
            text: opt.text || '',
            media_url: opt.media_url || '',
            is_correct: !!opt.is_correct
        }))
    }
    const el = document.getElementById('question-form')
    if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const cancelEdit = () => {
    editingQuestionId.value = null
    formError.value = ''
    clearAllFileInputs()
    form.value = defaultForm()
}

// Validation helper
const validateForm = () => {
    formError.value = ''

    if (form.value.options.length < 2 || form.value.options.length > 5) {
        formError.value = "Questions must have between 2 and 5 options."
        return false
    }

    // Option images consistency: If one option has an image, others need them aswell.
    const hasImages = form.value.options.map(opt => !!opt.media_url)
    if (hasImages.some(Boolean) && !hasImages.every(Boolean)) {
        formError.value = "If one option has an image, all options must have an image."
        return false
    }

    // Single correct option rule (not counting ghost)
    const correctCount = form.value.options.filter(opt => opt.is_correct).length
    if (form.value.question_type === 'ghost') {
        if (correctCount > 0) {
            formError.value = "Ghost questions cannot have any correct options."
            return false
        }
    } else {
        if (correctCount !== 1) {
            formError.value = "There must be exactly one correct option selected."
            return false
        }
    }

    return true
}

// Save or Update
const saveQuestion = async () => {
    if (!validateForm()) return

    const endpoint = editingQuestionId.value
        ? `${API_BASE}/questions/${editingQuestionId.value}`
        : `${API_BASE}/questions`
    const method = editingQuestionId.value ? 'PUT' : 'POST'

    try {
        const res = await fetch(endpoint, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form.value)
        })

        if (!res.ok) {
            const data = await res.json()
            formError.value = data.error || "Failed to save question."
            return
        }

        cancelEdit()
        await fetchQuestions()
    } catch (error) {
        formError.value = "Error saving question: " + error.message
    }
}

const deleteQuestion = async (id) => {
    if (!confirm('Are you sure you want to delete this question?')) return
    try {
        await fetch(`${API_BASE}/questions/${id}`, { method: 'DELETE' })
        if (editingQuestionId.value === id) {
            cancelEdit()
        }
        await fetchQuestions()
    } catch (error) {
        console.error("Error deleting question", error)
    }
}
</script>