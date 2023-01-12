import os
from dotenv import load_dotenv

load_dotenv()

GDG_REDIS_HOST=os.getenv("GDG_REDIS_HOST") or "localhost"
GDG_REDIS_PORT=os.getenv("GDG_REDIS_PORT") or  6379
GDG_MODEL_HOSTNAME=os.getenv("GDG_MODEL_HOSTNAME") or "0"
GDG_BUMP_MODEL_START=os.getenv("GDG_BUMP_MODEL_START") or False

def bump_model_hostname():
    if GDG_BUMP_MODEL_START:
        split = GDG_MODEL_HOSTNAME.split("-")
        v = 0
        if len(split) > 1:
            v_str = split[-1]
            try: 
                v = int(v_str)
            except (TypeError, ValueError) as error:
                v = 0
        os.putenv("GDG_MODEL_HOSTNAME", f"{GDG_MODEL_HOSTNAME}-{v}")
        os.system("echo $GDG_MODEL_HOSTNAME")