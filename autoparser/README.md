# autoparser


i am sick and tired of doing something like:

```
_foo = api_result.get("FOO")
if _foo is None:
    _foo = api_result.get("foo")
_bars = api_result.get("bar_list")
_baz = api_result.get("baz")
_baz = "baz_default" if _baz is None else baz

try:
    _bar = float(_bars[0].get('bar_name'))
except (IndexError, TypeError) as e:
    logger.exception(e)
    return None

if _foo and _bar:
    return Foo(_foo, _bar, source="api", baz=_baz)

```

now I can do:
```
template = {
    "foo": ("FOO|foo", str, True),
    "bar": ("bar_list/0/bar_name", float, True),
    "baz": ("baz", str, False, "baz_default"),
    "source": "api",
}
foo, err = autoparse(Foo, api_result, template)
if err:
    logger.info(err)
    return None
return foo
```

much better I think!
