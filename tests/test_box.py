import json

from adreader.utils.codecs import AdreaderEncoder, AdreaderDecoder
from adreader.gui import Point, Box


def test_point():
    lll = 17, 45
    p = Point(*lll)
    encoded = AdreaderEncoder().encode(p)
    assert encoded == '"Point[17, 45]"'
    assert p == Point(17, 45)


def test_box():
    box = Box(Point(11, 22), Point(133, 144))
    encoded = AdreaderEncoder().encode(box)
    assert encoded == '"Box[11, 22, 133, 144]"'
    assert box == Box(11, 22, 133, 144)


def test_json_codec():
    d = dict(
        point1=Point(17, 45),
        box1=Box(11, 22, 133, 144)
    )
    encoded = json.dumps(d, cls=AdreaderEncoder)
    assert encoded == '{"point1": "Point[17, 45]", "box1": "Box[11, 22, 133, 144]"}'

    decoded = json.loads(encoded, cls=AdreaderDecoder)
    assert list(decoded.keys()) == list(d.keys())
    assert decoded == d


def test_box_math():
    assert Box(11, 22, 233, 144) > Box(12, 22, 233, 144)
    assert Box(11, 22, 233, 144) > Box(11, 23, 233, 144)
    assert Box(11, 22, 233, 144) > Box(11, 22, 232, 144)
    assert Box(11, 22, 233, 144) > Box(11, 22, 233, 143)
    assert Box(11, 22, 233, 144) < Box(10, 22, 233, 144)
