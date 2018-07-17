import json
import random
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import os
from Blog import settings
from django.shortcuts import render, redirect, HttpResponse
from blog_CN import models
from django.db import transaction
from django.contrib import auth
from django.db.models import Count, Max, Avg, F
from django.http import JsonResponse
from bs4 import BeautifulSoup
from blog_CN.form import UserForm


# Create your views here.

# def cat_list(username):
#     user = models.UserInfo.objects.filter(username=username).first()
#     blog = user.blog
#
#     # 查询当前站点每一个分类的名称以及对应的文章数
#     category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title',
#                                                                                                               'c')
#
#     # 查询当前站点每一个标签的名称以及对应的文章数
#
#     tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')
#
#     # 日期归档
#
#     date_list = models.Article.objects.filter(user=user).extra(
#         select={'y_date': "strftime('%%Y/%%m',create_time)"}).values('y_date').annotate(c=Count("title")).values_list(
#         'y_date', 'c')
#
#     return {'blog':blog,'user':user,"category_list":category_list,"tag_list":tag_list,
#             "date_list":date_list,"username":username}

def check_code(width=120, height=30, char_length=5, font_file='kumo.ttf', font_size=28):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    def rndChar():
        """
        生成随机字母
        :return:
        """
        return chr(random.randint(65, 90))

    def rndColor():
        """
        生成随机颜色
        :return:
        """
        return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))

    # 写文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h = random.randint(0, 4)
        draw.text([i * width / char_length, h], char, font=font, fill=rndColor())

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())

    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line((x1, y1, x2, y2), fill=rndColor())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, ''.join(code)


def code(request):
    img, reg_code = check_code()
    request.session['reg_code'] = reg_code
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def index(request):
    '''
    首页
    :param request:
    :return: 首页和渲染页面所需要的元素
    '''
    arcicle_list = models.Article.objects.all()

    return render(request, 'index.html', locals())


def login(request):
    '''
    登陆页面
    :param request:
    :return:
    '''
    if request.method == 'POST':
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        reg_code = request.POST.get("code")
        print(reg_code)
        print(request.session["reg_code"])

        if reg_code.upper() != request.session["reg_code"].upper():
            return render(request,'login.html', {"msg": "验证码错误"})

        user = auth.authenticate(username=username, password=pwd)

        if user:
            auth.login(request, user)
            return redirect('/index/')

    return render(request, 'login.html', locals())


def logout(request):
    auth.logout(request)

    return redirect('/index/')


def homePage(request, username, **kwargs):
    '''
    主页面
    :param request:
    :param username:
    :param kwargs:
    :return:
    '''
    user = models.UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request, '404Page.html')
    blog = user.blog

    print('kwargs:', kwargs)
    if not kwargs:
        print('-' * 20)
        arcitle_list = models.Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get('condition')
        parms = kwargs.get('parms')

        print('*' * 20)
        print(condition, parms)

        if condition == 'category':
            arcitle_list = models.Article.objects.filter(user__username=username).filter(category__title=parms)
        elif condition == 'tag':
            arcitle_list = models.Article.objects.filter(user__username=username).filter(tags__title=parms)
        else:
            year, month = parms.split('/')
            arcitle_list = models.Article.objects.filter(user__username=username).filter(create_time__year=year,
                                                                                         create_time__month=month)

    # 查询当前站点每一个分类的名称以及对应的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title',
                                                                                                              'c')

    # 查询当前站点每一个标签的名称以及对应的文章数

    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')

    # 日期归档

    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_date': "strftime('%%Y/%%m',create_time)"}).values('y_date').annotate(c=Count("title")).values_list(
        'y_date', 'c')

    return render(request, 'homePage.html', locals())


def article_detail(request, username, article_id):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()

    # 查询当前站点每一个分类的名称以及对应的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title',
                                                                                                              'c')

    # 查询当前站点每一个标签的名称以及对应的文章数

    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')

    # 日期归档

    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_date': "strftime('%%Y/%%m',create_time)"}).values('y_date').annotate(c=Count("title")).values_list(
        'y_date', 'c')

    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, 'article.html', locals())


def like(request):
    '''
    点赞功能
    :param request:
    :return:
    '''
    is_up = json.loads(request.POST.get('is_up'))
    article_id = request.POST.get('article_id')
    user_id = request.user.pk
    aud_obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    responce = {'stace': True, "handled": None}

    if aud_obj:
        responce['stace'] = False
        responce['handled'] = aud_obj.is_up

    else:
        with transaction.atomic():
            obj = models.ArticleUpDown.objects.create(user_id=user_id, is_up=is_up, article_id=article_id)
            if is_up:
                models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
            else:
                models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

    return JsonResponse(responce)


def comment(request):
    print('*' * 20)
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    user_id = request.user.pk

    comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                parent_comment_id=pid)
    models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    response = {'static': True}

    response["timer"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["content"] = comment_obj.content
    response["user"] = request.user.username

    return JsonResponse(response)


def background(request):
    user = request.user
    artictle_obj = models.Article.objects.filter(user=user)

    return render(request, "back_manage/background.html", locals())


def add_article(request):
    if request.method == "POST":

        title = request.POST.get("Editor$Edit$txbTitle")
        content = request.POST.get("content")
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")

        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():
            if tag.name in ["script", ]:
                tag.decompose()
        desc = soup.text[0:150]

        article_obj = models.Article.objects.create(title=title, content=str(soup), user=user, category_id=cate_pk,
                                                    desc=desc)

        for tag_pk in tags_pk_list:
            models.Article2Tag.objects.create(article_id=article_obj.pk, tag_id=tag_pk)

        return redirect("/background/")


    else:

        blog = request.user.blog
        cate_list = models.Category.objects.filter(blog=blog)
        tags = models.Tag.objects.filter(blog=blog)
        return render(request, "back_manage/add_article.html", locals())


def del_article(request, article_id):
    models.Article.objects.get(pk=article_id).delete()

    return redirect('/background/')


def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")
    name = obj.name

    path = os.path.join(settings.BASE_DIR, "static", "upload_files", name)
    with open(path, "wb") as f:
        for line in obj:
            f.write(line)

    import json

    res = {
        "error": 0,
        "url": "/static/upload_files/" + name
    }

    return HttpResponse(json.dumps(res))


def compile_article(request, article_id):
    article_obj = models.Article.objects.get(pk=article_id)

    return render(request, "back_manage/article_compile.html", locals())


def register(request):
    if request.method == 'POST':
        ret = UserForm(request.POST)
        if ret.is_valid():
            print("*" * 20, request.POST, "\n", "-" * 20, request.FILES)
            user = request.POST.get("name")
            pwd = request.POST.get("pwd")
            email = request.POST.get("email")
            tel = request.POST.get("tel")
            img = request.FILES.get("MultiValueDict")
            return redirect("/index/")
        else:
            error_msg = ret.errors
            g_error = ret.errors.get("__all__")
            if g_error:
                g_error = g_error[0]

            return render(request, "regiest.html", locals())

    else:
        ret = UserForm()
        return render(request, "regiest.html")
