# Create your views here.
from apps.blog.models import Post, PostType
from apps.catalog.models import Service
from apps.core.helpers import (
    render_to, get_object_or_404, paginate
)
from django.conf import settings


@render_to('blog/index.html')
def index(request):
    posts = Post.objects.all()
    page = request.GET.get('page', 1)
    services = posts.values('type__service').distinct()
    posts = paginate(posts, page, pages=settings.DEFAULT_PAGES_COUNT)

    #c = posts.count()
    #_posts = []
    #_posts.append(posts[c/2:])
    #_posts.append(posts[:c/2])
    dt = {'posts': posts, 'services': services}
    if settings.SAUSAGE_SCROLL_ENABLE:
        if int(page) != 1:
            dt.update({'_template': 'blog/include/posts_index.html'})
    return dt


@render_to('blog/index.html')
def category(request, pk):
    category = get_object_or_404(PostType, pk=pk)
    posts = Post.objects.filter(type=category)

    services = posts.values('type__service').distinct()
    page = request.GET.get('page', 1)
    posts = paginate(posts, page, pages=settings.DEFAULT_PAGES_COUNT)

    #_posts = []
    #c = posts.count()
    #_posts.append(posts[c/2:])
    #_posts.append(posts[:c/2])
    dt = {
        'posts': posts, 'services': services,
        'category': category
    }
    if settings.SAUSAGE_SCROLL_ENABLE:
        if int(page) != 1:
            dt.update({'_template': 'blog/include/posts_index.html'})
    return dt


@render_to('blog/post.html')
def post(request, pk):
    services = Post.objects.all().values('type__service').distinct()
    return {'post': get_object_or_404(Post, pk=pk), 'services': services}


@render_to('blog/index.html')
def search(request):
    q = request.GET.get('q', '')
    if q:
        posts = (
            Post.objects.filter(title__icontains=q) |
            Post.objects.filter(announce__icontains=q) |
            Post.objects.filter(content__icontains=q)
        )
    else:
        posts = Post.objects.all()
    page = request.GET.get('page', 1)
    services = posts.values('type__service').distinct()
    posts = paginate(posts, page, pages=settings.DEFAULT_PAGES_COUNT)
    #c = posts.count()
    #_posts = []
    #_posts.append(posts[c/2:])
    #_posts.append(posts[:c/2])
    dt = {'posts': posts, 'G': request.GET, 'search': True, 'services': services}
    if settings.SAUSAGE_SCROLL_ENABLE:
        if int(page) != 1:
            dt.update({'_template': 'blog/include/posts_index.html'})
    return dt
