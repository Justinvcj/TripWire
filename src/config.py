import yaml
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_model: str
    judge_model: str
    confidence_threshold: float
    similarity_threshold: float
    escalation_precision_floor: float
    retrieval_k: int
    max_reply_chars: int
    max_verifier_retries: int
    tune_slice_path: str
    holdout_slice_path: str
    
    class Config:
        env_file = ".env"

def load_config() -> Settings:
    with open('config.yaml', 'r') as f:
        data = yaml.safe_load(f)
    settings = Settings(**data)
    
    assert settings.judge_model != settings.llm_model, \
        "Judge must use a different model than the generator to avoid self-preference bias (see ARCHITECTURE_v2 §4)"
    
    return settings

settings = load_config()
