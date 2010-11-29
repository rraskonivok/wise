from wise.worksheet.models import Expression, Workspace, Cell, \
Assumption

from reversion.admin import VersionAdmin
from django.contrib import admin

class ExpressionsInline(admin.StackedInline):
    extra = 1
    model = Expression

class AssumptionsInline(admin.StackedInline):
    extra = 1
    model = Expression

class WorkspaceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]

class CellAdmin(admin.ModelAdmin):
    inlines = [ExpressionsInline, AssumptionsInline]

class VersionedWorkspace(VersionAdmin):
    pass

class VersionedExpression(VersionAdmin):
    pass

class VersionedAssumption(VersionAdmin):
    pass

admin.site.register(Workspace, VersionedWorkspace)
admin.site.register(Expression, VersionedExpression)
admin.site.register(Assumption, VersionedAssumption)
admin.site.register(Cell, CellAdmin)
