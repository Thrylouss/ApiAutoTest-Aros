# conftest.py
import os
import time
import pytest
import httpx
from dotenv import load_dotenv
from utils.tg_report import send_telegram_report

load_dotenv()

# Глобальное время старта прогона
_run_start_ts = None


@pytest.fixture(scope="session")
def guest_client():
    """Постоянный гостевой клиент без авторизации"""
    with httpx.Client(base_url=os.getenv("BASE_URL"), timeout=10.0) as client:
        yield client


@pytest.fixture(scope="session")
def auth_client():
    """Постоянный авторизованный клиент"""
    base_url = os.getenv("BASE_URL")
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        login_response = client.post("/web/v2/users/login_with_password/", json={
            "username": os.getenv("TEST_USERNAME", "+998998987882"),
            "password": os.getenv("TEST_PASSWORD", "Sh2004Sh"),
        })

        if login_response.status_code == 200:
            token = login_response.json().get("token")
            client.headers.update({"Authorization": f"Token {token}"})
        else:
            pytest.exit(
                f"Setup failed: Could not login. Status: {login_response.status_code}"
            )

        yield client


def pytest_sessionstart(session):
    global _run_start_ts
    _run_start_ts = time.time()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Отправка отчёта в TG после завершения прогона."""

    # Если переменная BOT_RUN_ID есть — значит запуск инициирован ботом,
    # тогда токен/chat_id может быть переопределён через env.
    token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    if not token or not chat_id:
        return  # Не настроено — молча выходим

    stats = {
        "total": terminalreporter._numcollected,
        "passed": len(terminalreporter.stats.get("passed", [])),
        "failed": len(terminalreporter.stats.get("failed", [])),
        "errors": len(terminalreporter.stats.get("error", [])),
    }

    failures = terminalreporter.stats.get("failed", [])
    errors = terminalreporter.stats.get("error", [])

    # Маркер из ENV — его пробрасывает бот при запуске по команде
    marker = os.getenv("RUN_MARKER")

    duration = None
    if _run_start_ts:
        duration = time.time() - _run_start_ts

    send_telegram_report(
        token=token,
        chat_id=chat_id,
        stats=stats,
        failures=failures,
        errors=errors,
        marker=marker,
        duration=duration,
    )