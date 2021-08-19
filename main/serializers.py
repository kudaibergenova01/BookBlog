from rest_framework import serializers
from rest_framework.decorators import action

from .models import Category, Post, PostImage, Comment, Like


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', read_only=True)
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        fields = ('id', 'title', 'category', 'author', 'created_at', 'text')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = ImageSerializer(instance.images.all(), many=True).data
        representation['likes'] = instance.likes.count()
        # action = self.context.get('action')
        if action == 'list':
            representation['replies'] = instance.replies.count()
        elif action == 'retrieve':
            representation['replies'] = PostSerializer(instance.replies.all(), many=True).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES
        post = Post.objects.create(
            author=request.user,
            **validated_data)
        for image in images_data.getlist('images'):
            PostImage.objects.create(image=image, post=post)
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        images_data = request.FILES
        instance.images.all().delete()
        for image in images_data.getlist('images'):
            PostImage.objects.create(
                image=image,
                post=instance
            )
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        comment = Comment.objects.create(
            author=request.user,
            **validated_data
        )
        return comment


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Like
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('posts')

        if Like.objects.filter(user=user, post=post):
            like = Like.objects.get(user=user, post=post)
            return like

        like = Like.objects.create(user=user, **validated_data)
        return like