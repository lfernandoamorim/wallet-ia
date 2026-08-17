"""
Ponto de entrada principal da aplicação FastAPI.
Inicializa o aplicativo e registra os roteadores da API.
"""

from fastapi import FastAPI
from app.domains.users.directive import router as users_router

app = FastAPI(title="Plataforma IA API")

app.include_router(users_router)

@app.get("/health")
def health_check():
    """
    Endpoint para verificação de integridade da aplicação.
    
    Returns:
        dict: O status da aplicação.
    """
    return {"status": "ok"}
