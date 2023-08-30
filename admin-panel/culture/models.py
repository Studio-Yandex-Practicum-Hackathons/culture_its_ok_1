from culture.utils import resize_photo
from django.db import models


class Route(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    photo = models.ImageField(
        upload_to='photos',
        verbose_name='Обложка'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес начала'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'
        ordering = ('pk',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            resize_photo(self.photo.path)


class Stage(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Адрес',
    )
    how_to_get = models.TextField(
        blank=True,
        null=True,
        verbose_name='Как добраться',
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Step(models.Model):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
        ('quiz', 'Квиз'),
        ('continue_button', 'Кнопки'),
    ]

    CHOICE_TO_TEXT = {_type: text for _type, text in TYPE_CHOICES}

    type = models.CharField(  # noqa: VNE003
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип шага'
    )
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текстовое содержимое',
    )
    photo = models.ImageField(
        upload_to='photos',
        blank=True,
        null=True,
        verbose_name='Фотография'
    )
    delay_after_display = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Задержка после показа',
    )

    class Meta:
        verbose_name = 'Шаг'
        verbose_name_plural = 'Шаги'
        ordering = ('-type',)

    def __str__(self):
        to_show = f'{self.CHOICE_TO_TEXT[self.type]}: '
        to_show += str(self.photo) if self.photo else f'{self.content[:25]}...'
        return to_show

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            resize_photo(self.photo.path)


class RouteStage(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут'
    )
    stage = models.ForeignKey(  # noqa: VNE003
        Stage,
        on_delete=models.CASCADE,
        verbose_name='Этап'
    )
    stage_priority = models.IntegerField(
        verbose_name='Приоритет этапа'
    )

    class Meta:
        ordering = ('stage_priority',)

    def __str__(self):
        return self.stage.name


class StageStep(models.Model):
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        verbose_name='Этап'
    )
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        verbose_name='Шаг'
    )
    step_priority = models.IntegerField(
        verbose_name='Приоритет шага'
    )

    class Meta:
        ordering = ('step_priority',)

    def __str__(self):
        if self.step.content:
            return f'{self.step.content[:50]}...'
        return str(self.step.photo)


class User(models.Model):
    id = models.BigIntegerField(  # noqa: VNE003
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    age = models.IntegerField(
        verbose_name='Возраст'
    )
    hobbies = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Интересы'
    )


class Progress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут'
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        verbose_name='Этап'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время начала'
    )
    finished_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Время окончания',
    )
    rating = models.IntegerField(
        verbose_name='Оценка маршрута пользователем',
        blank=True,
        null=True,
    )


class Reflection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут'
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        verbose_name='Этап'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рефлексии'
    )
    question = models.TextField(
        verbose_name='Вопрос для рефлексии'
    )
    answer = models.TextField(
        verbose_name='Текстовое содержимое рефлексии',
        blank=True,
        null=True,
    )
    voice = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Аудиофайл рефлексии'
    )
