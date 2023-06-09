import logging
from abc import ABC, abstractclassmethod, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)

PRE_AUTHENTICATED_HEADER = "x-iou-pre-authencticated"


class AuthenticationError(Exception):
    """Error raised if authentication fails"""


class AuthorizationError(Exception):
    """ "Error raised if authorization check fails"""


@dataclass
class Authentication(ABC):
    """Authentication information"""

    # TODO: implement more authentication properties
    username: str


@dataclass
class AuthenticationPreAuthenticated(Authentication):
    """Authentication info from pre-authentication header"""

    @classmethod
    def from_headers(cls, headers: Dict[str, Any]) -> "AuthenticationPreAuthenticated":
        """Parse auth info from x-iou-pre-authenticated header"""
        logger.debug(
            f"Trying to parse authorization pre-authenticated header from: {headers}"
        )
        try:
            return AuthenticationPreAuthenticated(
                username=str(headers.get(PRE_AUTHENTICATED_HEADER))
            )
        except KeyError:
            raise AuthenticationError("Could not parse x-iou-pre-authenticated header")


@dataclass
class Authorization(ABC):
    """Authorization information"""

    # TODO: implement more authorization properties
    admin: bool = True

    @abstractmethod
    def authorized(self, operation: str | None = None) -> bool:
        """Check if a user-attached authz info grants this operation"""


@dataclass
class AuthorizationPreAuthenticated(Authorization):
    """Authorization info parsed from headers"""

    def authorized(self, operation: str | None = None) -> bool:
        # TODO: implement authorization
        logger.debug(f"Checking authorization for operation: {operation}")
        if operation is None and not self.admin:
            raise AuthorizationError("No operation to authorize this context")
        return self.admin


# TODO: implement AuthorizationOidc class which uses an OIDC token's claims

# TODO: implement AuthorizationKeycloak class which uses Keycloak
#       Authorization Services
#       https://www.keycloak.org/docs/latest/authorization_services/index.html
