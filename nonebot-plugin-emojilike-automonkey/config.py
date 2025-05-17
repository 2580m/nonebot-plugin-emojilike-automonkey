
from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    automonkey_users: List[str]
    automonkey_groups: List[str]