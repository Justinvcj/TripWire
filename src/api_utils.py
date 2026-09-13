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
        
        self.request_timestamps = []
        self.token_timestamps = [] # list of (timestamp, tokens)
        self.daily_requests = 0
        
        # 80% pacing target
        self.target_rpm = max(1, int(self.rpm_limit * 0.8))
        self.min_delay_between_requests = 60.0 / self.target_rpm if self.target_rpm > 0 else 0
        self.last_request_time = 0

    def check_and_pace(self, estimated_tokens: int = 500):
        now = time.time()
        
        # Clean up old timestamps (older than 60s)
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        if self.tpm_limit:
            self.token_timestamps = [(ts, tk) for ts, tk in self.token_timestamps if now - ts < 60]
            
        # Pacing minimum delay
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_delay_between_requests:
            sleep_time = self.min_delay_between_requests - time_since_last
            time.sleep(sleep_time)
            now = time.time()
            
        # RPD Check
        if self.rpd_limit and self.daily_requests >= self.rpd_limit:
            raise Exception("Daily request limit reached. Cannot proceed today.")
            
        # TPM Check
        if self.tpm_limit:
            current_tpm = sum(tk for ts, tk in self.token_timestamps)
            if current_tpm + estimated_tokens > self.tpm_limit * 0.8:
                # Sleep until enough tokens clear
                sleep_time = 60 - (now - self.token_timestamps[0][0]) + 1
                logger.warning(f"TPM pacing: Sleeping {sleep_time:.1f}s to respect limits.")
                time.sleep(max(0, sleep_time))
                
        self.last_request_time = time.time()
        self.request_timestamps.append(self.last_request_time)
        if self.tpm_limit:
            self.token_timestamps.append((self.last_request_time, estimated_tokens))
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
                
                # Exponential backoff with jitter
                delay = (settings.backoff_factor ** retries) + random.uniform(0, 1)
                logger.warning(f"Rate limit hit. Retrying in {delay:.2f}s... (Attempt {retries+1}/{settings.max_api_retries})")
                time.sleep(delay)
                retries += 1
            else:
                raise e
