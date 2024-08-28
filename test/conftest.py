import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--check-messages",
        action="store",
        nargs='?',
        const='normal',
        default=False,
        choices=['normal', 'strict'],
        help="Enable comparing the outputted error messages match the specified error messages. Use 'strict' for treating empty message specs as errors instead of warnings."
    )

@pytest.fixture
def check_messages(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--check-messages")