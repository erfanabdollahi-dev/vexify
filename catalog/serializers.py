from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Category, Artist, Song, Album, Playlist, Favorite
# Lightweight Song for artist page
class SongLightSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    class Meta:
        model = Song
        fields = ['id', 'name', 'duration', 'popularity','cover','categories']

# Lightweight Album for artist page
class AlbumLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'name', 'cover']


class ArtistLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'image','bio']

class PlaylistLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'cover']


# ---------- CATEGORY ----------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'cover']


# ---------- ARTIST ----------
class ArtistSerializer(serializers.ModelSerializer):
    top_songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio','image', 'top_songs', 'albums']


    def get_top_songs(self, obj):
        songs = obj.songs.order_by('-popularity')
        return SongLightSerializer(songs, many=True, context=self.context).data

    def get_albums(self, obj):
        albums = obj.albums.all()
        return AlbumLightSerializer(albums, many=True, context=self.context).data




# ---------- ALBUM ----------
class AlbumSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True,read_only=True)
    songs = serializers.SerializerMethodField()
    artist = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'name', 'artist', 'categories', 'songs', 'cover', 'release_date']

    def get_songs(self, obj):
        from .serializers import SongLightSerializer
        songs = obj.songs.all().order_by('-popularity')
        return SongLightSerializer(songs,many=True,context=self.context).data



# ---------- SONG ----------
class SongSerializer(serializers.ModelSerializer):
    artist = serializers.PrimaryKeyRelatedField(queryset=Artist.objects.all(), many=True)
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), required=False, allow_null=True)
    categories = serializers.StringRelatedField(many=True, required=False, allow_null=True,read_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'name', 'artist', 'album', 'duration', 'popularity','categories',
            'cover', 'audio_file', 'release_date','created_date'
        ]


# ---------- PLAYLIST ----------
class PlaylistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user', 'songs', 'cover', 'created_at']



# ---------- FAVORITE ----------
class FavoriteSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    playlists = PlaylistSerializer(many=True, read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'songs', 'albums', 'playlists', 'artists']
