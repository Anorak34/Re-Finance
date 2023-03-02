from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('buy/', views.buy, name='buy'),
    path('history/', views.history, name='history'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('quote/', views.quote, name='quote'),
    path('register/', views.register, name='register'),
    path('sell/', views.sell, name='sell'),
    path('add_cash/', views.add_cash, name='add_cash'),
    path('change_password/', views.change_password, name='change_password'),
    path('account/', views.account, name='account'),
]