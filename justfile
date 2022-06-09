@_default:
    just --list

@check:
    poetry run mypy src tests
    poetry run pytest
