import pytest

from rxio.getters import Self, Attr, Item


def test_self():
    assert Self == Self

    obj = object()

    assert Self(obj) is obj
    assert Self._root is Self
    assert str(Self) == "_"


def test_attr():
    attr = Self.spam
    assert isinstance(attr, Attr)

    assert attr._root is Self
    assert attr._arg == "spam"

    assert str(attr) == "_.spam"

    match attr:
        case Attr(_, "eggs"):
            assert False
        case Attr(_, "spam"):
            assert True
        case _:
            assert False

    class SpamClass:
        def __init__(self):
            self.spam = "spam"

    obj = SpamClass()
    assert attr(obj) == obj.spam


def test_item():
    item = Self["spam"]
    assert item > Self
    
    assert item._root is Self
    assert item._arg == "spam"
    assert str(item) == "_['spam']"

    match item:
        case Item(_, "eggs"):
            assert False
        case Item(_, "spam"):
            assert True
        case _:
            assert False

    obj = {"spam": "spam"}

    assert item(obj) == obj['spam']


def test_attr_attr():
    attr = Self.spam.ham

    assert attr == Self.spam.ham
    assert attr >= Self.spam.ham
    assert attr <= Self.spam.ham

    assert attr >= Self.spam
    assert attr > Self.spam
    assert Self.spam < attr
    assert Self.spam <= attr

    assert str(attr) == "_.spam.ham"

    match attr:
        case Attr(_, "eggs"):
            assert False
        case Attr(_, "spam"):
            assert True
        case _:
            assert False

    class SpamClass:
        def __init__(self):
            self.spam = "spam"

    obj = SpamClass()
    assert attr(obj) == obj.spam
