from app.api.optimization import router as optimization_router
from fastapi import FastAPI

app = FastAPI(title='CampusFlow')

app.include_router(optimization_router)
