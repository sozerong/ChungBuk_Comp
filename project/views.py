from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from .models import Proj_Post, Proj_Category, Proj_Tag, Proj_Comment
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .forms import CommentForm


class Proj_PostList(ListView):
    model = Proj_Post
    ordering = '-pk'
    paginate_by = 5
    template_name = 'proj_post_list.html'
    def get_context_data(self, **kwargs):
        context = super(Proj_PostList, self).get_context_data()
        context['categories'] = Proj_Category.objects.all()
        context['no_category_post_count'] = Proj_Post.objects.filter(category=None).count()
        return context


class Proj_PostDetail(DetailView):
    model = Proj_Post

    def get_context_data(self, **kwargs):
        context = super(Proj_PostDetail, self).get_context_data()
        context['categories'] = Proj_Category.objects.all()
        context['no_category_post_count'] = Proj_Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class Proj_PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Proj_Post
    fields = ['title', 'tools', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'project/post_form.html'
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(Proj_PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Proj_Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
                return redirect('/project/')


class Proj_PostUpdate(LoginRequiredMixin, UpdateView):
    model = Proj_Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'project/proj_post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(Proj_PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(Proj_PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(Proj_PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Proj_Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response



def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Proj_Post.objects.filter(category=None)
    else:
        category = Proj_Category.objects.get(slug=slug)
        post_list = Proj_Post.objects.filter(category=category)

    return render(
        request,
        'project/proj_post_list.html',
        {
            'post_list': post_list,
            'categories': Proj_Category.objects.all(),
            'no_category_post_count': Proj_Post.objects.filter(category=None).count(),
            'category': category,
        }
    )


def tag_page(request, slug):
    tag = Proj_Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'project/proj_post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Proj_Category.objects.all(),
            'no_category_post_count': Proj_Post.objects.filter(category=None).count(),
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Proj_Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


class Proj_CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Proj_Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(Proj_CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Proj_Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


class Proj_PostSearch(Proj_PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Proj_Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(Proj_PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context
