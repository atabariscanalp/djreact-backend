from rest_framework import serializers, exceptions
from rest_framework.serializers import HyperlinkedIdentityField, SerializerMethodField
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from dj_rest_auth.serializers import UserDetailsSerializer

import cv2

from posts.models import Post, Rate
from comments.models import Comment, CommentRate
from users.models import CustomUser, Profile

from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists, get_username_max_length
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email


post_detail_url = HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')

class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        # user.profile.save()
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    # class Meta:
    #     model = CustomUser
    #     fields = ('username', 'password')
    #     extra_kwargs = {
    #         'password': {'write_only': True}
    #     }
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user


    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = None
        user = self._validate_username(username, password)

        # Did we get back an active user?
        if user:
            print("I AM HERE!")
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)


        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    profile_photo = SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'profile_photo')
        read_only_fields = ('email',)

    def get_profile_photo(self, obj):
        return obj.profile.profile_photo.url if obj.profile.profile_photo else ""
    
class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name')


class ProfilePhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_photo',)

class ProfileDetailSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()
    post_num = SerializerMethodField()
    average_rate = SerializerMethodField()
    posts = SerializerMethodField()
    profile_photo = SerializerMethodField()
    class Meta:
        model = Profile
        fields = ('id', 'user', 'posts', 'post_num', 'average_rate',  'location', 'profile_photo')
    def get_user(self, obj):
        userdata = UserSerializer(obj.user).data
        return userdata
    def get_post_num(self, obj):
        shared_posts = Post.objects.filter(author=obj.user)
        return len(shared_posts)
    def get_average_rate(self, obj):
        rates = 0
        rate_count = 0
        for rate in Rate.objects.filter(is_active=True, rater=obj.user):
            rates += rate.rate
            rate_count += 1
        return '{:0.2f}'.format(rates / rate_count) if rate_count > 0 else 0
    def get_posts(self, obj):
        posts = Post.objects.filter(author=obj.user)
        serializerdata = PostListSerializer(posts, many=True).data
        return serializerdata
    def get_profile_photo(self, obj):
        return obj.profile_photo.url if obj.profile_photo else ""

    # def commented_posts(self, obj):
    #     return Posts.objects.filter(author=obj.user, )

class CommentChildSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(),source='parent.id')
    author = SerializerMethodField()
    avg_rate = serializers.ReadOnlyField()
    rated_by = SerializerMethodField()
    rate_count = serializers.ReadOnlyField()
    class Meta:
        model = Comment
        fields = ('author', 'content', 'id','parent_id', 'avg_rate', 'rate_count', 'rated_by')

    def get_author(self, obj):
        serializer = UserSerializer(obj.author, read_only=True)
        return serializer.data

    def create(self, validated_data):
        subject = parent.objects.create(parent=validated_data['parent']['id'], content=validated_data['content'])

    def get_rated_by(self, obj):
        rates = []
        for rate in obj.rates.filter(is_active=True):
            rates.append(rate)
        ratedata = RateSerializer(rates, many=True, read_only=True).data
        dict = {v["id"]: v for v in ratedata}
        return dict

class CommentSerializer(serializers.ModelSerializer):
    reply_count = SerializerMethodField()
    author = SerializerMethodField()
    replies = SerializerMethodField()
    # replies = CommentChildSerializer(many=True)
    avg_rate = serializers.ReadOnlyField()
    rated_by = SerializerMethodField()
    rate_count = serializers.ReadOnlyField()
    class Meta:
        model = Comment
        fields = ('id','content', 'author', 'reply_count', 'avg_rate', 'rate_count', 'rated_by', 'replies')
        depth = 1

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0

    def get_author(self, obj):
        serializer = UserSerializer(obj.author, read_only=True)
        return serializer.data

    def get_rated_by(self, obj):
        rates = []
        for rate in obj.rates.filter(is_active=True):
            rates.append(rate)
        ratedata = RateSerializer(rates, many=True, read_only=True).data
        dict = {v["id"]: v for v in ratedata}
        return dict

    def get_replies(self, obj):
        if obj.is_parent:
            data = CommentChildSerializer(obj.children(), many=True).data
            dict = {v["id"]: v for v in data}
            return dict
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField()
    parent = serializers.ReadOnlyField()
    class Meta:
        model = Comment
        fields = ('parent', 'content', 'post')

class CommentRateSerializer(serializers.ModelSerializer):
    comment_id = SerializerMethodField()
    class Meta:
        model = CommentRate
        fields = ('rate', 'comment_id')

    def get_comment_id(self, obj):
        return obj.id

class CommentDetailSerializer(serializers.ModelSerializer):
    replies = SerializerMethodField()
    author = SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'replies', 'post')
    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None

    def get_author(self, obj):
        return obj.author.username


class PostDetailSerializer(serializers.ModelSerializer):
    image = SerializerMethodField()
    video = SerializerMethodField()
    video_width = SerializerMethodField()
    video_height = SerializerMethodField()
    author = SerializerMethodField()
    comments = SerializerMethodField()
    avg_rate = serializers.ReadOnlyField()
    rate_count = serializers.ReadOnlyField()
    rated_by = SerializerMethodField()
    class Meta:
        model = Post
        fields = ('author', 'image', 'image_width', 'image_height', 'video', 'video_width', 'video_height', 'title', 'category','created_at', 'rate_count', 'rated_by', 'avg_rate', 'slug', 'comments')

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image

    def get_video(self, obj):
        try:
            video = obj.video.url
        except:
            video = None
        return video

    def get_video_width(self, obj):
        if(obj.video):
            vid = cv2.VideoCapture(obj.video.url)
            width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            return width
        return 0

    def get_video_height(self, obj):
        if(obj.video):
            vid = cv2.VideoCapture(obj.video.url)
            height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            return height
        return 0

    def get_author(self, obj):
        return obj.author.username

    def get_comments(self, obj):
        queryset = obj.comments.filter(parent__isnull=True)
        comments = CommentSerializer(queryset, many=True, read_only=True).data
        return comments

    def get_rated_by(self, obj):
        rates = []
        for rate in obj.rates.filter(is_active=True):
            rates.append(rate)
        ratedata = RateSerializer(rates, many=True, read_only=True).data
        return ratedata

class PostListSerializer(serializers.ModelSerializer):
    # url = post_detail_url
    author = SerializerMethodField()
    image = SerializerMethodField()
    video = SerializerMethodField()
    video_width = SerializerMethodField()
    video_height = SerializerMethodField()
    comments = SerializerMethodField()
    avg_rate = serializers.ReadOnlyField()
    rate_count = serializers.ReadOnlyField()
    rated_by = SerializerMethodField()
    category = SerializerMethodField()
    class Meta:
        model = Post
        fields = ('id','title', 'created_at', 'image', 'image_width', 'image_height', 'video', 'video_width', 'video_height', 'category', 'author', 'rate_count', 'rated_by', 'avg_rate', 'slug', 'comments')

    def get_author(self, obj):
        serializer = UserSerializer(obj.author, read_only=True)
        return serializer.data

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image

    def get_video(self, obj):
        try:
            video = obj.video.url
        except:
            video = None
        return video

    def get_video_width(self, obj):
        if(obj.video):
            vid = cv2.VideoCapture(obj.video.url)
            width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            return width
        return 0

    def get_video_height(self, obj):
        if(obj.video):
            vid = cv2.VideoCapture(obj.video.url)
            height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            return height
        return 0

    def get_comments(self, obj):
        queryset = obj.comments.filter(parent__isnull=True)
        comments = CommentSerializer(queryset, many=True, read_only=True).data
        dict = {v["id"]: v for v in comments}
        return dict

    def get_category(self, obj):
        return obj.category.title

    def get_rated_by(self, obj):
        rates = []
        for rate in obj.rates.filter(is_active=True):
            rates.append(rate)
        ratedata = RateSerializer(rates, many=True, read_only=True).data
        dict = {v["id"]: v for v in ratedata}
        return dict

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'category', 'image')


class PostRateSerializer(serializers.ModelSerializer):
    post_title = SerializerMethodField()
    class Meta:
        model = Rate
        fields = ('rate','post_title')

    def get_post_title(self, obj):
        return obj.post.slug


class RateSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()
    user_id = SerializerMethodField()
    profile_photo = SerializerMethodField()
    class Meta:
        model = Rate
        fields = ('id', 'rate', 'user', 'user_id', 'profile_photo')

    def get_user(self, obj):
        return obj.rater.username

    def get_user_id(self, obj):
        return obj.rater.id

    def get_profile_photo(self, obj):
        return (obj.rater.profile.profile_photo.url if obj.rater.profile.profile_photo else '')

class CommentRatedBySerializer(serializers.ModelSerializer):
    user = SerializerMethodField()
    user_id = SerializerMethodField()
    profile_photo = SerializerMethodField()
    class Meta:
        model = CommentRate
        fields = ('rate', 'user', 'user_id', 'profile_photo')

    def get_user(self, obj):
        return obj.rater.username

    def get_user_id(self, obj):
        return obj.rater.id

    def get_profile_photo(self, obj):
        return (obj.rater.profile.profile_photo.url if obj.rater.profile.profile_photo else '')
