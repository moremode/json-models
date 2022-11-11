from enum import Enum
import enum
import json
import typing
from typing import Type, Any
import sys

if (sys.version_info[0] < 3):
    exit(0)

def get_origin(attr_type):
    if (sys.version_info[1] > 7):
        return typing.get_origin(attr_type)
    else:
        try:
            return attr_type.__origin__
        except:
            return None

def get_args(attr_type):
    if (sys.version_info[1] > 7):
        return typing.get_args(attr_type)
    else:
        try:
            return attr_type.__args__
        except:
            return None

class JsonModel:
    pass

def is_any(obj, attr_type):
    if (attr_type == Any):
        return (0, obj)
    return (1, None)

def is_model(obj, attr_type):
    if (type(attr_type) != type):
        return (1, None)
    if (type(obj) == dict and issubclass(attr_type, JsonModel)):
        obj = parse_dict(obj, attr_type)
        return (0, obj)
    return (1, None)

def is_default(obj, attr_type):
    if (type(attr_type) == type):
        if (type(obj) != attr_type):
            return (2, None)
        return (0, obj)
    return (1, obj)

def is_enum(obj, attr_type):
    if (type(attr_type) != enum.EnumMeta):
        return (1, None)
    if (issubclass(attr_type, Enum)):
        if (type(obj) == str):
            obj = attr_type[obj]
            return (0, obj)
        return (2, None)
    return (1, None)

def parse_list(objs: list, attr_type: type):
    output_list = []
    for obj in objs:
        res = full_parser(obj, attr_type)
        if (res[0] != 0):
            raise TypeError(f"{obj} is not {attr_type} format")
        output_list.append(res[1])
    return output_list

def is_list(obj, attr_type):
    origin = get_origin(attr_type)
    if (not origin is list):
        return (1, None)
    list_args = get_args(attr_type)
    if (len(list(list_args)) != 1):
        if (type(obj) != list):
            return (2, None)
        return (0, obj)
    try:
        obj = parse_list(obj, list_args[0])
        return (0, obj)
    except:
        return (2, None)

def is_union(obj, attr_type):
    origin = get_origin(attr_type)
    if (origin != typing.Union):
        return (1, None)
    union_attrs = get_args(attr_type)
    for union_type in union_attrs:
        res = full_parser(obj, union_type)
        if (res[0] == 0):
            return res
    return (2, None)

parsers = [is_any, is_model, is_enum, is_default, is_list, is_union]

def full_parser(obj, attr_type):
    for parser in parsers:
        parse_result = parser(obj, attr_type)
        if (parse_result[0] != 1):
            return parse_result
    return (1, None)

def get_class_props(cls):   
    return [i[0] for i in cls.__dict__.items() if i[0][:1] != '_' and type(i[1]) != function]

def get_obj_props(obj):
    return dict([(i[0], i[1]) for i in obj.__dict__.items() if i[0][:1] != '_' and not callable(i[1])])

def parse_dict(obj: dict, model: Type[JsonModel]):
    props = get_class_props(model)
    obj_model = model()
    for key, val in obj.items():
        if (key in props):
            attr_type = getattr(model, key)
            res = full_parser(val, attr_type)
            if (res[0] == 0):
                setattr(obj_model, key, res[1])
            elif (res[0] == 1):
                raise TypeError(f"{key} ::: {val} is unknown type")
            else:
                raise TypeError(f"{key} ::: {val} is not {attr_type} format")
            props.remove(key)
        else:
            raise TypeError(f"Unexpected value {key} ::: {val}")
    for prop in props:
        setattr(obj_model, prop, None)
    return obj_model

def parse_model(obj: str, model: Type[JsonModel]):
    json_dump = json.loads(obj)
    return parse_dict(json_dump, model)

def dump_model(obj):
    return json.dumps(obj, default=lambda o: get_obj_props(obj), sort_keys=True, indent=4)