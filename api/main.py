from fastapi import FastAPI
from routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)