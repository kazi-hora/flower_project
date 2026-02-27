from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('flowers/', views.flowers, name='flowers'),
    path('shopplants/', views.shopplants, name='shopplants'),   # ✅ matches views.py
    path('weddings/', views.weddings, name='weddings'),         # ✅ matches views.py
    path('workshop/', views.workshop, name='workshop'), 
    path('about/', views.about, name='about'),
    path('returns/', views.returns_view, name='returns'),
    
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return-order/<int:order_id>/', views.return_order, name='return_order'),


    path('orders/', views.orders, name='orders'),
    path('map/', views.map, name='map'),
    path('contact/', views.contact, name='contact'),
    path('contact/refund/', views.refund_request, name='refund_request'),

    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),

    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy/<int:flower_id>/', views.buy_now, name='buy_now'),
]
