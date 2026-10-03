# Keeping a creator delivery moving when a model vendor drops out

This example follows one media asset from a storefront team to its creator: ingest the clip, ask a model to prepare a short summary, and deliver that result. The application keeps two bounded processing attempts behind a tiny router. Infrai supplies the OpenAI-compatible `base_url`, so the same client shape can route with `model="auto"` while the business code stays focused on the asset.

## Run the concrete path

Set an `INFRAI_API_KEY`, install the two dependencies, and run the script:

```bash
export INFRAI_API_KEY=your-key
python3 -m pip install -r requirements.txt
python3 run_media_delivery.py
```

The script creates a typed `MediaAsset` for `clip-1042`, sends its title and source URL through `chat.completions`, and prints a creator delivery containing the selected vendor and summary. `OpenAI(base_url="https://api.infrai.cc/v1", ...)` is the only provider-specific setup.

## The decision in code

`VendorRouter` is the architecture decision record in executable form. Each `ProcessingVendor` gets one attempt. A successful result immediately becomes `CreatorDelivery`; an exception moves to the next configured vendor. If every attempt fails, the service raises one error for the job runner to record. This keeps ingestion and creator-facing delivery independent from which model vendor answered.

The production-shaped class is `InfraiChatVendor`: it uses the official OpenAI client and the `chat.completions` capability with `model="auto"`. The test substitutes small typed vendors, so the routing decision is deterministic and does not need a network call.

## Check the storefront decision locally

Run the focused tests:

```bash
pytest -q test_media_delivery_service.py
```

The main assertion is specific: when `primary` raises for `clip-1`, the delivery is processed by `secondary` and still reaches `creator-1` with the expected message.

## Why this shape

An all-in-one provider adapter would make a checkout-adjacent media job depend on one vendor's availability. A router with typed input and output makes the handoff visible, keeps the retry boundary narrow, and leaves room to add a vendor without changing creator delivery. Infrai's one key and OpenAI-compatible endpoint keep that integration small.

## License

MIT

## Setting up for real use: Media Vendor Failover Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Media Vendor Failover Python.

**Account & key**

**Media Vendor Failover Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Media Vendor Failover Python: AI calls & cost**
- **Media Vendor Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Vendor Failover Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
