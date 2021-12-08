#import libraries
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind = engine)

#instantiate the app
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

#define the root path
@app.get("/")

#define the function
async def root():
    return {"message": "Hello World"}

# #test the database connection
# @app.get("/sqlalchemy")
# async def test_posts(db: Session = Depends(get_db)):
#     post = db.query(models.Post).all()
#     # post = db.query(model.Post) -> returns a query object( select post.id as post_id, post.title as post_title, post.content as post_content, post.published as post_published, post.created_at as post_created_at from post)
#     return {"data": post}

# @app.get("/items")
# async def get_items():
#     return {"1": "item1", "2": "item2"}

# #no async in post method
# #import Body from fastapi.params

# my_posts = [{"title":"favourite foods", "content":"i like fruits", "id": 2}]



