from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('posts/', views.PostsView.as_view(), name="posts"),
    path('post/<slug:slug>/', views.PostView.as_view(), name="post"),
    path('profile/', views.ProfileView.as_view(), name="profile"),

    # CRUD PATHS

    path('create_post/', views.CreatePostView.as_view(), name="create_post"),
    path('update_post/<slug:slug>/', views.UpdatePostView.as_view(), name="update_post"),
    path('delete_post/<slug:slug>/', views.DeletePostView.as_view(), name="delete_post"),

    path('send_email/', views.SendEmailView.as_view(), name="send_email"),

    path('login/', views.LoginPageView.as_view(), name="login"),
    path('register/', views.RegisterPageView.as_view(), name="register"),
    path('logout/', views.LogoutUserView.as_view(), name="logout"),

    path('account/', views.UserAccountView.as_view(), name="account"),
    path('update_profile/', views.UpdateProfileView.as_view(), name="update_profile"),
]
