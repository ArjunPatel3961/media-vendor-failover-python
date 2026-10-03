"""Media asset processing and creator delivery with vendor failover."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    creator_id: str
    source_url: str
    title: str


@dataclass(frozen=True)
class ProcessingResult:
    asset_id: str
    vendor: str
    summary: str


class ProcessingVendor(Protocol):
    name: str

    def process(self, asset: MediaAsset) -> ProcessingResult:
        """Return a processed asset or raise a processing exception."""


class VendorRouter:
    def __init__(self, vendors: list[ProcessingVendor]) -> None:
        if not vendors:
            raise ValueError("at least one processing vendor is required")
        self._vendors = vendors

    def process(self, asset: MediaAsset) -> ProcessingResult:
        failures: list[str] = []
        for vendor in self._vendors:
            try:
                return vendor.process(asset)
            except Exception as exc:  # each vendor gets one bounded attempt
                failures.append(f"{vendor.name}: {exc}")
        raise RuntimeError("all processing vendors failed: " + "; ".join(failures))


@dataclass(frozen=True)
class CreatorDelivery:
    creator_id: str
    asset_id: str
    message: str
    processed_by: str


def ingest_process_and_deliver(
    asset: MediaAsset, router: VendorRouter
) -> CreatorDelivery:
    """Process one storefront media asset, then create its creator-facing delivery."""
    result = router.process(asset)
    return CreatorDelivery(
        creator_id=asset.creator_id,
        asset_id=asset.asset_id,
        message=f"{asset.title}: {result.summary}",
        processed_by=result.vendor,
    )
