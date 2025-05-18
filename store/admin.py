from django.contrib import admin
from .models import Product,variation,ReviewRating

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
     list_display = ('id','product_name','price','stock','category','modified_date','is_available')
     prepopulated_fields = {'slug':('product_name',)}
     list_display_links=('product_name',)

class VariationAdmin(admin.ModelAdmin):
    list_display = ['product','variation_category','variation_value','is_active']
    list_filter = ('product','variation_category','variation_value','is_active')     

class ReviewRatingAdmin(admin.ModelAdmin):
     list_display = ['user']
admin.site.register(Product,ProductAdmin)
admin.site.register(variation,VariationAdmin)
admin.site.register(ReviewRating)