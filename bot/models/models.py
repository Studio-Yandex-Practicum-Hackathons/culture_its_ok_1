from datetime import datetime

from db.postgres import Base
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship


class Route(Base):
    name = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)

    @property
    def stages(self):
        """Метод возвращает список активных этапов маршрута, проходя сквозь
        m2m таблицу."""
        return [
            _stage.stage
            for _stage in self._stages if _stage.stage.is_active
        ]

    _stages = relationship('RouteStage', lazy="joined",
                           order_by='asc(RouteStage.stage_priority)')

    def __repr__(self):
        return f'Маршрут ({self.name})'


class Stage(Base):
    name = Column(String(255), nullable=False)
    address = Column(String(255))
    how_to_get = Column(Text)
    is_active = Column(Boolean, default=False)

    @property
    def steps(self):
        """Метод возвращает список шагов этапа, проходя сквозь m2m таблицу."""
        return [_step.step for _step in self._steps]

    _steps = relationship('StageStep', lazy="joined",
                          order_by='asc(StageStep.step_priority)')

    def __repr__(self):
        return f'Этап ({self.name})'


class Step(Base):
    _TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
        ('quiz', 'Квиз'),
        ('continue_button', 'Кнопки'),
    ]
    _CHOICE_TO_TEXT = {_type: text for _type, text in _TYPE_CHOICES}

    type = Column(String(20), info={'choices': _TYPE_CHOICES},  # noqa: VNE003
                  nullable=False)
    content = Column(Text)
    photo = Column(String(255))
    delay_after_display = Column(Integer)

    def __repr__(self):
        to_show = f'{self._CHOICE_TO_TEXT[self.type]}: '
        to_show += str(self.photo) if self.photo else f'{self.content[:25]}...'
        return f'Шаг ({to_show})'

    def to_dict(self):
        return dict(
            type=self.type,
            content=self.content,
            photo=self.photo,
            delay_after_display=self.delay_after_display
        )


class RouteStage(Base):
    route_id = Column(ForeignKey('culture_route.id'), primary_key=True)
    stage_id = Column(ForeignKey('culture_stage.id'), primary_key=True)
    stage_priority = Column(Integer, nullable=False)

    stage = relationship("Stage", lazy="joined")  # noqa: VNE003


class StageStep(Base):
    stage_id = Column(ForeignKey('culture_stage.id'), primary_key=True)
    step_id = Column(ForeignKey('culture_step.id'), primary_key=True)
    step_priority = Column(Integer, nullable=False, primary_key=True)

    step = relationship("Step", lazy="joined")


class User(Base):
    id = Column(BigInteger, primary_key=True)  # noqa: VNE003
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    interests = Column(String(255))

    def __repr__(self):
        return f'Пользователь ({self.name}:{self.age})'


class Progress(Base):
    user_id = Column(ForeignKey('culture_user.id'))
    route_id = Column(ForeignKey('culture_route.id'))
    stage_id = Column(ForeignKey('culture_stage.id'))
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    finished_at = Column(DateTime)
    rating = Column(Integer)


class Reflection(Base):
    user_id = Column(ForeignKey('culture_user.id'))
    route_id = Column(ForeignKey('culture_route.id'))
    stage_id = Column(ForeignKey('culture_stage.id'))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    voice = Column(String(255))
