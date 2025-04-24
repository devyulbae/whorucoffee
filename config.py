import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")  # 해시된 비밀번호 저장
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # 세션 유효기간 1시간
