#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from KPI.kpi import KPICALL


def main():
    #KPICALL()  # 스마트공장 솔루션 로그 자동 수집 API 적용

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seoulsoft_mes.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
