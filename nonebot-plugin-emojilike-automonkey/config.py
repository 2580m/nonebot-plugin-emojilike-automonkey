try:
    from pydantic import BaseModel, model_validator
except ImportError:
    from pydantic import BaseModel, root_validator
from typing import List

class Config(BaseModel):
    automonkey_users: List[str]
    automonkey_groups: List[str]

    try:
        # pydantic v2
        @model_validator(mode="after")
        def check_automonkey_users(cls, values: "Config") -> "Config":
            if values.automonkey_users is not None and not (
                isinstance(values.automonkey_users, list) and all(isinstance(x, str) for x in values.automonkey_users)
            ):
                raise ValueError("automonkey_users must be a list of strings")
            return values

        @model_validator(mode="after")
        def check_automonkey_groups(cls, values: "Config") -> "Config":
            if values.automonkey_groups is not None and not (
                isinstance(values.automonkey_groups, list) and all(isinstance(x, str) for x in values.automonkey_groups)
            ):
                raise ValueError("automonkey_groups must be a list of strings")
            return values
    except TypeError:
        @root_validator
        def check_automonkey_users(cls, values: dict) -> dict:
            users = values.get("automonkey_users")
            if users is not None and not (isinstance(users, list) and all(isinstance(x, str) for x in users)):
                raise ValueError("automonkey_users must be a list of strings")
            return values

        @root_validator
        def check_automonkey_groups(cls, values: dict) -> dict:
            groups = values.get("automonkey_groups")
            if groups is not None and not (isinstance(groups, list) and all(isinstance(x, str) for x in groups)):
                raise ValueError("automonkey_groups must be a list of strings")
            return values