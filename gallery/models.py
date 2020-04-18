from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.


class Image(models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=250)
    img_hash = models.CharField(verbose_name=_("hash of image file"), max_length=250, null=True, unique=True)
    camera = models.CharField(verbose_name=_("camera"), max_length=250, blank=True, null=True)
    size = models.FloatField(verbose_name=_("size"), default=0.0)
    creation_date = models.DateTimeField(verbose_name=_("image created"), blank=True, null=True)
    upload_date = models.DateTimeField(verbose_name=_("image uploaded"), blank=True, null=True, auto_now=True)
    url = models.CharField(verbose_name=_("url"), max_length=850)
    thumb_url = models.CharField(verbose_name=_("thumbnail"), max_length=850)

    class Meta:
        get_latest_by = 'upload_date'
        ordering = ['-creation_date']
        indexes = [
            models.Index(fields=['img_hash']),
        ]

