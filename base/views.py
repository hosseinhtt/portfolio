from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import View
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.models import User

from .decorators import admin_only
from .forms import PostForm, CustomUserCreationForm, ProfileForm, UserForm, CommentForm
from .filters import PostFilter
from .models import Post, PostComment, Profile

class HomeView(View):
    template_name = 'base/index.html'

    def get(self, request):
        posts = Post.objects.filter(active=True, featured=True)[0:3]
        context = {'posts': posts}
        return render(request, self.template_name, context)

class PostsView(View):
    template_name = 'base/posts.html'

    def get(self, request):
        posts = Post.objects.filter(active=True).order_by('-created')  # Add order_by here
        myFilter = PostFilter(request.GET, queryset=posts)
        posts = myFilter.qs

        page = request.GET.get('page')

        paginator = Paginator(posts, 5)

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {'posts': posts, 'myFilter': myFilter}
        return render(request, self.template_name, context)


class PostView(View):
    template_name = 'base/post.html'

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {'post': post}
        return render(request, self.template_name, context)

    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        PostComment.objects.create(
            author=request.user.profile,
            post=post,
            body=request.POST['comment']
        )
        messages.success(request, "Your comment was successfully posted!")
        return redirect('base:post', slug=post.slug)

class ProfileView(View):
    template_name = 'base/profile.html'

    def get(self, request):
        return render(request, self.template_name)


class CreatePostView(View):
    template_name = 'base/post_form.html'

    def get(self, request):
        form = PostForm()
        context = {'form': form}
        return render(request, self.template_name, context)
    
    @admin_only
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('base:posts')
        context = {'form': form}
        return render(request, self.template_name, context)
    

class UpdatePostView(View):
    template_name = 'base/post_form.html'

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        form = PostForm(instance=post)
        context = {'form': form}
        return render(request, self.template_name, context)

    @admin_only
    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('base:posts')
        context = {'form': form}
        return render(request, self.template_name, context)

class DeletePostView(View):
    template_name = 'base/delete.html'

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {'item': post}
        return render(request, self.template_name, context)

    @admin_only
    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        post.delete()
        return redirect('base:posts')

class SendEmailView(View):
    template_name = 'base/email_sent.html'

    def post(self, request):
        template = render_to_string('base/email_template.html', {
            'name': request.POST['name'],
            'email': request.POST['email'],
            'message': request.POST['message'],
        })

        email = EmailMessage(
            request.POST['subject'],
            template,
            settings.EMAIL_HOST_USER,
            ['seven.number73@gmail.com']
        )
        email.fail_silently = False
        email.send()

        return render(request, self.template_name)

class LoginPageView(View):
    template_name = 'base/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('base:home')
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('base:home')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Little Hack to work around re-building the user model
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except:
            messages.error(request, 'User with this email does not exist')
            return redirect('base:login')
        
        if user is not None:
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, 'Email OR password is incorrect')
        
        context = {}
        return render(request, self.template_name, context)

class RegisterPageView(View):
    template_name = 'base/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('base:home')
        form = CustomUserCreationForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('base:home')
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Account successfully created!')
            user = authenticate(request, username=user.username, password=request.POST['password1'])
            if user is not None:
                login(request, user)
            next_url = request.GET.get('next')
            if next_url == '' or next_url == None:
                next_url = 'base:home'
            return redirect(next_url)
        else:
            messages.error(request, 'An error has occurred with registration')
        context = {'form': form}
        return render(request, self.template_name, context)

class LogoutUserView(View):
    def get(self, request):
        logout(request)
        return redirect('base:home')

class UserAccountView(View):
    template_name = 'base/account.html'

    def get(self, request):
        profile = request.user.profile
        context = {'profile': profile}
        return render(request, self.template_name, context)

class UpdateProfileView(View):
    template_name = 'base/profile_form.html'

    def get(self, request):
        user = request.user
        profile = user.profile
        form = ProfileForm(instance=profile)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        profile = user.profile
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('base:account')
        context = {'form': form}
        return render(request, self.template_name, context)

# class ProfileDetailView(DetailView):
#     model = Profile
#     template_name = 'profiles/profile_detail.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


# class PostListView(ListView):
#     model = Post
#     template_name = 'base/post_list.html'
#     context_object_name = 'posts'
#     queryset = Post.objects.filter(active=True).order_by('-created')

# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'base/post_detail.html'
#     context_object_name = 'post'

# class PostCommentCreateView(CreateView):
#     model = PostComment
#     template_name = 'comments/comment_form.html'
#     form_class = CommentForm  # Replace with your actual form class
#     success_url = reverse_lazy('base:post-list')  # Replace with the URL where you want to redirect after comment submission
