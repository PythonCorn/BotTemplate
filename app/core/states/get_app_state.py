from fastapi import Request

from app.core.states.app_state import AppState


def get_app_state(request: Request) -> AppState:
    state: AppState = request.app.state.app_state
    if not isinstance(state, AppState):
        raise RuntimeError("AppState is not set in the request")
    return state
