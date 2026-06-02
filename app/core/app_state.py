from dataclasses import dataclass

from fastapi import Request

from app.core.container import Container


@dataclass(slots=True)
class AppState:
    container: Container


def get_app_state(request: Request) -> AppState:
    state: AppState = request.app.state.app_state
    if not isinstance(state, AppState):
        raise RuntimeError("AppState is not set in the request")
    return state
