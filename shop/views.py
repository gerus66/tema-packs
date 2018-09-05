# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.core import mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from shop.models import Brand,Category,Good,Article,Image,Action,Text,Char,Option,Info,Order,Basket
from django.db.models import Count
from django.db import connections
#from DjangoNginxCache import cache_page_nginx

def list_of_cats ():
    cats = []
    for cat in Category.objects.all().order_by("name"):
        count = cat.goods.filter(sites = settings.SITE_ID, available = 1).count()
        if count:
            cats.append(cat)
    return cats

def list_of_brands ():
    brs = []
    for br in Brand.objects.all().order_by("name"):
        count = br.goods.filter(sites = settings.SITE_ID, available = 1).count()
        if count:
            brs.append(br)
    return brs

def list_of_parents (cats):
    prs = []
    for cat in cats:
        pr = cat.parent
        if prs.count(pr) == 0:
            prs.append(pr)
    return prs

def list_of_childs (P, cats):
    chs = []
    for ct in cats:
        if ct.parent == P:
            chs.append(ct)
    return chs

def xx (req):
    try:
        x = 0
        cart = req.session['cart']
        for k, v in cart.iteritems():
		    x += v['qty']
        return x
    except KeyError:
        return 0	

def buy_goods (req):
    try:
        ccart = req.session['cart']
        gs = []
        for k, v in ccart.iteritems():
            g = Good.objects.get(id=v['id'])
            g.qty = v['qty']
            gs.append(g)
        return gs
    except KeyError:
        return ''

def sum (req):
    try:
        ccart = req.session['cart']
        s = 0
        for k, v in ccart.iteritems():
            s += v['price']*v['qty']
        return s
    except KeyError:
        return ''
		
def minibasket (req):
    return render_to_response('minibasket.html',{'gs': buy_goods(req), 's': sum(req)})
	
def minibasketq (req): 
    if xx(req) == 0:
        s = ''
    else:
        s = '(' + str(xx(req)) + ')'
    return HttpResponse(s)
	
def minibasketbuy (req):
    if xx(req) == 0:
        s = ''
    else:
        s = '<a class="buy" href="/basket">Купить!</a>'
    return HttpResponse(s)
	
def index(req):
    info = []
    a = Article.objects.get(id="40")
    for inf in Text.objects.filter(article=a).order_by("-id"):
        info.append(inf)
    return render_to_response('index.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'info': info, 'a': a})

def delivery(req):
    info = []
    a = Article.objects.get(id="1")
    for inf in Text.objects.filter(article=a).order_by("id"):
        info.append(inf)
    return render_to_response('delivery.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'info': info})

def contacts(req):
    info = []
    a = Article.objects.get(id="2")
    for inf in Text.objects.filter(article=a).order_by("id"):
        info.append(inf)
    return render_to_response('contacts.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'info': info})

def tech(req):
    a = Article.objects.get(id="15")
    return render_to_response('tech.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'a': a})

def catalog(req, p_id, c_id, b_id, sort):
    B = ''
    if b_id <> '0':
        B = Brand.objects.get(id=b_id)
    C = ''
    if c_id <> '0':
        C = Category.objects.get(id=c_id)
    P = Category.objects.get(id=p_id)
    goods=[]
    if C == '' and B == '':
        for ch in list_of_childs(P, list_of_cats()):
            for good in Good.objects.filter(category = ch, available = 1, sites = settings.SITE_ID).order_by("name"):
                goods.append(good)
    elif C == '':
        for ch in list_of_childs(P, list_of_cats()):
            for good in Good.objects.filter(category = ch, brand = B, available = 1, sites = settings.SITE_ID).order_by("name"):
                goods.append(good)
    elif B == '':
        for good in Good.objects.filter(category = C, available = 1, sites = settings.SITE_ID).order_by("name"):
            goods.append(good)
    else:
        for good in Good.objects.filter(brand = B, category = C, available = 1, sites = settings.SITE_ID).order_by("name"):
            goods.append(good)
    if sort == '0':
        goods.sort(key=lambda good: good.name)
    elif sort == '1':
        goods.sort(key=lambda good: int(good.price))
    elif sort == '2':
        op_name = "Объем, л"
        option = Option.objects.filter(name=op_name)[0]
        chars = []
        for good in goods:
            char = Char.objects.filter(option=option, good=good)[0]
            chars.append(char)
        goods = []
        chars.sort(key=lambda char: float(char.value))
        for char in chars:
            good = Good.objects.get(name=char.good)
            goods.append(good)
    elif sort == '3':
        op_name = "Вес, кг"
        option = Option.objects.filter(name=op_name)[0]
        chars = []
        for good in goods:
            char = Char.objects.filter(option=option, good=good)[0]
            chars.append(char)
        goods = []
        chars.sort(key=lambda char: float(char.value))
        for char in chars:
            good = Good.objects.get(name=char.good)
            goods.append(good)
    gs = []
    i = 0
    for good in goods:
        gs.append(good)
        i = i + 1
        if i == 4:
            gs.append('')
            i = 0
    cts = []
    if B == '':
        cts = list_of_childs(P, list_of_cats())
    else:
        goods = []
        for ch in list_of_childs(P, list_of_cats()):
            for good in Good.objects.filter(category = ch, brand = B, available = 1, sites = settings.SITE_ID):
                goods.append(good)
        for good in goods:
            ct = good.category
            if cts.count(ct) == 0:
                cts.append(ct)
    brds = []
    if C == '':
        goods = []
        for ch in list_of_childs(P, list_of_cats()):
            for good in Good.objects.filter(category = ch, available = 1, sites = settings.SITE_ID):
                goods.append(good)
        for good in goods:
            brd = good.brand
            if brds.count(brd) == 0:
                brds.append(brd)
    else:
        goods = []
        for good in Good.objects.filter(category = C, available = 1, sites = settings.SITE_ID):
            goods.append(good)
        for good in goods:
            brd = good.brand
            if brds.count(brd) == 0:
                brds.append(brd)
    cts.sort(key=lambda ct: ct.name)
    brds.sort(key=lambda brd: brd.name)
    return render_to_response('catalog.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'gs': gs, 'B': B, 'C': C, 'P': P, 'sort': sort, 'chs': cts, 'brds': brds})

def brand(req, b_id, sort):
    B = Brand.objects.get(id=b_id)
    goods = []
    for good in Good.objects.filter(brand = B, available = 1, sites = settings.SITE_ID).order_by("name"):
        goods.append(good)
    if sort == '1':
        goods.sort(key=lambda good: int(good.price))
    elif sort == '2':
        goods.sort(key=lambda good: good.category)
    gs = []
    i = 0
    for good in goods:
        gs.append(good)
        i = i + 1
        if i == 4:
            gs.append('')
            i = 0
    return render_to_response('brand.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'gs': gs, 'B': B, 'sort': sort})

def good(req, g_id):
    g = Good.objects.get(id=g_id)
    Si = g.sites.all()[0]
    S = Si.id
    op_names = ["Вес, кг", "Объем, л", "Размер, см", "Материал", "Подвесная система"]
    chars = []
    for op_name in op_names:
        option = Option.objects.filter(name=op_name)[0]
        chart = Char.objects.filter(option=option, good=g)
        if len(chart) == 0:
            char = ''
        else: 
            char = Char.objects.filter(option=option, good=g)[0]
        chars.append(char)
    return render_to_response('good.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'good': g, 'S': S, 'chars': chars})

def basket (req):
    return render_to_response('basket.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats())})

def buy (request, g_id):
    ccart = request.session.get('cart',{})
    gg = Good.objects.get(id=g_id)
    i = 0
    for k, v in ccart.iteritems():
        if v['id'] == gg.id:
            v['qty'] = v['qty'] + 1
            i = 1
    if i == 0:
        ccart[gg.id] = {'id':gg.id,'name':gg.name,'price':gg.price,'brand':gg.brand.name,'qty':1}
    request.session['cart'] = ccart
    if request.is_ajax():
        return HttpResponse('') #TODO: AJAX
    else:
        url = request.META['HTTP_REFERER'].split('?')
        return HttpResponseRedirect('&'.join(url))

def delete (request, g_id):
    ccart = request.session.get('cart',{})
    gg = Good.objects.get(id=g_id)
    if ccart[gg.id]['qty'] == 1:
        del ccart[gg.id]
    else:
        ccart[gg.id]['qty'] = ccart[gg.id]['qty'] - 1
    request.session['cart'] = ccart
    if request.is_ajax():
        return HttpResponse('') #TODO: AJAX
    else:
        url = request.META['HTTP_REFERER'].split('?')
        return HttpResponseRedirect('&'.join(url))

def order (req):
    if (not req.POST.get('name', '')) or (not req.POST.get('email', '')) or (not req.POST.get('adress', '')) or (not req.POST.get('phone', '')):
        w = "Заполните все поля, отмеченные *"
        return render_to_response ('basket.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'gs': buy_goods(req), 's': sum(req), 'w': w, 
                                                  'name': req.POST.get('name', ''), 'name_1': req.POST.get('name_1', ''), 'name_2': req.POST.get('name_2', ''), 'email': req.POST.get('email', ''),
                                                  'adress': req.POST.get('adress', ''), 'phone': req.POST.get('phone', ''), 'comments': req.POST.get('comments', '')})
    else:
        ccart = req.session['cart']
        data = {}
        info = req.POST.get('name', '') + "\n" + req.POST.get('email', '') + "\n" + req.POST.get('phone', '') + "\n" + req.POST.get('adress', '')
        if req.POST.get('name_1', ''):
            info = info + "\n" + req.POST.get('name_1', '')
        if req.POST.get('name_2', ''):
            info = info + "\n" + req.POST.get('name_2', '')
        if req.POST.get('comments', ''):
            info = info + "\n" + req.POST.get('comments', '')
            data['user_comment'] = req.POST.get('comments', '')
        u = User.objects.get(username__exact='order')
        o = Order.objects.create(user = u, user_comment = info, total = 0)
        g = Good.objects.filter(id__in=ccart.keys())
        data['count'] = 0
        data['goods'] = []
        total = 0
        for good in g:
            Basket.objects.create(order = o, good = good, qty = ccart[good.id]['qty'], total = ccart[good.id]['qty'] * good.price)
            total = total + good.price * ccart[good.id]['qty']
            data['goods'].append(good)
            good.qty = ccart[good.id]['qty']
            data['count'] = data['count'] + good.qty
            del ccart[good.id]
        o.total = data['total'] = total
        o.save()
        req.session['cart'] = ccart
        data['name'] = req.POST.get('name', '')
        data['id'] = o.id
        site = Site.objects.get_current()
        data['site'] = site.domain
        connection = mail.get_connection(use_tls = True)
        msg = mail.EmailMessage(u'заказ '+str(o.id), render_to_string('order_letter.html', data), u'Магазин ТЕМА <order@tema-sport.ru>', [req.POST.get('email','')])
        msg.content_subtype = "html"  # Main content is now text/html
        msg_o = mail.EmailMessage(u'заказ '+str(o.id), '<a href="http://www.outdoor-cooking.ru/admin/shop/order/'+str(o.id)+u'"> заказ тут </a>', 'order@tema-sport.ru', ['unforgiven8@yandex.ru','order@tema-sport.ru'])
        msg_o.content_subtype = "html"
        try:
            connection.send_messages([msg, msg_o])
        except Exception:           
            return HttpResponseRedirect('/basket/2/')
        else:
            return HttpResponseRedirect('/basket/1/')

def order_made (req):
    ww = "Ваш заказ принят! Информация о заказе отправлена Вам на указанную почту. В ближайшее время с Вами свяжется наш консультант для уточнения деталей доставки."
    return render_to_response('basket.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'ww': ww})

def order_not_made (req):
    ww = "Ваш заказ принят, но e-mail не отправлен. Возможно, Вы указали неверный электронный адрес. Если в ближайшее время с вами не свяжется наш консультант, пожалуйста, свяжитесь с нами по телефону (495)604-42-26"
    return render_to_response('basket.html',{'cats': list_of_cats(), 'brs': list_of_brands(), 'prs': list_of_parents(list_of_cats()), 'ww': ww})
