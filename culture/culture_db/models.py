from django.db import models


class Route(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название маршрута')
    photo = models.ImageField(upload_to='photos', verbose_name='Фото маршрута')
    description = models.TextField(verbose_name='Описание маршрута')
    address = models.CharField(max_length=255, verbose_name='Адрес маршрута')
    welcome_message = models.TextField(
        verbose_name='Приветственное сообщение',
        blank=True,
        null=True
    )
    goodbye_message = models.TextField(
        verbose_name='Прощальное сообщение',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'
        ordering = ('-pk',)

    def __str__(self):
        return self.name


class Step(models.Model):
    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('reflection', 'Рефлексия'),
        ('continue_button', 'Кнопка продолжить'),
    ]

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут шага'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип шага'
    )
    content = models.TextField(
        verbose_name='Контент шага',
        blank=True,
        null=True
    )
    delay_after_display = models.IntegerField(
        verbose_name='Задержка после показа'
    )

    class Meta:
        verbose_name = 'Шаг'
        verbose_name_plural = 'Шаги'
        ordering = ('-pk',)

    def __str__(self):
        return self.type


class Object(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    author = models.CharField(max_length=255, verbose_name='Автор')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    how_to_get = models.TextField(verbose_name='Как добраться')

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class RouteObject(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Маршрут'
    )
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    object_priority = models.IntegerField(verbose_name='Приоритет')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        verbose_name = 'Путь к объекту'
        verbose_name_plural = 'Пути к объектам'

    def __str__(self):
        return self.route.name


class ObjectStep(models.Model):
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        verbose_name='Шаг'
    )
    step_priority = models.IntegerField(verbose_name='Приоритет шага')

    class Meta:
        verbose_name = 'Шаг к объекту'
        verbose_name_plural = 'Шаги к объектам'
        ordering = ('-step_priority',)

    def __str__(self):
        return self.object.name


class User(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    age = models.IntegerField(verbose_name='Возраст')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Progress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name='Путь'
    )
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время начала'
    )
    finished_at = models.DateTimeField(
        verbose_name='Время конца',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'Прогресс пользователей'
        ordering = ('-started_at',)

    def __str__(self):
        return self.user.name


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
        verbose_name='Путь'
    )
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='Тип'
    )
    content = models.TextField(verbose_name='Контент')

    class Meta:
        verbose_name = 'Рефлексия'
        verbose_name_plural = 'Рефлексия'

    def __str__(self):
        return self.user.name
