"""Isolated parse timing and retained endpoint-string count for a real AF."""

import hashlib
import json
from pathlib import Path
import sys
import time

from argumentation.interop.iccma import parse_af, write_af


def main():
    text = Path(sys.argv[1]).read_text()
    started = time.perf_counter()
    framework = parse_af(text)
    elapsed = time.perf_counter() - started
    seen = set()
    retained_bytes = 0
    for edge in framework.defeats:
        for endpoint in edge:
            identity = id(endpoint)
            if identity not in seen:
                seen.add(identity)
                retained_bytes += sys.getsizeof(endpoint)
    print(
        json.dumps(
            {
                "parse_seconds": elapsed,
                "arguments": len(framework.arguments),
                "attacks": len(framework.defeats),
                "endpoint_string_objects": len(seen),
                "endpoint_string_bytes": retained_bytes,
                "canonical_af_sha256": hashlib.sha256(
                    write_af(framework).encode()
                ).hexdigest(),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
