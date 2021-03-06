from wise.worksheet.models import MathematicalEquation, Workspace, Cell, Symbol, Function, Rule, RuleSet

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
admin.site.register(Symbol)
admin.site.register(Function)
admin.site.register(Rule)
admin.site.register(RuleSet)
