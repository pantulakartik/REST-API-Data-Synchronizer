#Runs the synchronization workflow

import logging
import sqlite3
import sys
from pathlib import Path
import requests

from api_client import fetch_users
from transformer import transform_users
from database import (
    initialize_database,
    upsert_users,
    get_user_count,
    get_all_users,
)

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "sync.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    logger.info("sync_started")

    try:
        raw_users = fetch_users()
        logger.info("records_fetched count=%s", len(raw_users))

        valid_users, rejected_users = transform_users(raw_users)

        logger.info(
            "validation_completed valid=%s rejected=%s",
            len(valid_users),
            len(rejected_users),
        )

        for record in rejected_users:
            logger.warning(
                "record_rejected index=%s reason=%s",
                record["record_index"],
                record["reason"],
            )

        initialize_database()

        processed = upsert_users(valid_users)
        total_users = get_user_count()

        logger.info("records_processed count=%s", processed)
        logger.info("database_total_users count=%s", total_users)

        for user in get_all_users()[:3]:
            logger.info(
                "sample_user external_id=%s email=%s",
                user["external_id"],
                user["email"],
            )

        logger.info("sync_completed status=success")

    except (
        requests.RequestException,
        ValueError,
        sqlite3.Error,
    ):
        logger.exception("sync_failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

