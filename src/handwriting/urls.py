from django.urls import path
from . import views


app_name = 'handwriting'
urlpatterns = [
    path('digits/', views.digits, name='digits'),
    path('create_dataset/<str:label>', views.create_dataset, name='add_to_dataset'),
    path('images/<str:fk_id>/<str:angle>', views.show_dataset_image, name='images'),
    path('train', views.train, name='train'),
    path('', views.index, name='index'),
]
