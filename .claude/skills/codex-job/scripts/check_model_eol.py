#!/usr/bin/env python3
"""
Check for models approaching end-of-life and suggest alternatives.

Usage:
    check_model_eol.py [--days DAYS] [--models-file PATH]

Options:
    --days DAYS          Warn about models expiring within N days (default: 90)
    --models-file PATH   Path to available_models.jsonl (default: ../references/available_models.jsonl)
    --format FORMAT      Output format: text (default), json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check for models approaching EOL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Warn about models expiring within N days (default: 90)"
    )
    parser.add_argument(
        "--models-file",
        type=str,
        help="Path to available_models.jsonl"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    return parser.parse_args()


def resolve_models_file(custom_path: Optional[str]) -> Path:
    """Resolve the models file path."""
    if custom_path:
        return Path(custom_path)

    # Try relative to this script
    script_dir = Path(__file__).parent.resolve()
    models_file = script_dir / "../references/available_models.jsonl"
    if models_file.exists():
        return models_file

    # Fallback to working directory
    models_file = Path("codex-job/references/available_models.jsonl")
    if models_file.exists():
        return models_file

    raise FileNotFoundError(
        "Cannot find available_models.jsonl. "
        "Specify path with --models-file or run from repository root."
    )


def load_models(models_file: Path) -> List[Dict]:
    """Load models from JSONL file."""
    models = []
    with open(models_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                model = json.loads(line)
                models.append(model)
            except json.JSONDecodeError as e:
                print(
                    f"Warning: Skipping invalid JSON on line {line_num}: {e}",
                    file=sys.stderr
                )
    return models


def check_eol(models: List[Dict], warning_days: int) -> List[Dict]:
    """Find models approaching or past EOL."""
    today = datetime.now().date()
    warning_threshold = today + timedelta(days=warning_days)

    warnings = []
    for model in models:
        eol_str = model.get('eol_date')
        if not eol_str:
            continue  # No EOL set

        try:
            eol_date = datetime.fromisoformat(eol_str).date()
        except (ValueError, TypeError):
            print(
                f"Warning: Invalid eol_date format for {model['model_id']}: {eol_str}",
                file=sys.stderr
            )
            continue

        days_until_eol = (eol_date - today).days

        if eol_date <= today:
            status = "EXPIRED"
        elif eol_date <= warning_threshold:
            status = "EXPIRING_SOON"
        else:
            continue  # Not approaching EOL

        # Find suggested alternatives (same tier, different model, no EOL)
        alternatives = [
            m['model_id'] for m in models
            if m.get('tier') == model.get('tier')
            and m['model_id'] != model['model_id']
            and not m.get('eol_date')
        ]

        warnings.append({
            'model_id': model['model_id'],
            'provider': model.get('provider'),
            'tier': model.get('tier'),
            'eol_date': eol_str,
            'days_until_eol': days_until_eol,
            'status': status,
            'alternatives': alternatives
        })

    return warnings


def format_text_output(warnings: List[Dict], warning_days: int) -> str:
    """Format warnings as human-readable text."""
    if not warnings:
        return f"✓ All models are current (checked for EOL within {warning_days} days)"

    lines = [f"⚠ Model EOL Warnings ({len(warnings)} models):", ""]

    for w in warnings:
        if w['status'] == 'EXPIRED':
            symbol = "❌"
            msg = "EXPIRED"
        else:
            symbol = "⚠️ "
            msg = f"expires in {w['days_until_eol']} days"

        lines.append(f"{symbol} {w['model_id']} ({w['provider']}, tier: {w['tier']})")
        lines.append(f"   EOL date: {w['eol_date']} - {msg}")

        if w['alternatives']:
            alt_list = ', '.join(w['alternatives'][:3])
            if len(w['alternatives']) > 3:
                alt_list += f" (+{len(w['alternatives']) - 3} more)"
            lines.append(f"   Suggested alternatives: {alt_list}")
        else:
            lines.append("   No direct alternatives available in same tier")
        lines.append("")

    return '\n'.join(lines)


def main():
    args = parse_args()

    try:
        models_file = resolve_models_file(args.models_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        models = load_models(models_file)
    except Exception as e:
        print(f"Error loading models: {e}", file=sys.stderr)
        return 1

    if not models:
        print("Warning: No models loaded from file", file=sys.stderr)
        return 1

    warnings = check_eol(models, args.days)

    if args.format == "json":
        output = {
            'checked_models': len(models),
            'warnings': warnings,
            'warning_threshold_days': args.days
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text_output(warnings, args.days))

    # Exit code: 0 if no warnings, 1 if warnings found
    return 1 if warnings else 0


if __name__ == '__main__':
    sys.exit(main())
