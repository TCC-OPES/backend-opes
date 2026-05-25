from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # jwt
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # auth 
    path('api/', include('core.urls.usuario')),
    path('api/transacoes/', include('core.urls.transacao')),
    path('api/cartoes/', include('core.urls.cartao')),
    path('api/metas/', include('core.urls.meta')),
    path('api/familia/', include('core.urls.familia')),
    path('api/dashboard/', include('core.urls.dashboard')),
]