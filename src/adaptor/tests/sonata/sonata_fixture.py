from pytest import fixture

@fixture
def auth_keys():
    return ['username', 'session_began_at', 'token']

