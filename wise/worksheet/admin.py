from wise.worksheet.models import MathematicalEquation,Workspace

from django.contrib import admin

class EquationInline(admin.StackedInline):
    model = MathematicalEquation
    extra = 3
    inlines = [MathematicalEquation]

class WorkspaceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
#        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [EquationInline]

admin.site.register(Workspace,WorkspaceAdmin)
admin.site.register(MathematicalEquation)
#admin.site.register(MathematicalTransform)
#admin.site.register(MathematicalIdentity)
