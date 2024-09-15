from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth
from django.utils import timezone
from datetime import datetime

#Cette classe permet d'inclure dans les middleware de django
#la gestion des sessions de l'utilsateur sur certains page comme le DASHBORD, et le Django-admin
class SessionIdleTimeoutMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Appliquer la règle uniquement aux utilisateurs authentifiés et exclure cette regle à la page d'admin de Django
        if not request.path.startswith('/aappgadmin/') and request.user.is_authenticated:
            # Récupérer le dernier timestamp de requête dans la session
            timestamp = request.session.get('last_request')
            if timestamp:
                # Convertir le timestamp en un objet datetime conscient du fuseau horaire
                last_request = timezone.make_aware(datetime.fromtimestamp(timestamp), timezone.get_default_timezone())
                # Si plus de 2 minutes se sont écoulées depuis la dernière requête, déconnecter l'utilisateur
                if (timezone.now() - last_request).total_seconds() > 300:
                    auth.logout(request)
                    # Ajouter un indicateur pour signaler que la session a expiré
                    request.session['session_expired'] = True
            # Enregistrer l'heure actuelle comme dernière requête
            request.session['last_request'] = timezone.now().timestamp()
        elif request.path.startswith('/aappgadmin/'):
            # Récupérer le dernier timestamp de requête dans la session
            timestamp = request.session.get('last_request')
            if timestamp:
                # Convertir le timestamp en un objet datetime conscient du fuseau horaire
                last_request = timezone.make_aware(datetime.fromtimestamp(timestamp), timezone.get_default_timezone())
                # Si plus de 2 minutes se sont écoulées depuis la dernière requête, déconnecter l'utilisateur
                if (timezone.now() - last_request).total_seconds() > 260:
                    auth.logout(request)
                    # Ajouter un indicateur pour signaler que la session a expiré
                    request.session['session_expired'] = True
            # Enregistrer l'heure actuelle comme dernière requête
            request.session['last_request'] = timezone.now().timestamp()

    def process_response(self, request, response):
        # Enlever l'indicateur après avoir rendu la page de connexion
        if request.path == '/admin-connexion' and request.session.get('session_expired'):
            del request.session['session_expired']
        elif request.path == '/aappgadmin' and request.session.get('session_expired'):
            del request.session['session_expired']
        return response

