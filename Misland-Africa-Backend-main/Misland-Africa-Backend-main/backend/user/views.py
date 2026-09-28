from django.shortcuts import render

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import APIException
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from user.backends import JWTAuthentication

#  rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from user.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserAccountActivateSerializer,
    RequestResetForgottenPasswordSerializer,
    ResetForgottenPasswordSerializer,
    # UserAccountDeleteSerializer,
    UserAccountDeleteRequestSerializer,
)
from user.models import UserProfile, CustomUser
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from user.serializers import ChangePasswordSerializer, UserUpdateSerializer
from user.permissions import IsAdminOrSelf
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings
from user.utils.settings_util import get_user_settings
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

User = get_user_model()


class EmailDeliveryUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("Email delivery is temporarily unavailable. Please try again.")
    default_code = "email_delivery_unavailable"


def build_email_action_url(base_url, uid, token):
    """Build an account-action URL and fail cleanly when it is not configured."""
    if not isinstance(base_url, str) or not base_url.strip():
        raise EmailDeliveryUnavailable(
            _("The account email link is not configured for this site.")
        )
    return "{}/{}/{}/".format(base_url.rstrip("/"), uid, token)


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Register a user
        """
        # restore those native datatypes into a dictionary of validated data.
        serializer = self.serializer_class(data=request.data)

        # checks if the data is as per serializer fields, otherwise throws an exception
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        # return an object instance, based on the validated data.
        with transaction.atomic():
            user = serializer.save()

            message = _("User registered successfully")
            if get_user_settings().enable_user_account_email_activation:
                if not self.send_activate_email(request, user):
                    raise EmailDeliveryUnavailable()
                message = _(
                    "Please confirm your email address to complete the registration"
                )

        status_code = status.HTTP_201_CREATED
        response = {"success": "true", "status_code": status_code, "message": message}
        return Response(response, status=status_code)

    def send_activate_email(self, request, user):
        """Send an email"""
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        from common.utils.url_map_util import get_mapped_url

        account_activation_url = get_mapped_url(
            url_key="account_activation_url", request=request
        )
        message = render_to_string(
            "user/activate_account.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": uid,
                "token": token,
                "endpoint": build_email_action_url(
                    account_activation_url, uid, token
                ),
            },
        )
        to_email = user.email
        subject = _("Activate your account")

        dct = model_to_dict(user)
        del dct["password"]
        del dct["password2"]
        from communication.utils import email_helper

        return email_helper.send_email(
            subject,
            message,
            [to_email],
            message_type="Account activation",
            reference_doctype=str(user),
            reference_docname=str(user.id),
            arguments=str(dct),
            method=request.META.get("PATH_INFO") if request.META else "",
            request=str(request),
        )


class UserAccountActivationView(viewsets.ReadOnlyModelViewSet):
    """
    View to manage activation of user accounts
    """

    # See https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef

    serializer_class = UserAccountActivateSerializer
    permission_classes = (AllowAny,)

    # def activate(self):#, uidb64, token):
    def activate(self, request, *args, **kwargs):
        """Activate user account"""
        try:
            uidb64 = self.kwargs.get(
                "uidb64", None
            )  # self.request.query_params.get('uidb64', None)
            token = self.kwargs.get(
                "token", None
            )  # self.request.query_params.get('token', None)
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _(
                    "Your account has been activated. You can now login to your account"
                ),
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status_code": status_code,
                "message": _("Activation link is invalid"),
            }
        return Response(response, status=status_code)


class UserLoginView(RetrieveAPIView):

    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        """
        Login and return a token generated for user if successful
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        response = {
            "success": "true",
            "status_code": status.HTTP_200_OK,
            "message": _("User logged in successfully"),
            "token": serializer.data["token"],
            # 'firebase_token': serializer.data['firebase_token']
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class UserList(generics.ListAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """
        If superuser, return all users, else return only the current user
        """
        if self.request.user.is_superuser or self.request.user.is_admin:
            return CustomUser.objects.all()
        else:
            return CustomUser.objects.filter(email=self.request.user.email)

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = UserRegistrationSerializer(queryset, many=True)
        return Response(serializer.data)


class UserRetrieveView(RetrieveUpdateAPIView):
    """
    RetrieveAPIView as we want to retrieve a single instance.
    Also, we have set permission_classes to IsAuthenticated so
    the only user who is authenticated can hit this API and the
    authentication_class should be JWT.
    """

    permission_classes = (IsAuthenticated, IsAdminOrSelf)
    authentication_classes = (JWTAuthentication,)  # (JSONWebTokenAuthentication, )

    def get_object(self, queryset=None, email=None):
        """If no email supplied, return the current user"""
        if not email:
            obj = self.request.user
        else:
            obj = CustomUser.objects.filter(email=email).first()
        if obj is None:
            return None
        # Ensure that permission classes (IsAuthenticated, IsAdminOrSelf) are applied
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request):
        user = self.get_object(email=request.query_params.get("email", None))
        if user:
            profile = UserProfile.objects.filter(user=user).first()
            if profile is None:
                return Response(
                    {"message": _("User profile does not exist")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _("User profile fetched successfully"),
                "data": [
                    {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profession": profile.profession,
                        "institution": profile.institution,
                        "title": profile.title,
                        "is_active": int(user.is_active),
                        "is_admin": int(user.is_admin),
                        # 'is_superuser': int(user.is_superuser),
                        "can_upload_custom_shapefile": int(
                            profile.can_upload_custom_shapefile
                        ),
                        "can_upload_standard_raster": int(
                            profile.can_upload_standard_raster
                        ),
                    }
                ],
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status_code": status_code,
                "message": _("User does not exist"),
            }
        return Response(response, status=status_code)


class RequestResetForgottenPasswordView(viewsets.ModelViewSet):
    """
    Endpoint for requesting resetting of forgotten password.
    It is different from the ChangePasswordView which takes care
    of normal updating of passwords
    """

    serializer_class = RequestResetForgottenPasswordSerializer
    model = CustomUser
    permission_classes = (AllowAny,)

    def request_password_reset(self, request, *args, **kwargs):
        """Request password change"""
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].lower()
        user = CustomUser.objects.filter(email=email).first()
        if user is not None and not self.send_reset_password_request_email(
            request, user
        ):
            raise EmailDeliveryUnavailable()

        # Use the same response whether the address exists to avoid account discovery.
        status_code = status.HTTP_200_OK
        response = {
            "success": "true",
            "status_code": status_code,
            "message": _(
                "If an account exists for this email, a password reset link has been sent."
            ),
        }
        return Response(response, status=status_code)

    def send_reset_password_request_email(self, request, user):
        """Send an email"""
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        from common.utils.url_map_util import get_mapped_url

        change_password_url = get_mapped_url(
            url_key="change_password_url", request=request
        )
        message = render_to_string(
            "user/change_password.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": uid,
                "token": token,
                "endpoint": build_email_action_url(
                    change_password_url, uid, token
                ),
            },
        )
        to_email = user.email
        subject = _("MISLAND Password Change Request")
        dct = model_to_dict(user)
        del dct["password"]
        from communication.utils import email_helper

        return email_helper.send_email(
            subject,
            message,
            [to_email],
            message_type="Password Change Request",
            reference_doctype=str(user),
            reference_docname=str(user.id),
            arguments=str(dct),
            method=request.META.get("PATH_INFO") if request.META else "",
            request=str(request),
        )


class ResetForgottenPasswordView(viewsets.ModelViewSet):
    """
    View to manage activation of user accounts
    """

    # See https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef

    serializer_class = ResetForgottenPasswordSerializer
    permission_classes = (AllowAny,)

    def reset_password(self, request, *args, **kwargs):
        """Reset forgotten user password"""
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uidb64 = serializer.validated_data["uid"]
            token = serializer.validated_data["token"]
            password = serializer.validated_data["new_password"]
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            try:
                validate_password(password, user=user)
            except DjangoValidationError as exc:
                return Response(
                    {"new_password": list(exc.messages)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(password)
            user.save()
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _("Password updated successfully"),
            }
            return Response(response, status_code)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status_code": status_code,
                "message": _("The reset password link is invalid"),
            }
        return Response(response, status=status_code)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Endpoint for changing password
    """

    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated, IsAdminOrSelf)

    def get_object(self, queryset=None, email=None):
        """If no email supplied, return the current user"""
        if not email:
            obj = self.request.user
        else:
            obj = CustomUser.objects.filter(email=email).first()
        if obj is None:
            return None
        # Ensure that permission classes (IsAuthenticated, IsAdminOrSelf) are applied
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(email=request.data.get("email"))
        if self.object is None:
            return Response(
                {"message": _("User does not exist")},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not self.object.check_password(
                serializer.validated_data["old_password"]
            ):
                status_code = status.HTTP_400_BAD_REQUEST
                response = {
                    "success": "false",
                    "status_code": status_code,
                    "message": _("Incorrect old password"),
                }
                return Response(response, status=status_code)

            try:
                validate_password(
                    serializer.validated_data["new_password"], user=self.object
                )
            except DjangoValidationError as exc:
                return Response(
                    {"new_password": list(exc.messages)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.object.set_password(serializer.validated_data["new_password"])
            self.object.save()
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _("Password updated successfully"),
            }
            return Response(response, status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(generics.UpdateAPIView):
    """
    Endpoint for updating user
    """

    serializer_class = UserUpdateSerializer
    # model = CustomUser
    permission_classes = (IsAuthenticated, IsAdminOrSelf)

    def get_object(self, queryset=None, email=None):
        obj = CustomUser.objects.filter(email=email).first()
        if obj is None:
            return None
        # Ensure that permission classes (IsAuthenticated, IsAdminOrSelf) are applied
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(email=request.data.get("email"))
        if not self.object:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status_code": status_code,
                "message": _("User does not exist"),
            }
            return Response(response, status=status_code)

        data = request.data.copy()

        """If user is not admin, disable sensitive fields"""
        if not request.user.is_admin:
            data.pop("is_admin", None)
            data.pop("is_superuser", None)
            data.pop("is_staff", None)
            profile = data.get("profile")
            if isinstance(profile, dict):
                profile.pop("can_upload_custom_shapefile", None)
                profile.pop("can_upload_standard_raster", None)

        serializer = self.serializer_class(self.object, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _("User details updated successfully"),
            }
            return Response(response, status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAccountDeleteRequestView(CreateAPIView):
    serializer_class = UserAccountDeleteRequestSerializer
    permission_classes = (IsAuthenticated, IsAdminOrSelf)

    def get_object(self, queryset=None, email=None):
        obj = CustomUser.objects.filter(email=email).first()
        if obj is None:
            return None
        # Ensure that permission classes (IsAuthenticated, IsAdminOrSelf) are applied
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request):
        """
        Request user deletion
        """
        # restore those native datatypes into a dictionary of validated data.
        serializer = self.serializer_class(data=request.data)

        # checks if the data is as per serializer fields, otherwise throws an exception
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        self.object = self.get_object(email=serializer.validated_data["email"])

        # return an object instance, based on the validated data.
        # serializer.validated_data.is_active = False
        # serializer.save()

        # if get_user_settings().enable_user_account_email_activation:
        if self.object is None:
            return Response(
                {"message": _("User does not exist")},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not self.send_delete_request_email(request, self.object):
            raise EmailDeliveryUnavailable()
        message = _("Please check your email to complete deleting your account.")

        status_code = status.HTTP_201_CREATED
        response = {"success": "true", "status_code": status_code, "message": message}
        return Response(response, status=status_code)

    def send_delete_request_email(self, request, user):
        """Send an email"""
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        from common.utils.url_map_util import get_mapped_url

        account_delete_request_url = get_mapped_url(
            url_key="account_delete_request_url", request=request
        )
        message = render_to_string(
            "user/delete_account.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": uid,
                "token": token,
                "endpoint": build_email_action_url(
                    account_delete_request_url, uid, token
                ),
            },
        )
        to_email = user.email
        subject = _("Delete your MISLAND account")

        dct = model_to_dict(user)
        del dct["password"]
        del dct["password2"]
        from communication.utils import email_helper

        return email_helper.send_email(
            subject,
            message,
            [to_email],
            message_type="Account deletion",
            reference_doctype=str(user),
            reference_docname=str(user.id),
            arguments=str(dct),
            method=request.META.get("PATH_INFO") if request.META else "",
            request=str(request),
        )


class UserAccountDeleteView(viewsets.ReadOnlyModelViewSet):
    """
    View to manage deleting of user accounts
    """

    # See https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef

    serializer_class = UserAccountDeleteRequestSerializer
    permission_classes = (AllowAny,)

    # def activate(self):#, uidb64, token):
    def deleteuser(self, request, *args, **kwargs):
        """Delete user account"""
        try:
            uidb64 = self.kwargs.get(
                "uidb64", None
            )  # self.request.query_params.get('uidb64', None)
            token = self.kwargs.get(
                "token", None
            )  # self.request.query_params.get('token', None)
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.delete()
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status_code": status_code,
                "message": _("Your account has been deleted successfully."),
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status_code": status_code,
                "message": _("Deletion link is invalid"),
            }
        return Response(response, status=status_code)


# class UserAccountDeleteView(generics.DestroyAPIView):
#     """
#     View to manage deleting of user accounts
#     """

#     # See https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef

#     serializer_class = UserAccountDeleteSerializer
#     permission_classes = (IsAuthenticated, IsAdminOrSelf)

#     def get_object(self, queryset=None, email=None):
#         obj = CustomUser.objects.filter(email=email).first()
#         # Ensure that permission classes (IsAuthenticated, IsAdminOrSelf) are applied
#         self.check_object_permissions(self.request, obj)
#         return obj

#     def post(self, request, *args, **kwargs):
#         """Delete user account"""
#         self.object = self.get_object(email=request.data.get("email"))
#         if not self.object:
#             # status_code = status.HTTP_400_BAD_REQUEST
#             # response = {
#             #     "success": "false",
#             #     "status_code": status_code,
#             #     "message": _("User does not exist"),
#             # }

#             # as a security issue, send email confirmation on email
#             status_code = status.HTTP_200_OK
#             response = {
#                 "success": "true",
#                 "status_code": status_code,
#                 "message": _("Your account has been deleted successfully."),
#             }
#             return Response(response, status=status_code)

#         res = self.object.delete()
#         if res:
#             status_code = status.HTTP_200_OK
#             response = {
#                 "success": "true",
#                 "status_code": status_code,
#                 "message": _("Your account has been deleted successfully."),
#             }
#         else:
#             status_code = status.HTTP_400_BAD_REQUEST
#             response = {
#                 "success": "false",
#                 "status_code": status_code,
#                 "message": _("Activation link is invalid"),
#             }
#         return Response(response, status=status_code)

#         try:
#             uidb64 = self.kwargs.get(
#                 "id", None
#             )  # self.request.query_params.get('uidb64', None)
#             token = self.kwargs.get(
#                 "token", None
#             )  # self.request.query_params.get('token', None)
#             # uid = urlsafe_base64_decode(uidb64).decode()
#             user = CustomUser.objects.get(pk=id)
#             user.delete()
#         except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#             user = None

#         if user is not None:
#             status_code = status.HTTP_200_OK
#             response = {
#                 "success": "true",
#                 "status_code": status_code,
#                 "message": _("Your account has been deleted successfully."),
#             }
#         else:
#             status_code = status.HTTP_400_BAD_REQUEST
#             response = {
#                 "success": "false",
#                 "status_code": status_code,
#                 "message": _("Activation link is invalid"),
#             }
#         return Response(response, status=status_code)


# class UserAccountActivationView(viewsets.ReadOnlyModelViewSet):
#     """
#     View to manage activation of user accounts
#     """

#     # See https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef

#     serializer_class = UserAccountActivateSerializer

#     # def activate(self):#, uidb64, token):
#     def activate(self, request, *args, **kwargs):
#         """Activate user account"""
#         try:
#             uidb64 = self.kwargs.get(
#                 "uidb64", None
#             )  # self.request.query_params.get('uidb64', None)
#             token = self.kwargs.get(
#                 "token", None
#             )  # self.request.query_params.get('token', None)
#             uid = urlsafe_base64_decode(uidb64).decode()
#             user = CustomUser.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#             user = None

#         if user is not None and default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             status_code = status.HTTP_200_OK
#             response = {
#                 "success": "true",
#                 "status_code": status_code,
#                 "message": _(
#                     "Your account has been activated. You can now login to your account"
#                 ),
#             }
#         else:
#             status_code = status.HTTP_400_BAD_REQUEST
#             response = {
#                 "success": "false",
#                 "status_code": status_code,
#                 "message": _("Activation link is invalid"),
#             }
#         return Response(response, status=status_code)
