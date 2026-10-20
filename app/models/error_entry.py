"""
Data model for error entries in the queue.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ErrorEntry:
    """Represents a single error entry in the queue."""

    error_type: str
    printers: List[str]
    pages: List[int]
    notes: str = ""

    # Context from when the error was added
    line_number: int = 0
    campaign: str = ""
    operator: str = ""
    firmware: str = ""

    # Test info fields captured at time of error
    climate: str = ""
    media: str = ""
    script: str = ""
    plexity: str = ""
    load: str = ""
    run: str = ""
    phase: str = ""

    @property
    def count(self) -> int:
        """Number of pages affected (equals tally count)."""
        return len(self.pages)

    @property
    def printer_summary(self) -> str:
        """Short summary of affected printers."""
        if len(self.printers) == 8:
            return "ALL"
        elif len(self.printers) > 3:
            return f"{len(self.printers)} printers"
        else:
            # Show last 3 chars of each printer name
            return ", ".join([p[-3:] for p in self.printers])

    @property
    def page_summary(self) -> str:
        """Short summary of affected pages."""
        if len(self.pages) > 3:
            return f"pg {self.pages[0]}, {self.pages[1]}... ({len(self.pages)} total)"
        else:
            return f"pg {', '.join(map(str, self.pages))}"

    def get_test_info(self) -> Dict[str, str]:
        """Return test info as a dictionary for cover sheet generation."""
        return {
            "climate": self.climate,
            "media": self.media,
            "script": self.script,
            "plexity": self.plexity,
            "load": self.load,
            "run": self.run,
            "phase": self.phase,
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "error_type": self.error_type,
            "printers": self.printers,
            "pages": self.pages,
            "count": self.count,
            "notes": self.notes,
            "line_number": self.line_number,
            "campaign": self.campaign,
            "operator": self.operator,
            "firmware": self.firmware,
            "climate": self.climate,
            "media": self.media,
            "script": self.script,
            "plexity": self.plexity,
            "load": self.load,
            "run": self.run,
            "phase": self.phase,
        }
