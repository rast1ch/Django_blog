from ..models import Post
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.simple_tag
def total_post():
    return Post.published.count()


@register.simple_tag
def the_most_commented(count=5):
    return Post.published.annotate(am_comments = Count('comments')).order_by('-am_comments')[:count]


@register.inclusion_tag("blog/post/lastest_post.html")
def show_lastest(count=5):
    lastest_posts = Post.published.order_by('-publish')[:count]
    return {'lastest_posts':lastest_posts}

@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))