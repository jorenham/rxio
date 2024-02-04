import rxio


def test_version():
    assert rxio.__version__
    assert all(map(str.isdigit, rxio.__version__.split('.')[:3]))
