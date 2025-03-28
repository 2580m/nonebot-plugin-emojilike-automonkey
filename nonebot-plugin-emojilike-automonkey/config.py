from pydantic import BaseModel, root_validator
from typing import List

class Config(BaseModel):
    automonkey_users: List[str]
    automonkey_groups: List[str]
    #automonkey_command_priority: int = 10
    automonkey_plugin_enabled: bool = True

    @root_validator
    @classmethod
    def check_priority(cls, values: dict) -> dict:
        priority = values.get("automonkey_command_priority")
        if priority is not None and priority < 1:
            raise ValueError("automonkey command priority must be greater than 1")
        return values