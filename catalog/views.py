from django.contrib.admin.utils import flatten
from django.db.models import Count, Q, F
from django.shortcuts import render
from django.utils.text import re_camel_case
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Artist, Song, Album, Playlist, Favorite
from .permisions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import CategorySerializer, ArtistSerializer, SongSerializer, SongLightSerializer, AlbumSerializer, \
    PlaylistSerializer, FavoriteSerializer, AlbumLightSerializer, ArtistLightSerializer, PlaylistLightSerializer


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['get'])
    def top_songs(self, request, pk=None):
        artist = self.get_object()
        top_songs = artist.songs.order_by('-popularity')
        serializer = SongLightSerializer(top_songs, many=True, context={'request':request})
        return Response(serializer.data)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAdminOrReadOnly]

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsAdminOrReadOnly]

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrAdminOrReadOnly]

    @action(detail=True , methods=['post'])
    def add_song(self,request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({"error": 'song_id is required!'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": 'Song dose not exists'}, status=status.HTTP_400_BAD_REQUEST)
        if playlist.songs.filter(id=song.id).exists():
            return Response({"error": 'Song already exists'}, status=status.HTTP_400_BAD_REQUEST)
        playlist.songs.add(song)
        return Response({"success": 'Song added'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_song(self,request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({"error": 'song_id is required!'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": 'Song dose not exists'}, status=status.HTTP_400_BAD_REQUEST)
        if not playlist.songs.filter(id=song.id).exists():
            return Response({"error": 'No Such Song'}, status=status.HTTP_400_BAD_REQUEST)
        playlist.songs.remove(song)
        return Response({"success": 'Song removed'}, status=status.HTTP_200_OK)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the current user when creating a Favorite
        serializer.save(user=self.request.user)

    # -------- Generic Add/Remove Helper --------
    def _add_item(self,request, model,related_name):
        item_id = request.data.get('id')
        if not item_id:
            return Response({"error":"id is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            return Response({"error": f'{model.__name__} does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        favorite , _ = Favorite.objects.get_or_create(user=request.user)
        relation = getattr(favorite, related_name)

        if relation.filter(id=item.id).exists():
            return Response({"error": f"{model.__name__} already in favorites"}, status=status.HTTP_400_BAD_REQUEST)

        relation.add(item)
        return Response({"success": f"{model.__name__} added to favorites"}, status=status.HTTP_200_OK)

    def _remove_item(self,request, model,related_name):
        item_id = request.data.get('id')
        if not item_id:
            return Response({"error":"id is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            return Response({"error": f'{model.__name__} does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        favorite , _ = Favorite.objects.get_or_create(user=request.user)
        relation = getattr(favorite, related_name)

        if not relation.filter(id=item.id).exists():
            return Response({"error": f"{model.__name__} not in favorites"}, status=status.HTTP_400_BAD_REQUEST)

        relation.remove(item)
        return Response({"success": f"{model.__name__} removed from favorites"}, status=status.HTTP_200_OK)

    # -------- Actions --------
    @action(detail=False, methods=['post'])
    def add_song(self,request):
        return self._add_item(request,Song,'songs')

    @action(detail=False, methods=['post'])
    def remove_song(self,request):
        return self._remove_item(request,Song,'songs')

    @action(detail=False, methods=['post'])
    def add_album(self,request):
        return self._add_item(request,Album,'albums')

    @action(detail=False, methods=['post'])
    def remove_album(self,request):
        return self._remove_item(request,Album,'albums')

    @action(detail=False, methods=['post'])
    def add_artist(self,request):
        return self._add_item(request,Artist,'artists')

    @action(detail=False, methods=['post'])
    def remove_artist(self,request):
        return self._remove_item(request,Artist,'artists')

    @action(detail=False, methods=['post'])
    def add_playlist(self,request):
        return self._add_item(request,Playlist,'playlists')

    @action(detail=False, methods=['post'])
    def remove_playlist(self,request):
        return self._remove_item(request,Playlist,'playlists')


class RecommendationView(APIView):
   permission_classes = [AllowAny]

   def get(self,request):

    # ---------- STEP 1: User favorites ----------
    user = request.user if request.user.is_authenticated else None
    if user:
        try :
            user_fav = Favorite.objects.get(user=user)
            fav_songs = user_fav.songs.all()
            fav_artists = user_fav.artists.all()
            fav_albums = user_fav.albums.all()
            fav_playlists = user_fav.playlists.all()
        except Favorite.DoesNotExist:
            fav_songs = fav_albums = fav_artists = fav_playlists = []
    else:
        fav_songs = fav_albums = fav_artists = fav_playlists = []


    # ---------- STEP 2: Similar users ----------
    if user and fav_songs:
        similar_users_favs = Favorite.objects.filter(
            Q(songs__in=fav_songs) |
            Q(artists__in=fav_artists) |
            Q(albums__in=fav_albums) |
            Q(playlists__in=fav_playlists)
        ).exclude(user=user).distinct()

    else:
        similar_users_favs = Favorite.objects.none()


    # ---------- STEP 3: Collect favorites items from similar users favs ----------
    similar_songs = Song.objects.filter(favorites__in=similar_users_favs).distinct()
    similar_albums = Album.objects.filter(favorited_by__in=similar_users_favs).distinct()
    similar_artists = Artist.objects.filter(favorited_by__in=similar_users_favs).distinct()
    similar_playlists = Playlist.objects.filter(favorited_by__in=similar_users_favs).distinct()

    # ---------- STEP 4: Category-based songs ----------
    if fav_songs:
        related_categories = Category.objects.filter(songs__in=fav_songs).distinct()
    else:
        related_categories = Category.objects.all()

    category_songs = Song.objects.filter(
        categories__in=related_categories
    ).distinct()

    if fav_songs:
        category_songs =  category_songs.exclude(id__in=fav_songs.values_list('id', flat=True))

    # ---------- STEP 5: Popularity fallback ----------
    popular_songs = Song.objects.all().order_by('-popularity')

    # ---------- STEP 6: Combine + weight results ----------
    recommended_songs = similar_songs.annotate(
        fav_count=Count('favorites')
    ).order_by('-fav_count','-popularity')
    if fav_songs:
        recommended_songs = recommended_songs.exclude(id__in=fav_songs.values_list('id', flat=True))


    recommended_albums = similar_albums.annotate(
        fav_count=Count('favorited_by')
    ).order_by('-fav_count')
    if  fav_albums:
        recommended_albums = recommended_albums.exclude(id__in=fav_albums.values_list('id',flat=True))


    recommended_artists = similar_artists.annotate(
        fav_count=Count('favorited_by')
    ).order_by('-fav_count')

    if fav_artists:
        recommended_artists = recommended_artists.exclude(id__in=fav_artists.values_list('id',flat=True))


    recommended_playlists = similar_playlists.annotate(
        fav_count = Count('favorited_by')
    ).order_by('-fav_count')

    if fav_playlists:
        recommended_playlists = recommended_playlists.exclude(id__in=fav_playlists.values_list('id',flat=True))


    recommended_categories = related_categories.annotate(
        song_count = Count('songs')
    ).order_by('-song_count')

    # ---------- STEP 7: Serialize ----------
    data = {
        'recommended_songs': SongSerializer(recommended_songs, many=True, context={'request': request}).data,
        'recommended_albums': AlbumLightSerializer(recommended_albums, many=True, context={'request': request}).data,
        'recommended_artists': ArtistLightSerializer(recommended_artists, many=True, context={'request': request}).data,
        'recommended_playlists': PlaylistSerializer(recommended_playlists, many=True, context={'request': request}).data,
        'recommended_categories': CategorySerializer(recommended_categories, many=True, context={'request': request}).data,
        'popular_songs': SongSerializer(popular_songs, many=True, context={'request': request}).data
    }

    return Response(data)


class SearchCatalogView(APIView):

    def get(self, request):
        q= request.GET.get('q').lower()

        # ---------- Songs ----------a
        songs = Song.objects.filter(
            Q(name__icontains=q) | Q(artist__name__icontains=q)
        ).order_by('-popularity').distinct()[:20]

        # ---------- Albums ----------
        albums = Album.objects.filter(
            Q(name__icontains=q) | Q(artist__name__icontains=q)
        ).annotate(score=Count('favorited_by')).order_by('-score').distinct()[:10]

        # ---------- Artists ----------
        artists = Artist.objects.filter(name__icontains=q).annotate(
            score=Count('favorited_by')
        ).order_by('-score').distinct()[:10]

        # ---------- Playlists ----------
        playlists = Playlist.objects.filter(name__icontains=q).annotate(
            score=Count('favorited_by')
        ).order_by('-score').distinct()[:10]

        # ---------- Categories ----------
        categories = Category.objects.filter(name__icontains=q).annotate(
            score=Count('songs')
        ).order_by('-score').distinct()[:10]


        # ---------- Top Result ----------
        top_result = None

        priority_order = [
            (songs, SongLightSerializer),
            (artists, ArtistLightSerializer),
            (albums, AlbumLightSerializer),
            (playlists, PlaylistLightSerializer),
            (categories, CategorySerializer),
        ]

        for model_list , serializer in priority_order:

            for item in model_list:
                if item.name.lower() == q:
                    top_result = serializer(item, context={'request': request}).data
                    top_result['type'] = item._meta.model_name
                    break
            if top_result:
                break

        if not top_result:
            for model_list, serializer in priority_order:
                if model_list.exists():
                    top_result = serializer(model_list[0],context={'request': request}).data
                    top_result['type'] = item._meta.model_name
                    break

        data = {
            'top_result' : top_result,
            'songs' : SongLightSerializer(songs, many=True, context={'request': request}).data,
            'playlists' : PlaylistLightSerializer(playlists, many=True, context={'request': request}).data,
            'artists' : ArtistLightSerializer(artists, many=True, context={'request': request}).data,
            'albums' : AlbumLightSerializer(albums, many=True, context={'request': request}).data,
            'categories' : CategorySerializer(categories, many=True, context={'request': request}).data,
        }

        return Response(data)
