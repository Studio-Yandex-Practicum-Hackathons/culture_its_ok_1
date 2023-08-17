from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db_base_settings import Base


class Route(Base):
    name = Column(String(255), nullable=False)
    photo = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    welcome_message = Column(Text)
    goodbye_message = Column(Text)
    is_active = Column(Boolean, default=True)

    steps = relationship('Step', backref='route')

    def __str__(self):
        return self.name


class Step(Base):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
        ('continue_button', 'Кнопка продолжить'),
    ]

    type = Column(String(20), info={'choices': TYPE_CHOICES}, nullable=False)
    content = Column(Text)
    delay_after_display = Column(Integer, nullable=False)

    route_id = Column(Integer, ForeignKey('route.id'))

    def __str__(self):
        return self.type


class Object(Base):
    name = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    how_to_get = Column(Text, nullable=False)

    route_objects = relationship('RouteObject', backref='object')
    object_steps = relationship('ObjectStep', backref='object')

    def __str__(self):
        return self.name


class RouteObject(Base):
    object_priority = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    route_id = Column(Integer, ForeignKey('route.id'))
    object_id = Column(Integer, ForeignKey('object.id'))

    def __str__(self):
        return self.route_id.name


class ObjectStep(Base):
    step_priority = Column(Integer, nullable=False)

    object_id = Column(Integer, ForeignKey('object.id'))
    step_id = Column(Integer, ForeignKey('step.id'))

    def __str__(self):
        return self.object_id.name


class User(Base):
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)

    progresses = relationship('Progress', backref='user')
    reflections = relationship('Reflection', backref='user')

    def __str__(self):
        return self.name


class Progress(Base):
    user_id = Column(Integer, ForeignKey('user.id'))
    route_id = Column(Integer, ForeignKey('route.id'))
    object_id = Column(Integer, ForeignKey('object.id'))

    def __str__(self):
        return self.user_id.name


class Reflection(Base):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('voice', 'Голос'),
    ]

    type = Column(String(10), info={'choices': TYPE_CHOICES}, nullable=False)
    content = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    route_id = Column(Integer, ForeignKey('route.id'))
    object_id = Column(Integer, ForeignKey('object.id'))

    def __str__(self):
        return self.user_id.name
