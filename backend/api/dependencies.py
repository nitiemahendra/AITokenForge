from fastapi import Request


def get_app_state(request: Request) -> dict:
    return request.app.state.app_state


def get_optimization_engine(request: Request):
    return request.app.state.app_state["optimization_engine"]


def get_token_analyzer(request: Request):
    return request.app.state.app_state["token_analyzer"]


def get_cost_estimator(request: Request):
    return request.app.state.app_state["cost_estimator"]
