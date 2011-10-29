from django.contrib import admin
from models import Server, ReportByServer, Database


class ReportByServerInline(admin.TabularInline):
    model = ReportByServer


class DatabaseInline(admin.TabularInline):
    model = Database


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "ip", "port", "available_reports")
    list_filter = ("port", "active")
    ordering = ("name", "ip", "active")
    inlines = [DatabaseInline, ReportByServerInline, ]


class ReportByServerAdmin(admin.ModelAdmin):
    list_display = ("server", "report", "order")


class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("server", "name")
    list_filter = ("server", "name")
    ordering = ("server", "name")


admin.site.register(Server, ServerAdmin)
admin.site.register(ReportByServer, ReportByServerAdmin)
admin.site.register(Database, DatabaseAdmin)
