from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import JsonResponse

from gallery.models import Image
from gallery.forms import ImageUploadForm
from gallery.tasks import handle_image, delete_image_task


class GalleryView(ListView):
    """
    GalleryView - class represents images uploaded by users
    """
    model = Image
    paginate_by = 100

    def get_context_data(self):
        context = super().get_context_data()
        context['gallery'] = 'active'
        return context


class UploadImageView(View):

    def get(self, request):
        context = {'upload': 'active'}
        template_name = "gallery/upload.html"
        return render(request, template_name, context)

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        import PIL.Image
        import io

        if form.is_valid():
            image = form.cleaned_data['image']
            image_title = request.POST['imageTitle']
            image_info = {"field_name": image.field_name,
                          "name": image.name,
                          "content_type": image.content_type,
                          "size": image.size,
                          "charset": image.charset,}
            print(image_info)
            result = handle_image.delay(image.read(), image_title, image_info)
            response = result.get()
            return JsonResponse({"message": response})
        else:
            return JsonResponse({"message": "Ошибка: Проверьте введеные данные и попробуйте снова."
                                            "Файл должен быть изображением"})


def delete_image(request, img_hash):
    print("img_hash 1")
    print(img_hash)
    if request.method == "POST":
        status = delete_image_task.delay(img_hash)
        return JsonResponse({"status": status.get()})

