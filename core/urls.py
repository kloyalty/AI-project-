from django.urls import path
from . import views

urlpatterns = [
    # Main flow
    path('', views.landing, name='landing'),
    path('select/', views.select_type, name='select_type'),
    path('reflection/', views.reflection, name='reflection'),
    path('review/', views.review, name='review'),
    path('print/', views.print_agreement, name='print_agreement'),
    path('photo/', views.photo, name='photo'),
    path('complete/', views.complete, name='complete'),
    
    # API endpoints
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/generate/', views.generate_agreement_view, name='generate_agreement'),
    
    # Archive
    path('archive/', views.archive, name='archive'),
]