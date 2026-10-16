#!/usr/bin/env python3
"""Compare required CloudKit fields with an exported schema; never contact iCloud."""
import argparse
from pathlib import Path
import re


def record_fields(path):
    schema = path.read_text(encoding='utf-8')
    records = {}
    for record in re.finditer(r'RECORD\s+TYPE\s+(\w+)\s*\((.*?)\);', schema, re.S):
        name, body = record.groups()
        if name in records:
            raise ValueError(f'{path}: duplicate record type {name}')
        fields = {}
        for line in body.splitlines():
            line = line.strip().rstrip(',')
            if not line or line.startswith('GRANT '):
                continue
            field = re.fullmatch(r'"?(\w+)"?\s+((?:ENCRYPTED\s+)?(?:LIST<\w+>|\w+))(?:\s+(?:QUERYABLE|SEARCHABLE|SORTABLE))*', line)
            if not field:
                raise ValueError(f'{path}: unsupported field declaration in {name}: {line}')
            field_name, field_type = field.groups()
            if not field_name.startswith('___'):
                if field_name in fields:
                    raise ValueError(f'{path}: duplicate field {name}.{field_name}')
                fields[field_name] = ' '.join(field_type.split())
        records[name] = fields
    if not records:
        raise ValueError(f'{path}: no RECORD TYPE definitions; obtain a .ckdb export')
    return records


def compare(expected, actual):
    errors = []
    for record_name, fields in expected.items():
        if record_name not in actual:
            errors.append(f'{record_name}: missing record type')
            continue
        for name, field_type in fields.items():
            found = actual[record_name].get(name)
            if found != field_type:
                errors.append(f'{record_name}.{name}: expected {field_type}, found {found or "missing"}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected', required=True, type=Path)
    parser.add_argument('--actual', required=True, type=Path)
    arguments = parser.parse_args()
    try:
        errors = compare(record_fields(arguments.expected), record_fields(arguments.actual))
    except (OSError, ValueError) as error:
        parser.exit(1, f'FAIL: {error}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print('PASS: required record types, fields and types match; indexes and grants not checked')


if __name__ == '__main__':
    main()
