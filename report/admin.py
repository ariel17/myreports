from django.contrib import admin

from models import Report, Section, Variable


class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "sections_involved" )
    list_filter = ("server", "sections")
    ordering = ("title",)


class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "variables_involved")
    list_filter = ("title", "variables")
    ordering = ("title",)


class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    list_filter = ("name", "description")
    ordering = ("name",)


admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Variable, VariableAdmin)
