from pydantic import BaseModel

__all__ = ["BlueprintsOptions"]


class BlueprintsOptions(BaseModel):
    data_version: int = 2975  # 1.18.2
    output_location: str = "{namespace}:{path}"
