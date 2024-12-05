import base64
import json
from hashlib import sha256
from typing import Any, Dict, Union, Callable, List, Tuple
from dataclasses import dataclass
import struct

import settings.idl_paths



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


def convert_bytes_to_type(data_type, **kwargs):
    if data_type == 'enum':
        variants = kwargs.get("variants")
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
        'publicKey': lambda b: base64.b64encode(b),
        'enum': lambda b: variants[int.from_bytes(b, 'little')]  # TODO get variants as input
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
class FieldLayout:
    name: str
    conversion_function: Callable
    length: int

    def __str__(self):
        return f"Layout: {self.name} \n   Conversion function: {self.conversion_function} \n   Bytes: {self.length}"

    def decode(self, msg: bytes) -> Tuple[Dict[str, Union[int, str]], bytes]:
        """ Decode message based on field layout. """
        sequence = msg[: self.length]
        decoded_msg = self.conversion_function(sequence)

        return {self.name: decoded_msg}, msg[self.length:]


@dataclass
class EventLayout:
    name: str
    fields: List[FieldLayout]

    def decode(self, msg: bytes) -> Tuple[Dict[str, Union[int, str]], bytes]:
        """ Decode message based on event layout. """
        decoded_message = dict()
        for field in self.fields:
            decoded_field, msg = field.decode(msg)
            decoded_message.update(decoded_field)
        return decoded_message, msg


class EventDecoder:
    def __init__(self, idl: Dict):
        self.layouts: Dict[str, EventLayout] = dict()
        self.discriminators = dict()

        if 'events' in idl:
            for event in idl['events']:
                event_layout = IdlCoder.get_event_layout(event, types=idl.get('types'))
                self.layouts[event['name']] = event_layout

                discriminator = base64.b64encode(self.event_discriminator(event['name']))
                self.discriminators[discriminator] = event['name']

    def decode(self, message: str) -> Union[Dict[str, Any], None]:
        """
        Decodes a Solana transaction log into a dictionary containing the decoded data and the event name.

        The method attempts to decode a base64 encoded string. It first extracts a discriminator from the
        initial part of the message, uses it to identify the event name, and then decodes the rest of the message
        according to a specific layout associated with that event.

        Parameters:
        - message (str): A base64 encoded string representing the message to be decoded.

        Returns:
        - dict: A dictionary with two keys: 'data' containing the decoded data, and 'name' containing the event name.

        Raises:
        - Exception: If the event name extracted from the message is unknown.
        - AssertionError: If the message is not fully consumed during decoding.
        """
        try:
            log_arr = base64.b64decode(message)
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
        data, msg = layout.decode(log_arr[8:])
        assert len(msg) == 0, f'Message was not fully consumed. Residual message: {msg}'
        return {"data": data, "name": event_name}

    @staticmethod
    def event_discriminator(name: str) -> bytes:
        return sha256(f"event:{name}".encode()).digest()[:8]


class IdlCoder:
    @staticmethod
    def field_layout(field, types=None) -> FieldLayout:
        field_name = camelcase(field.get('name')) if field.get('name') else None
        field_type = field.get('type')

        if isinstance(field_type, str):
            # basic type events
            if field_type in bytes_map:
                conversion_func = convert_bytes_to_type(field_type)
                bytes_size = bytes_map.get(field_type)
                return FieldLayout(name=field_name, conversion_function=conversion_func, length=bytes_size)

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
    def type_def_layout(type_def, types=None, name=None) -> FieldLayout | EventLayout:
        kind = type_def['type']['kind']

        if kind == "struct":
            # Handling a struct type
            field_layouts = [IdlCoder.field_layout(f, types) for f in type_def['type']['fields']]
            return EventLayout(name=name, fields=field_layouts)

        elif kind == "enum":
            # Handling an enum type
            conversion_func = convert_bytes_to_type('enum', variants = [v.get('name') for v in type_def['type']['variants']])
            bytes_size = bytes_map.get('enum')
            return FieldLayout(name=name, conversion_function=conversion_func, length=bytes_size)

        elif kind == "alias":
            # Handling an alias type
            return IdlCoder.field_layout({'type': type_def['type']['value'], 'name': type_def['name']}, types)

        else:
            raise NotImplementedError(f"Not yet implemented for kind: {kind}")

    @staticmethod
    def get_event_layout(type_def, types=None) -> EventLayout:
        """ Creates event layout from event Idl. """
        event_layout = EventLayout(
            name=type_def.get('name'),
            fields=[IdlCoder.field_layout(f, types) for f in type_def['fields']]
        )
        return event_layout


if __name__ == '__main__':
    # TODO: This is here for testing purposes.
    # program_data = 'dZKDSrOa27JbF8fIam5zn68XUYGDY+lPkIvzcATObT+88Ze90vUfHAMAciRhcXkQURwAAAAAAAAAAHIkYXF5EFEcAAAAAAAAAADE4tumMfvqCQAAAAAAAAAAZz5zDgAAAAC84t9SD3gBAAAAAAAAAAAAAABnb4YDieoJAAAAAAAAAAC4YN6RBROBUwdaAAAAAAAASPdg8Okq6H/PggAAAAAAAORtEAAAAAAAq7UNyTEAAAAAAAAAAAAAAA=='
    # program_data = 'DIvOZyn+1zhbF8fIam5zn68XUYGDY+lPkIvzcATObT+88Ze90vUfHAAAdGRnKPNFl6IPAAAAAAAAAGf6Z/VJKnIWEAAAAAAAAACq06/DT5cAAAAAAAAAAAAADCqyNA8AAQAAAAAAAAAAAAwqsjQPAAEAAAAAAAAAAAB+neSNMfr0XFQaBQAAAAAAAAAUrkcBAAAAAAAAAAAAABi/duIO5Q5RSBzvAQAAAACehrsYNFb9rv5xWwMAAAAAdTFbKOorAAAAAAAAAAAAAARf+GVMGQAAAAAAAAAAAAA='
    program_data = 'dZKDSrOa27JbF8fIam5zn68XUYGDY+lPkIvzcATObT+88Ze90vUfHAMASX+Bzs0DEB4AAAAAAAAAAEl/gc7NAxAeAAAAAAAAAADAsho3P9OnCAAAAAAAAAAA1jKFDgAAAACYOgKf4XoCAAAAAAAAAAAAAACzGjc/06cIAAAAAAAAAACsDOf8mtHrnR9RAAAAAAAAVAvgV6H6V2NhkQAAAAAAAATZEgAAAAAAt8MCGUIAAAAAAAAAAAAAAA=='
    with open(settings.idl_paths.MANGO_IDL_PATH) as fp:
        event_decoder = EventDecoder(json.load(fp))

    result = event_decoder.decode(program_data)

    print(result)
