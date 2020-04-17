import io
from datetime import datetime

from celery import shared_task
import PIL.Image, PIL.ExifTags
import imagehash
from boto3.exceptions import (
    ResourceLoadException, ResourceNotExistsError, S3TransferFailedError, S3UploadFailedError
)

from django.core.files.uploadedfile import InMemoryUploadedFile

from gallery.utils import (
    get_exif_data, resize_image, save_to_s3,
    BUCKET_NAME, remove_from_s3
)
from gallery.models import Image


@shared_task
def handle_image(img_bin, image_title, image_info):

    img = InMemoryUploadedFile(io.BytesIO(img_bin), **image_info)
    img = PIL.Image.open(img)
    img_hash = imagehash.average_hash(img)

    # Проверяем не был ли файл загружен ранее
    exited_hashes = Image.objects.values_list('img_hash', flat=True)

    if str(img_hash) in list(exited_hashes):
        return 'Этот файл уже был загружен ранее'

    ext = img.format.lower()
    imagepath = f"user_id/{img_hash}.{ext}"

    # Сохраняем оригинальную картинку в хранилище
    try:
        save_to_s3(img, imagepath, ext)

    except (ResourceLoadException, ResourceNotExistsError,
            S3TransferFailedError, S3UploadFailedError) as e:
        return f'ОШИБКА сохранения: {e}'

    # Создаем миниатюру
    thumb = resize_image(img)

    # Сохраняем миниатюру
    thumb_path = "thumbs/" + imagepath
    try:
        save_to_s3(thumb, thumb_path, ext)
    except (ResourceLoadException, ResourceNotExistsError,
            S3TransferFailedError, S3UploadFailedError, ValueError) as e:

        # Удаляем ранее сохраненную картинку если не удалось сохранить миниатюру
        remove_from_s3(imagepath)

        return f'ОШИБКА сохранения миниатюры: {e}'

    # Получаем метаинфу о картинке
    exif_data = get_exif_data(img)

    creation_date = exif_data.get('DateTimeOriginal')
    if creation_date:
        creation_date = datetime.strptime(creation_date, "%Y:%m:%d %H:%M:%S")
    camera = exif_data.get('DeviceSettingDescription')

    # Делаем запись в базе
    Image.objects.create(title=image_title,
                         img_hash=img_hash,
                         camera=camera,
                         size=image_info["size"],
                         creation_date=creation_date,
                         url=f"{BUCKET_NAME}/{imagepath}",
                         thumb_url=f"{BUCKET_NAME}/thumbs/{imagepath}",
                         )

    return "Картинка успешно сохранена!"


@shared_task
def delete_image_task(img_hash):
    print("img_hash")
    print(img_hash)
    try:
        img = Image.objects.get(img_hash=img_hash)
    except Image.DoesNotExist:
        return 'wrong hash'
    imagepath = '/'.join(img.url.split('/')[1:])
    thumbpath = "thumbs/" + imagepath

    try:
        remove_from_s3(imagepath)
        remove_from_s3(thumbpath)
    except (ResourceLoadException, ResourceNotExistsError,
            S3TransferFailedError, S3UploadFailedError) as e:
        return 'ОШИБКА удаления из хранилища'

    img.delete()
    return 'success'
