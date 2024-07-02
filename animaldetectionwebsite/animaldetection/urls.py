from django.urls import path
from . import views

app_name = 'animaldetection'

urlpatterns = [
    path('', views.signin, name='signin'),
    path('signup/', views.signup, name="signup"),
    path('reset/', views.reset, name="reset"),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('last/', views.lastdocument, name='lastdocument'),
    path('all/', views.alldocuments, name='alldocuments')
]
