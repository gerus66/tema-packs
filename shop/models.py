# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from tinymce import models as tinymce_models
from sorl.thumbnail import default
from datetime import date

class Common(models.Model):
    created = models.DateTimeField('Создан', auto_now_add=True, editable=False)
    changed = models.DateTimeField('Изменен', auto_now=True, editable=False)
    changed_by = models.ForeignKey(User, blank=True, null=True, editable=False)
    class Meta:
        abstract = True
        ordering = ['-changed']
        get_latest_by = 'changed'

class Option(Common):
    name = models.CharField('Имя', max_length = 200,unique=True)
    class Meta(Common.Meta):
        verbose_name = u'Свойство'
        verbose_name_plural = u'Свойства'
    def __unicode__(self):
        return self.name

class Info(Common):
    name = models.CharField(u'Название', max_length = 200)
    value = models.CharField(u'Значение', max_length = 200)
    code = models.CharField(u'Код', max_length = 20, help_text=u'Код для доступа из шаблона, A-z0-9')
    class Meta(Common.Meta):
        verbose_name = u'Элемент'
        verbose_name_plural = u'Элементы'
    def __unicode__(self):
        return self.name

class Action(Common):
    name = models.CharField(u'Название', max_length = 200)
    start = models.DateField(u'Начало')
    end = models.DateField(u'Конец', blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Акция'
        verbose_name_plural = u'Акции'
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/action/%i/" % self.id

class Brand(Common):
    name = models.CharField(u'Название',max_length = 20, unique=True)
    prefix = models.CharField(u'Префикс',max_length = 2, unique=True)
    yandex = models.BooleanField(u'В Яндекс')
    sites = models.ManyToManyField(Site, verbose_name=u'Сайты', blank=True, null=True)
    action = models.ForeignKey(Action, related_name='brands', verbose_name=u'Акции', blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Бренд'
        verbose_name_plural = u'Бренды'
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/catalog/brand/%i/" % self.id

class Category(Common):
    name = models.CharField(u'Название',max_length = 50, unique=True)
    parent = models.ForeignKey('self', verbose_name=u'Принадлежит', blank=True, null=True, related_name='child_set')
    yandex = models.BooleanField(u'В Яндекс')
    not_in_path = models.BooleanField(u'Не ставить в путь')
    sites = models.ManyToManyField(Site, verbose_name=u'Сайты', blank=True, null=True)
    action = models.ForeignKey(Action, verbose_name=u'Акции', related_name='categories',blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Категория'
        verbose_name_plural = u'Категории'
    def __unicode__(self):
        name = self.name
        if self.parent :
            name = self.parent.name + ': ' + name
        return name
    def get_absolute_url(self):
        return "/catalog/category/%i/" % self.id

class Good(Common):
    name = models.CharField(u'Название',max_length = 200)
    art = models.CharField(u'Артикул',max_length = 50,unique=True)
    desc = tinymce_models.HTMLField(u'Описание')
    characteristic = models.ManyToManyField(Option, through='Char', verbose_name=u'Характеристики')
    brand = models.ForeignKey(Brand, verbose_name=u'Бренд', related_name='goods')
    category = models.ForeignKey(Category, verbose_name=u'Категория', related_name='goods')
    new = models.BooleanField(u'Новинка')
    old = models.BooleanField(u'Старая коллекция')
    price = models.IntegerField(u'Цена')
    old_price = models.IntegerField(u'Старая цена', blank=True, null=True)
    available = models.BooleanField(u'В наличии')
    related = models.ManyToManyField('self', verbose_name=u'Связанные товары', symmetrical=False, blank=True, null=True, related_name='related_set')
    action = models.ForeignKey(Action, verbose_name=u'Акции', related_name='goods', blank=True, null=True)
    sites = models.ManyToManyField(Site, verbose_name=u'Сайты', blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Товар'
        verbose_name_plural = u'Товары'
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/catalog/%i/" % self.id

class Char(Common):
    good = models.ForeignKey(Good, verbose_name=u'Товар', related_name='chars_set')
    option = models.ForeignKey(Option, verbose_name=u'Свойство')
    value = models.CharField(u'Значение', max_length = 50)
    art_code = models.CharField(u'Как кодируется в артикуле', help_text=u'Часть артикула, отвечающая за это свойство', max_length = 10, blank=True, null=True)
    is_another_art = models.BooleanField(u'Другой артикул', help_text=u'Отметить если характеристика соответствует совсем другому артикулу')
    class Meta(Common.Meta):
        verbose_name = u'Характеристика'
        verbose_name_plural = u'Характеристики'
    def __unicode__(self):
        return self.option.name

class Article(Common):
    name = models.CharField(u'Название',max_length = 200)
    abstract = tinymce_models.HTMLField(u'Абстракт')
    goods = models.ManyToManyField(Good, verbose_name=u'Относится к товарам', related_name='articles', blank=True, null=True)
    brands = models.ManyToManyField(Brand, verbose_name=u'Относится к брендам', related_name='articles', blank=True, null=True)
    categories = models.ManyToManyField(Category, verbose_name=u'Относится к категориям', related_name='articles', blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Статья'
        verbose_name_plural = u'Статьи'
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/%i/" % self.id

class Text(Common):
    title = models.CharField(u'Заголовок',max_length = 200)
    body = tinymce_models.HTMLField(u'Текст')
    on_main_page = models.BooleanField(u'На главной')
    rel = models.PositiveIntegerField(u'Позиция', blank=True, null=True)
    position = models.PositiveSmallIntegerField(u'Расположение', blank=True, null=True, choices=((0,u'Левая колонка'),(1,u'Центр'),(2,u'Правая колонка')))
    article = models.ForeignKey(Article, related_name='texts', blank=True, null=True)
    action = models.ForeignKey(Action, related_name='texts', blank=True, null=True)
    brand = models.ForeignKey(Brand, related_name='texts', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='texts', blank=True, null=True)
    class Meta(Common.Meta):
        verbose_name = u'Текст'
        verbose_name_plural = u'Тексты'
        ordering = ['rel']
    def __unicode__(self):
        return self.title

class Image(Common):
    title = models.CharField(u'Название',max_length = 200, blank=True)
    good = models.ForeignKey(Good, blank=True, null=True)
    text = models.ForeignKey(Text, related_name='images', blank=True, null=True)
    article = models.ForeignKey(Article, related_name='images', blank=True, null=True)
    action = models.ForeignKey(Action, related_name='images', blank=True, null=True)
    brand = models.ForeignKey(Brand, related_name='images', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='images', blank=True, null=True)
    height = models.IntegerField(u'Высота')
    width = models.IntegerField(u'Ширина')
    photo = models.ImageField(u'Файл', upload_to='i',height_field='height', width_field='width')
    rel = models.PositiveIntegerField(u'Позиция', blank=True, null=True)
    def delete(self, *args, **kwargs):
        super(Image, self).delete(*args, **kwargs)
        default.backend.delete(self)
    class Meta(Common.Meta):
        ordering = ['rel']
        verbose_name = u'Картинка'
        verbose_name_plural = u'Картинки'

class Order(Common):
    status = models.PositiveSmallIntegerField(u'Статус', default=0, choices=((0,u'Новый'),(1,u'Согласован'),(2,u'В доставке'),(3,u'Доставлен'),(4,u'Отменен'),(5,u'Возврат')))
    goods = models.ManyToManyField(Good, verbose_name=u'Товары', through='Basket')
    total = models.PositiveIntegerField(u'Всего')
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='customer')
    user_comment = models.TextField(u'Комментарий', blank=True)
    staff_comment = models.TextField(u'Пометки', default='', blank=True)
    delivery = models.PositiveSmallIntegerField(u'Доставка', default=0, choices=((0,u'Курьер'),(1,u'Почта'),(2,u'СПСР-Экспресс'),(3,u'EMS')))
    class Meta(Common.Meta):
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'
        ordering = ['status','-changed','-created']
    def __unicode__(self):
        return u'Заказ № %i' % self.id

class Basket(Common):
    order = models.ForeignKey(Order, verbose_name=u'Заказ')
    good = models.ForeignKey(Good, verbose_name=u'Товар')
    qty = models.PositiveIntegerField(u'Количество')
    total = models.PositiveIntegerField(u'Цена')
    class Meta(Common.Meta):
        verbose_name = u'Товар'
        verbose_name_plural = u'Товары'
    def __unicode__(self):
        return "%s (%i * %i = %i)" % (self.good.name, self.good.price, self.qty, self.total)
    def get_absolute_url(self):
        return "/catalog/%i/" % self.good.id
    def good_price(self):
        return self.good.price
    def get_total(self):
        return self.good.price * self.qty

class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=u'Пользователь')
    middlename = models.CharField(u'Отчество',max_length = 200, blank=True)
    phone = models.CharField(u'Телефон',max_length = 20)
    address = models.TextField(u'Адрес')
    card_number = models.BigIntegerField(u'Номер карточки')
    card_procent = models.IntegerField(u'Скидка, %')
