from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped, mapped_column
from flask import current_app
from datetime import datetime
from typing import List


class Base(DeclarativeBase):
    pass


class Passwords(Base):
    """
    Saves passwords - right now basically just the admin login password
    """
    __tablename__ = "passwords"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str]


class Shoot(Base):
    __tablename__ = "shoot"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str]
    description: Mapped[str]
    creation: Mapped[datetime]
    max_images: Mapped[int]  # max images to give a "keep" to (if we also accept unedited images, this is edited)
    done: Mapped[bool]
    unedited_images: Mapped[bool]  # Whether we can also choose unedited images
    max_unedited: Mapped[int]  # max unedited images to keep

    pictures: Mapped[List["Pictures"]] = relationship(back_populates="shoot", order_by="Pictures.filename")

    def done_state(self):
        if self.max_images == 0:
            # Case: No max images.
            # If everything is rated: "all"; Some are rated: "some"; None are rated: "none"
            status = "none"
            green_possible = True
            for pic in self.pictures:
                if pic.status is None:
                    green_possible = False
                else:
                    status = "some"
                if not green_possible and status == "some":
                    return status

            if status == "none":
                return "none"
            else:
                return "all"
        else:
            # Case: Max images.
            # If [max_images] are rated: "all", if some images are rated: "some"; if none are rated: "none"
            print(self.max_images)
            print(self.keep_count())
            if self.max_images == self.keep_count():
                return "all"
            elif self.unedited_images and \
                    (self.max_images == self.keep_count()['edited']) and \
                    (self.max_unedited == self.keep_count()['unedited']):
                return "all"
            elif self.keep_count() != 0:
                return "some"
            else:
                return "none"

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
        return f"ID: {self.id}, Shooting with link {self.link}"


class Pictures(Base):
    __tablename__ = "pictures"

    id: Mapped[int] = mapped_column(primary_key=True)
    shoot_id: Mapped[int] = mapped_column(ForeignKey('shoot.id'))
    filename: Mapped[str] = mapped_column(unique=True)
    star_rating: Mapped[int]
    status: Mapped[str]  # Keep/Don't keep
    comment: Mapped[str]

    shoot: Mapped[List["Shoot"]] = relationship(back_populates="pictures")

    def prev_pic(self):
        cur = self.shoot.pictures.index(self)
        if cur == 0:
            raise StopIteration
        else:
            return self.shoot.pictures[cur-1]
    
    def next_pic(self):
        cur = self.shoot.pictures.index(self)
        if cur == len(self.shoot.pictures)-1:
            raise StopIteration
        else:
            return self.shoot.pictures[cur+1]

    def prev_pic_link(self):
        try:
            return f"/{self.shoot.link}/{self.prev_pic().filename}/"
        except StopIteration:
            return f"/{self.shoot.link}/"

    def next_pic_link(self):
        try:
            return f"/{self.shoot.link}/{self.next_pic().filename}/"
        except StopIteration:
            return f"/{self.shoot.link}/"

    def __repr__(self):
        return f"ID: {self.id}, for shoot id: {self.shoot_id}"





def get_session():
    try:
        db_uri = current_app.config["DATABASE"]
    except:
        db_uri = 'sqlite:////app/data/rate.db'
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
