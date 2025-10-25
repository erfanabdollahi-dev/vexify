from django.urls import  path, include
from rest_framework.routers import DefaultRouter
from . import  views
router = DefaultRouter()
router.register('categories', views.CategoryViewSet )
router.register('artists', views.ArtistViewSet )
router.register('albums', views.AlbumViewSet )
router.register('songs', views.SongViewSet )
router.register('playlists', views.PlaylistViewSet )
router.register('favorites', views.FavoriteViewSet )

urlpatterns=[
    path('', include(router.urls)),
    path('recommendation/', views.RecommendationView.as_view(),name='recommendation'),
    path('search/', views.SearchCatalogView.as_view(),name='search')
]