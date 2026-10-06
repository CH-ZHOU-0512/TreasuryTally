"""Chain-facing models that preserve source and integer amounts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransferRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    chain_id: int
    token_address: str
    transaction_hash: str
    log_index: int = Field(ge=0)
    block_number: int = Field(ge=0)
    block_hash: str | None
    from_address: str
    to_address: str
    amount_base_units: int = Field(ge=0)
    token_decimals: int = Field(ge=0, le=255)
    source: Literal["rpc", "blockscout"]

    @property
    def event_key(self) -> tuple[int, str, int]:
        return (self.chain_id, self.transaction_hash, self.log_index)


class RpcProbeResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    chain_id: int
    latest_block: int
    historical_block: int
    transfer: TransferRecord
