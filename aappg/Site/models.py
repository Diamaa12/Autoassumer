import uuid

from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string

# Create your models here.

'''UserManger.
'''


class AappgCustomUserManger(BaseUserManager):
    #Creation de la fonction qui inscrive les utilisateurs dans le Models
    def create_user(self,  user, email,  password, telephone, city, poste):
        if not email:
            raise ValueError("L'Adresse Email est obligatoire.")
        user = self.model( user= user, email=email, telephone=telephone, city=city, poste=poste)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.save()
        return user
    #Creation de superuser
    def create_superuser(self,  user, email, password, telephone, city,  poste):
        user = self.create_user( user=user, email=email,  password=password, telephone=telephone, city=city, poste=poste)
        user.is_superuser = True
        user.save()
        return user
    #Recuperation de l'utilisateur
    def recup_user_name(self, user):
        usr = AappgCustomUser.objects.get(user=user)
        return usr


'''Classe de création d'utilisateur
dans l'administration.
'''
class AappgCustomUser(AbstractBaseUser, PermissionsMixin):
    #Les champs que contient la base de données

    user = models.CharField(max_length=60, blank=False)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=255, blank=False)
    telephone = models.CharField(max_length=255, blank=True, default='224 666 66 66')
    city = models.CharField(max_length=255, blank=False, default='Lelouma')
    poste = models.CharField(max_length=255, blank=True)


    #Gerer les groupes
    groupes = models.ManyToManyField(Group)

    #Les champs requis
    REQUIRED_FIELDS = ['user', 'password', 'telephone', 'city', 'poste']
    #Le username obligatoire
    USERNAME_FIELD = 'email'

    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(blank=True, null=True, unique=True)
    email_verification_expiration = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=1), null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    #Initialisation de Manager
    objects = AappgCustomUserManger()

    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

    def is_token_expired(self):
        if not self.email_verification_token:
            return True
        return timezone.now() > self.email_verification_expiration

class AappgCustomGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(AappgCustomUser, related_name='custom_groups')

#Gestions d'articles du site
class AappgArticlesPost(models.Model):
    CATEGORY_CHOICES = [
        ('politique', 'Politique'),
        ('societe', 'Société'),
        ('economie', 'Économie'),
        ('guinee', 'Guinée'),
        ('diaspora', 'Diaspora'),
        ('communaute', 'Communauté'),
        ('histoire', 'Histoire'),
    ]

    author = models.ForeignKey(AappgCustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='politique')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.URLField(blank=True, null=True)  # Stockage d'URL de vidéos (par exemple, YouTube)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
class AappgCommunique(models.Model):
    author = models.ForeignKey(AappgCustomUser, on_delete=models.CASCADE)
    titre = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
