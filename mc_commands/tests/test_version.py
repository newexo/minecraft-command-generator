import mc_commands


def test_version():
    assert mc_commands.__version__ is not None
