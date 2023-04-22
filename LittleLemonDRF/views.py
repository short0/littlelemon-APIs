from rest_framework import generics
from django.contrib.auth.models import User, Group
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import UserSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, IsDeliveryCrew, IsCustomer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['title', 'price']
    search_fields = ['title']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        elif self.request.method in ['POST']:
            # return [IsManager()]
            return [IsAdminUser()]
        return [AllowAny()]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [AllowAny()]


class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        menuitem_id = self.request.data.get('menuitem_id')
        menuitem = MenuItem.objects.get(pk=menuitem_id)
        quantity = self.request.data.get('quantity')
        unit_price = self.request.data.get('unit_price')
        price = unit_price * quantity
        cart = Cart(
            user=user,
            menuitem_id=menuitem_id,
            quantity=quantity,
            unit_price=unit_price,
            price=price,
        )
        cart.save()

    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=204)

    def get_permissions(self):
        return [IsCustomer()]


class OrdersView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['id']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='DeliveryCrew').exists():
            return Order.objects.filter(delivery_crew=user)
        elif user.groups.filter(name='Customer').exists():
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.groups.filter(name='Customer').exists():
            cart = Cart.objects.filter(user=user)
            order = serializer.save(user=user)

            for item in cart:
                OrderItem.objects.create(order=order, menuitem=item.menuitem,
                                        quantity=item.quantity, unit_price=item.unit_price, price=item.price)
                item.delete()


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if user.groups.filter(name='Manager').exists() or user.groups.filter(name='DeliveryCrew').exists():
            super().perform_update(serializer)

    def perform_destroy(self, serializer):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            super().perform_destroy(serializer)


class ManagerUsersView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        group = Group.objects.get(name='Manager')
        queryset = User.objects.filter(groups=group)
        return queryset

    def perform_create(self, serializer):
        group = Group.objects.get(name='Manager')
        user = serializer.save()
        user.groups.add(group)

    def get_permissions(self):
        # return [IsManager()]
        return [IsAdminUser()]


class SingleManagerUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, serializer):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            group = Group.objects.get(name='Manager')
            user.groups.remove(group)

    def get_permissions(self):
        return [IsManager()]


class DeliveryCrewUsersView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        group = Group.objects.get(name='DeliveryCrew')
        queryset = User.objects.filter(groups=group)
        return queryset

    def perform_create(self, serializer):
        group = Group.objects.get(name='DeliveryCrew')
        user = serializer.save()
        user.groups.add(group)

    def get_permissions(self):
        return [IsManager()]


class SingleDeliveryCrewUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, serializer):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            group = Group.objects.get(name='DeliveryCrew')
            user.groups.remove(group)

    def get_permissions(self):
        return [IsManager()]
