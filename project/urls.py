from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:q>/', views.Proj_PostSearch.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('update_comment/<int:pk>/', views.Proj_CommentUpdate.as_view()),
    path('update_post/<int:pk>/', views.Proj_PostUpdate.as_view()),
    path('create_post/', views.Proj_PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/new_comment/', views.new_comment),
    path('<int:pk>/', views.Proj_PostDetail.as_view()),
    path('', views.Proj_PostList.as_view()),
    # path('<int:pk>/', views.single_post_page),
    # path('', views.index),
]
