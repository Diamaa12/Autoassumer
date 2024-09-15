from xml.dom import ValidationErr
from PIL import Image

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm
from django import forms

from Site.models import AappgCustomUser, AappgArticlesPost


class AappgCustomUserModelForm(UserCreationForm):
    class Meta:
        model = AappgCustomUser
        fields = ('user',
                  'email',
                  'password',
                  'telephone',
                  'city',
                  'poste',
                  )

class AappgArticleForm(ModelForm):
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # Extracted a constant for max image size

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'article ici'}),
        required=True
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenu de l\'article ici'}),
        required=True
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*;'}),
        required=False
    )
    video = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': '(URL Youtube ou Vimeo)'}),
        required=False
    )

    class Meta:
        fields = ['title', 'content', 'image', 'video']
        model = AappgArticlesPost

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaned_data = None

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # Ajoutez vos validations spécifiques pour le champ title
        if len(title) < 5:
            raise forms.ValidationError("Le titre doit comporter au moins 5 caractères.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError('Un article doit comporter au moin une phrase.')
        return content

    def clean_url(self):
        url = self.cleaned_data.get('video')
        if url:
            if not url.startswith(('http://', 'https://')):
                raise forms.ValidationError('L’URL doit commencer par http:// ou https://')
        return url
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            self._validate_image(image)
        return image

    def _validate_image(self, image):
        """Méthode extraite pour valider l'image."""
        if image.size > self.MAX_IMAGE_SIZE:
            raise ValidationError(f"L'image ne doit pas dépasser {self.MAX_IMAGE_SIZE / (5 * 1024 * 1024)} MB.")
        try:
            # Utilise Pillow pour ouvrir et valider l'image
            img = Image.open(image)
            img.verify()  # Vérifie si l'image est valide
        except (IOError, SyntaxError):
            raise ValidationError('Le fichier téléchargé doit être une image valide.')
class AappgArticleEditForm(forms.ModelForm):
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # Extracted a constant for max image size
    class Meta:
        model = AappgArticlesPost
        fields = ['title', 'content', 'image', 'video']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
    def clean_title(self):
        title = self.cleaned_data.get('title')
        # Ajoutez vos validations spécifiques pour le champ title
        if len(title) < 5:
            raise forms.ValidationError("Le titre doit comporter au moins 5 caractères.")
        return title
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError('Un article doit comporter au moin une phrase.')
        return content

    def clean_image(self):
        image = self.cleaned_data.get('image', None)
        if image:
            self._validate_image(image)
            return image
        else:
            return None

    def _validate_image(self, image):
        """Méthode extraite pour valider l'image."""
        if image.size > self.MAX_IMAGE_SIZE:
            raise ValidationError(f"L'image ne doit pas dépasser {self.MAX_IMAGE_SIZE / (5 * 1024 * 1024)} MB.")
        try:
            # Utilise Pillow pour ouvrir et valider l'image
            img = Image.open(image)
            img.verify()  # Vérifie si l'image est valide
        except (IOError, SyntaxError):
            raise ValidationError('Le fichier téléchargé doit être une image valide.')
    def clean_url(self):
        url = self.cleaned_data.get('video')
        if url:
            if not url.startswith(('http://', 'https://')):
                raise forms.ValidationError('L’URL doit commencer par http:// ou https://')
        return url