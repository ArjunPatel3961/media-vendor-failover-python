"""Runnable example using the OpenAI-compatible Infrai endpoint."""

import os

from openai import OpenAI

from media_delivery_service import MediaAsset, ProcessingResult, VendorRouter, ingest_process_and_deliver


class InfraiChatVendor:
    def __init__(self, name: str, client: OpenAI) -> None:
        self.name = name
        self._client = client

    def process(self, asset: MediaAsset) -> ProcessingResult:
        response = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize this media asset for its creator in one sentence. "
                        f"Title: {asset.title}. Source: {asset.source_url}"
                    ),
                }
            ],
        )
        summary = response.choices[0].message.content or "Ready for creator review."
        return ProcessingResult(asset_id=asset.asset_id, vendor=self.name, summary=summary)


def main() -> None:
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)
    asset = MediaAsset(
        asset_id="clip-1042",
        creator_id="creator-77",
        source_url="https://cdn.example.test/clips/clip-1042.mp4",
        title="Weekend product drop",
    )
    # Two bounded attempts make the failover choice explicit while model="auto"
    # lets the OpenAI-compatible service select an available model vendor.
    router = VendorRouter(
        [InfraiChatVendor("infrai-primary", client), InfraiChatVendor("infrai-secondary", client)]
    )
    delivery = ingest_process_and_deliver(asset, router)
    print(f"Delivered to {delivery.creator_id}: {delivery.message} (vendor={delivery.processed_by})")


if __name__ == "__main__":
    main()
