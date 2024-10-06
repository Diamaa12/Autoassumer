
from django.urls import path
from django.conf.urls.static import static

from django.conf import settings
from .views import test, index, aappg_donate, aappg_actualites, aappg_le_mouvement, aappg_contacts, aappg_adherants, \
    aappg_home, aappg_tv, aappg_admin_inscription, aappg_admin_connexion, aappg_admin_page, logout_view, \
    aappg_articles_edit, \
    articles_poster, aappg_news, article_detail, modify_article, custom_permission_denied_view, article_list, \
    delete_articles, aappg_valeurs, aappg_chartes, aappg_reglement, pagination_test, email_verification_sent, \
    email_verification, test_form, email_verified_success, create_communique, communique_detail, trigger_error

app_name = 'my_site'
urlpatterns = [

    path('test/', test, name='test'),
    path('test-form/', test_form, name='test_form'),
    path('pagination-test/', pagination_test, name='pagination_test'),

    path('index/', index, name='index'),
    path('home/', aappg_home, name='home'),
    path('donate/', aappg_donate, name='donate'),
    path('actualites/', aappg_actualites, name='actualites'),
    path('le mouvement/', aappg_le_mouvement, name='lemouvement'),
    path('contacts/', aappg_contacts, name='contacts'),
    path('adherants/', aappg_adherants, name='adherer'),
    path('antisystem', aappg_tv, name='teleantisytem'),

    path('valeurs/', aappg_valeurs, name='valeurs'),
    path('chartes/', aappg_chartes, name='chartes'),
    path('reglement/', aappg_reglement, name='reglement'),


    path('admin-inscription', aappg_admin_inscription, name='admin-inscription'),
    path('admin-connexion', aappg_admin_connexion, name='admin-connexion'),
    path('admin-deconnexion', logout_view, name='logout'),
    path('admin-page', aappg_admin_page, name='admin-page'),

    path('email-verification-sent/', email_verification_sent, name='email_verification_sent'),
    path('verify-email/<uuid:token>/', email_verification, name='verify-email'),
    path('success_email_verification', email_verified_success, name='success_email_verification'),

    path('create-communique', create_communique, name='create-communique'),
    path('communique/<int:id>/', communique_detail, name='communique'),

    path('articles-edit', aappg_articles_edit, name='articles-edit'),
    path('articles-publier', articles_poster, name='articles-publier'),
    path('news/', aappg_news, name='news'),
    path('article/<int:id>/', article_detail, name='article_detail'),
    path('article/<int:pk>/edit', modify_article, name='modify_article'),
    path('articles-list/', article_list, name='articles_list'),
    path('articles-delete/<int:post_id>/', delete_articles, name='delete_article'),
    path('403/', custom_permission_denied_view, name='403'),

    path('sentry-debug/', trigger_error),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
