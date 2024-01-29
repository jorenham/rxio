def test_version():
    import rxio

    assert rxio.__version__
    assert all(map(str.isdigit, rxio.__version__.split('.')[:3]))
