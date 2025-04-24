import os
from dotenv import load_dotenv

load_dotenv()

def verify_password(password: str) -> bool:
    """
    환경변수에 설정된 관리자 비밀번호와 비교
    """
    return password == os.getenv('ADMIN_PASSWORD', 'admin123@')
