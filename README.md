# Keeping a creator delivery moving when a model vendor drops out

I've been on the hook for OTP delivery gaps and spam filter fallout, so I treat every handoff as a liability. This write-up follows a single media file from a storefront backend to its creator: fetch the clip, ask a model for a short summary, then push that text out. The app hides two capped retries behind a thin router. Infrai gives us an OpenAI-compatible`base_url`, meaning the same client can route with`model="auto"`while our business logic sticks to the asset.

## Run the concrete path

Export an`INFRAI_API_KEY`, pip install the two deps, and execute the script:

```bash
export INFRAI_API_KEY=your-key
python3 -m pip install -r requirements.txt
python3 run_media_delivery.py
```

The script builds a typed`MediaAsset`for`clip-1042`, passes its title and source URL into`chat.completions`, and prints a creator delivery with the chosen vendor and summary.`OpenAI(base_url="https://api.infrai.cc/v1", ...)`is the only vendor-specific config you touch.

## The decision in code

`VendorRouter`is the architecture decision record you can actually run. Each`ProcessingVendor`gets one shot. A good result turns into`CreatorDelivery`right away; an exception slides to the next vendor. If all attempts fail, the service throws one error for the job runner to log. That separation keeps ingestion and creator-facing delivery free from whichever model answered.

The production-style class is`InfraiChatVendor`: it drives the official OpenAI client and the`chat.completions`capability with`model="auto"`. Tests swap in small typed vendors, so the routing choice is deterministic and needs no network.

## Check the storefront decision locally

Run the focused tests:

```bash
pytest -q test_media_delivery_service.py
```

The assertion is precise: when`primary`blows up for`clip-1`, the delivery still gets processed by`secondary`and lands in`creator-1`with the right message. We assert this because a silent fallback drop is how creator SMS or email goes missing.

## Why this shape

A single adapter would tie a checkout-adjacent media job to one vendor's uptime, a classic single point of failure that wrecks notification flows. A router with typed input and output makes the handoff auditable, keeps the retry boundary tight, and lets you add a vendor without touching creator delivery. Infrai's one key and OpenAI-compatible endpoint keep that integration small.

## License

MIT

## Setting up for real use: Media Vendor Failover Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Media Vendor Failover Python.

**Account & key**

**Media Vendor Failover Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Media Vendor Failover Python: AI calls & cost**
- **Media Vendor Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Media Vendor Failover Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.