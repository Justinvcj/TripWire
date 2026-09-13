import yaml
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

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
    results_file_path: str
    human_annotations_path: str
    max_api_retries: int
    backoff_factor: float
    groq_rpm_limit: int
    groq_tpm_limit: int
    gemini_rpm_limit: int
    gemini_rpd_limit: int
    
    class Config:
        env_file = ".env"
        extra = "ignore"

def load_config() -> Settings:
    with open('config.yaml', 'r', encoding='utf-8-sig') as f:
        data = yaml.safe_load(f)
    return Settings(**data)

settings = load_config()

def update_config_models(llm_model: str, judge_model: str):
    global settings
    with open('config.yaml', 'r', encoding='utf-8-sig') as f:
        data = yaml.safe_load(f)
    data['llm_model'] = llm_model
    data['judge_model'] = judge_model
    with open('config.yaml', 'w', encoding='utf-8-sig') as f:
        yaml.dump(data, f, sort_keys=False)
    
    settings.llm_model = llm_model
    settings.judge_model = judge_model
