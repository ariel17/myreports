from django.contrib import admin
from django.conf import settings

if settings.DEBUG:
    from models import Snapshot
    
    class SnapshotAdmin(admin.ModelAdmin):
        list_display = ("server", "variable", "time", "value" )
        list_filter = ("server", "variable", "time")
        ordering = ("server", "variable", )
    
    admin.site.register(Snapshot, SnapshotAdmin)
