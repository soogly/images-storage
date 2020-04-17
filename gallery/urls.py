from django.urls import path

from gallery.views import GalleryView, UploadImageView, delete_image

urlpatterns = [
    path('', GalleryView.as_view(), name="gallery"),
    path('upload/', UploadImageView.as_view(), name="upload"),
    path('delete/<img_hash>', delete_image, name="delete"),
]
