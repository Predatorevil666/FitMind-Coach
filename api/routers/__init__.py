from fastapi import APIRouter

from api.routers import auth, lab, meals, users, workouts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    workouts.router, prefix="/workouts", tags=["workouts"]
)
api_router.include_router(meals.router, prefix="/meals", tags=["meals"])
api_router.include_router(lab.router, prefix="/lab", tags=["lab_results"])
