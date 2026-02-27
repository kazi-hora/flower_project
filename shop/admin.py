from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Flower, Order
from .models import Flower, Order, Refund
from .models import Refund
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# ===================== GLOBAL ADMIN TITLES =====================
admin.site.site_header = "🌸 Flower Shop Admin"
admin.site.site_title = "Flower Admin Portal"
admin.site.index_title = "Welcome to Flower Shop Dashboard"


# ===================== Flower Admin =====================
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'photo_preview')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('id',)
    actions_selection_counter = True
    actions = ['delete_selected']

    # Custom Admin CSS Load
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

    # Flower Image Preview + Buttons
    def photo_preview(self, obj):
        if obj.image:
            edit_url = reverse('admin:shop_flower_change', args=[obj.id])
            delete_url = reverse('admin:shop_flower_delete', args=[obj.id])
            return format_html(
                '''
                <div style="text-align:center;">
                    <img src="{}" width="80" height="80"
                         style="border-radius:10px; object-fit:cover; box-shadow:0 2px 6px rgba(0,0,0,0.2);" />
                    <div style="margin-top:6px;">
                        <a href="{}" style="color:#2c7be5; font-weight:bold;">✏️ Edit</a> | 
                        <a href="{}" style="color:#e63757; font-weight:bold;">🗑 Delete</a>
                    </div>
                </div>
                ''',
                obj.image.url, edit_url, delete_url
            )
        return format_html("<span style='color:gray;'>No Image</span>")

    photo_preview.short_description = "Photo"


# ===================== Order Admin =====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'flower',
        'flower_category',
        'flower_photo',
        'quantity',
        'order_type',
        'total_price',
        'action_buttons'
    )
    list_display_links = ('customer_name', 'flower')
    search_fields = ('customer_name', 'flower__name', 'order_type')
    list_filter = ('order_type', 'flower__category')
    ordering = ('-id',)

    # Custom Admin CSS Load
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

    # Flower Category
    def flower_category(self, obj):
        return obj.flower.category
    flower_category.short_description = "Category"

    # Flower Photo Preview
    def flower_photo(self, obj):
        if obj.flower.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px; object-fit:cover; box-shadow:0 2px 6px rgba(0,0,0,0.2);" />',
                obj.flower.image.url
            )
        return format_html("<span style='color:gray;'>No Image</span>")
    flower_photo.short_description = "Photo"

    # Edit / Delete Buttons
    def action_buttons(self, obj):
        edit_url = reverse('admin:shop_order_change', args=[obj.id])
        delete_url = reverse('admin:shop_order_delete', args=[obj.id])
        return format_html(
            '''
            <a href="{}" style="color:green; font-weight:bold;">✏️ Edit</a>
            &nbsp; | &nbsp;
            <a href="{}" style="color:red; font-weight:bold;">🗑 Delete</a>
            ''',
            edit_url, delete_url
        )
    action_buttons.short_description = "Actions"

class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }

# ===================== Refund Admin =====================
from django.contrib import admin
from django.utils.html import format_html
from .models import Refund


class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order",
        "issue_type",
        "status",
        "email",
        "created_at",
        "photo_preview",
    )
    list_filter = ("status", "issue_type", "created_at")
    search_fields = ("user__username", "email", "order__id")

    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:80px; height:80px; object-fit:cover; border-radius:6px;" />',
                obj.photo.url
            )
        return "No Photo"

    photo_preview.short_description = "Photo Preview"

admin.site.register(Refund, RefundAdmin)

@login_required
def refund_request(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        issue_type = request.POST.get("issue_type")
        description = request.POST.get("description")
        photo = request.FILES.get("photo")   # 📸 FILE yaha bata aauxa

        # ✅ DATABASE MA SAVE
        Refund.objects.create(
            user=request.user,
            name=name,
            email=email,
            issue_type=issue_type,
            description=description,
            photo=photo
        )

        messages.success(request, "Your support request has been sent successfully! ✅")
        return redirect("refund")

    return render(request, "shop/contact.html")
