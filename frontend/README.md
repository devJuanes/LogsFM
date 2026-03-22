# Frontend logsfm.com

Frontend Next.js para la plataforma de radio.

## Instalación

```bash
npm install
npm run dev
```

## Estructura

```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
└── components/
    ├── Header.tsx
    ├── RadioPlayer.tsx
    ├── ListenerCount.tsx
    ├── ScheduleGrid.tsx
    ├── LiveChat.tsx
    └── ParticipateForm.tsx
```

## Variables de Entorno

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## Páginas

- `/` - Página principal con reproductor y programación
- `/schedule` - Programación completa
- `/participate` - Formulario de participación
- `/login` - Inicio de sesión
- `/register` - Registro de usuario

## Desarrollo

```bash
# Desarrollo
npm run dev

# Producción
npm run build
npm start
```
