# -*- coding: utf-8 -*-
from shop.models import Good,Brand,Category,Image,Article,Action,Text,Order,Basket,Common,Info,Option,Char,UserProfile
from django.contrib import admin

class Common(admin.ModelAdmin):
    date_hierarchy = 'changed'
    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        obj.save()

class CommonTabularInline(admin.TabularInline):
    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        obj.save()

class CommonStackedInline(admin.StackedInline):
    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        obj.save()

class OptionAdmin(Common):
    model = Option

class CharInline(CommonTabularInline):
    model = Char
    extra = 3

class BasketInline(CommonTabularInline):
    fields = ['good', 'qty', 'total']
    model = Basket
    extra = 1

class ImageInline(CommonTabularInline):
	fields = ['title', 'rel', 'photo']
	model = Image
	extra = 1

class TextForMain(Common):
    model = Text
    fields = ['title', 'body', 'position', 'rel']
    inlines = [ImageInline]

class TextInline(CommonStackedInline):
    fields = ['title', 'body']
    model = Text
    extra = 1

class ArticleAdmin(Common):
    model = Article
    list_display = ('name',)
    list_filter = ('goods', 'brands', 'categories')
    search_fields = ('^name','@abstract')
    fieldsets = [
        (None,          {'fields': ['name', 'abstract']}),
        ('Связи',       {'fields': ['goods', 'brands', 'categories'], 'classes': ['collapse']})
    ]
    inlines = [TextInline, ImageInline]

class ActionAdmin(Common):
    list_display = ('name','start','end')
    list_editable = ('start','end')
    model = Action
    inlines = [TextInline, ImageInline]

class GoodAdmin(Common):
    list_display = ('art','name','brand','category','price','new','old','available')
    list_display_links = ('art','name')
    list_editable = ('new','old','price','available')
    list_filter = ('brand','category','new','old','available')
    search_fields = ('@name','=brand__name','=category__name','=art')
    model = Good
    inlines = [CharInline, ImageInline]
    actions = ['mark_new','mark_old','mark_available','mark_not_available','no_action']
    def mark_new(self, request, queryset):
        rows = queryset.update(new=True,old=False)
        self.message_user(request, u"Товаров помечено как новые: %i" % rows)
    mark_new.short_description = u'Новинка!'
    def mark_old(self, request, queryset):
        rows = queryset.update(new=False,old=True)
        self.message_user(request, u"Товаров помечено как старые: %i" % rows)
    mark_old.short_description = u'В старые...'
    def mark_available(self, request, queryset):
        rows = queryset.update(available=True)
        self.message_user(request, u"Товаров помечено \"в наличии\": %i" % rows)
    mark_available.short_description = u'В наличии!'
    def mark_not_available(self, request, queryset):
        rows = queryset.update(available=False)
        self.message_user(request, u"Товаров помечено \"отсутсвует\": %i" % rows)
    mark_not_available.short_description = u'Отсутствует...'
    def no_action(self, request, queryset):
        rows = queryset.update(action='')
        self.message_user(request, u"Товаров снесено из всех акций: %i" % rows)
    no_action.short_description = u'Снести из всех акций'

class OrderAdmin(Common):
    list_display = ('__unicode__','status','delivery','user','total')
    list_editable = ('status','delivery')
    list_filter = ('status','delivery')
    fieldsets = (
        (None,  {
            'fields': ('status','user','delivery','total'),
        }),
        (u'Дополнительно',   {
            'fields':   ('user_comment','staff_comment'),
            'classes':  ('collapse',)
        })
    )
    model = Order
    inlines = [BasketInline]

class BrandAdmin(Common):
    list_display = ('prefix','name','yandex')
    list_editable = ('yandex',)
    list_filter = ('yandex',)
    search_fields = ('=prefix','^name')
    model = Brand
    inlines = [ImageInline]
    actions = ['to_yandex','no_yandex']
    def to_yandex(self, request, queryset):
        rows = queryset.update(yandex=True)
        self.message_user(request, u"Брендов отправлено в Яндекс: %i" % rows)
    to_yandex.short_description = u'Отдавать в Яндекс'
    def no_yandex(self, request, queryset):
        rows = queryset.update(yandex=False)
        self.message_user(request, u"Брендов отобрано у Яндекса: %i" % rows)
    no_yandex.short_description = u'Не отдавать в Яндекс'

class CategoryAdmin(Common):
    model = Category
    list_display = ('__unicode__','yandex','not_in_path')
    list_editable = ('yandex','not_in_path')
    list_filter = ('yandex','parent')
    search_fields = ('^name',)
    actions = ['to_yandex','no_yandex']
    def to_yandex(self, request, queryset):
        rows = queryset.update(yandex=True)
        self.message_user(request, u"Брендов отправлено в Яндекс: %i" % rows)
    to_yandex.short_description = u'Отдавать в Яндекс'
    def no_yandex(self, request, queryset):
        rows = queryset.update(yandex=False)
        self.message_user(request, u"Брендов отобрано у Яндекса: %i" % rows)
    no_yandex.short_description = u'Не отдавать в Яндекс'

class InfoAdmin(Common):
    model = Info

admin.site.register(Article, ArticleAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Good, GoodAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Info, InfoAdmin)
admin.site.register(Option, OptionAdmin)
