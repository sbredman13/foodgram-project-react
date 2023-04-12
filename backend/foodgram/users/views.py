from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Subscriptions, User
from users.serializers import (CustomUserSerializer, SignupSerializer,
                               SubscriptionSerializer)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def get_serializer_class(self):
        if self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        elif self.action == "me":
            return settings.SERIALIZERS.current_user
        return self.serializer_class

    @action(
        methods=["GET", "PATCH"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = CustomUserSerializer(
                user,
                context={"request": request}
            )
            return Response(serializer.data)
        serializer = CustomUserSerializer(
            user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(["post"], detail=False, permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request,
                context
            ).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("get",),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.subscribes.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)

        if self.request.method == "POST":
            if user == author:
                raise exceptions.ValidationError(
                    "Подписка на самого себя запрещена."
                )
            if Subscriptions.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError("Подписка уже оформлена.")

            Subscriptions.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Subscriptions.objects.filter(
                user=user, author=author
            ).exists():
                raise exceptions.ValidationError(
                    "Подписка не была оформлена, либо уже удалена."
                )

            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
