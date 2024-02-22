from fastapi import FastAPI
from routers.user import auth_router


app = FastAPI(title="User Authentication System")

app.include_router(auth_router)
