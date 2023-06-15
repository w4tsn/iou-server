IOU
===

*As in I o(we) (yo)u 5€.*

Shared expenses management tool that does not spy on you (currently in pre-alpha).

Contributing
---

```bash
git clone ssh://git.notourserver.de:2222/victor/iou.git
cd iou
python -m venv --upgrade-deps .venv
source .venv/bin/activate{.fish} # omit depending on shell used
pip install -e .[dev]
alembic upgrade head # apply database migrations to local iou.db
python example.py
python -m iou
pre-commit install # sets up static type checking, linting, etc.
```

Run linting and tests:

```bash
pytest --cov-report term --cov-report html --cov-report=xml:pytest-cobertura.xml --cov=iou test
pre-commit run --all
```

Find the docs after starting the project under [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

You may want to build a python package and upload it using twine:

```bash
python -m build
twine upload --verbose --skip-existing dist/*
```

Manage database migrations:

Alembic is used to compose and apply database migration scripts.

Check if migrations are missing:

```
alembic check
```

Then generate a new migration:

```
alembic revision --autogenerate
```

Apply the latest migration:

```
alembic upgrade head
```
