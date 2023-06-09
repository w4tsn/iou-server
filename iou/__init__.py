"""IOU"""

from ._version import VERSION as __version__  # noqa: F401


def run() -> None:
    """
    Entrypoint to run the IOU API server
    """
    # This is defined here in __init__ and not in main for the `IOU` console_script
    # specified in pyproject.toml
    # pylint: disable=import-outside-toplevel
    from multiprocessing import Process

    import uvicorn

    from iou.config import Environment, settings  # noqa: 402

    Process(
        target=uvicorn.run,
        kwargs={
            "app": "iou.main:app",
            "host": settings.IOU_SERVER_HOST,
            "port": settings.IOU_SERVER_PORT,
            "log_level": "info",
            "reload": settings.IOU_ENVIRONMENT == Environment.DEVELOP,
            "workers": 2 if settings.IOU_ENVIRONMENT == Environment.DEVELOP else 4,
        },
    ).start()
