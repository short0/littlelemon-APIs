from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category_id', 'category']


class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    menuitem_id = serializers.IntegerField()
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'quantity', 'unit_price', 'user_id', 'user', 'menuitem_id', 'menuitem']


class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    delivery_crew_id = serializers.IntegerField()
    delivery_crew = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'user', 'delivery_crew_id', 'delivery_crew', 'status']


class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField()
    order = OrderSerializer(read_only=True)
    menuitem_id = serializers.IntegerField()
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price', 'price', 'order_id', 'order', 'menuitem_id', 'menuitem']
