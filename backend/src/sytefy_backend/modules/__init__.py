from fastapi import APIRouter

from sytefy_backend.modules.auth.web.router import router as auth_router
from sytefy_backend.modules.customers.web.router import router as customers_router
from sytefy_backend.modules.users.web.router import router as users_router
from sytefy_backend.modules.appointments.web.router import router as appointments_router
from sytefy_backend.modules.services.web.router import router as services_router
from sytefy_backend.modules.notifications.web.router import router as notifications_router
from sytefy_backend.modules.finances.web.router import router as finances_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(users_router)
api_router.include_router(appointments_router)
api_router.include_router(services_router)
api_router.include_router(notifications_router)
api_router.include_router(finances_router)

__all__ = ["api_router"]
