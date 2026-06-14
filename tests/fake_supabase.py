"""Cliente Supabase falso, in-memory, para uso nos testes."""

from __future__ import annotations


class _Response:
    def __init__(self, data: list) -> None:
        self.data = data


class _Query:
    def __init__(self, store: list) -> None:
        self._store = store
        self._op: str | None = None
        self._payload: object = None
        self._eq: dict = {}
        self._neq: dict = {}
        self._order_col: str | None = None
        self._order_desc: bool = False

    def select(self, *_args: object) -> "_Query":
        self._op = "select"
        return self

    def insert(self, payload: object) -> "_Query":
        self._op = "insert"
        self._payload = payload
        return self

    def delete(self) -> "_Query":
        self._op = "delete"
        return self

    def update(self, payload: object) -> "_Query":
        self._op = "update"
        self._payload = payload
        return self

    def upsert(self, payload: object) -> "_Query":
        self._op = "upsert"
        self._payload = payload
        return self

    def eq(self, col: str, val: object) -> "_Query":
        self._eq[col] = val
        return self

    def neq(self, col: str, val: object) -> "_Query":
        self._neq[col] = val
        return self

    def order(self, col: str, *, desc: bool = False) -> "_Query":
        self._order_col = col
        self._order_desc = desc
        return self

    def _matches(self, row: dict) -> bool:
        for k, v in self._eq.items():
            if row.get(k) != v:
                return False
        for k, v in self._neq.items():
            if row.get(k) == v:
                return False
        return True

    def execute(self) -> _Response:
        if self._op == "select":
            rows = [r for r in self._store if self._matches(r)]
            if self._order_col:
                rows = sorted(
                    rows,
                    key=lambda r: r.get(self._order_col, ""),
                    reverse=self._order_desc,
                )
            return _Response(rows)

        if self._op == "insert":
            rows = self._payload if isinstance(self._payload, list) else [self._payload]
            self._store.extend(rows)
            return _Response(list(rows))

        if self._op == "delete":
            removed = [r for r in self._store if self._matches(r)]
            for r in removed:
                self._store.remove(r)
            return _Response(removed)

        if self._op == "update":
            updated = []
            for r in self._store:
                if self._matches(r):
                    assert isinstance(self._payload, dict)
                    r.update(self._payload)
                    updated.append(r)
            return _Response(updated)

        if self._op == "upsert":
            rows = self._payload if isinstance(self._payload, list) else [self._payload]
            for new_row in rows:
                assert isinstance(new_row, dict)
                key = "id" if "id" in new_row else "ticker"
                existing = next(
                    (r for r in self._store if r.get(key) == new_row.get(key)), None
                )
                if existing is not None:
                    existing.update(new_row)
                else:
                    self._store.append(new_row)
            return _Response(list(rows))

        return _Response([])


class FakeSupabaseClient:
    """Substituto in-memory do supabase.Client para testes unitários."""

    def __init__(self) -> None:
        self._tables: dict[str, list] = {}

    def table(self, name: str) -> _Query:
        if name not in self._tables:
            self._tables[name] = []
        return _Query(self._tables[name])
