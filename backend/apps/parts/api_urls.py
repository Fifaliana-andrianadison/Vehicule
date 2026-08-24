from django.urls import path
from apps.parts import api

app_name = 'parts_api'

urlpatterns = [
    path('', api.part_list, name='list'),
    path('categories/', api.part_categories, name='categories'),
    path('<int:pk>/', api.part_detail, name='detail'),
    path('<int:pk>/compatibilities/', api.add_compatibility, name='compatibility'),
]