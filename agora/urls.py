from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from agora.core import views as core_views
from home import views as home_views
from search import views as search_views

from .api_v1 import api as api_v1

user_urls = [
    # Cover both the handle and the ID
    path("profile/<int:id>/", core_views.ProfileView.as_view(), name="profile"),
    path("profile/<str:handle>/", core_views.ProfileView.as_view(), name="profile"),
    # Redirect to the profile page of the current user
    path("profile/", core_views.ProfileRedirectView.as_view(), name="profile"),
]

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("", include("user.urls")),
    path("dashboard", home_views.dashboard, name="dashboard"),
    path("", include((user_urls, "user"))),
    path("accounts/", include("allauth.urls")),
    path("careers/", TemplateView.as_view(template_name="home/careers.html"), name="careers"),
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("join/", home_views.join_waiting_list, name="join_waiting_list"),
    path("api/v1/", api_v1.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.TESTING:
    urlpatterns += debug_toolbar_urls()

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
