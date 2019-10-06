import pytest


@pytest.fixture(scope="function")
def service_init_mock(mocker):
    with mocker.patch("backend.dao.es.ES") as MockES:
        def mock_init(self):
            self.es = MockES()

        return mock_init
