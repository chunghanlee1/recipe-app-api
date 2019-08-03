from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# recommended convention to convert strings in Python to human readable text
# pass string through translation engine that supports multiple languages
from django.utils.translation import gettext as _
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']

    # define the sections for the fieldsets in the admin
    # edit user detail page
    fieldsets = (
        # (title of the section, content of the section)
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    # fieldset details for the create/add user page
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')}),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
