import json
import os

import click
from fastapi import FastAPI
from uvicorn.importer import import_from_string


@click.command()
@click.argument("app")
@click.argument("output")
@click.option(
    "--file-name",
    "file_name",
    default="openapi.json",
    show_default=True,
    help="Filename of the OpenAPI document (json)",
)
def main(app: str, output: str, file_name: str = "openapi.json") -> None:
    """Generate the OpenAPI spec from a FastAPI module"""

    fastapi: FastAPI = import_from_string(app)

    os.makedirs(output, exist_ok=True)

    with open(f"{output}/{file_name}", "w+", encoding="utf-8") as openapi:
        openapi.write(json.dumps(fastapi.openapi(), indent=2))
        openapi.close()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
