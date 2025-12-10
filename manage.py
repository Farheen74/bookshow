#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
    print("Warning: python-dotenv not installed. Continuing without .env file support.")

def main():
    """Run administrative tasks."""
    
    # Only for Local Development - Load environment variables from the .env file
    if not 'WEBSITE_HOSTNAME' in os.environ:
        if load_dotenv:
            print("Loading environment variables for .env file")
            load_dotenv('./.env')
        else:
            print("Note: .env file not loaded (python-dotenv not installed)")

    # When running on Azure App Service you should use the production settings. as it will inject environment varianles
    settings_module = "movieticket.production" if 'WEBSITE_HOSTNAME' in os.environ else 'movieticket.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movieticket.settings')
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
