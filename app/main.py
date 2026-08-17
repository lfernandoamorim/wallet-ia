from fastapi import FastAPI
from app.domains.users.directive import router as users_router

app = FastAPI(title="Plataforma IA API")

app.include_router(users_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
