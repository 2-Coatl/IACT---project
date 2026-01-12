"""Pruebas para el router de base de datos de solo lectura."""

import pytest


@pytest.mark.parametrize("app_label", ["ivr", "ivr.sub"])
def test_router_previene_escrituras_en_ivr(app_label):
    from callcentersite.database_router import IVRReadOnlyRouter

    DummyModel = type(
        "DummyModel",
        (),
        {
            "_meta": type(
                "_meta",
                (),
                {"app_label": app_label, "label": f"{app_label}.Dummy"},
            )
        },
    )

    router = IVRReadOnlyRouter()

    with pytest.raises(ValueError) as error:
        router.db_for_write(DummyModel())

    assert "READ-ONLY" in str(error.value)


def test_router_permite_escrituras_en_default():
    from callcentersite.database_router import IVRReadOnlyRouter

    class DummyModel:
        class _meta:
            app_label = "analytics"

    router = IVRReadOnlyRouter()

    assert router.db_for_write(DummyModel()) == "default"
