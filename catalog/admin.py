from django.contrib import admin
from .models import Artist, Album, Playlist, Favorite, Song, Category

# Inline to show songs in an album
class SongInline(admin.TabularInline):
    model = Song
    extra = 1  # how many empty forms to show
    fields = ['name', 'artist', 'cover', 'audio_file', 'duration', 'popularity','categories']

class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'release_date']
    search_fields = ['name', 'artist__name']
    list_filter = ['artist', 'release_date', 'categories']
    inlines = [SongInline]  # show songs directly in the album page

class AlbumInline(admin.TabularInline):
    model = Album
    extra = 1
    fields = ['name', 'cover', 'release_date']

class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [AlbumInline]

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['songs']  # nicer multiple selection widget

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['songs', 'albums', 'playlists', 'artists']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, )  # you can keep simple or add filters
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Category, CategoryAdmin)
