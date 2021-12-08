from fastapi import APIRouter, Response, status, Depends, HTTPException
from ..import schemas, database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(prefix="/vote", tags=["Vote"])

@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Vote)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Vote for a post
    """
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if (vote.dir ==1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already voted for this post")
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote added"}

    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesn't exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Vote deleted"}
