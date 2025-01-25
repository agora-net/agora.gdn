def onboarding_not_required(view_func):
    """
    Decorator for views that removes the need for a user to be fully onboarded.
    """
    view_func.onboarding_required = False
    return view_func
