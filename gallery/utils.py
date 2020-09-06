import io
import os
import PIL.ExifTags, PIL.Image
import boto3
from botocore.exceptions import ClientError


def get_exif_data(img):

    exif_data_pil = img._getexif()

    exif_data = {}

    for k, v in PIL.ExifTags.TAGS.items():

        if exif_data_pil and k in exif_data_pil:
            value = exif_data_pil[k]
        else:
            value = None

        if len(str(value)) > 64:
            value = str(value)[:65] + "..."

        exif_data[v] = value
    return exif_data


def resize_image(img):
    basewidth = 300
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    return img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)


"""
STORAGE UTILS 
"""

ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

BUCKET_NAME = 'users-images'


s3 = boto3.resource('s3',
                    endpoint_url=ENDPOINT_URL,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    )


content_types_map = {'png': 'image/png',
                     'jpeg': 'image/jpg',
                     'gif': 'image/gif',
                     }


def save_to_s3(img, filepath, ext):

    try:
        s3.meta.client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET_NAME)

    origin_buf = io.BytesIO()
    img.save(origin_buf, format=ext)
    origin_buf.seek(0)

    # Сохраняем оригинальную картинку в хранилище
    s3.Bucket(BUCKET_NAME).put_object(ACL='public-read',
                                      Key=filepath,
                                      Body=origin_buf,
                                      ContentType=content_types_map.get(ext)
                                      )


def remove_from_s3(filepath):
    s3.Bucket(BUCKET_NAME).delete_objects(
        Delete={
            'Objects': [
                {
                    'Key': filepath,
                }
            ]
        },
    )
