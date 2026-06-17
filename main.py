from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import auth_routes, sync_routes, profile_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BabyTime API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(sync_routes.router)
app.include_router(profile_routes.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "BabyTime API is running"}
