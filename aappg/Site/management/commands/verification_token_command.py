from django.core.management.base import BaseCommand
from Site.models import AappgCustomUser  # Remplace `yourapp` par le nom de ton application
import uuid

class Command(BaseCommand):
    help = 'Remplit le champ email_verification_token pour les utilisateurs existants'

    def handle(self, *args, **kwargs):
        # Supprimer les tokens invalides
        AappgCustomUser.objects.filter(email_verification_token__isnull=False).update(email_verification_token=None)
        self.stdout.write(self.style.WARNING("Tous les tokens invalides ont été supprimés."))

        users_without_token = AappgCustomUser.objects.filter(email_verification_token__isnull=True)
        updated_count = 0

        for user in users_without_token:
            # Génère un token unique
            token = str(uuid.uuid4())

            # Vérifie si ce token est déjà utilisé pour éviter les doublons
            while AappgCustomUser.objects.filter(email_verification_token=token).exists():
                token = str(uuid.uuid4())  # Regénère un nouveau token si doublon

            # Affecte le token à l'utilisateur
            user.email_verification_token = token
            user.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'{updated_count} utilisateurs mis à jour avec des tokens uniques.'))
