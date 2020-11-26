from django.contrib import admin
from django.urls import path, include

from .views import (PostListAPIView,
                    PostByCategoryListAPIView,
                    PostCreateAPIView,
                    PostDetailAPIView,
                    PostDeleteAPIView,
                    PostRateAPIView,
                    PostRateUpdateAPIView,
                    CommentAPIView,
                    CommentDetailAPIView,
                    CommentCreateAPIView,
                    CommentReplyCreateAPIView,
                    CommentDeleteAPIView,
                    CommentRateAPIView,
                    CommentRateUpdateAPIView,
                    ProfileDetailAPIView,
                    ProfilePhotoUploadAPIView,
                    UserDetailAPIView,
                    UserListAPIView,
                    GetUserAPIView,
                    UserEditAPIView,
                    CheckEmailExistsAPIView)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    #POST
    path('', PostListAPIView.as_view(), name='home'),
    path('p/<int:categoryId>', PostByCategoryListAPIView.as_view(), name='post-by-category'),
    path('p/create/', PostCreateAPIView.as_view(), name='post-create'),
    path('p/rate/<int:post_id>', PostRateAPIView.as_view(), name='post-rate'),
    path('p/<slug:slug>/', PostDetailAPIView.as_view(), name='post-detail'),
    path('p/delete/<slug:slug>', PostDeleteAPIView.as_view(), name='post-delete'),
    path('p/rate/update/<int:post_id>', PostRateUpdateAPIView.as_view(), name='post-rate-update'),
    #COMMENT
    path('comments/', CommentAPIView.as_view(), name='comments'),
    path('comments/<int:pk>', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/rate', CommentRateAPIView.as_view(), name='comment-rate'),
    path('comments/<int:comment_id>/rate/update', CommentRateUpdateAPIView.as_view(), name='comment-rate'),
    path('comments/delete/<int:pk>', CommentDeleteAPIView.as_view(), name='comment-delete'),
    path('comments/create/<int:post_id>', CommentCreateAPIView.as_view(), name='comment-create'),
    path('comments/<int:pk>/reply', CommentReplyCreateAPIView.as_view(), name='comment-reply-create'),
    #USER
    path('user/', GetUserAPIView.as_view(), name='user-view'),
    path('users/', UserListAPIView.as_view(), name='user-list'), #using profile object!!
    path('user/<str:username>', UserDetailAPIView.as_view(), name='user-detail'),
    path('user/<str:username>/profile', ProfileDetailAPIView.as_view(), name='profile'),
    path('user/profile/addphoto', ProfilePhotoUploadAPIView.as_view(), name='profile-add-photo'),
    path('user/edit/', UserEditAPIView.as_view(), name='user-edit'),
    #TOKEN
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #AUTH
    path('email/<str:email>/', CheckEmailExistsAPIView.as_view(), name="check-email-exists"),

]
