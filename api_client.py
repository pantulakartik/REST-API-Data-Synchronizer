#Retrieves data from the API

import logging
import time

import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def fetch_users(max_attempts=3):
    """
    Fetch user records with bounded retries for temporary failures.
    """

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(API_URL, timeout=10)

            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt == max_attempts:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After", "")
                delay = (
                    int(retry_after)
                    if retry_after.isdigit()
                    else 2 ** (attempt - 1)
                )

                logger.warning(
                    "api_retry status=%s attempt=%s delay_seconds=%s",
                    response.status_code,
                    attempt,
                    delay,
                )
                time.sleep(min(delay, 30))
                continue

            response.raise_for_status()

            users = response.json()

            if not isinstance(users, list):
                raise ValueError("API response must be a list")

            if not all(isinstance(user, dict) for user in users):
                raise ValueError("API response contains a non-object record")

            logger.info("api_fetch_success record_count=%s", len(users))
            return users

        except (requests.Timeout, requests.ConnectionError) as error:
            if attempt == max_attempts:
                logger.exception(
                    "api_fetch_failed attempts=%s", attempt
                )
                raise

            delay = 2 ** (attempt - 1)

            logger.warning(
                "api_retry error_type=%s attempt=%s delay_seconds=%s",
                type(error).__name__,
                attempt,
                delay,
            )
            time.sleep(delay)

        except requests.HTTPError:
            # Non-retryable HTTP errors, or the final failed attempt.
            logger.exception("api_http_error")
            raise

    raise RuntimeError("API fetch ended without a response")
