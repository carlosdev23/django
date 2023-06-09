from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth import get_user_model
import django.contrib.auth.admin


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Business info'), {'fields': ('title', 'service', 'phone_number',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'client'),
        }),
    )

    list_display = ('email', 'name', 'is_staff')
    search_fields = ('name', 'email')
    ordering = ('email',)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(get_user_model(), UserAdmin)
