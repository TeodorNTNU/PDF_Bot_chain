from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, PDFViewSet, ChatConsumer

# Initialize the router
router = DefaultRouter()

# Register the viewsets with the router
router.register(r'items', ItemViewSet, basename='item')
router.register(r'pdfs', PDFViewSet, basename='pdf')

# Define the URL patterns
urlpatterns = [
    path('api/', include(router.urls)),  # Include router URLs under the `/api/` prefix
    path('ws/chat/', ChatConsumer.as_asgi()),  # WebSocket route
]
