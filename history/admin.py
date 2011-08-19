from django.contrib import admin

from models import History


class HistoryAdmin(admin.ModelAdmin):
    list_display = ("server", "variable", "time", "value" )
    list_filter = ("server", "variable", "time")
    ordering = ("server", "variable", )


admin.site.register(History, HistoryAdmin)
