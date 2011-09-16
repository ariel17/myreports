from django.conf import settings
from django.contrib import admin

from models import Report, Section, Variable


class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "sections_involved",)
    list_filter = ("server", "sections",)
    ordering = ("title",)

    
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "variables_involved",)
    list_filter = ("variables",)
    ordering = ("title",)


class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "description",)
    list_filter = ("type",)
    ordering = ("name", "type",)


admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Variable, VariableAdmin)
