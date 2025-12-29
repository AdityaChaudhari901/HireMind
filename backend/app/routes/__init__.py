from app.routes.auth import router as auth_router
from app.routes.questions import router as questions_router
from app.routes.test import router as test_router
from app.routes.results import router as results_router

__all__ = [
    "auth_router",
    "questions_router", 
    "test_router",
    "results_router"
]
