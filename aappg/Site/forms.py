from xml.dom import ValidationErr
from PIL import Image

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, EmailValidator, RegexValidator
from django.forms import ModelForm
from django import forms
import re

from Site.models import AappgCustomUser, AappgArticlesPost


class AappgCustomUserModelForm_backup(UserCreationForm):
    class Meta:
        model = AappgCustomUser
        fields = ('user',
                  'email',
                  'password',
                  'telephone',
                  'city',
                  'poste',
                  )


class AappgCustomUserModelForm_save(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AappgCustomUser
        fields = ('user', 'email', 'password', 'telephone', 'city', 'poste',)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data

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


class AappgCustomUserModelForm(forms.ModelForm):
    class Meta:
        model = AappgCustomUser
        fields = ('user',
                  'email',
                  'password',
                  'telephone',
                  'city',
                  'poste',
                  )
    user = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'user-id',
            'name': 'user',
            'placeholder': 'Votre prénom & nom '
        })
    )
    email = forms.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")],
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'text-field w-input"',
            'id': 'email-id',
            'name': 'email',
            'placeholder': 'Votre mail '
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'text-field w-input"',
            'id': 'password-id',
            'name': 'password',
            'placeholder': 'Mot de passe '
        }),
        required=True,
        min_length=6,
        max_length=100
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'text-field w-input"',
            'id': 'confirm-pass',
            'name': 'confirm-pass',
            'placeholder': 'Repeat password '
        }),
        required=True,
        min_length=6,
        max_length=100
    )
    telephone = forms.CharField(
        max_length=15,
        required=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                   message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'telephone-id',
            'name': 'telephone',
            'placeholder': 'Votre numéro de Tél'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'city-id',
            'name': 'city',
            'placeholder': 'Ville '
        })
    )
    poste = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'poste-id',
            'name': 'poste',
            'placeholder': 'Le poste que vous occupez  '
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        #S'assurer que l'email entré est disponible, et n'a pas été encore pris
        if AappgCustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé, veillez-en choisir un autre.")
        # Regular expression for validating an email
        regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$'

        # Check if email matches the regex
        if not re.match(regex, email):
            raise forms.ValidationError("Entrez un email au format valide.")

        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone.startswith('+'):
            raise forms.ValidationError("Le numéro de téléphone doit commencer par '+'.")
        return telephone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Les mots de passe ne correspond pas.")
            if len(password) < 5:
                raise forms.ValidationError("Le mot de passe doit comporter au moins 8 caractères")

        return cleaned_data

class UserProfileForm(forms.Form):
    user = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'user-id',
            'name': 'user',
            'placeholder': 'Votre prenom & nom '
        })
    )
    email = forms.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")],
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'text-field w-input"',
            'id': 'email-id',
            'name': 'email',
            'placeholder': 'Votre mail '
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'text-field w-input"',
            'id': 'password-id',
            'name': 'password',
            'placeholder': 'Mot de passe '
        }),
        required=True,
        min_length=6,
        max_length=100
    )
    telephone = forms.CharField(
        max_length=15,
        required=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                   message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'telephone-id',
            'name': 'telephone',
            'placeholder': 'Votre numéro de Tél'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'city-id',
            'name': 'city',
            'placeholder': 'Ville '
        })
    )
    poste = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'text-field w-input"',
            'id': 'poste-id',
            'name': 'poste',
            'placeholder': 'Le poste que vous occupez  '
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if "example.com" not in email:
            raise forms.ValidationError("We only accept emails from 'example.com' domain.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone.startswith('+'):
            raise forms.ValidationError("Phone number must start with a '+'.")
        return telephone