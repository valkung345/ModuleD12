from typing import Any, Dict
from django.urls import resolve
from .models import *
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import NewsForm
from .models import BaseRegisterForm
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_managers, EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, m2m_changed




class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    paginate_by = 10

    def post(self, request, *args, **kwargs):
        category_id = request.POST['cat']
        re = Post.objects.filter(postCategory=category_id)
        ca = Category.objects.all()
        cat_name = request.POST['btn']
        return render(request, 'posts.html', {'posts': re, 'categories': ca, 'cat_name': cat_name})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostList(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'filter'
    queryset = Post.objects.order_by('-id')
    paginate_by = 1


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context
    

class PostsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('newapp.add_post',)
    template_name = 'posts_create.html'
    form_class = NewsForm


class PostsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('newapp.change_post',)
    template_name = 'posts_create.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostsDeleteView(DeleteView):
    template_name = 'posts_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')


@login_required
def Subscribers(request):
	user = request.user
	if request.POST['sub']:
		subs = request.POST['sub']
		category_sub = Category.objects.get(name=subs)
		category_sub.subscribers.add(user.id)
		category_sub.save()
	return redirect('/')

