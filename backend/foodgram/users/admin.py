from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'get_subscribtion',
                    'get_recipe')
    list_filter = ('username', 'email')
    show_full_result_count = True

    @admin.display(description='Подписчики')
    def get_subscribtion(self, obj):
        return obj.follower.count()

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return obj.recipes.count()


admin.site.register(User, UserAdmin)
