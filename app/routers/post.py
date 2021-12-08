from fastapi import Response, status, HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.sql.functions import func
from ..import schemas, models, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(new_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post_dict = new_post.dict()
    # post_dict["id"] = randrange(0 ,100000)
    # my_posts.append(post_dict)

    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ",(new_post.title,new_post.content, new_post.published))
    # post = cursor.fetchone()
    # conn.commit()
    # return {"data": post}

    post = models.Post(owner_id=current_user.id, **new_post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# title str, content str, category str
@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = "", limit: int = 10, skip: int = 0):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # print(posts)

    # post = db.query(models.Post).filter(
    #     models.Post.owner_id == current_user.id).all()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # if not post:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="No posts created")

    return post


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # for post in my_posts:
    #     if post["id"] == id:
    #         return {"data": post}

    # cursor.execute("SELECT * FROM  posts WHERE id = %s", (str(id),))
    # post = cursor.fetchone()

    # post_query = db.query(models.Post).filter(models.Post.id == id)
    # post = post_query.first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return post

# def find_index_post(id):
#     for index, post in enumerate(my_posts):
#         if post["id"] == id:
#             return index
#         return None


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # for post in my_posts:
    #     if post["id"] == id:
    #         my_posts.remove(post)
    #         return Response(status_code = status.HTTP_204_NO_CONTENT)
    # raise HTTPException(status_code =  status.HTTP_404_NOT_FOUND, detail = "Post not found")

    # index = find_index_post(id)
    # print(index)
    # if index is None:
    #     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with {id} does not exist")
    # my_posts.pop(index)
    # return Response(status_code = status.HTTP_204_NO_CONTENT)
    # cursor.execute("DELETE FROM posts WHERE id= %s RETURNING *",(str(id),))
    # post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post  with {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this post")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
async def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # index = find_index_post(id)
    # if index is None:
    #     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = f"post with {id} does not exist")
    # print(post.dict())
    # post_dict = post.dict()
    # post_dict["id"] = id
    # my_posts[index] = post_dict

    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * ",(post.title, post.content, post.published, str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    # print(post)

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this post")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
