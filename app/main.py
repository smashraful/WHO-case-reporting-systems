from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.info import router as info_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.user import router as user_router
from app.api.v1.routers.locations import router as locations_router
from app.api.v1.routers.patients import router as patients_router
from app.api.v1.routers.cases import router as cases_router
from app.api.v1.routers.lab_results import router as lab_results_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(info_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(locations_router)
app.include_router(patients_router)
app.include_router(cases_router)
app.include_router(lab_results_router)


@app.get("/")
def root():
    return {"message": "WHO case reporting api"}
