from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenBlacklistView)

from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('create_superuser/', views.CreateSuperUser.as_view()),
    path('create_manager/', views.CreateManager.as_view()),
    path('create_employee/', views.CreateEmployee.as_view()),

    path('login/', views.EMAUserLogin.as_view()),
    path('logout/',views.Logout.as_view()),

    path('users_list/', views.UsersList.as_view()),
    path('employees/', views.Employees.as_view()),

    path('employee/<int:pk>', views.RetrieveUpdateDestroyEmployee.as_view()),

    path('forgot_password/<int:pk>', views.ForgotPassword.as_view()),
    path('reset_password/<int:pk>',views.ResetPassword.as_view()),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
