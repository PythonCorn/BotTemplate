from fastapi import Request

from app.core.states.app_state import AppState


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state