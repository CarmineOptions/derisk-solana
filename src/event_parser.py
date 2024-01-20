import base64
from hashlib import sha256
from typing import Any, Dict, Union, Callable
from dataclasses import dataclass
import struct

bytes_map = {
    'bool': 1,
    'u8': 1,
    'i8': 1,
    'u16': 2,
    'i16': 2,
    'u32': 4,
    'i32': 4,
    'f32': 4,
    'u64': 8,
    'i64': 8,
    'f64': 8,
    'u128': 16,
    'i128': 16,
    'u256': 32,
    'i256': 32,
    'bytes': None,
    'string': None,
    'publicKey': 32,
    'enum': 1
}

def convert_bytes_to_type(data_type):
    conversion_functions = {
        'bool': lambda b: bool(int.from_bytes(b, 'little')),
        'u8': lambda b: b[0],
        'i8': lambda b: int.from_bytes(b, 'little', signed=True),
        'u16': lambda b: int.from_bytes(b, 'little'),
        'i16': lambda b: int.from_bytes(b, 'little', signed=True),
        'u32': lambda b: int.from_bytes(b, 'little'),
        'i32': lambda b: int.from_bytes(b, 'little', signed=True),
        'f32': lambda b: struct.unpack('<f', b)[0],
        'u64': lambda b: int.from_bytes(b, 'little'),
        'i64': lambda b: int.from_bytes(b, 'little', signed=True),
        'f64': lambda b: struct.unpack('<d', b)[0],
        'u128': lambda b: int.from_bytes(b, 'little'),
        'i128': lambda b: int.from_bytes(b, 'little', signed=True),
        'u256': lambda b: int.from_bytes(b, 'little'),
        'i256': lambda b: int.from_bytes(b, 'little', signed=True),
        'bytes': lambda b: b,
        'string': lambda b: b.decode('utf-8'),
        'publicKey': lambda b: b,
        'enum': lambda b: int.from_bytes(b, 'little')  # TODO get variants as input
    }
    return conversion_functions[data_type]


def camelcase(s):
    """
    Convert a string into camelCase.
    """
    parts = s.split()
    # Lowercase the first word and capitalize subsequent words
    return ''.join([parts[0].lower()] + [word.capitalize() for word in parts[1:]])


@dataclass
class Layout:
    name: str
    conversion_function: Callable
    length: int

    def __str__(self):
        return f"Layout: {self.name} \n   Conversion function: {self.conversion_function} \n   Bytes: {self.length}"

    def decode(self):
        raise NotImplementedError


class EventDecoder:
    def __init__(self, idl: Dict):
        self.layouts: Dict[str, Layout] = dict()
        self.discriminators = dict()

        if 'events' in idl:
            for event in idl['events']:
                event_layout = IdlCoder.get_event_layout(event, types=idl.get('types'))
                self.layouts[event['name']] = event_layout

                discriminator = base64.b64encode(self.event_discriminator(event['name']))
                self.discriminators[discriminator] = event['name']

    def decode(self, log: str) -> Union[Dict[str, Any], None]:
        try:
            log_arr = base64.b64decode(log)
        except Exception as e:
            return None

        disc = base64.b64encode(log_arr[:8])
        event_name = self.discriminators.get(disc)

        if event_name is None:
            return None

        if event_name not in self.layouts:
            raise Exception(f"Unknown event: {event_name}")

        layout = self.layouts[event_name]
        # Assuming layout.decode decodes the event data
        data = layout.decode(log_arr[8:])
        return {"data": data, "name": event_name}

    @staticmethod
    def event_discriminator(name: str) -> bytes:
        return sha256(f"event:{name}".encode()).digest()[:8]


class IdlCoder:
    @staticmethod
    def field_layout(field, types=None):
        field_name = camelcase(field.get('name')) if field.get('name') else None
        field_type = field.get('type')

        if isinstance(field_type, str):
            # basic type events
            if field_type in bytes_map:
                conversion_func = convert_bytes_to_type(field_type)
                bytes_size = bytes_map.get(field_type)
                return Layout(name=field_name, conversion_function=conversion_func, length=bytes_size)


        # Handling complex types
        elif isinstance(field_type, dict):
            if 'vec' in field_type:
                # Handling a vector (array) of items
                return IdlCoder.field_layout({'name': None, 'type': field_type['vec']}, types)
            elif 'option' in field_type:
                # Handling an optional (nullable) type
                return IdlCoder.field_layout({'name': None, 'type': field_type['option']}, types)
            elif 'array' in field_type:
                # Handling a fixed-size array
                element_type = field_type['array'][0]
                array_length = field_type['array'][1]
                return IdlCoder.field_layout({'name': None, 'type': element_type}, types)

            elif 'defined' in field_type:
                # Handling a user-defined type
                if not types:
                    raise NotImplementedError("User defined types not provided")

                defined_type = field_type['defined']
                matching_types = [t for t in types if t['name'] == defined_type]
                if not matching_types:
                    raise ValueError(f"Type not found: {defined_type}")

                return IdlCoder.type_def_layout(matching_types[0], types, field_name)

            else:
                raise NotImplementedError(f"Not yet implemented for complex type: {field_type}")

        else:
            raise NotImplementedError(f"Not yet implemented: {field_type}")

    @staticmethod
    def type_def_layout(type_def, types=None, name=None):
        kind = type_def['type']['kind']

        if kind == "struct":
            # Handling a struct type
            field_layouts = [IdlCoder.field_layout(f, types) for f in type_def['type']['fields']]
            return field_layouts

        elif kind == "enum":
            # Handling an enum type
            variants = []
            for variant in type_def['type']['variants']:
                variant_name = camelcase(variant['name'])
                if not variant.get('fields'):
                    variants.append(([], variant_name))
                else:
                    field_layouts = []
                    for f in variant['fields']:
                        if isinstance(f, dict) and 'name' in f:
                            field_layouts.append(IdlCoder.field_layout(f, types))
                        else:
                            # Handling unnamed fields in enum variants
                            field_layouts.append(IdlCoder.field_layout({'type': f, 'name': str(i)}, types))
                    variants.append((field_layouts, variant_name))
            conversion_func = convert_bytes_to_type('enum')
            bytes_size = bytes_map.get('enum')
            return Layout(name=name, conversion_function=conversion_func, length=bytes_size)

        elif kind == "alias":
            # Handling an alias type
            return IdlCoder.field_layout({'type': type_def['type']['value'], 'name': type_def['name']}, types)

        else:
            raise NotImplementedError(f"Not yet implemented for kind: {kind}")

    @staticmethod
    def get_event_layout(type_def, types=None):
        kind = type_def.get('kind', 'struct')

        if kind == "struct":
            # Handling a struct type
            field_layouts = [IdlCoder.field_layout(f, types) for f in type_def['fields']]
            return field_layouts
        else:
            raise NotImplementedError(f"Not yet implemented for kind: {kind}")
