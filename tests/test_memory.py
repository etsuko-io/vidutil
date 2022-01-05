from vidutil.memory import get_current_memory


def test_get_current_memory():
    mem = get_current_memory()
    assert mem
