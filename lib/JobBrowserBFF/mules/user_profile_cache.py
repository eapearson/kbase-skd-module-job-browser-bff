from threading import Thread
import time
from JobBrowserBFF.cache.UserProfileCache import UserProfileCache
from JobBrowserBFF.Config import Config

config = Config()
LOOP_INTERVAL = config.get_int("cache-refresh-interval")
INITIAL_DELAY = config.get_int("cache-refresh-initial-delay")


def refresh_cache():
    cache_path = config.get("cache-directory") + "/user_profile.db"
    cache = UserProfileCache(
        path=cache_path,
        user_profile_url=config.get("user-profile-url"),
        upstream_timeout=60,
    )
    cache.reload()


def start():
    time.sleep(INITIAL_DELAY)
    while True:
        try:
            refresh_cache()
        except Exception:
            print("Error refreshing user_profile_cache")
        time.sleep(LOOP_INTERVAL)


t = Thread(target=start)
t.daemon = True
t.start()
