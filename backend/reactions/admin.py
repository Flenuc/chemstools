from django.contrib import admin
from .models import BalancedReaction

@admin.register(BalancedReaction)
class BalancedReactionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para BalancedReaction
    """
    list_display = ('original_equation', 'balanced_equation', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('original_equation', 'balanced_equation')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Ecuación', {
            'fields': ('original_equation', 'balanced_equation')
        }),
        ('Detalles', {
            'fields': ('coefficients', 'reaction_type')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )