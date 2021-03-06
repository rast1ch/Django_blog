
from re import search
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentPostForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.postgres.search import SearchVector
from django.db.models import Count
from .forms import SearchForm
from taggit.models import Tag


def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        posts = Post.published.filter(tags__in=[tag])
    paginator = Paginator(posts,3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html',{'posts':posts,
                                                    'page':page,
                                                    'tag':tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug = post, status = 'published',
                            publish__year = year, publish__month = month,
                            publish__day = day)
    comments = post.comments.filter(active = True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentPostForm(data=request.POST)
        if comment_form.is_valid():
            new_comment  =comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            comment_form = CommentPostForm()
    else:
        comment_form = CommentPostForm()
    post_tags_id = post.tags.values_list('id', flat = True)
    similar_posts= Post.published.filter(tags__in=post_tags_id).exclude(id=post.id)
    similar_posts  = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post':post,
                                                    'comments': comments,
                                                    'new_comment':new_comment,
                                                    'comment_form': comment_form,
                                                    'similar_posts':similar_posts})


def post_share(request,post_id):
    post = get_object_or_404(Post, id= post_id, status = 'published')
    sent =False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'],cd['email'],post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url,cd['name'],cd['comments'])
            send_mail(subject,message,'admin@myblog.com',[cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                {'post':post, 'form':form, 'sent':sent})


def post_search(request):
    form = SearchForm()
    query = None
    results=[]
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query=form.cleaned_data['query']
        results=Post.objects.annotate(search=SearchVector('title','body'),).filter(search=query)
    return render(request,'blog/post/search.html', {'form':form,
                                                    'query':query,
                                                    'results':results})
    