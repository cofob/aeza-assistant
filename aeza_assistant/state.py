from dataclasses import dataclass


@dataclass
class BotState:
    """Bot state."""

    current_statuses: dict[str, bool]
