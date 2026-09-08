from chessvision.constants import Orientation, Turn


def test_orientation_white() -> None:
    assert Orientation.WHITE.ranks == ("8", "7", "6", "5", "4", "3", "2", "1")
    assert Orientation.WHITE.files == ("a", "b", "c", "d", "e", "f", "g", "h")

    coords = Orientation.WHITE.grid_coordinates
    assert len(coords) == 64
    assert coords[0] == "a8"
    assert coords[-1] == "h1"


def test_orientation_black() -> None:
    assert Orientation.BLACK.ranks == ("1", "2", "3", "4", "5", "6", "7", "8")
    assert Orientation.BLACK.files == ("h", "g", "f", "e", "d", "c", "b", "a")

    coords = Orientation.BLACK.grid_coordinates
    assert len(coords) == 64
    assert coords[0] == "h1"
    assert coords[-1] == "a8"


def test_turn_symbol() -> None:
    assert Turn.WHITE.symbol == "w"
    assert Turn.BLACK.symbol == "b"
