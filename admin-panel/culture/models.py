from django.db import models
from PIL import Image

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


class Object(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Автор',
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
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Step(models.Model):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
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
        ordering = ('-pk',)

    def __str__(self):
        to_show = f'{self.CHOICE_TO_TEXT[self.type]}: '
        to_show += str(self.photo) if self.photo else f'{self.content[:20]}...'
        return to_show
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        SIZE= 300,300
        if self.photo:
            image=Image.open(self.photo.path)
            image.thumbnail(SIZE,Image.LANCZOS)
            image.save(self.photo.path)   

class RouteObject(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут'
    )
    object = models.ForeignKey(  # noqa: VNE003
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    object_priority = models.IntegerField(
        verbose_name='Приоритет объекта'
    )

    class Meta:
        ordering = ('object_priority',)

    def __str__(self):
        return self.object.name


class ObjectStep(models.Model):
    object = models.ForeignKey(  # noqa: VNE003
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
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
    id = models.IntegerField(  # noqa: VNE003
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    age = models.IntegerField(
        verbose_name='Возраст'
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
    object = models.ForeignKey(  # noqa: VNE003
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
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


class Reflection(models.Model):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('voice', 'Голос'),
    ]

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
    object = models.ForeignKey(  # noqa: VNE003
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    question = models.TextField(
        verbose_name='Вопрос бота'
    )
    answer_type = models.CharField(  # noqa: VNE003
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='Тип ответа'
    )
    answer_content = models.TextField(
        verbose_name='Содержимое ответа'
    )
