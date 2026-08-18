# Frontend - Movie Discovery Platform

React (Vite) + Tailwind CSS + React Router + Axios.

## Structure

```
src/
  components/   reusable UI pieces (Navbar, MovieCard, MovieGrid, etc.)
  pages/        one file per route
  services/     Axios calls to the backend, grouped by feature
  context/      AuthContext - global auth state
```

## How it talks to the backend

`src/services/api.js` holds one Axios instance. A request interceptor
attaches the JWT from `localStorage` to every call. A response interceptor
catches 401s and redirects to `/login`. Every other service file
(`authService.js`, `movieService.js`, `userService.js`) just calls
`api.get/post/delete` - no file besides `api.js` knows about tokens.

## Run

```bash
npm install
cp .env.example .env   # points VITE_API_BASE_URL at the backend
npm run dev
```

Runs at http://localhost:5173. Requires the backend running at
http://localhost:8000 (see backend/README.md).
