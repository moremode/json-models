import json

def p_generate_model(objs: dict, name: str="Model"):
    models = 0
    result_model = f"class {name}(JsonModel):\n"
    for key, val in objs.items():
        class_name = ""
        if (type(val) == dict):
            class_name = key[0].upper() + key[1:] + "Model"
            internal_model = p_generate_model(val, class_name)
            result_model = internal_model + result_model
        else:
            class_name = str(type(val)).split("'")[1]
        result_model += f"\t{key}: {class_name} = {class_name}\n"
    result_model += "\n"
    return result_model


def generate_model(json_str: str, name: str="Model"):
    objs: dict = json.loads(json_str)
    return p_generate_model(objs, name)
    