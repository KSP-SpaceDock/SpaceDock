from SpaceDock.config import _cfg
from SpaceDock.celery import update_patreon
import celery
import redis
import time
import json

donation_cache = redis.Redis(host=_cfg('patreon-host'), port=_cfg('patreon-port'), db=_cfg('patreon-db'))

def GetDonationAmount():
    last_update_time = donation_cache.get('patreon_update_time')
    donation_amount = donation_cache.get('patreon_donation_amount')
    request_update = False

    if donation_amount is None:
        donation_amount = 0
        donation_cache.set('patreon_donation_amount', 0)
    else:
        donation_amount = int(donation_amount.decode('utf-8'))
    
    if last_update_time is None:
        request_update = True
    else:
        last_update_time = float(last_update_time.decode('utf-8'))
        time_delta = time.time() - last_update_time
        #Update every 10 minutes
        if time_delta > 600:
            request_update = True
    
    if request_update:
        update_patreon.delay()
    
    return donation_amount
