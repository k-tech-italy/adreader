import contextlib
import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from adreader.gui import Point, Box


@pytest.fixture
def cm_cache():

    @contextlib.contextmanager
    def fx():
        from adreader.utils.cache import Cache
        old = Cache.CACHE_LOC
        with tempfile.TemporaryDirectory() as tdir:
            tfile = Path(tdir) / 'cache.json'
            Cache.CACHE_LOC = tfile
            yield tfile
            Cache.CACHE_LOC = old

    return fx


def test_cache(cm_cache):
    with cm_cache() as tdir:
        from adreader.utils.cache import Cache
        cache = Cache()
        assert cache.read() == {}

        cache.write(pippo=11)

        vals = cache.read()
        assert vals == {'pippo': 11}

        cache.write(point1=Point(1,5), box1=Box(2, 5, 100, 155))
        vals = cache.read()
        assert vals == {'pippo': 11, 'point1': Point(1,5), 'box1': Box(2, 5, 100, 155)}
