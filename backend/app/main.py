from fastapi import FastAPI

from app.api.optimization import router as optimization_router

app = FastAPI(title="CampusFlow")

app.include_router(optimization_router)
