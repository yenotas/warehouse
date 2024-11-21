import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

if ENVIRONMENT == 'docker':
    from .docker import *
elif ENVIRONMENT == 'local':
    from .local import *
else:
    raise ValueError(f"Unknown environment: {ENVIRONMENT}")