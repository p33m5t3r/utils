
from typing import Any, Union
from dataclasses import dataclass, _MISSING_TYPE


def autoparse(t: Union[type, object], data: dict, template: dict[str, tuple],       
              ignore_existing=False, strict=False) -> (Any, dict):
    """
    @param t: dataclass class or dataclass instance
    @param data: input data
    @param template: rules for parsing
        { field_name: (<query>, <type>, <required>, <optional: default>) OR string_literal }
    @param ignore_existing: if True, will not overwrite existing fields on an instance t
    @param strict: if True, requires 1:1 mapping

    @return: (parsed_object, error) where error := None | (Exception, instigating template key, data key)
    """

    def _fmt_err(k, v, err) -> (Any, dict):
        return (None if isinstance(t, type) else t, (err, {k, v}))

    def _get(d, k):
        try:
            k = int(k)
        except ValueError:
            pass
        if isinstance(k, int) or "|" not in k:
            try:
                return d[k]
            except TypeError as e:
                return e
            
        subqs = k.split('|')
        match = next(filter(lambda _k: _k in subqs, d.keys()), None)
        if match is None:
            return KeyError("no matching keys found")
        return d[match]

    def _query(d, qs):
        if len(qs) == 1:
            try:
                return _get(d, qs[0]) 
            except (KeyError, IndexError) as _err:
                return _err
        return _query(_get(d, qs[0]), qs[1:])

    if not "__dataclass_fields__" in dir(t):
        raise TypeError

    if ignore_existing and isinstance(t, type):
        raise ValueError("ignore_existing cannot be True if t is a type!")

    _fields = t.__dataclass_fields__.values()
    field_names = [f.name for f in _fields]
    required_fields = [f.name for f in filter(lambda _f: isinstance(_f.default, _MISSING_TYPE), _fields)]
    if isinstance(t, type) or strict:
        if not set(required_fields).issubset(set(template.keys())):
            _name = t.__name__ if isinstance(t, type) else t.__class__.__name__
            raise KeyError(f"template doesn't have all required_fields for {_name}!")

    if strict and not set(template.keys()).issubset(set(required_fields)):
        _name = t.__name__ if isinstance(t, type) else t.__class__.__name__
        raise KeyError(f"templateError: template has extra fields for {_name}!")

    t_builder = {}
    for k, v in template.items():
        if isinstance(v, str):
            t_builder.update({k: v})
            continue

        if (ignore_existing and hasattr(t, k)) or k not in field_names:
            continue

        _qs, _converter, _required = v[0].split('/'), v[1], v[2]
        _has_default = len(v) == 4
        _default = v[3] if _has_default else None
        result = _query(data, _qs)

        if isinstance(result, Exception) and not _has_default:
            if _required:
                return _fmt_err(k, v, result)
            continue
        
        if isinstance(result, Exception):
            t_builder[k] = _default
            continue

        try:                                
            t_builder[k] = _converter(result)
        except ValueError as err:           
            return _fmt_err(k, v, err)

    if isinstance(t, type):
        return t(**t_builder), None
    
    for k, v in t_builder.items():
        t.__setattr__(k, v)
    return t, None




# ==== usage example =====
# template format:
"""
template = {
    field_name: (<query>, <type>, <required>, <optional: default>) OR string_literal
}
where <query> := (whatever your field is keyed under in the input dict)
                 "key|key2"             => matches first of key1 or key2 in input dict
                 "key1/key2/.../key_n"  => looks for input_dict[key1][key2]...[key_n]
                                            (can also be an index of a list!) 

      <type> := callable(whatever_the_query_returns)
                lambda _: _             => returns literally whatever_the_query_returns
                lambda _: 1             => fuck it, just return 1

      string_literal => unconditionally put this value on the field_name for every input

"""
template = {
    "foo": ("annoyingFooName", str, True),
    "bar": ("bars|BARS/-1/name", lambda _: _, True),
    "baz": ("maybeBaz", float, False, "baz_default"),
    "buz": ("buz|BUZ", lambda s: int(float(s)), False, "baz_default"),
    "source": "tiltApi",
}

@dataclass
class Foo:
    source: str
    foo: str
    bar: Any
    baz: int = None
    buz: int = None

data = {"annoyingFooName": "foo!",
        "bars": [{"name": "wrong bar!"}, {"name": "right bar!"}],
        "BUZ": "420.314159"}
more_data = {"annoyingFooName": "new name!"}

foo, err = autoparse(Foo, data, template)
# foo = Foo(source='tiltApi', foo='foo!', bar='right bar!', baz='baz_default', buz=420)
print(foo)
_, err = autoparse(foo, more_data, {"foo": template["foo"]})
print(foo)
# _, err = autoparse(foo, more_data, {"some_random_field": template["foo"]}) -> won't err, won't do anything
# _, err = autoparse(foo, more_data, {"some_random_field": template["foo"]}, strict=True) -> will error

# output:
# [1] Foo(source='tiltApi', foo='foo!', bar='right bar!', baz='baz_default', buz=420)
# [2] Foo(source='tiltApi', foo='new name!', bar='right bar!', baz='baz_default', buz=420)

