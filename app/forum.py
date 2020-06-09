from flask_login import current_user
from app import db
from app.models import Group, UserGroup, Post, Thread

def validate_group_link(groupID):
    group = Group.query.filter_by(id=groupID).first_or_404()
    if UserGroup.query.filter_by(userID=current_user.id, groupID=groupID).first() is not None:
        return group

def save_post(form):
    post = Post(userID=current_user.id, threadID=threadID, 
                    timestamp=datetime.datetime.now(), 
                    title=form.title, content=form.post)
    db.session.add(post)
    db.session.commit()
       