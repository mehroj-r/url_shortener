from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from apps.account.models import User


class UserCreationForm(AdminUserCreationForm):

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name')


class UserUpdateForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserUpdateForm
    add_form = UserCreationForm
    list_display = ('username', 'email', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('-created_at',)
    filter_horizontal = ()
    readonly_fields = ('last_login', 'created_at', 'updated_at', 'deleted_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'usable_password', 'password1', 'password2'),
        }),
    )
