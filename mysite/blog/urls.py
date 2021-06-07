from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name= 'post_detail'),
    path('<int:post_id>/share',views.post_share, name='share')
]