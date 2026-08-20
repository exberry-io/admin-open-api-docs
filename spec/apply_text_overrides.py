#!/usr/bin/env python3
"""Apply spec/text-overrides.yaml onto docs/openapi.json.

The overlay is THE authoritative source for prose:
- info description, every tag description, every operation summary/description
- coverage is enforced: a tag or operationId missing from the overlay FAILS (exit 1)
- unknown overlay keys (typos, removed endpoints) are warnings
- idempotent; property descriptions stay in the schema (schema_descriptions = targeted fixes)

Usage:  python3 spec/apply_text_overrides.py  Requires: PyYAML
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.normpath(os.path.join(BASE, '..', 'docs', 'openapi.json'))
OVERLAY_PATH = os.path.join(BASE, 'text-overrides.yaml')

try:
    import yaml
except ImportError:
    venv_python = os.path.join(BASE, '..', '.venv', 'bin', 'python')
    if venv_python and os.path.isfile(venv_python) and os.access(venv_python, os.X_OK):
        os.execv(venv_python, [venv_python, *sys.argv])
    sys.exit("PyYAML is required:  python3 -m pip install pyyaml")

def clean(text):
    if not isinstance(text, str):
        return text
    return '\n'.join(line.rstrip() for line in text.split('\n')).rstrip('\n')


def main():
    with open(SPEC_PATH, encoding='utf-8') as f:
        spec = json.load(f)
    with open(OVERLAY_PATH, encoding='utf-8') as f:
        overlay = yaml.safe_load(f) or {}

    changed, warnings, missing = 0, [], []

    # --- info ---
    for key, text in (overlay.get('info') or {}).items():
        if spec['info'].get(key) != clean(text):
            spec['info'][key] = clean(text)
            changed += 1

    # --- tags (full coverage required) ---
    ov_tags = overlay.get('tags') or {}
    tag_by_name = {t['name']: t for t in spec.get('tags', [])}
    for name in tag_by_name:
        if name not in ov_tags:
            missing.append(f"tag: {name}")
    for name, text in ov_tags.items():
        t = tag_by_name.get(name)
        if t is None:
            warnings.append(f"overlay tag not in spec: {name}")
            continue
        if t.get('description') != clean(text):
            t['description'] = clean(text)
            changed += 1

    # --- operations (full coverage required) ---
    ov_ops = overlay.get('operations') or {}
    ops = {}
    for methods in spec.get('paths', {}).values():
        for op in methods.values():
            if isinstance(op, dict) and 'operationId' in op:
                ops[op['operationId']] = op
    for opid in ops:
        if opid not in ov_ops:
            missing.append(f"operation: {opid}")
    for opid, fields in ov_ops.items():
        op = ops.get(opid)
        if op is None:
            warnings.append(f"overlay operationId not in spec: {opid}")
            continue
        for key, text in (fields or {}).items():
            if op.get(key) != clean(text):
                op[key] = clean(text)
                changed += 1

    # --- targeted schema field descriptions ---
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

    if missing:
        print("\nERROR: text-overrides.yaml is missing entries for:")
        for m in missing:
            print(f"  - {m}")
        print("Add them (the overlay is the authoritative source for all prose).")
        sys.exit(1)


if __name__ == '__main__':
    main()
