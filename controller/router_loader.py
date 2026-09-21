# api/controller/router_loader.py

import pkgutil
import importlib
from fastapi import FastAPI
import controller as controller_package


def register_routers(app: FastAPI):
    for _, module_name, _ in pkgutil.iter_modules(controller_package.__path__):

        # skip this file
        if module_name == "router_loader":
            continue

        module = importlib.import_module(f"controller.{module_name}")

        if hasattr(module, "router"):
            router = getattr(module, "router")
            app.include_router(router)
