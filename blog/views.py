from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseNotFound, JsonResponse
from blog.models import Post
from .forms import PostForm
from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer
import json

# Create your views here

def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/post_list.html', {'posts':posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm()
	return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

class IntruderImage(viewsets.ModelViewSet):
	#permission_classes = (IsAuthenticated,)
	queryset = Post.objects.all()
	serializer_class = PostSerializer
	authentication_classes = [TokenAuthentication]
	def perform_create(self, serializer):
		serializer.save(author = self.request.user)

class PostListView(generics.ListAPIView):
	serializer_class = PostSerializer
	authentication_classes = [TokenAuthentication]
	def get_queryset(self):
		create_after = self.request.query_params.get('create_after')
		queryset = Post.objects.filter(published_date__gt = create_after)
		return queryset
