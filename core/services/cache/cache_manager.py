import typing


class CacheItem(dict):
    def __getattr__(self, item):
        return self.get(item)


class CacheManager:
    def __init__(self, name: str, max_size: int):
        self.items = []
        self._max_size = max_size
        self.name = name

    def get(self, **kwargs) -> typing.Optional[CacheItem]:
        for item in self.items:
            if all([item[key] == value for key, value in kwargs.items()]):
                return CacheItem(**item)

        return None

    def find(self, **kwargs) -> typing.List[CacheItem]:
        return [
            CacheItem(**item)
            for item in self.items
            if all([item[key] == value for key, value in kwargs.items()])
        ]

    def add(self, item) -> None:
        self.items.append(item)

        if len(self.items) > self._max_size:
            self.items.pop(0)

    def update(self, new_data, **kwargs) -> typing.Optional[CacheItem]:
        item = self.get(**kwargs)
        if item is None:
            return None

        self.items[self.items.index(item)] = new_data
        return CacheItem(**item)

    def remove(self, **kwargs) -> typing.Optional[CacheItem]:
        item = self.get(**kwargs)
        if item is None:
            return None

        self.items.remove(item)
        return CacheItem(**item)

    def all(self) -> typing.List[CacheItem]:
        return [CacheItem(**item) for item in self.items]

    def count(self) -> int:
        return len(self.items)

    def __repr__(self):
        return "CacheManager(name={0.name}, max_size={0._max_size} items=[".format(self)+("\n".join([
            f"Item({CacheItem(**item)})"
            for item in self.items
        ]))+"])"