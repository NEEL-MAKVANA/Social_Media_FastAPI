from fastapi import FastAPI
from src.routers.user import auth_router
from src.routers.follower_following import follower_following_router
from src.routers.post import post_router
from src.routers.story import story_router



app = FastAPI(title="User Authentication System")

app.include_router(auth_router)
app.include_router(follower_following_router)
app.include_router(post_router)
app.include_router(story_router)




