from rest_framework.permissions import BasePermission


class ChildBasePermission(BasePermission):
    group = ''

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.groups.filter(name=self.group):
                return True
        return False


class IsManager(ChildBasePermission):
    group = 'Manager'


class IsDeliveryCrew(ChildBasePermission):
    group = 'DeliveryCrew'


class IsCustomer(ChildBasePermission):
    group = 'Customer'
    