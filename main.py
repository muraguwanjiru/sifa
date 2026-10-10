from fastapi import FastAPI
from database import Base, engine
from app.routers.user import router as user_router
from app.routers.device import router as device_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIFA API", version="1")

app.include_router(user_router)
app.include_router(device_router)

@app.get("/")
def read_root():
    return {"status": "online"}
