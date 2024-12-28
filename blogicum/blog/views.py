from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.db.models import Count

from .models import Post, Category, Comment
from . import forms
from .utils import post_filter

User = get_user_model()


# Mixins.
class AuthorRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != self.request.user:
            return redirect('blog:post_detail', self.object.id)
        return super(AuthorRequiredMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )


class UserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if self.object != self.request.user:
            return redirect('accounts/login', self.object.id)
        return super(UserRequiredMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )


# Function views.
def index(request):

    template_name = 'blog/index.html'

    post_list = post_filter(
        Post.objects.annotate(
            comment_count=Count('comments')
        ).select_related(
            'category',
            'location',
            'author'
        )
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def post_detail(request, post_id):

    template_name = 'blog/detail.html'

    post = get_object_or_404(
        Post.objects.all().select_related(
            'category',
            'location',
            'author',
        ),
        pk=post_id
    )

    if post.author != request.user:

        if post.pub_date > timezone.now():
            raise Http404

        if not post.is_published:
            raise Http404

        if not post.category.is_published:
            raise Http404

    form = forms.CreateCommentForm()

    comments = Comment.objects.filter(post=post)

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, template_name, context)


def category_posts(request, category_slug):

    template_name = 'blog/category.html'

    category = get_object_or_404(Category, slug=category_slug)

    if not category.is_published:
        raise Http404()

    post_list = post_filter(
        category.posts.annotate(
            comment_count=Count('comments')
        ).select_related(
            'category',
            'location',
            'author'
        )
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def profile(request, username):

    template_name = 'blog/profile.html'

    profile = get_object_or_404(User, username=username)

    post_list = profile.posts.annotate(
        comment_count=Count('comments')
    ).select_related(
        'category',
        'location',
        'author'
    ).order_by(
        '-pub_date'
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


# Class based views.
class UpdateUser(LoginRequiredMixin, UpdateView):

    model = User

    fields = ('first_name', 'last_name', 'email')

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CreatePost(LoginRequiredMixin, CreateView):

    model = Post

    form_class = forms.CreatePostForm

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdatePost(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):

    model = Post

    form_class = forms.CreatePostForm

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class DeletePost(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):

    model = Post

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:index',
        )


class CreateComment(LoginRequiredMixin, CreateView):

    model = Comment

    form_class = forms.CreateCommentForm

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['post_id'])
        return super().form_valid(form)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = forms.CreateCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class UpdateComment(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):

    model = Comment

    fields = ('text', )

    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class DeleteComment(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):

    model = Comment

    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
