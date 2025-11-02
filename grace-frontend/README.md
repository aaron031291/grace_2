# Grace Frontend

React + TypeScript + Vite frontend for Grace autonomous assistant.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Visit http://localhost:5173

## Routes

- `/` - Main chat interface (OrbInterface)
- `/test` - Backend connection test

## Features

- **Login/Auth** - Token-based authentication with localStorage
- **Chat Interface** - Real-time chat with Grace backend
- **Connection Test** - Health check for backend connectivity

## Backend Requirements

The frontend expects the backend to be running at `http://localhost:8000` with these endpoints:

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /chat` - Send message to Grace
- `GET /health` - Health check

## Environment

Make sure the Grace backend is running:

```bash
cd ..
python main.py
```

## Testing the Flow

1. Start backend: `python main.py` (from root directory)
2. Start frontend: `npm run dev` (from grace-frontend directory)
3. Visit http://localhost:5173/test to verify backend connection
4. Visit http://localhost:5173 and login with your credentials
5. Start chatting with Grace!

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- Axios
