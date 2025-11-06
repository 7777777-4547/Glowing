from PackWrapper.Utils import EventType, Event

from typing import Any
from pathlib import Path
import threading

def path_relative(path_original: str | Path, path_base: str | Path, path_rebase) -> Path:
    
    rel_path = Path(path_original).relative_to(path_base)
    dest_path =  path_rebase / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    return dest_path

def list_to_tuple(obj, level: int = -1) -> Any:

    if isinstance(obj, list) and level < 0:
        return tuple(list_to_tuple(item) for item in obj)
    elif isinstance(obj, list) and level > 0:
        return tuple(list_to_tuple(item, level - 1) for item in obj)
    else:
        return obj
    


class EventListener():
    
    def __init__(self, event: EventType, data, expected_data,):
        self.event = event
        self.data = data
        self.expected_data = expected_data
        self._event_thread = threading.Event()
    
    def setup(self):
        Event.subscribe(EventType.RESOURCEPACK_EXPORTING_COPY, self.wait_and_start_with_data)

    def wait_and_start_with_data(self, data):
        self._rp_data = data
        if data == self.expected_data:
            self._event_thread.set()

    