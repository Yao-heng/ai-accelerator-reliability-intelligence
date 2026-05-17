import re

from app.models.schemas import AcceleratorLogEntry, Severity


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+)\s+"
    r"(?P<severity>INFO|WARNING|ERROR|CRITICAL)\s+"
    r"accelerator=(?P<accelerator_id>\S+)\s+"
    r"rack=(?P<rack_id>\S+)\s+"
    r"fw=(?P<firmware_version>\S+)\s+"
    r"subsystem=(?P<subsystem>\S+)\s+"
    r"event=(?P<event_code>\S+)\s+"
    r"message=\"(?P<message>[^\"]+)\""
    r"(?P<tail>.*)$"
)

KV_PATTERN = re.compile(r"(?P<key>[a-zA-Z0-9_]+)=(?P<value>[^\s]+)")


class LogParser:
    """Converts accelerator platform logs into structured incident records."""

    def parse(self, raw_logs: str) -> list[AcceleratorLogEntry]:
        entries: list[AcceleratorLogEntry] = []

        for line in raw_logs.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            match = LOG_PATTERN.match(line)
            if not match:
                entries.append(self._parse_unstructured_line(line))
                continue

            fields = match.groupdict()
            metadata = {
                item.group("key"): item.group("value").strip('"')
                for item in KV_PATTERN.finditer(fields.get("tail") or "")
            }

            entries.append(
                AcceleratorLogEntry(
                    timestamp=fields["timestamp"],
                    severity=Severity(fields["severity"]),
                    accelerator_id=fields["accelerator_id"],
                    rack_id=fields["rack_id"],
                    firmware_version=fields["firmware_version"],
                    subsystem=fields["subsystem"],
                    event_code=fields["event_code"],
                    message=fields["message"],
                    metadata=metadata,
                )
            )

        return entries

    def _parse_unstructured_line(self, line: str) -> AcceleratorLogEntry:
        return AcceleratorLogEntry(
            timestamp="unknown",
            severity=Severity.warning,
            accelerator_id="unknown",
            subsystem="log-ingestion",
            event_code="UNSTRUCTURED_LOG_LINE",
            message=line,
            metadata={"parser_action": "fallback"},
        )
