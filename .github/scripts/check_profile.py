"""Check that local Markdown links in the public portfolio resolve."""

from html import unescape
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = [ROOT / "README.md", *sorted(ROOT.glob("projects/**/README.md"))]
LINK = re.compile(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def main() -> int:
    checked = 0
    errors = []
    for document in DOCUMENTS:
        if not document.is_file():
            errors.append(f"Missing document: {document.relative_to(ROOT)}")
            continue
        for line_number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
            for match in LINK.finditer(line):
                target = urlsplit(unescape(match.group(1).strip("<>")))
                if target.scheme or target.netloc or not target.path:
                    continue
                checked += 1
                resolved = (document.parent / unquote(target.path)).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    errors.append(
                        f"{document.relative_to(ROOT)}:{line_number}: "
                        f"unresolved local link: {match.group(1)}"
                    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked {len(DOCUMENTS)} documents and {checked} local links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
