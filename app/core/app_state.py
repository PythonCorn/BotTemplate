from dataclasses import dataclass

from fastapi import Request
from starlette.datastructures import State

from app.core.container import Container


@dataclass(slots=True)
class AppState:
    """
    Represents the state of an application.

    This class is designed to encapsulate the state of the application, providing
    a structured way to manage and access core components like the container. It
    utilizes Python's `dataclass` and `slots` for memory efficiency and immutability.

    Attributes:
        container (Container): The dependency injection container or service locator
            used to manage and resolve application dependencies.
    """

    container: Container


def get_app_state(request: Request[State]) -> AppState:
    """
    Retrieves the `AppState` instance from the application state associated with the given request.
    This function ensures that the application state is properly set and casts it to the expected
    `AppState` type. If the application state is not available or is of an incorrect type,
    a `RuntimeError` is raised.

    Args:
        request (Request[State]): The HTTP request object containing the application state.

    Returns:
        AppState: The application state extracted from the request.

    Raises:
        RuntimeError: If the application state is not set or does not match the expected `AppState` type.
    """
    state: AppState = request.app.state.app_state
    if not isinstance(state, AppState):
        raise RuntimeError("AppState is not set in the request")
    return state
