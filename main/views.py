from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import *
from .permissions import IsAuthorPermission
from .serializers import CategorySerializer, PostSerializer, CommentSerializer


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
    # permission_class = [AllowAny, ]
    # permission_classes = [IsAuthenticated, ]

    # @action(detail=False, methods=['get'])                # router builds path posts/search/?q=paris
    # def search(self, request, pk=None):
    #     q = request.query_params.get('q')                    # request.query_params = request.GET
    #     queryset = self.get_queryset()
    #     queryset = queryset.filter(Q(title__icontains=q) |
    #                                Q(text__icontains=q))
    #     serializer = PostSerializer(queryset, many=True, context={'request': request})
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context


class CommentViewSet(PermissionMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


