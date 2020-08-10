from typing import List, Union, Any


async def async_iterable(elts: List[Union[Any, Exception]]):
  for elt in elts:
    if isinstance(elt, Exception):
      raise elt
    yield elt
