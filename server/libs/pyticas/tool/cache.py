__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import threading

class LRUCache:

    def __init__(self, maxsize=1000):
        self.maxsize = maxsize
        self.mapping = {}

        PREV, NEXT, KEY, VALUE = 0, 1, 2, 3 
        self.head = [None, None, None, None]        # oldest
        self.tail = [self.head, None, None, None]   # newest
        self.head[NEXT] = self.tail

    def make_key(self, obj):
        try:
            hash(obj)
            return obj, type(obj)
        except:
            pass
        if isinstance(obj, set): obj = sorted(obj)        
        if isinstance(obj, (list, tuple)): return tuple(self.make_key(e) for e in obj)
        if isinstance(obj, dict):
            return tuple(sorted(((self.make_key(k), self.make_key(v)) for k, v in obj.items())))
        raise ValueError("%r can not be hashed. Try providing a custom key function." % obj)

    def cache(self, func):

        context = threading.RLock()

        def _cache_func(*args, **kwargs):
            return func(*args, **kwargs)

        #     PREV, NEXT = 0, 1
        #     mapping, head, tail = self.mapping, self.head, self.tail
        #     hash_key = self.make_key([func, list(args), kwargs])
        #     link = mapping.get(hash_key, head)
        #     if link is head:
        #         value = func(*args, **kwargs)
        #         with context:
        #             if len(mapping) >= self.maxsize:
        #                 old_prev, old_next, old_key, old_value = head[NEXT]
        #                 head[NEXT] = old_next
        #                 old_next[PREV] = head
        #                 del mapping[old_key]
        #             last = tail[PREV]
        #             link = [last, tail, hash_key, value]
        #             mapping[hash_key] = last[NEXT] = tail[PREV] = link
        #     else:
        #         with context:
        #             link_prev, link_next, hash_key, value = link
        #             link_prev[NEXT] = link_next
        #             link_next[PREV] = link_prev
        #             last = tail[PREV]
        #             last[NEXT] = tail[PREV] = link
        #             link[PREV] = last
        #             link[NEXT] = tail
        #     return value
        #
        return _cache_func

lru_cache = LRUCache(maxsize=1000).cache