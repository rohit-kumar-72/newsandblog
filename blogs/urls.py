from django.urls import path
from .views import home,login_user,register_user,forgot_password,logout_user,get_user_blog,single_blog,delete_blog,create_blog,edit_blog,getallnews,news_detail,BlogView,BlogDeleteView


urlpatterns = [
    path('', home, name="home"),
    path('login/', login_user, name="login_user"),
    path('forgot-password/', forgot_password, name="forgot_password"),
    path('register/', register_user, name="register_user"),
    path('logout/', logout_user, name="logout_user"),
    path('my-blogs/', get_user_blog, name="get_user_blog"),
    path('create-blog/', create_blog, name="create_blog"),
    path('<int:id>/blog/', single_blog, name="single_blog"),
    path('<int:id>/edit-blog', edit_blog, name="edit_blog"),
    path('<int:id>/delete-blog', delete_blog, name="delete_blog"),

    path('news/',getallnews,name="get_all_news"),
    path('news/<str:id>/', news_detail, name='news_detail'),
    path('api',BlogView.as_view()),
    path('api/delete/<int:blog_id>',BlogDeleteView.as_view()),
]