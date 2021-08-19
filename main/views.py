from datetime import timedelta
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import *
from .permissions import IsAuthorPermission
from .serializers import CategorySerializer, PostSerializer, CommentSerializer, LikeSerializer


class PermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission]
        else:
            permissions = []
        return [permission() for permission in permissions]


class CategoryViewSet(PermissionMixin, ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context


class PostViewSet(PermissionMixin, ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        weeks_count = int(self.request.query_params.get('week', 0))
        if weeks_count > 0:
            start_date = timezone.now() - timedelta(weeks=weeks_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(text__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)


class CommentViewSet(PermissionMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeViewSet(PermissionMixin, ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    bad_request_message = 'An error has occurred'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    # def post(self, request):
    #     post = get_object_or_404(Post, slug=request.data.get('slug'))
    #     if request.user not in post.favourite.all():
    #         post.favourite.add(request.user)
    #         return Response({'detail': 'User added to post'}, status=status.HTTP_200_OK)
    #     return Response({'detail': self.bad_request_message}, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request):
    #     post = get_object_or_404(Post, slug=request.data.get('slug'))
    #     if request.user in post.favourite.all():
    #         post.favourite.remove(request.user)
    #         return Response({'detail': 'User removed from post'}, status=status.HTTP_204_NO_CONTENT)
    #     return Response({'detail': self.bad_request_message}, status=status.HTTP_400_BAD_REQUEST)
