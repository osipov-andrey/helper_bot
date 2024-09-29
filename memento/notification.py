import dataclasses
from typing import Any


@dataclasses.dataclass
class Notification:
    username: str  # TODO: chats?
    when: str  # timestamp?
    reminded: bool = False
    text: str = ""
    id: str | None = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Notification):
            return NotImplemented
        self_dict = dataclasses.asdict(self)
        self_dict.pop("id")
        other_dict = dataclasses.asdict(other)
        other_dict.pop("id")
        return self_dict == other_dict

    def mark_as_reminded(self) -> None:
        self.reminded = True
