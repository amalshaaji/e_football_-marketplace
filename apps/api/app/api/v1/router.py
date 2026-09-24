from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.accounts.routes import router as accounts_router
from app.listings.routes import router as listings_router
from app.orders.routes import router as orders_router
from app.favorites.routes import router as favorites_router
from app.engagement.routes import router as engagement_router
from app.admin.routes import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(accounts_router, prefix="/users/me", tags=["users and accounts"])
api_router.include_router(listings_router, prefix="/listings", tags=["marketplace listings"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders and payments"])
api_router.include_router(favorites_router, prefix="/favorites", tags=["favorites"])
api_router.include_router(engagement_router, prefix="/engagement", tags=["reviews and messaging"])
api_router.include_router(admin_router, prefix="/admin", tags=["administration"])
