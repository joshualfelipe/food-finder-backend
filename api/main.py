from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.router_loader import register_routers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(app)


@app.get("/")
async def root():
    return {"message": "API is running"}
