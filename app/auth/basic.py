import re
import time
from collections import defaultdict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session
from services.crud import user as UserService
from database.database import get_session
import logging

logger = logging.getLogger(__name__)

security = HTTPBasic()

# Rate limiting storage (in production use Redis)
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300  # 5 minutes

def validate_password_strength(password: str) -> bool:
    """
    Проверяет надежность пароля.
    
    Args:
        password: Пароль для проверки
        
    Returns:
        bool: True если пароль соответствует требованиям
    """
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter, one lowercase letter, one digit
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    
    return True

def check_rate_limit(identifier: str) -> bool:
    """
    Проверяет, превысил ли пользователь лимит попыток входа.
    
    Args:
        identifier: Идентификатор пользователя (email или IP)
        
    Returns:
        bool: True если лимит превышен
    """
    now = time.time()
    attempts = login_attempts[identifier]
    
    # Remove old attempts outside the window
    attempts = [t for t in attempts if now - t < WINDOW_SECONDS]
    login_attempts[identifier] = attempts
    
    return len(attempts) >= MAX_ATTEMPTS

def record_login_attempt(identifier: str, success: bool):
    """
    Записывает попытку входа для ограничения частоты.
    
    Args:
        identifier: Идентификатор пользователя (email или IP)
        success: Успешность входа
    """
    if not success:
        login_attempts[identifier].append(time.time())
    
    # Log the attempt
    log_level = logging.INFO if success else logging.WARNING
    logger.log(log_level, f"Login attempt for {identifier}: {'SUCCESS' if success else 'FAILED'}")

def get_current_user(
    creds: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    """
    Получает текущего аутентифицированного пользователя с усиленной безопасностью.
    
    Args:
        creds: HTTP Basic учетные данные
        session: Сессия базы данных
        
    Returns:
        User: Объект аутентифицированного пользователя
        
    Raises:
        HTTPException: Если аутентификация не удалась или превышен лимит попыток
    """
    # Check rate limiting
    if check_rate_limit(creds.username):
        logger.warning(f"Rate limit exceeded for user: {creds.username}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    try:
        user = UserService.get_user_by_email(creds.username, session)
        if not user or not UserService.verify_password(creds.password, user.password_hash):
            record_login_attempt(creds.username, False)
            logger.warning(f"Failed login attempt for user: {creds.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        
        # Successful login
        record_login_attempt(creds.username, True)
        logger.info(f"Successful login for user: {creds.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication for {creds.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Basic"},
        )