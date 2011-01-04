from wise.worksheet.models import Expression, Workspace, Cell, \
Assumption

from django.contrib import admin

class ExpressionsInline(admin.StackedInline):
    extra = 1
    model = Expression

class AssumptionsInline(admin.StackedInline):
    extra = 1
    model = Assumption

class WorkspaceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]

class CellAdmin(admin.ModelAdmin):
    inlines = [ExpressionsInline, AssumptionsInline]

admin.site.register(Workspace)
admin.site.register(Expression)
admin.site.register(Assumption)
admin.site.register(Cell, CellAdmin)
