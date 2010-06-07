from wise.worksheet.models import MathematicalEquation, Workspace, Cell

from django.contrib import admin

#class EquationInline(admin.StackedInline):
#    extra = 3
#    inlines = [MathematicalEquation]

class WorkspaceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
#        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    #inlines = [EquationInline]

admin.site.register(Workspace)
admin.site.register(MathematicalEquation)
admin.site.register(Cell)
#admin.site.register(MathematicalIdentity)
