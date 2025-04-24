from werkzeug.security import generate_password_hash, check_password_hash
import secrets


def generate_secure_password():
    """안전한 관리자 비밀번호 생성"""
    return secrets.token_urlsafe(16)


def hash_password(password):
    """비밀번호 해싱"""
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    """비밀번호 검증"""
    return check_password_hash(stored_hash, password)
