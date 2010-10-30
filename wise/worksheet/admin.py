from wise.worksheet.models import MathematicalEquation, Workspace, Cell, Symbol, Function, Rule, RuleSet

from reversion.admin import VersionAdmin
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

class VersionedWorkspace(VersionAdmin):
    pass

admin.site.register(Workspace,VersionedWorkspace)
admin.site.register(MathematicalEquation)
admin.site.register(Cell)
