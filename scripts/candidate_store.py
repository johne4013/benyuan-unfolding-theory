#!/usr/bin/env python3
"""
candidate_store.py — SQLite-backed candidate store

SQLite alternative to the JSON file store in evolution_candidate_manager.py.
Provides indexed queries, atomic writes, and import/export to/from JSON dirs.
"""

import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CandidateStore:
    """SQLite-backed store for theory evolution candidates."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        priority TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'CANDIDATE',
        evidence_count INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        data_json TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_status ON candidates(status);
    CREATE INDEX IF NOT EXISTS idx_type ON candidates(type);
    CREATE INDEX IF NOT EXISTS idx_created ON candidates(created_at);
    CREATE INDEX IF NOT EXISTS idx_type_status ON candidates(type, status);
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            from paths import runtime_dir
            db_path = str(runtime_dir() / "candidates.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # DB initialisation
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(self.SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def save(self, candidate: dict) -> str:
        """Upsert a candidate. Sets updated_at. Returns candidate id."""
        cid = candidate.get("id")
        if not cid:
            raise ValueError("Candidate must have an 'id' field")

        now = datetime.now().isoformat()
        # Keep original created_at if present, else use now
        created_at = candidate.get("created_at", now)

        # Build a fresh copy with updated_at stamped
        data = dict(candidate)
        data["updated_at"] = now

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO candidates
                    (id, type, priority, title, status, evidence_count,
                     created_at, updated_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type          = excluded.type,
                    priority      = excluded.priority,
                    title         = excluded.title,
                    status        = excluded.status,
                    evidence_count= excluded.evidence_count,
                    updated_at    = excluded.updated_at,
                    data_json     = excluded.data_json
                """,
                (
                    cid,
                    candidate.get("type", ""),
                    candidate.get("priority", "medium"),
                    candidate.get("title", ""),
                    candidate.get("status", "CANDIDATE"),
                    candidate.get("evidence_count", 1),
                    created_at,
                    now,
                    json.dumps(data, ensure_ascii=False),
                ),
            )
        return cid

    def load(self, candidate_id: str) -> dict:
        """Load a candidate by ID. Raises FileNotFoundError if missing."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data_json FROM candidates WHERE id = ?", (candidate_id,)
            ).fetchone()
        if row is None:
            raise FileNotFoundError(f"Candidate not found: {candidate_id}")
        return json.loads(row["data_json"])

    def delete(self, candidate_id: str) -> None:
        """Delete a candidate by ID."""
        with self._connect() as conn:
            conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        status: Optional[str] = None,
        candidate_type: Optional[str] = None,
        since: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """Query candidates with optional filters.

        Args:
            status:         Filter by status string (e.g. 'CANDIDATE').
            candidate_type: Filter by type (e.g. 'PATTERN').
            since:          ISO datetime string — only return created_at >= since.
            search:         Substring search in title or data_json.
            limit:          Maximum number of results.
        """
        sql = "SELECT data_json FROM candidates WHERE 1=1"
        params: list = []

        if status is not None:
            sql += " AND status = ?"
            params.append(status)

        if candidate_type is not None:
            sql += " AND type = ?"
            params.append(candidate_type)

        if since is not None:
            sql += " AND created_at >= ?"
            params.append(since)

        if search is not None:
            sql += " AND (title LIKE ? OR data_json LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like])

        sql += " ORDER BY created_at DESC"

        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [json.loads(r["data_json"]) for r in rows]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Return aggregate stats: total, by_type, by_status, pattern_avg_evidence."""
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]

            by_type_rows = conn.execute(
                "SELECT type, COUNT(*) as cnt FROM candidates GROUP BY type"
            ).fetchall()
            by_type = {r["type"]: r["cnt"] for r in by_type_rows}

            by_status_rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM candidates GROUP BY status"
            ).fetchall()
            by_status = {r["status"]: r["cnt"] for r in by_status_rows}

            avg_row = conn.execute(
                "SELECT AVG(evidence_count) as avg FROM candidates WHERE type = 'PATTERN'"
            ).fetchone()
            pattern_avg = round(avg_row["avg"], 2) if avg_row["avg"] is not None else 0.0

        return {
            "total": total,
            "by_type": by_type,
            "by_status": by_status,
            "pattern_avg_evidence": pattern_avg,
        }

    # ------------------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------------------

    def find_potential_duplicates(self) -> List[Tuple[str, str]]:
        """Return (id1, id2) pairs that share the same type and normalised title prefix."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, type, title FROM candidates ORDER BY type, title"
            ).fetchall()

        pairs: List[Tuple[str, str]] = []
        items = [(r["id"], r["type"], r["title"].strip().lower()) for r in rows]

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                id1, type1, title1 = items[i]
                id2, type2, title2 = items[j]
                if type1 != type2:
                    continue
                # Simple heuristic: same first 10 chars of title
                if title1[:10] == title2[:10] and title1[:10]:
                    pairs.append((id1, id2))

        return pairs

    # ------------------------------------------------------------------
    # Import / Export
    # ------------------------------------------------------------------

    def import_from_json_dir(self, json_dir: str) -> dict:
        """Import all *.json files from a directory. Returns {imported, failed}."""
        imported = 0
        failed = 0
        for path in Path(json_dir).glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    candidate = json.load(f)
                self.save(candidate)
                imported += 1
            except Exception as e:
                print(f"Warning: failed to import {path.name}: {e}", file=sys.stderr)
                failed += 1
        return {"imported": imported, "failed": failed}

    def export_to_json_dir(self, json_dir: str) -> int:
        """Export all candidates as JSON files to a directory. Returns count."""
        out_dir = Path(json_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        candidates = self.query()
        for candidate in candidates:
            cid = candidate.get("id", "unknown")
            ctype = candidate.get("type", "unknown").lower()
            filename = f"{cid}-{ctype}.json"
            filepath = out_dir / filename

            tmp_fd, tmp_path = tempfile.mkstemp(dir=out_dir, suffix=".tmp")
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    json.dump(candidate, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, filepath)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

        return len(candidates)


# ======================================================================
# CLI
# ======================================================================

def _cli_stats(store: CandidateStore) -> None:
    stats = store.get_stats()
    print(f"Total candidates: {stats['total']}")
    print(f"By type:   {stats['by_type']}")
    print(f"By status: {stats['by_status']}")
    print(f"PATTERN avg evidence: {stats['pattern_avg_evidence']}")


def _cli_list(store: CandidateStore, args: list) -> None:
    status = None
    ctype = None
    search = None
    i = 0
    while i < len(args):
        if args[i] == "--status" and i + 1 < len(args):
            status = args[i + 1]
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            ctype = args[i + 1]
            i += 2
        elif args[i] == "--search" and i + 1 < len(args):
            search = args[i + 1]
            i += 2
        else:
            i += 1

    results = store.query(status=status, candidate_type=ctype, search=search)
    if not results:
        print("No candidates found.")
        return
    for c in results:
        print(
            f"  {c.get('id')}  [{c.get('type')}]  {c.get('status')}  {c.get('title', '')[:60]}"
        )


def _cli_duplicates(store: CandidateStore) -> None:
    pairs = store.find_potential_duplicates()
    if not pairs:
        print("No potential duplicates found.")
        return
    for id1, id2 in pairs:
        print(f"  Possible duplicate: {id1}  <->  {id2}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  candidate_store.py stats")
        print("  candidate_store.py import <dir>")
        print("  candidate_store.py export <dir>")
        print("  candidate_store.py list [--status S] [--type T] [--search Q]")
        print("  candidate_store.py duplicates")
        sys.exit(0)

    store = CandidateStore()
    cmd = args[0]

    if cmd == "stats":
        _cli_stats(store)

    elif cmd == "import" and len(args) >= 2:
        result = store.import_from_json_dir(args[1])
        print(f"Imported: {result['imported']}, Failed: {result['failed']}")

    elif cmd == "export" and len(args) >= 2:
        count = store.export_to_json_dir(args[1])
        print(f"Exported {count} candidates to {args[1]}")

    elif cmd == "list":
        _cli_list(store, args[1:])

    elif cmd == "duplicates":
        _cli_duplicates(store)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
