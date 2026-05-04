import os

import pytest
import httpx
from dotenv import load_dotenv

from utils.tg_report import send_telegram_report

load_dotenv()

@pytest.fixture(scope="session")
def api_client():
    # Используем синхронный клиент
    with httpx.Client(base_url=os.getenv("BASE_URL"), timeout=10.0) as client:
        yield client
    # Клиент закроется сам после завершения тестов

@pytest.fixture(scope="session")
def auth_api(api_client):
    from utils.client import AuthAPI
    return AuthAPI(api_client)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Хук, который вызывается после завершения всех тестов"""

    # Собираем статистику
    stats = {
        "total": terminalreporter._numcollected,
        "passed": len(terminalreporter.stats.get('passed', [])),
        "failed": len(terminalreporter.stats.get('failed', [])),
        "errors": len(terminalreporter.stats.get('error', [])),
    }

    # Отправляем отчет
    send_telegram_report(os.getenv("TG_TOKEN"), os.getenv("TG_CHAT_ID"), stats)