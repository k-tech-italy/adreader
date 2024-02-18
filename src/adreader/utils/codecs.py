import json

from adreader.gui import ParsableMixin, Point, Box


class AdreaderEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ParsableMixin):
            return str(obj)
        elif isinstance(obj, dict):
            # Iterate through the dictionary and encode custom objects
            return {key: self.default(value) for key, value in obj.items()}
        return super().default(obj, ensure_ascii=False)


class AdreaderDecoder(json.JSONDecoder):
    def _parse_object(self, s):
        if isinstance(s, str):
            if s.startswith('Point[') and s.endswith(']'):
                return Point.parse(s)
            if s.startswith('Box[') and s.endswith(']'):
                return Box.parse(s)

    def object_hook(self, d):
        if isinstance(d, str) and (parsed := self.parse_string(d)):
            return parsed
        elif isinstance(d, dict):
            # Decode custom objects if "__class__" key is present
            for key, value in d.items():
                if "__class__" in value:
                    d[key] = self.decode_custom_object(value)
            return d
        return d

    def decode(self, s, _w=...):
        if ret := self._parse_object(s):
            return ret

        ret = super().decode(s)
        if isinstance(ret, list):
            subret = []
            for item in ret:
                if isinstance(item, str) and (parsed := self._parse_object(item)):
                    item = parsed
                subret.append(item)
            return subret
        elif isinstance(ret, dict):
            subret = {}
            for k, v in ret.items():
                if isinstance(v, str) and (parsed := self._parse_object(v)):
                       v = parsed
                subret[k] = v
            return subret
        return ret

    def object_hook(self, s: str):
        if s.startswith('Point[') and s.endswith(']'):
            return Point.parse(s)
        if s.startswith('Box[') and s.endswith(']'):
            return Box.parse(s)
        return super().decode(s)
