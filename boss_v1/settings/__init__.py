from .base import *
#import environ
#env = environ.Env()
#environ.Env.read_env()
#print(REGISTERS_LOG)
BOSS_ENV="local" 
if BOSS_ENV == "prod":
    from .prod import *
else:
    from .dev import *
