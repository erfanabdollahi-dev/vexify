from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Category, Artist, Song, Album, Playlist, Favorite

# ---------- CATEGORY ----------
class CategorySerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'cover_url']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        elif obj.cover:
            return obj.cover.url
        return None

# ---------- ARTIST ----------
class ArtistSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'image_url', 'songs', 'albums']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

    def get_songs(self, obj):
        from .serializers import SongSerializer
        songs = obj.songs.all()
        return SongSerializer(songs,context=self.context).data


# ---------- ALBUM ----------
class AlbumSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    songs = serializers.SerializerMethodField()
    artist = ArtistSerializer(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'name', 'artist', 'categories', 'songs', 'cover_url', 'release_date']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        elif obj.cover:
            return obj.cover.url
        return None

    def get_songs(self, obj):
        from .serializers import SongSerializer
        songs = obj.songs.all()
        return SongSerializer(songs,context=self.context).data

# ---------- SONG ----------
class SongSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    audio_file_url = serializers.SerializerMethodField()
    artist = ArtistSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True, required=False)

    class Meta:
        model = Song
        fields = [
            'id', 'name', 'artist', 'album', 'duration', 'popularity',
            'cover_url', 'audio_file_url', 'release_date'
        ]

    def get_audio_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.audio_file:
            return request.build_absolute_uri(obj.audio_file.url)
        elif obj.audio_file:
            return obj.audio_file.url
        return None

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        elif obj.cover:
            return obj.cover.url
        return None

# ---------- PLAYLIST ----------
class PlaylistSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user', 'songs', 'cover_url', 'created_at']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        elif obj.cover:
            return obj.cover.url
        return None

# ---------- FAVORITE ----------
class FavoriteSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    playlists = PlaylistSerializer(many=True, read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'songs', 'albums', 'playlists', 'artists']
