from functools import wraps
import asyncio

WIDGETS = {}

def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.
    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS 
            dictionary. This should follow the same structure as other entries 
            in WIDGETS.
    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator