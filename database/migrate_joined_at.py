"""Add and backfill student_detail.joined_at for older local databases."""

import mysql.connector

from config import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER, MYSQL_PORT


def migrate_joined_at():
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            """,
            (MYSQL_DATABASE, "student_detail", "joined_at"),
        )

        if not cursor.fetchone()[0]:
            cursor.execute("ALTER TABLE student_detail ADD COLUMN joined_at DATETIME NULL")
            print("Added student_detail.joined_at.")

        cursor.execute(
            """
            UPDATE student_detail sd
            LEFT JOIN student_admission sa ON sa.application_id = sd.application_id
            SET sd.joined_at = COALESCE(sd.joined_at, sa.submitted_at, CURRENT_TIMESTAMP)
            WHERE sd.joined_at IS NULL
            """
        )
        connection.commit()
        print(f"Backfilled {cursor.rowcount} student record(s).")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    migrate_joined_at()
