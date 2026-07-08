#!/usr/bin/env python3
"""
Example Use Case Loader

Loads the shared use-case configuration from example_use_cases.json at the
repository root. Used by both generate_userguide_examples.py (to pick which
columns of the Examples sheet to render) and generate_example_videos.py (to
pick the source media file to embed metadata into).
"""

import json
import os
from typing import Dict, List, Optional


REQUIRED_FIELDS = (
    'name', 'display_name', 'range', 'example_column', 'notes_column',
    'source_file', 'thumbnail',
)


def get_config_path() -> str:
    """Path to example_use_cases.json at the repository root."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(repo_root, 'example_use_cases.json')


def load_config() -> Dict:
    """Load and validate the whole example_use_cases.json file."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Use-case configuration file not found: {config_path}\n"
            f"Please create example_use_cases.json in the repository root."
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if 'use_cases' not in config or not isinstance(config['use_cases'], list):
        raise ValueError("example_use_cases.json must contain a 'use_cases' list")
    if 'examples_base_url' not in config:
        raise ValueError("example_use_cases.json must contain 'examples_base_url'")

    for i, uc in enumerate(config['use_cases']):
        missing = [f for f in REQUIRED_FIELDS if f not in uc]
        if missing:
            raise ValueError(
                f"Use case at index {i} ({uc.get('name', '?')}) is missing "
                f"required fields: {', '.join(missing)}"
            )
    return config


def load_use_cases() -> List[Dict]:
    """Load and validate the list of example use cases."""
    return load_config()['use_cases']


def get_examples_base_url() -> str:
    """Base URL where published example files live (must end with '/')."""
    url = load_config()['examples_base_url']
    return url if url.endswith('/') else url + '/'


def get_use_case(name: str) -> Optional[Dict]:
    """Look up a single use case by name, or return None if not found."""
    for uc in load_use_cases():
        if uc['name'] == name:
            return uc
    return None


def list_use_case_names() -> List[str]:
    return [uc['name'] for uc in load_use_cases()]


if __name__ == '__main__':
    config = load_config()
    cases = config['use_cases']
    print(f"Loaded {len(cases)} use cases from {get_config_path()}")
    print(f"  examples_base_url: {config['examples_base_url']}")
    for uc in cases:
        print(f"  - {uc['name']:35s}  source: {uc['source_file']:20s}  "
              f"thumb: {uc['thumbnail']}")
