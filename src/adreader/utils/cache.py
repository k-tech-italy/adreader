import json
from pathlib import Path


from adreader.utils.codecs import AdreaderDecoder, AdreaderEncoder


class Cache:
    CACHE_LOC = Path(__file__).parent / '.cache.json'

    def read(self):
        if self.CACHE_LOC.exists():
            cache = json.loads(self.CACHE_LOC.read_text() or "{}", cls=AdreaderDecoder)
            return cache
        return {}

    def write(self, **kwargs):
        cache = self.read()
        cache |= kwargs
        with self.CACHE_LOC.open('wt') as fo:
            fo.write(json.dumps(cache, cls=AdreaderEncoder))
