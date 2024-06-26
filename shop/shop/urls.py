#shop/urls.py
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('profile/order_history/', views.order_history, name='order_history'),
    path('products/', views.product_list, name='product_list'),
    path('products/category/<int:category_id>/', views.product_list, name='product_list_by_category'),  # Фильтрация по категориям
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.product_list, name='product_search'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/order_success/<int:order_id>/', views.order_success, name='order_success'),

]
