"""Append-only SQLite repository for tasks, submissions, and verification runs."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from trust_receipt.hashing import canonical_json_bytes
from trust_receipt.models.submissions import ServiceSubmission
from trust_receipt.models.tasks import TaskSpec
from trust_receipt.models.verification import VerificationResult
from trust_receipt.services.ports import FaultInjection, ReportDelivery
from trust_receipt.storage.models import AttemptRecord, StoredTask, TaskState


class RepositoryStateError(RuntimeError):
    pass


class SQLiteRepository:
    """Small explicit repository; domain models never depend on SQLite types."""

    def __init__(self, database: str | Path) -> None:
        self._database = str(database)
        if self._database != ":memory:":
            Path(self._database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_json TEXT NOT NULL,
                    state TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    task_id TEXT NOT NULL,
                    attempt INTEGER NOT NULL CHECK (attempt IN (1, 2)),
                    submission_id TEXT NOT NULL UNIQUE,
                    submission_json TEXT NOT NULL,
                    fault_json TEXT NOT NULL,
                    PRIMARY KEY (task_id, attempt),
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                );
                CREATE TABLE IF NOT EXISTS verification_results (
                    submission_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    FOREIGN KEY (submission_id) REFERENCES attempts(submission_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                );
                """
            )

    @staticmethod
    def _dump(model) -> str:
        return canonical_json_bytes(model).decode("utf-8")

    def add_task(self, task: TaskSpec) -> None:
        try:
            with closing(self._connect()) as connection, connection:
                connection.execute(
                    "INSERT INTO tasks(task_id, task_json, state) VALUES (?, ?, ?)",
                    (task.task_id, self._dump(task), TaskState.CONFIRMED.value),
                )
        except sqlite3.IntegrityError as error:
            raise RepositoryStateError(f"task already exists: {task.task_id}") from error

    def get_task(self, task_id: str) -> StoredTask:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT task_json, state FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return StoredTask(task=TaskSpec.model_validate_json(row["task_json"]), state=TaskState(row["state"]))

    def _attempt_count(self, connection: sqlite3.Connection, task_id: str) -> int:
        row = connection.execute("SELECT COUNT(*) AS count FROM attempts WHERE task_id = ?", (task_id,)).fetchone()
        return int(row["count"])

    def request_attempt(self, task_id: str) -> int:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            count = self._attempt_count(connection, task_id)
            allowed = {TaskState.CONFIRMED} if count == 0 else {TaskState.FAIL, TaskState.INCONCLUSIVE}
            state = TaskState(row["state"])
            if state not in allowed or count >= 2:
                raise RepositoryStateError(
                    "an attempt can be requested only once initially and once after a terminal retryable result"
                )
            if count == 1:
                connection.execute(
                    "UPDATE tasks SET state = ? WHERE task_id = ?", (TaskState.RETRY_REQUESTED.value, task_id)
                )
            connection.execute(
                "UPDATE tasks SET state = ? WHERE task_id = ?", (TaskState.REQUESTED.value, task_id)
            )
            return count + 1

    def cancel_attempt_request(self, task_id: str) -> None:
        """Undo a request only when no delivery was persisted for that request."""
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            if TaskState(row["state"]) is not TaskState.REQUESTED:
                raise RepositoryStateError("only an unfulfilled request can be cancelled")
            count = self._attempt_count(connection, task_id)
            if count == 0:
                previous = TaskState.CONFIRMED
            else:
                latest = connection.execute(
                    """SELECT v.result_json
                       FROM attempts a
                       JOIN verification_results v ON v.submission_id = a.submission_id
                       WHERE a.task_id = ? ORDER BY a.attempt DESC LIMIT 1""",
                    (task_id,),
                ).fetchone()
                if latest is None:
                    raise RepositoryStateError("cannot cancel after a delivery was persisted")
                outcome = VerificationResult.model_validate_json(latest["result_json"]).outcome.value
                previous = TaskState(outcome)
            connection.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (previous.value, task_id))

    def save_delivery(self, delivery: ReportDelivery) -> None:
        submission = delivery.submission
        try:
            with closing(self._connect()) as connection, connection:
                row = connection.execute(
                    "SELECT state FROM tasks WHERE task_id = ?", (submission.task_id,)
                ).fetchone()
                if row is None:
                    raise KeyError(submission.task_id)
                if TaskState(row["state"]) is not TaskState.REQUESTED:
                    raise RepositoryStateError("delivery requires a requested attempt")
                expected_attempt = self._attempt_count(connection, submission.task_id) + 1
                if submission.attempt != expected_attempt:
                    raise RepositoryStateError(f"expected attempt {expected_attempt}, got {submission.attempt}")
                connection.execute(
                    """INSERT INTO attempts(
                           task_id, attempt, submission_id, submission_json, fault_json
                       ) VALUES (?, ?, ?, ?, ?)""",
                    (
                        submission.task_id,
                        submission.attempt,
                        submission.submission_id,
                        self._dump(submission),
                        self._dump(delivery.fault_injection),
                    ),
                )
                connection.execute(
                    "UPDATE tasks SET state = ? WHERE task_id = ?",
                    (TaskState.SUBMITTED.value, submission.task_id),
                )
        except sqlite3.IntegrityError as error:
            raise RepositoryStateError("attempts and submissions are append-only and cannot be overwritten") from error

    def begin_verification(self, task_id: str, submission_id: str) -> None:
        with closing(self._connect()) as connection, connection:
            task = connection.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            attempt = connection.execute(
                "SELECT 1 FROM attempts WHERE task_id = ? AND submission_id = ?", (task_id, submission_id)
            ).fetchone()
            if task is None:
                raise KeyError(task_id)
            if attempt is None or TaskState(task["state"]) is not TaskState.SUBMITTED:
                raise RepositoryStateError("verification must target the current submitted attempt")
            connection.execute(
                "UPDATE tasks SET state = ? WHERE task_id = ?", (TaskState.VERIFYING.value, task_id)
            )

    def save_verification(self, result: VerificationResult) -> None:
        target_state = TaskState(result.outcome.value)
        try:
            with closing(self._connect()) as connection, connection:
                task = connection.execute(
                    "SELECT state FROM tasks WHERE task_id = ?", (result.task_id,)
                ).fetchone()
                if task is None:
                    raise KeyError(result.task_id)
                if TaskState(task["state"]) is not TaskState.VERIFYING:
                    raise RepositoryStateError("verification result requires VERIFYING state")
                connection.execute(
                    "INSERT INTO verification_results(submission_id, task_id, result_json) VALUES (?, ?, ?)",
                    (result.submission_id, result.task_id, self._dump(result)),
                )
                connection.execute(
                    "UPDATE tasks SET state = ? WHERE task_id = ?", (target_state.value, result.task_id)
                )
        except sqlite3.IntegrityError as error:
            raise RepositoryStateError("verification results are append-only and cannot be overwritten") from error

    def get_attempt(self, task_id: str, attempt: int) -> AttemptRecord:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """SELECT a.submission_json, a.fault_json, v.result_json
                   FROM attempts a
                   LEFT JOIN verification_results v ON v.submission_id = a.submission_id
                   WHERE a.task_id = ? AND a.attempt = ?""",
                (task_id, attempt),
            ).fetchone()
        if row is None:
            raise KeyError((task_id, attempt))
        result = VerificationResult.model_validate_json(row["result_json"]) if row["result_json"] else None
        return AttemptRecord(
            submission=ServiceSubmission.model_validate_json(row["submission_json"]),
            fault_injection=FaultInjection.model_validate(json.loads(row["fault_json"])),
            verification_result=result,
        )

    def list_attempts(self, task_id: str) -> tuple[AttemptRecord, ...]:
        with closing(self._connect()) as connection:
            numbers = connection.execute(
                "SELECT attempt FROM attempts WHERE task_id = ? ORDER BY attempt", (task_id,)
            ).fetchall()
        return tuple(self.get_attempt(task_id, int(row["attempt"])) for row in numbers)
