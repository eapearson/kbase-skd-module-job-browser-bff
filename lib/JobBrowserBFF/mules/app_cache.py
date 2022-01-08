from threading import Thread
import time
from JobBrowserBFF.cache.AppCache import AppCache
from JobBrowserBFF.Config import Config

config = Config()
LOOP_INTERVAL = config.get_int("cache-refresh-interval")
INITIAL_DELAY = config.get_int("cache-refresh-initial-delay")


def refresh_cache():
    cache_path = config.get("cache-directory") + "/app.db"
    cache = AppCache(
        path=cache_path,
        narrative_method_store_url=config.get("nms-url"),
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
