from django.contrib import admin

from models import Report, Section


class ReportAdmin(admin.ModelAdmin):
    list_display = ("server", "title", )
    list_filter = ("server", "title")
    ordering = ("title",)


class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "variables")
    list_filter = ("title", "variables")
    ordering = ("title",)


admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
