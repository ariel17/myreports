from django.contrib import admin
from django.conf import settings

if settings.DEBUG:
    from models import VariableSnapshot, UsageSnapshot
    
    class VariableSnapshotAdmin(admin.ModelAdmin):
        list_display = ("server", "variable", "value", "time")
        list_filter = ("server", "variable")
        ordering = ("server", "variable")


    class UsageSnapshotAdmin(admin.ModelAdmin):
        list_display = ("database", "qid", "duration", "time")
        list_filter = ("database",)
        ordering = ("database",)

    
    admin.site.register(VariableSnapshot, VariableSnapshotAdmin)
    admin.site.register(UsageSnapshot, UsageSnapshotAdmin)
