"""Module contain authenticators"""
import abc

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import (
    InvalidToken as JWTInvalidToken,
    TokenError as JWTTokenError,
)

from django_ws_app.exceptions import InvalidToken


class AuthenticatorInterface(metaclass=abc.ABCMeta):
    """Authenticator interface"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "find_user")
            and callable(subclass.find_user)
            or NotImplemented
        )

    @abc.abstractmethod
    def find_user(self, data):
        """Find user"""
        raise NotImplementedError


class JWTAuthenticator(AuthenticatorInterface):
    """JWT Authenticator"""
    def find_user(self, data):
        try:
            jwt = JWTAuthentication()
            token = jwt.get_validated_token(data)
            return jwt.get_user(token)
        except JWTInvalidToken as exception:
            raise InvalidToken() from exception
        except JWTTokenError as exception:
            raise InvalidToken() from exception
