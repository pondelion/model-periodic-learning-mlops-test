def pytest_addoption(parser):
    parser.addoption(
        "--run-prod-tests",
        action="store_true",
        default=False,
        help="Run production summary generator tests"
    )
