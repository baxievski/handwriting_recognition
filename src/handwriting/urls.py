from django.urls import path
from . import views


app_name = "handwriting"
urlpatterns = [
    path("predict/<str:dataset>", views.predict, name="predict"),
    path("create_dataset/<str:label>", views.create_dataset, name="add_to_dataset"),
    path("images/<str:fk_id>/<str:angle>", views.show_dataset_image, name="images"),
    path("", views.index, name="index"),
]
