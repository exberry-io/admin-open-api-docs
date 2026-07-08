#!/usr/bin/env python3
"""Apply spec/text-overrides.yaml onto docs/openapi.json.

- Idempotent: running it any number of times yields the same result.
- Texts only: info/tags/operations(summary+description)/schema field descriptions.
- Warns (does not fail) on overlay paths that don't exist in the spec.

Usage:  python3 spec/apply_text_overrides.py
Requires: PyYAML  (py -m pip install pyyaml   |   pip install pyyaml)
"""
import json, os, sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  py -m pip install pyyaml")

BASE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.normpath(os.path.join(BASE, '..', 'docs', 'openapi.json'))
OVERLAY_PATH = os.path.join(BASE, 'text-overrides.yaml')


def clean(text):
    """Normalize overlay strings: strip one trailing newline block scalars add."""
    return text.rstrip('\n') if isinstance(text, str) else text


def main():
    with open(SPEC_PATH, encoding='utf-8') as f:
        spec = json.load(f)
    with open(OVERLAY_PATH, encoding='utf-8') as f:
        overlay = yaml.safe_load(f) or {}

    changed, warnings = 0, []

    # --- info ---
    for key, text in (overlay.get('info') or {}).items():
        if spec['info'].get(key) != clean(text):
            spec['info'][key] = clean(text)
            changed += 1

    # --- tags ---
    tag_by_name = {t['name']: t for t in spec.get('tags', [])}
    for name, text in (overlay.get('tags') or {}).items():
        t = tag_by_name.get(name)
        if t is None:
            warnings.append(f"tag not found: {name}")
            continue
        if t.get('description') != clean(text):
            t['description'] = clean(text)
            changed += 1

    # --- operations (by operationId) ---
    ops = {}
    for methods in spec.get('paths', {}).values():
        for op in methods.values():
            if isinstance(op, dict) and 'operationId' in op:
                ops[op['operationId']] = op
    for opid, fields in (overlay.get('operations') or {}).items():
        op = ops.get(opid)
        if op is None:
            warnings.append(f"operationId not found: {opid}")
            continue
        for key, text in (fields or {}).items():
            if op.get(key) != clean(text):
                op[key] = clean(text)
                changed += 1

    # --- schema field descriptions (dotted path under components/schemas) ---
    for dotted, text in (overlay.get('schema_descriptions') or {}).items():
        node = spec.get('components', {}).get('schemas', {})
        ok = True
        for part in dotted.split('.'):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                warnings.append(f"schema path not found: {dotted}")
                ok = False
                break
        if ok and isinstance(node, dict) and node.get('description') != clean(text):
            node['description'] = clean(text)
            changed += 1

    for w in warnings:
        print(f"WARNING: {w}")

    if changed:
        with open(SPEC_PATH, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        print(f"applied {changed} text change(s) -> {SPEC_PATH}")
    else:
        print("overlay already applied - no changes")


if __name__ == '__main__':
    main()
