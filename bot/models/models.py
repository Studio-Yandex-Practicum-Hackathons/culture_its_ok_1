from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from db.postgres import Base


class Route(Base):
    name = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    welcome_message = Column(Text)
    goodbye_message = Column(Text)
    is_active = Column(Boolean, default=False)

    def __repr__(self):
        return f'Маршрут ({self.name})'


class Object(Base):
    name = Column(String(255))
    author = Column(String(255))
    address = Column(String(255), nullable=False)
    how_to_get = Column(Text)
    is_active = Column(Boolean, default=False)

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
    delay_after_display = Column(Integer, nullable=False)

    def __repr__(self):
        to_show = f'{self._CHOICE_TO_TEXT[self.type]}: '
        to_show += str(self.photo) if self.photo else f'{self.content[:20]}...'
        return f'Шаг ({to_show})'


class User(Base):
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f'Пользователь ({self.name}:{self.age})'


class Progress(Base):
    user_id = Column(ForeignKey('user.id'), primary_key=True)
    route_id = Column(ForeignKey('route.id'), primary_key=True)
    object_id = Column(ForeignKey('object.id'), primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    finished_at = Column(DateTime)


class Reflection(Base):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('voice', 'Голос'),
    ]

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    route_id = Column(ForeignKey('route.id'), primary_key=True)
    object_id = Column(ForeignKey('object.id'), primary_key=True)
    question = Column(Text, nullable=False)
    answer_type = Column(String(10), info={'choices': TYPE_CHOICES},  # noqa: VNE003
                         nullable=False)
    answer_content = Column(Text, nullable=False)

