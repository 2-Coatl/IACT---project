"""Router que protege la base de datos legacy del IVR."""

from __future__ import annotations

from typing import Any, Optional


class IVRReadOnlyRouter:
    """Enruta operaciones de base de datos protegiendo el origen IVR."""

    ivr_apps = {"ivr"}

    def db_for_read(self, model: Any, **hints: Any) -> Optional[str]:
        app_label = getattr(getattr(model, "_meta", None), "app_label", "")
        if app_label.startswith("ivr"):
            return "ivr_readonly"
        return "default"

    def db_for_write(self, model: Any, **hints: Any) -> Optional[str]:
        app_label = getattr(getattr(model, "_meta", None), "app_label", "")
        if app_label.startswith("ivr"):
            label = getattr(getattr(model, "_meta", None), "label", app_label)
            raise ValueError(
                "CRITICAL RESTRICTION VIOLATED: Attempted write operation on IVR "
                f"database. Model: {label}. IVR database is READ-ONLY. Only SELECT operations "
                "are allowed."
            )
        return "default"

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> Optional[bool]:
        dbs = {getattr(obj1._state, "db", None), getattr(obj2._state, "db", None)}
        if dbs <= {None, "default", "ivr_readonly"}:
            return True
        return None

    def allow_migrate(
        self, db: str, app_label: str, model_name: Optional[str] = None, **hints: Any
    ) -> bool:
        if db == "ivr_readonly":
            return False
        if app_label.startswith("ivr"):
            return False
        return True
