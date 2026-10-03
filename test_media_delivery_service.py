import pytest

from media_delivery_service import MediaAsset, ProcessingResult, VendorRouter, ingest_process_and_deliver


class FailingVendor:
    name = "primary"

    def process(self, asset: MediaAsset) -> ProcessingResult:
        raise RuntimeError("capacity reached")


class WorkingVendor:
    name = "secondary"

    def process(self, asset: MediaAsset) -> ProcessingResult:
        return ProcessingResult(asset.asset_id, self.name, "A creator-ready cut")


def test_delivery_uses_next_vendor_when_first_attempt_fails() -> None:
    asset = MediaAsset("clip-1", "creator-1", "https://cdn.example.test/clip.mp4", "Launch clip")
    delivery = ingest_process_and_deliver(asset, VendorRouter([FailingVendor(), WorkingVendor()]))

    assert delivery.processed_by == "secondary"
    assert delivery.message == "Launch clip: A creator-ready cut"


def test_router_requires_a_vendor() -> None:
    with pytest.raises(ValueError, match="at least one"):
        VendorRouter([])
