from slowapi import Limiter
from slowapi.util import get_remote_address

from utils.config import settings

# Create a single Limiter instance for the entire app
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.ACCESS_LIMIT])
