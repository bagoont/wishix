from fastapi import APIRouter

from app.api.routers import login, reservations, users, wishes, wishlists

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(wishlists.router, prefix="/wishlists", tags=["wishlists"])
api_router.include_router(wishes.router, prefix="/wishlists/{wishlist_id}/wishes", tags=["wishes"])
api_router.include_router(
    reservations.router,
    prefix="/wishlists/{wishlist_id}/wishes/{wish_id}/reservation",
    tags=["reservations"],
)
