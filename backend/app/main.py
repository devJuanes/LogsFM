from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, episodes, chat, participation, stream, websocket
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Radio API",
    description="Backend API for radio platform logsfm.com",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(episodes.router)
app.include_router(chat.router)
app.include_router(participation.router)
app.include_router(stream.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "radio": "Radio API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/api/status")
def api_status():
    return {"status": "operational", "api": "running"}


@app.get("/health")
def health():
    return {"health": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
