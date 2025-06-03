#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # 在生产环境中使用settings_production
    if os.environ.get('RAILWAY_ENVIRONMENT', '') == 'production':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings_production')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 