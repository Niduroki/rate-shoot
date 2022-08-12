from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask import current_app

Base = declarative_base()


class Passwords(Base):
    """
    Saves passwords - right now basically just the admin login password
    """
    __tablename__ = "passwords"
    
    id = Column(Integer, primary_key=True)
    password = Column(String)


class Shoot(Base):
    __tablename__ = "shoot"

    id = Column(Integer, primary_key=True)
    link = Column(String)
    description = Column(String)
    creation = Column(DateTime)
    max_images = Column(Integer)  # max images to give a "keep" to (if we also accept unedited images, this is edited)
    done = Column(Boolean)
    unedited_images = Column(Boolean)  # Whether we can also choose unedited images
    max_unedited = Column(Integer)  # max unedited images to keep

    def keep_count(self):
        if self.unedited_images:
            count = {'edited': 0, 'unedited': 0}
            for pic in self.pictures:
                if pic.status == "yes_edited":
                    count['edited'] += 1
                elif pic.status == "yes_unedited":
                    count['unedited'] += 1
        else:
            count = 0
            for pic in self.pictures:
                if pic.status == "yes":
                    count += 1
        return count

    def uncertain_count(self):
        count = 0
        for pic in self.pictures:
            if pic.status == "unsafe":
                count += 1
        return count

    def __repr__(self):
        return f"ID: {self.id}, Shooting with link {self.link}, Done = {self.done}"


class Pictures(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    shoot_id = Column(Integer, ForeignKey('shoot.id'))
    filename = Column(String, unique=True)
    star_rating = Column(Integer)
    status = Column(String)  # Keep/Don't keep
    comment = Column(String)

    shoot = relationship("Shoot", back_populates="pictures")
    
    def next_pic(self):
        cur = self.shoot.pictures.index(self)
        if cur == len(self.shoot.pictures)-1:
            raise StopIteration
        else:
            return self.shoot.pictures[cur+1]

    def next_pic_link(self):
        try:
            return f"/{self.shoot.link}/{self.next_pic().filename}/"
        except StopIteration:
            return f"/{self.shoot.link}/"

    def __repr__(self):
        return f"ID: {self.id}, for shoot id: {self.shoot_id}"


Shoot.pictures = relationship("Pictures", back_populates="shoot", order_by="Pictures.filename")


def get_session():
    try:
        db_uri = current_app.config["DATABASE"]
    except:
        db_uri = 'sqlite:////app/data/rate.db'
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
