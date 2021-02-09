from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic.base import TemplateView

from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.views import LoginView
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.app_settings import (JWTSerializer, TokenSerializer,
                                       create_token)

from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings

from fcm_django.models import FCMDevice

from .notifications import send_notification, send_silent_notification
from .permissions import IsOwnerOrReject
from posts.models import Post, Rate, Category
from users.models import CustomUser, Profile
from comments.models import Comment, CommentRate
from .serializers import (PostDetailSerializer,
                          PostCreateSerializer,
                          PostRateSerializer,
                          RateSerializer,
                          PostListSerializer,
                          CommentCreateSerializer,
                          CommentDetailSerializer,
                          CommentRateSerializer,
                          CommentRatedBySerializer,
                          CommentSerializer,
                          CommentChildSerializer,
                          UserLoginSerializer,
                          UserSerializer,
                          UserEditSerializer,
                          ProfileDetailSerializer,
                          ProfileListSerializer,
                          ProfilePhotoUploadSerializer,
                          ProfileLanguageUpdateSerializer,
                          FCMDeviceSerializer)



class UserLoginAPIView(LoginView):
    def get_response(self):
        serializer_class = self.get_response_serializer()
        data = {
            'user': self.user,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
        serializer = serializer_class(instance=data,
                                      context=self.get_serializer_context())

        response = Response(serializer.data, status=status.HTTP_200_OK)
        cookie_name = "refresh_token"
        cookie_secure = True
        cookie_httponly = True
        cookie_samesite = 'Strict'
        domain = "127.0.0.1"
        from rest_framework_simplejwt.settings import api_settings as jwt_settings
        if cookie_name:
            from datetime import datetime
            expiration = (datetime.utcnow() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            response.set_cookie(
                cookie_name,
                self.refresh_token,
                expires=expiration,
                secure=cookie_secure,
                httponly=cookie_httponly,
                samesite=cookie_samesite,
                domain=domain
            )
        return response

class UserRegisterAPIView(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        user.save()
        if allauth_settings.EMAIL_VERIFICATION != \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            if getattr(settings, 'REST_USE_JWT', False):
                self.access_token, self.refresh_token = jwt_encode(user)
            else:
                create_token(self.token_model, user, serializer)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user

class CustomPaginationAPIView(PageNumberPagination):
    # page_size = 1
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    # max_page_size = 1


class PostListAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPaginationAPIView

# Use /?q=atabaris(post owner) or /?q=new post(post title) to get the post
    def get_queryset(self, *args, **kwargs):
        queryset_list = Post.objects.all()
        query_category = self.request.GET.get("category")
        if query_category:
            queryset_list = queryset_list.filter(
                Q(category__title__icontains = query_category)
            ).distinct()
        query_title = self.request.GET.get("search")
        if query_title:
            queryset_list = queryset_list.filter(
                Q(title__istartswith = query_title)
            ).distinct()
        # dict = {v["id"]: v for v in queryset_list}
        return queryset_list

class PostByCategoryListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    lookup_field = ('category')
    lookup_url_kwargs = ('categoryId')
    queryset = Post.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset_list = Post.objects.filter(category=self.kwargs.get('categoryId'))
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__istartswith = query)
            ).distinct()
        return queryset_list

class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    parser_classes = (MultiPartParser,) #FormParser

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return Response({
                'detail': 'User was not provided!'
            }, status=status.HTTP_400_BAD_REQUEST)
        title = request.data.get("title")
        image = request.data.get("image")
        video = request.data.get("video")
        category_id = request.data.get("category")
        category = Category.objects.get(id=category_id)
        if image:
            obj = Post.objects.create(author=user, title=title, image=image, category=category)
        else:
            obj = Post.objects.create(author=user, title=title, video=video, category=category)
        obj.save()
        serializer = PostListSerializer(obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    lookup_field = ('pk')
    permission_classes = [AllowAny]


#FIX THAT LATER!
class PostDeleteAPIView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = 'slug'


class PostRateAPIView(generics.CreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('post')
    lookup_url_kwargs = ('post_id')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        title = post.author.username
        en_message = '{username} rated your post!'.format(username=self.request.user.username)
        tr_message = '{username} gönderinizi puanladı!'.format(username=self.request.user.username)
        data = { 'link': 'rateet://app/post-detail/' + str(post.id) }
        user = self.request.user
        if post.author.pk != user.pk:
            if post.author.profile.language == 'en':
                send_notification(user_id=post.author.pk, title=title, message=en_message, data=data)
            else:
                send_notification(user_id=post.author.pk, title=title, message=tr_message, data=data)
        serializer.save(rater=user, post=post)


class PostRateUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('post')
    lookup_url_kwargs = ('post_id')

    def get_object(self):
         queryset = self.get_queryset()
         post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
         obj = queryset.filter(post=post, rater=self.request.user).get()
         serializer = PostRateSerializer(obj)
         title = post.author.username
         # message = '{username} rated your post!'.format(username=self.request.user.username)
         # send_notification(user_id=post.author.pk, title=title, message=message, data=data)
         data = { 'link': 'rateet://app/post-detail/' + str(post.id) }
         if post.author.pk != self.request.user.pk:
            send_silent_notification(user_id=post.author.pk, data=data)
         return obj

class CommentRateUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = CommentRate.objects.all()
    serializer_class = CommentRatedBySerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('comment')
    lookup_url_kwargs = ('comment_id')

    def get_object(self):
         queryset = self.get_queryset()
         comment = get_object_or_404(Comment, id=self.kwargs.get('comment_id'))
         obj = queryset.filter(comment=comment, rater=self.request.user).get()
         serializer = CommentRateSerializer(obj)
         title = comment.author.username
         # message = '{username} rated your comment!'.format(username=self.request.user.username)
         # send_notification(user_id=comment.author.pk, title=title, message=message, data=data)
         data = { 'link': 'rateet://app/post-detail/' +  str(comment.post.id) + '/comment/' + str(comment.id)}
         if comment.author.pk != self.request.user.pk:
            send_silent_notification(data=data)
         return obj

class CommentAPIView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Comment.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(content__icontains = query) |
                Q(author__username__icontains = query)
            ).distinct()
        return queryset_list

class GetPostCommentsAPIView(generics.ListAPIView):
    lookup_field = ('post')
    lookup_url_kwargs = ('post_id')
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.filter(parent=None)

class CommentCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('post')
    lookup_url_kwargs = ('post_id')

    # def perform_create(self,serializer):
    #     post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
    #     serializer.save(author=self.request.user, post=post)

    def create(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        if not post_id:
            return Response({
                'detail': 'Post was not provided!'
            }, status=status.HTTP_400_BAD_REQUEST)
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if not user:
            return Response({
                'detail': 'User was not provided!'
            }, status=status.HTTP_400_BAD_REQUEST)
        content = request.data.get("content")
        obj = Comment.objects.create(author=user, post=post, content=content)
        obj.save()
        serializer = CommentSerializer(obj)
        title = post.author.username
        en_message = '{username} commented to your post!'.format(username=user.username)
        tr_message = '{username} gönderinize yorum yaptı!'.format(username=user.username)
        data = { 'link': 'rateet://app/post-detail/' + str(post.id) + '/comment/' + str(obj.id)}
        if post.author.pk != user.pk:
            if post.author.profile.language == 'en':
                send_notification(user_id=post.author.pk, title=title, message=en_message, data=data)
            else:
                send_notification(user_id=post.author.pk, title=title, message=tr_message, data=data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentReplyCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('pk')

    def create(self, request, *args, **kwargs):
        parent_id = kwargs.get('pk')
        parent = get_object_or_404(Comment, id=parent_id)
        if not parent:
            return Response({
            'detail': 'Parent was not provided!'
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        if not user:
            return Response({
                'detail': 'User was not provided!'
            }, status=status.HTTP_400_BAD_REQUEST)
        content = request.data.get('content')
        obj = Comment.objects.create(author=user, post=parent.post, content=content, parent=parent)
        serializer = CommentChildSerializer(obj)
        title = parent.author.username
        en_message = '{username} replied to your comment!'.format(username=user.username)
        tr_message = '{username} yorumunuzu cevapladı!'.format(username=user.username)
        data = { 'link': 'rateet://app/post-detail/' + str(parent.post.id) + '/comment/' + str(parent.id) + '/reply/' + str(obj.id)}
        if user.pk != parent.author.pk:
            if parent.author.profile.language == 'en':
                send_notification(user_id=parent.author.pk, title=title, message=en_message, data=data)
            else:
                send_notification(user_id=parent.author.pk, title=title, message=tr_message, data=data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentRateAPIView(generics.CreateAPIView):
    queryset = CommentRate.objects.all()
    serializer_class = CommentRatedBySerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    lookup_field = ('comment')
    lookup_url_kwargs = ('comment_id')

    def perform_create(self, serializer):
        comment = get_object_or_404(Comment, id=self.kwargs.get('comment_id'))
        title = comment.author.username
        en_message = '{username} rated your comment!'.format(username=self.request.user.username)
        tr_message = '{username} yorumunuzu puanladı!'.format(username=self.request.user.username)
        data = { 'link': 'rateet://app/post-detail/' + str(comment.post.id) + '/comment/' + str(comment.id)}
        user = self.request.user
        if comment.author.pk != user.pk:
            if comment.author.profile.language == 'en':
                send_notification(user_id=comment.author.pk, title=title, message=en_message, data=data)
            else:
                send_notification(user_id=comment.author.pk, title=title, message=tr_message, data=data)
        serializer.save(rater=user, comment=comment)

#FIX THAT LATER!
class CommentDeleteAPIView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]

class CommentDetailAPIView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer
    lookup_field = ('pk')

class UserListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Profile.objects.all()
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(user__username__istartswith = query)
            ).distinct()
        return queryset_list

class GetUserAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = CustomUser.objects.all()

    def get_object(self):
        obj = get_object_or_404(get_user_model(),username=self.kwargs['username'])
        return obj

class UserEditAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserEditSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated | IsAdminUser]

    def get_object(self):
           return self.request.user

class ProfileDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProfileDetailSerializer
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(Profile, user__username=self.kwargs['username'])
        self.check_object_permissions(self.request, obj)
        return obj

class ProfilePhotoUploadAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilePhotoUploadSerializer
    # permission_classes = [IsAuthenticated | IsAdminUser]
    parser_classes = (MultiPartParser,)

    def get_object(self):
        obj = get_object_or_404(Profile, user = self.request.user.id)
        return obj

class ProfileLanguageUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileLanguageUpdateSerializer

    def get_object(self):
        obj = get_object_or_404(Profile, user = self.request.user.id)
        return obj

class CheckEmailExistsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        try:
            user = CustomUser.objects.get(email=email)
        except user.DoesNotExist:
            return Response(data={'message': 'valid'})
        else:
            return Response(data={'message': 'not-valid'})

class DeleteFCMDeviceAPIView(generics.RetrieveDestroyAPIView):
    lookup_field = 'fcm_token'
    serializer_class = FCMDeviceSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(FCMDevice, registration_id=self.kwargs['fcm_token'])
        return obj

class PrivacyPolicyView(TemplateView):
    template_name='termsANDpolicy/privacy_policy.html'

#FOR AUTHENTICATE USER AFTER PASSWORD RESET
#CAN BE USED LATER
#class PasswordResetConfirmView(PasswordResetConfirmView):
    #post_reset_login = True
    #post_reset_login_backend = None
