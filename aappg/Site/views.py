import datetime
import urllib
import uuid
from lib2to3.fixes.fix_input import context
from tempfile import template
from urllib.parse import urlencode

import sentry_sdk
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.transaction import commit
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.views.decorators.cache import cache_control

from Site.forms import AappgCustomUserModelForm, AappgArticleForm, AappgArticleEditForm, UserProfileForm, \
    AappgCommuniqueForm
from Site.models import AappgCustomUser, AappgCustomGroup, AappgArticlesPost, AappgCommunique


# Create your views here.
def test_form(request):
    template_name = 'test.html'
    context = {}
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Traiter les données du formulaire propres à l'application
            # Par exemple, sauvegarder dans la base de données ou effectuer d'autres actions
            return redirect('success_url')
    else:
        form = UserProfileForm()
        context['form'] = form
    return render(request, template_name=template_name, context=context)


#Admin Inscription
def aappg_admin_inscription_save(request):
    template_name = 'aappg_admin/inscription.html'
    context = {}
    formulaire = AappgCustomUserModelForm()
    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get("email")
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        tel = request.POST.get('tel')
        city = request.POST.get('city')
        poste = request.POST.get('poste')

        #On verifie si l'email n'est pas déjá utilisé par un autre
        email_exists = AappgCustomUser.objects.filter(email=email).exists()

        print(name, email)
        if password == confirm_password:
            if len(password) > 5:
                if not email_exists:
                    email_verification_token = uuid.uuid4()
                    user = AappgCustomUser.objects.create_user(user=name,
                                                        email=email,
                                                        password=confirm_password,
                                                        telephone=tel,
                                                        city=city,
                                                        poste=poste,
                                                        email_verification_token=email_verification_token,
                                                       )
                    if user:
                        #On desactive certains fonctionnalité en attendant que l'email soit verifiés
                        user.is_active = False
                        user.is_staff = False
                        user.save()
                        # Générer l'URL de vérification et le message
                        token = str(user.email_verification_token)
                        params = urlencode({'token': token})
                        verification_url = f"{request.scheme}://{request.get_host()}/aappg/admin/verify-email/?{params}"
                        message = f"Veuillez vérifier votre email en cliquant sur ce lien: {verification_url}"
                        print(token, message)
                        # Envoyer

                        mail_sender = send_mail(
                            "Verifier Votre email",
                            message,
                            "m-cherif@leyssare.net",
                            [user.email,],
                            fail_silently=False,
                        )
                        if mail_sender:
                            print("l'email est envoyé avec succés. ")
                            context['mail'] = "l'email est envoyé avec succés. "
                        else:
                            print("Une erreur s'est produite pendant l'envoie de mail.")

                        context['succes'] = 'User has bin registrer with succes'
                        return redirect('my_site:email_verification_sent')
                else:
                    context["error"] = "L'email est déjá utilisé, veillez en choisir un autre"

                #context['succes'] = 'Utilsateur crée avec succés.'

                #pdf = pdf_generator()
                #context['pdf'] = pdf

                #return render(request, template_name=template_name, context=context)
            else:
                context['error'] = 'Le mot de passe doit avoir 5 caratétres minimum.'
                return render(request, template_name=template_name, context=context)
        else:
            context['error'] = 'Les mots de passe ne correspondent pas.'
            return render(request, template_name=template_name, context=context)


    context['form'] = formulaire
    return render(request, template_name=template_name, context=context)

# views.py

def aappg_admin_inscription_backup(request):
    template_name = 'aappg_admin/inscription.html'
    context = {}
    if request.method == 'POST':
        formulaire = AappgCustomUserModelForm(request.POST)
        if formulaire.is_valid():
            user = AappgCustomUser(
                user=formulaire.cleaned_data['user'],
                email=formulaire.cleaned_data['email'],
                password=formulaire.cleaned_data['password'],
                telephone=formulaire.cleaned_data['telephone'],
                city=formulaire.cleaned_data['city'],
                poste=formulaire.cleaned_data['poste']
            )
            user.save()
            # Générer l'URL de vérification et le message
            token = user.email_verification_token
            params = urlencode({'token': token})
            verification_url = f"{request.scheme}://{request.get_host()}/aappg/admin/verify-email/?{params}"
            message = f"Veuillez vérifier votre email en cliquant sur ce lien: {verification_url}"
            print(token, message)
            # Envoyer l'email de vérification
            mail_sender = send_mail(
                "Vérifiez votre email",
                message,
                "m-cherif@leyssare.net",
                [user.email],
                fail_silently=False,
            )
            if mail_sender:
                context['mail'] = "L'email a été envoyé avec succès."
            else:
                context['error'] = "Une erreur s'est produite pendant l'envoi de l'email."

            context['success'] = "L'utilisateur a été enregistré avec succès."
            return redirect('my_site:email_verification_sent')
        else:
            context['form'] = formulaire
            print(context.values())
    else:
        formulaire = AappgCustomUserModelForm()

    context['form'] = formulaire
    return render(request, template_name, context)


def aappg_admin_inscription(request):
    template_name = 'aappg_admin/inscription.html'
    context = {}
    if request.method == 'POST':
        formulaire = AappgCustomUserModelForm(request.POST)
        if formulaire.is_valid():
            user = formulaire.save(commit=False)
            user.is_active = False  # Désactiver l'utilisateur jusqu'à ce qu'il vérifie son email
            user.is_staff = False
            #On ajoute le token de verification d'email et son expiration,
            #On hash le mot de passe avant de le sauvgarder.
            user.email_verification_token = uuid.uuid4()
            user.email_verification_expiration = timezone.now() + timezone.timedelta(days=2)
            user.set_password(formulaire.cleaned_data['password'])
            user.save()
            # Générer l'URL de vérification et le message
            token = str(user.email_verification_token)
            params = urlencode({'token': token})
            #verification_url = f"{request.scheme}://{request.get_host()}/aappg/admin/verify-email/?{params}"
            verification_url = request.build_absolute_uri(
                reverse('my_site:verify-email', kwargs={'token': user.email_verification_token})
            )
            message = f"Veuillez vérifier votre email en cliquant sur ce lien: {verification_url}"
            print(token, message)
            # Envoyer l'email de vérification
            mail_sender = send_mail(
                "Vérifiez votre email",
                message,
                "m-cherif@leyssare.net",
                [user.email],
                fail_silently=False,
            )
            if mail_sender:
                context['mail'] = "L'email a été envoyé avec succès."
            else:
                context['error'] = "Une erreur s'est produite pendant l'envoi de l'email."

            context['success'] = "Un email de confirmation a été envoyé. Veuillez vérifier votre email."
            return redirect('my_site:email_verification_sent')
        else:
            context['form'] = formulaire
            print(context.values())
    else:
        formulaire = AappgCustomUserModelForm()

    context['form'] = formulaire
    return render(request, template_name, context)


def email_verification_sent(request):
    template_name = 'aappg_admin/email_verification_sent.html'
    return render(request, template_name=template_name)
#Verification d'email
# views.py
def email_verified_success(request):
    template_name = 'aappg_admin/email_verification_success.html'
    context = {}
    return render(request, template_name=template_name)
def email_verification(request, token):
    # Vérifiez que le token est bien passé dans l'URL
    if not token:
        return HttpResponse("Token manquant.", status=400)

    user = get_object_or_404(AappgCustomUser, email_verification_token=token)

    template_name = 'aappg_admin/email_verification_success.html'
    context = {}

    if user.is_token_expired():
        context['error'] = "Le lien de vérification a expiré."
        user.email_verification_token = None
        user.email_verification_expiration = None
    else:
        # Activer l'utilisateur et marquer l'email comme vérifié
        user.is_active = True
        user.is_staff = True
        user.email_verified = True

        user.save()  # Sauvegarder les modifications

        sentry_sdk.capture_message(f"{user.user} vient de crée son compte sur aapp-guinee.org", level="error")
        context['success'] = "Votre email a été vérifié avec succès. Vous pouvez maintenant vous connecter."
        #return redirect('my_site:success_email_verification')

    return render(request, template_name=template_name, context=context)

#Admin connexion

#empecher la mis en cache de formulaie pour ainsi éviter les erreurs de csrf_token
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def aappg_admin_connexion(request):

    template_name = "aappg_admin/login.html"
    context = {}
    if request.method == 'POST':
        mail = request.POST.get('email')
        password = request.POST.get('password')

        if AappgCustomUser.objects.filter(email=mail).exists():
            username = authenticate(email=mail, password=password)
            if username:
                login(request, username)
                # On recupere les sessions de l'utilisateur
                request.session['user_name'] = username.user
                request.session['user_email'] = username.email
                request.session['user_poste'] = username.poste
                request.session['user_city'] = username.city
                request.session['user_tel'] = username.telephone
                print(username)

                session_expired = request.session.get('session_expired', 0)
                print(session_expired)
                context['session_expired'] = session_expired
                # On recupère les keys correspondants à la variable request.session['user_name] defini en haut
                context['session_name'] = request.session.get('user_name')
                context['session_email'] = request.session.get('user_email')
                context['session_city'] = request.session.get('user_city')
                context['session_poste'] = request.session.get('user_poste')
                context['session_tel'] = request.session.get('user_tel')

                if 'session_expired' not in request.session:
                    request.session['session_expired'] = 1
                else:
                    request.session['session_expired'] += 1

                for i in request.POST:
                    print(i)
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('my_site:admin-page')

            context['error'] = f'Le mot de passe est incorrect.'
            return render(request, template_name=template_name, context=context)
        else:
            context['error'] = 'Votre email est incorrect. '
            return render(request, template_name=template_name, context=context)
    else:
        context['login_required'] = 'Veillez vous connecter d abord pour acceder à cette page. '
        # Vérifiez si la session à expirer
        # Cette condition permet d'afficher un message à l'utilsateur en L'indiquant qu'il a éte deconnecté parceque sa session a expiré
        session_expirer = request.session.get('session_expired')
        print(f"voici le resultat {session_expirer}")
        if session_expirer:
            context['session_expired'] = "Votre session a expiré en raison de l'inactivité."
            print(context.values())
            del request.session['session_expired']  # Supprimer l'indicateur après avoir montré le message
    return render(request, template_name, context=context)


def logout_view(request):
    template_name = "aappg_admin/login.html"
    if request.user:

        logout(request)
    context = {'data':'Vous etes deconnecter'}
    return render(request, template_name=template_name, context=context)
def test(request):
    template_name = 'test.html'

    # Récupérer toutes les permissions
    permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')

    # Dictionnaire pour stocker les utilisateurs par permissions
    users_by_permission = {permission: [] for permission in permissions}

    # Récupérer tous les utilisateurs
    users = AappgCustomUser.objects.all()

    # Assigner les utilisateurs à leurs permissions
    for user in users:
        user_permissions = set(user.user_permissions.all())
        group_permissions = set(Permission.objects.filter(group__user=user))
        all_permissions = user_permissions | group_permissions

        for permission in all_permissions:
            users_by_permission[permission].append(user)

    context = {
        'users_by_permission': users_by_permission,
    }

    return render(request, template_name=template_name, context=context)
def pagination_test(request):
    template_name = 'pagination_by_content_test.html'
    context = {}
    posts = AappgArticlesPost.objects.order_by('-created_at')
    context['newest_posts'] = posts.first()
    context['older_posts'] = posts[1:]
    # Systéme de pagination
    paginator = Paginator(posts, 8)

    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # Exclure le dernier article publié si on est sur la première page
    if page in [None, '1']:
        articles = posts[1:]
        paginator = Paginator(articles, 8)
        page_obj = paginator.get_page(page)
    context['page_obj'] = page_obj
    return render(request, template_name, context)
def index(request):
    template_name = 'index.html'
    context = {'value':'My site'}
    return render(request, template_name=template_name, context=context)
def aappg_home(request):
    template_name = 'base.html'
    context = {'data':'value'}
    return render(request, template_name=template_name, context=context)
def aappg_donate(request):
    template_name = 'aappg/donate.html'
    context = {'data':'value'}
    return render(request, template_name=template_name, context=context)
def aappg_contacts(request):
    template_name = 'aappg/contacts.html'
    context = {'data': 'value'}
    return render(request, template_name=template_name, context=context)
def aappg_actualites(request):
    template_name = 'aappg/actualites.html'
    context = {'data': 'value'}
    return render(request, template_name=template_name, context=context)
def aappg_le_mouvement(request):
    template_name = 'aappg/leparti.html'
    context = {'data': 'value'}
    return render(request, template_name=template_name, context=context)
def aappg_adherants(request):
    template_name = 'aappg/adherer.html'
    context = {'data': 'value'}
    return render(request, template_name=template_name, context=context)
def aappg_tv(request):
    template_name = 'aappg/teleantisysteme.html'
    context = {'data': 'value'}
    return render(request, template_name=template_name, context=context)
def aappg_valeurs(request):
    template_name = 'aappg/valeurs.html'
    return render(request, template_name=template_name)
def aappg_chartes(request):
    template_name = 'aappg/statuts.html'
    return render(request, template_name=template_name)

def aappg_reglement(request):
    template_name = 'aappg/reglement.html'
    return render(request, template_name=template_name)

@login_required
def aappg_admin_page(request):
    template_name = 'aappg_admin/admin_page.html'
    usr = request.session.get('user_name', 'Votre session à expiré, veillez vous reconnecter.')
    session_expired = request.session.get('session_expired', 0)
    print(session_expired)
    context = {}
    context['session'] = usr
    context['session_expired'] = session_expired
    return render(request, template_name=template_name, context=context)
@login_required
def aappg_articles_edit(request):
    template_name = 'articles/articles.html'
    context = {}
    if request.method == 'POST':
        form = AappgArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.image = form.cleaned_data['image']
            article.author = request.user
            article.save()
            sentry_sdk.capture_message(f"{article.author} vient de publier une article", level="error")
            print('formulaire poster avec succes')
            pk = 1
            for f in form:
                print(f)
            return redirect('my_site:news')  # Redirige vers la liste des articles ou une page de succès
        else:
            context['form'] = form
    else:
        print('formulaire non poster')
        form = AappgArticleForm()
        context['form'] = form
    return render(request, template_name=template_name, context=context)
def articles_poster(request):
    #post = get_object_or_404(AappgArticlesPost)
    posts = AappgArticlesPost.objects.all().order_by('-created_at')
    context = {}
    context['posts'] = posts
    #context['post'] = post
    return render(request, 'articles/articles_publier.html', context=context)

def aappg_news(request):
    template_name = 'articles/aappg_news.html'
    context = {}

    posts = AappgArticlesPost.objects.order_by('-created_at')
    context['newest_posts'] = posts.first()
    context['older_posts'] = posts[1:]

    # Récupérer tous les communiqués, triés par date de création (du plus récent au plus ancien)
    # Récupérer les 4 derniers communiqués
    latest_communiques = AappgCommunique.objects.all().order_by('-id')[:4]
    # Assigner à des variables distinctes
    communique1 = latest_communiques[0] if latest_communiques.count() > 0 else None
    communique2 = latest_communiques[1] if latest_communiques.count() > 1 else None
    communique3 = latest_communiques[2] if latest_communiques.count() > 2 else None
    communique4 = latest_communiques[3] if latest_communiques.count() > 3 else None

    context['communique1'] = communique1
    context['communique2'] = communique2
    context['communique3'] = communique3
    context['communique4'] = communique4


    #Systéme de pagination
    paginator = Paginator(posts, 8)

    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # Exclure le dernier article publié si on est sur la première page
    if page in [None, '1']:
        articles = posts[1:]
        paginator = Paginator(articles, 8)
        page_obj = paginator.get_page(page)
    context['page_obj'] = page_obj
    return render(request, template_name, context)

#Une fonction qui permet de rediriger vers la page 403 ou 404
def custom_permission_denied_view(request, exception=None):
    # Le bon template doit être utilisé pour une erreur 403
    template_name = 'errors/403.html'
    response = render(request, template_name)
    response.status_code = 403
    return response
def custom_page_not_found_view(request, exception=None):
    template_name = 'errors/404.html'
    response = render(request, template_name)
    response.status_code = 404
    return response
def article_detail(request, id):
    template_name = 'articles/detail_articles.html'
    context = {}
    #Recupération ID de l'article pour le trasferer via l'url
    # Recupération du contenue de AappgArticlePost lié à l'url trasmis
    article = get_object_or_404(AappgArticlesPost, id=id)
    context['category'] = article.category
    context['title'] = article.title
    context['content'] = article.content
    context['video'] = article.video
    context['image'] = article.image
    context['created_at'] = article.created_at
    context['author'] = article.author

    context['article'] = article
    return render(request, template_name, context)
#Detail communiquer

def communique_detail(request, id):
    template_name = 'communiquer/detail_communiquer.html'
    context = {}
    #Recupération ID de l'article pour le trasferer via l'url
    # Recupération du contenue de AappgArticlePost lié à l'url trasmis
    article = get_object_or_404(AappgCommunique, id=id)
    context['titre'] = article.titre
    context['content'] = article.content
    context['created_at'] = article.created_at
    context['author'] = article.author

    return render(request, template_name, context)
@login_required
def modify_article(request, pk):
    article = get_object_or_404(AappgArticlesPost, pk=pk)

    # Vérifier si l'utilisateur est l'auteur de l'article ou un superuser
    if request.user != article.author and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = AappgArticleEditForm(request.POST, request.FILES, instance=article)

        # Désactivez la validation du champ image si aucun fichier n'est téléchargé
        if 'image' not in request.FILES:
            form.fields['image'].required = False
        if form.is_valid():
            form.save()
            sentry_sdk.capture_message(f"{request.user} vient de modifier un article", level="error")
            print('formulaire poster avec succes')
            return redirect('my_site:news')
    else:
        print('formulaire non poster')
        form = AappgArticleEditForm(instance=article)
    return render(request, 'articles/edit_article.html', {'form': form})

#Suppression d'articles
@login_required
def delete_articles(request, post_id):
    template_name = 'articles/delete_article.html'
    context={}
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete this post.")

    article = get_object_or_404(AappgArticlesPost, id=post_id)

    if request.method == 'POST':
        article.delete()

        sentry_sdk.capture_message(f"{request.user} vient de supprimer une article", level="info")
        messages.success(request, "Blog post deleted successfully")
        return redirect('my_site:articles_list')  # Change 'blogpost_list' to the name of your list view
    context['article'] = article
    return render(request, template_name=template_name, context=context)
#Listes des articles à modifier ou à supprimer selon que la personne soit
#superuser ou author
@login_required
def article_list(request):
    templane_name = "articles/articles_list.html"
    context = {}
    if request.user.is_superuser:
        articles = AappgArticlesPost.objects.all()
        context['articles'] = articles
    else:
        articles = AappgArticlesPost.objects.filter(author=request.user)
        context['articles'] = articles
    #On vérifie si l'utilsateur a dèjá d'Articles écrit à son compte
    user_has_published_articles = articles.exists()
    context['user_has_published_articles'] = user_has_published_articles

    #on récupère le nom de l'utilsateur connecté
    context['user_name'] = request.user.user
    return render(request, template_name=templane_name, context=context)
@login_required
def create_communique(request):
    template_name = 'communiquer/create_communique.html'
    context = {}

    if request.method == 'POST':
        form = AappgCommuniqueForm(request.POST)
        if form.is_valid():
            communique = form.save(commit=False)  # Ne pas encore enregistrer en base
            communique.author = request.user  # Attribuer l'utilisateur connecté comme auteur
            communique.save()  # Enregistrer maintenant avec l'auteur
            sentry_sdk.capture_message(f"{request.user} vient de publier un communiqué.", level="error")
            print('Communiquer publier avec success')
            return redirect('my_site:news')  # Rediriger vers une page de succès après l'enregistrement
        else:
            print('Une erreur s est produit', form.errors)
    else:
        print("Resoumission du formulaire.",)
        form = AappgCommuniqueForm()

    context['form'] = form
    return render(request, template_name, context)

#Tester les erreurs de Centry
def trigger_error(request):
    division_by_zero = 1 / 0
    return render(request, 'errors/505.html', context={'division_by_zero': division_by_zero})