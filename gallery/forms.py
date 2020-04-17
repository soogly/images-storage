from django import forms


class ImageUploadForm(forms.Form):
    """Image upload form."""
    title = forms.CharField
    image = forms.ImageField()
