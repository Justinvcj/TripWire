import time
import random
import logging
from typing import Callable, Any
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, rpm_limit: int, tpm_limit: int = None, rpd_limit: int = None):
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.rpd_limit = rpd_limit
        self.daily_requests = 0

    def check_and_pace(self, estimated_tokens: int = 500):
        if self.rpd_limit and self.daily_requests >= self.rpd_limit:
            logger.error("Daily request limit reached. Provider halted.")
            raise Exception("Daily request limit reached.")
        self.daily_requests += 1

groq_limiter = RateLimiter(rpm_limit=settings.groq_rpm_limit, tpm_limit=settings.groq_tpm_limit)
gemini_limiter = RateLimiter(rpm_limit=settings.gemini_rpm_limit, rpd_limit=settings.gemini_rpd_limit)

def with_retry_and_pacing(limiter: RateLimiter, estimated_tokens: int, func: Callable, *args, **kwargs) -> Any:
    retries = 0
    while retries <= settings.max_api_retries:
        limiter.check_and_pace(estimated_tokens)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower() or "quota" in err_str.lower():
                if retries == settings.max_api_retries:
                    logger.error(f"Max retries reached. Error: {e}")
                    raise e
                
                delay = (settings.backoff_factor ** retries) + random.uniform(0, 1)
                logger.warning(f"Rate limit hit. Backing off for {delay:.2f}s... (Attempt {retries+1})")
                time.sleep(delay)
                retries += 1
            else:
                raise e
