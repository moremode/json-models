from enum import Enum
import json
import typing
from typing import Type

class JsonModel:
    pass

def get_class_props(cls):   
    return [i for i in cls.__dict__.keys() if i[:1] != '_']

def parse_list(objs: list, attr_type: type):
    output_list = []
    for obj in objs:
        if (type(obj) == dict and issubclass(attr_type, JsonModel)):
            obj = parse_dict(obj, attr_type)
        elif (issubclass(attr_type, Enum)):
            if (type(obj) == str):
                obj = attr_type[obj]
        elif (type(obj) != attr_type):
            raise TypeError(f"{obj} is not {attr_type} format")
        output_list.append(obj)
    return output_list

def parse_dict(obj: dict, model: Type[JsonModel]):
    props = get_class_props(model)
    obj_model = model()
    for key, val in obj.items():
        if (key in props):
            attr_type = getattr(model, key)
            origin = typing.get_origin(attr_type)
            if (type(attr_type) == type):
                if (type(val) == dict and issubclass(attr_type, JsonModel)):
                    val = parse_dict(val, attr_type)
                elif (type(val) != attr_type):
                    raise TypeError(f"{key} is not {attr_type} format")
                setattr(obj_model, key, val)
            elif (origin == list):
                list_args = typing.get_args(attr_type)
                if (len(list(list_args)) == 1):
                    val = parse_list(val, list_args[0])
                elif (type(val) != attr_type):
                    raise TypeError(f"{key} is not {attr_type} format")
                setattr(obj_model, key, val)
            elif (origin == typing.Union):
                valid = 0
                union_attrs = typing.get_args(attr_type)
                for union_type in union_attrs:
                    union_origin = typing.get_origin(union_type)
                    if (type(union_type) == type):
                        if (type(val) == dict and issubclass(union_type, JsonModel)):
                            val = parse_dict(val, union_type)
                            setattr(obj_model, key, val)
                            valid = 1
                            break
                        elif (type(val) == union_type):
                            setattr(obj_model, key, val)
                            valid = 1
                            break
                    elif (union_origin == list):
                        list_args = typing.get_args(union_type)
                        if (len(list(list_args)) == 1):
                            val = parse_list(val, list_args[0])
                            setattr(obj_model, key, val)
                            valid = 1
                            break
                        elif (type(val) != union_type):
                            setattr(obj_model, key, val)
                            valid = 1
                            break
                    elif (issubclass(union_type, Enum)):
                        if (type(val) == str):
                            val = union_type[val]
                            setattr(obj_model, key, val)
                            valid = 1
                            break
                if (not valid):
                    raise TypeError(f"{key} is not {attr_type} format")
            elif (issubclass(attr_type, Enum)):
                if (type(val) == str):
                    val = attr_type[val]
                    setattr(obj_model, key, val)
            else:
                raise TypeError(f"{key} invalid {attr_type} type")
            props.remove(key)
        else:
            raise TypeError(f"Unexpected value {key}")
    for prop in props:
        setattr(obj_model, prop, None)
    return obj_model

def parse_model(obj: str, model: Type[JsonModel]):
    json_dump = json.loads(obj)
    return parse_dict(json_dump, model)
