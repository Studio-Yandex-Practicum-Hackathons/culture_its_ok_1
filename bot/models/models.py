from datetime import datetime

from db.postgres import Base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class Route(Base):
    name = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)

    @property
    def objects(self):
        """Метод возвращает список активных объектов маршрута, проходя сквозь
        m2m таблицу."""
        return [
            _object.object
            for _object in self._objects if _object.object.is_active
        ]

    _objects = relationship('RouteObject', lazy="joined",
                            order_by='asc(RouteObject.object_priority)')

    def __repr__(self):
        return f'Маршрут ({self.name})'


class Object(Base):
    name = Column(String(255), nullable=False)
    author = Column(String(255))
    address = Column(String(255))
    how_to_get = Column(Text)
    is_active = Column(Boolean, default=False)

    @property
    def steps(self):
        """Метод возвращает список шагов объекта, проходя сквозь m2m
        таблицу."""
        return [_step.step for _step in self._steps]

    _steps = relationship('ObjectStep', lazy="joined",
                          order_by='asc(ObjectStep.step_priority)')

    def __repr__(self):
        return f'Объект ({self.name})'


class Step(Base):
    _TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
        ('continue_button', 'Кнопка продолжить'),
    ]
    _CHOICE_TO_TEXT = {_type: text for _type, text in _TYPE_CHOICES}

    type = Column(String(20), info={'choices': _TYPE_CHOICES},  # noqa: VNE003
                  nullable=False)
    content = Column(Text)
    photo = Column(String(255))
    delay_after_display = Column(Integer)

    def __repr__(self):
        to_show = f'{self._CHOICE_TO_TEXT[self.type]}: '
        to_show += str(self.photo) if self.photo else f'{self.content[:20]}...'
        return f'Шаг ({to_show})'


class RouteObject(Base):
    route_id = Column(ForeignKey('culture_route.id'), primary_key=True)
    object_id = Column(ForeignKey('culture_object.id'), primary_key=True)
    object_priority = Column(Integer, nullable=False)

    object = relationship("Object", lazy="joined")  # noqa: VNE003


class ObjectStep(Base):
    object_id = Column(ForeignKey('culture_object.id'), primary_key=True)
    step_id = Column(ForeignKey('culture_step.id'), primary_key=True)
    step_priority = Column(Integer, nullable=False, primary_key=True)

    step = relationship("Step", lazy="joined")


class User(Base):
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f'Пользователь ({self.name}:{self.age})'


class Progress(Base):
    user_id = Column(ForeignKey('culture_user.id'), primary_key=True)
    route_id = Column(ForeignKey('culture_route.id'), primary_key=True)
    object_id = Column(ForeignKey('culture_object.id'), primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    finished_at = Column(DateTime)


class Reflection(Base):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('voice', 'Голос'),
    ]

    user_id = Column(ForeignKey('culture_user.id'), primary_key=True)
    route_id = Column(ForeignKey('culture_route.id'), primary_key=True)
    object_id = Column(ForeignKey('culture_object.id'), primary_key=True)
    question = Column(Text, nullable=False)
    answer_type = Column(String(10), info={'choices': TYPE_CHOICES},
                         nullable=False)  # noqa: VNE003
    answer_content = Column(Text, nullable=False)
