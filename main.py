import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import setting
from src.worker.celery_worker import celery_app
# from src.config.mqtt_client import start_mqtt
from src.app.plc_module.router import router


app = FastAPI(
    title=setting.TITLE,
    docs_url="/plc" if setting.DEBUG else None,
    debug=setting.DEBUG,
)
celery = celery_app

app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/plc", tags=["Plc"])
# @app.on_event("startup")
# def startup_event():
#     start_mqtt()



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(setting.HOST_PORT), reload=True)
