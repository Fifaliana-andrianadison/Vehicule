from django.contrib import admin

from apps.expenses.models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'category', 'amount', 'date', 'description']
    list_filter = ['category', 'date']
    search_fields = ['vehicle__name', 'description']