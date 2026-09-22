import { io } from 'socket.io-client'

// In browser, connects through Vite's proxy (/socket.io) to the Flask backend
const socket = io({
    autoConnect: true,
    transports: ['websocket', 'polling']
})

export default socket

