import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from crawl4ai import AsyncWebCrawler
import asyncio
@dataclass
class Snapshot:
    url: str
    fetched_at: str     
    content_path: str       
    content_hash: Optional[str] = None


@dataclass
class VerificationIssue:
    severity: str  # "highlight" | "incorrect" | "info"
    message: str
    url: Optional[str] = None


class SnapshotManager:
    def __init__(self, out_dir: str = "snapshots") -> None:
        self.out_dir = out_dir
        self.crawler = AsyncWebCrawler() if AsyncWebCrawler is not None else None

    def _safe_name(self, url: str) -> str:
        import hashlib
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    def snapshot_url(self, url: str) -> Optional[Snapshot]:
        """
        Create an in-memory snapshot for the URL. Returns Snapshot or None.
        Only extracts text content (no HTML), and does not write to disk.
        """
        safe = self._safe_name(url)

        fetched_at = datetime.utcnow().isoformat()

        text_content = ""
        if self.crawler is not None:
            try:
                async def run_in_thread(url):
                    result = await self.crawler.arun(url)
                    return result

                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(run_in_thread(url))
                text_content = getattr(result, "text", "") or ""
            except Exception:
                pass

        if not text_content:
            # Fallback fetch
            try:
                from urllib.request import urlopen
                raw = urlopen(url, timeout=15).read().decode("utf-8", "ignore")
                text_content = re.sub(r"<[^>]+>", " ", raw)
            except Exception:
                return None

        # Hash
        try:
            import hashlib
            content_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
        except Exception:
            content_hash = None

        snap = Snapshot(
            url=url,
            fetched_at=fetched_at,
            content_path=f"memory://{safe}",
            content_hash=content_hash,
        )

        return snap


def _days_between(a_iso: str, b_iso: str) -> int:
    """Calculate days between two ISO datetime strings."""
    a = datetime.fromisoformat(a_iso.replace("Z", "+00:00"))
    b = datetime.fromisoformat(b_iso.replace("Z", "+00:00"))
    return abs((b - a).days)

