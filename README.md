# Mystery Reactions — Product & Engineering Spec (Canonical)

This README is the single source of truth for v0.  
**Quickstart with AI Coder:**
1) Open GitHub → Actions → “AI Coder” → Run workflow.
2) Paste a plain-English task (see “How to Use This Document” at the bottom).
3) Review the PR the agent opens; merge when checks pass.

Mystery Reactions — Product & Engineering Spec (Canonical)
Status: v0 blueprint agreed
Scope: iOS, Android, Website (landing) + full backend/media/payments/auth stack
Quality bar: Production grade, trust first, privacy first, secure, observable, testable
Build mode: AI first development (GitHub Actions “AI Coder” opens PRs; you approve)
 
0) Table of Contents
1.	Vision & Core Principles
2.	Platforms & Scope
3.	User Journeys (v0)
4.	Feature Set by Release
5.	Third Party Short Video Integration (TikTok/Shorts/Reels)
6.	System Architecture (high level)
7.	Services (by responsibility)
8.	Data Model (primary entities)
9.	Media & AI Pipeline (transcode, mux, AI trim)
10.	Authenticity & Trust (liveness, attestation, signing, verification)
11.	Payments (Free / Paid / Rush Paid, escrow, refunds, fees)
12.	Privacy, Moderation, & Ephemerality
13.	Ratings & Discovery
14.	Notifications & Real Time
15.	Public API Surface (GraphQL + Webhooks)
16.	Infrastructure & Environments
17.	CI/CD, QA, and AI Agent Workflow
18.	Security, Compliance, & Risk Controls
19.	SLOs, Metrics, Observability
20.	Roadmap (v1 / v2) — excludes the vouch/kin features per request
21.	Repo Layout & Local Dev Quickstart
22.	Secrets & Configuration
23.	Appendices (Acceptance Criteria checklists)
 
1) Vision & Core Principles
•	Capture authentic first reactions to shared content, then deliver beautiful, verifiable composite videos.
•	Trust & safety first: in app capture only, liveness & device attestation, cryptographic signing, verification page.
•	Privacy by default: short TTLs, one tap deletion, minimal data retention.
•	Reliable money flows: escrow, auto refund on SLA miss, clear fees, Stripe Connect.
•	Operational excellence: deterministic workflows (Temporal), test coverage, strong observability.
 
2) Platforms & Scope
•	iOS app: Swift/SwiftUI + AVFoundation; push via APNs.
•	Android app: Kotlin/Compose + CameraX/ExoPlayer; push via FCM.
•	Website (v0): Next.js landing page (marketing + waitlist).
•	Backend: NestJS (TypeScript) GraphQL API + webhooks.
•	Media workers: Python (FastAPI) + FFmpeg for HLS, mux, watermark, AI trim helpers.
•	Orchestration: Temporal.io for timers and multi step jobs.
•	Payments: Stripe Connect (Express).
•	Infra: AWS (S3, CloudFront, ECS Fargate, RDS Postgres, Redis, SQS, KMS, Secrets Manager, CloudWatch, WAF).
 
3) User Journeys (v0)
Send a mystery message (free/paid/rush):
1.	Sender selects recipient(s) and attaches text / image / video (≤2 min).
2.	(Paid/Rush) Sender agrees to price & optional SLA (e.g., 1h/24h). Funds escrowed.
3.	Receiver opens → 3 2 1 auto record front camera + mic.
4.	AI trim picks best 3–10s (text/image); video reactions last ≥ source duration; manual override allowed.
5.	Send uploads reaction (capture/capture don’t share). On Send, escrow captures; on Don’t share, refund/void.
6.	Server side mux (split, Pause→PiP, audio only), watermark (timestamp + drift), deliver to sender; show verification page.
Groups:
•	Each member reacts independently upon opening; watch individually or as synchronized montage (manual sync v0; AI sync v2).
Reminders:
•	“React later” list; Rush shows SLA countdown; otherwise low pressure.
 
4) Feature Set by Release
✅ v0 (launch)
•	Messaging: DMs & groups; blind open mode (no preview; recording starts on open).
•	Reaction capture: auto record + consent sheet; visible recording badge.
•	Deliverables: split screen, Pause→PiP, audio only fallback; server side mux only (no user composites).
•	Message types: Free, Paid, Rush Paid (escrow, capture/refund, platform fee 20%).
•	Authenticity: in app capture only; liveness/face match; device attestation (AppAttest/Play Integrity); source SHA 256; signed metadata; soft authenticity watermark; public verification page.
•	Privacy & safety: reactions TTL 7d; source TTL 14d; one tap delete; content moderation baseline (CSAM/extremism/nudity); mature content age gate.
•	Profiles & ratings: creator badges (IG≥2k, TikTok≥3k, YT≥2k); tags/discipline; multi axis ratings(Real/Funny/Insightful/Creative/Spiritual/Aware) with anti abuse.
•	Discovery (basic): search/browse creators by discipline, price, SLA, language.
•	Charity: pledged % split via Stripe (in transaction routing) + badge.
•	Notifications: push + fetch.
•	Web: landing page only.
▶ v1
•	Rich creator directory filters & detail pages.
•	Disputes flow & moderation console v1.
•	Web client (send/view).
•	Creator/admin portal basics (pricing menus, queue, payouts).
•	Optional group unlock after react mode.
•	Add WebSockets where useful (e.g., SLA countdowns, group readiness).
▶ v2
•	AI Auto Sync Group View (precise beat alignment).
•	AI Montage Editing (auto cut, format, title multi reaction compilations).
•	Commercial rights upsell at checkout; verification page logging.
•	Brand briefs / B2B campaigns; advanced creator analytics; stronger rating trust models.
•	Web creator/admin portal advanced (analytics, exports).
Explicitly excluded from future add ons (per product decision): kinship graph & closeness %, vouch power, star friends, business/personal vouches, VouchWeb, kin based events & invites.
 
5) Third Party Short Video Integration (TikTok/YouTube Shorts/IG Reels)
Goal: Let users share links from TikTok/Shorts/Reels and view them inside our app using official embeds—we do notdownload/rehost.
•	Share in: iOS Share Extension; Android Intent filter to accept URLs.
•	Playback: WebView with official players (YouTube IFrame API; TikTok Embed; Instagram oEmbed).
•	Discovery feed: Start curated links; optionally YouTube Data API mostPopular for a general shelf; creator authorized feeds (user OAuth) for TikTok; no scraping.
•	Reactions: Keep record to view for DMs/groups. For browsing feeds, use “React to unlock” (explicit tap) with a persistent recording indicator; do not auto record while scrolling.
 
6) System Architecture (High Level)
Clients: iOS, Android, Next.js site.
Edge: CloudFront CDN; WAF; signed URLs/cookies for HLS.
Core services (ECS Fargate):
•	API Gateway (NestJS GraphQL) — auth, messaging, payments, ratings, directory, notifications.
•	Media Service (Python FastAPI + workers) — upload pre sign, transcode (FFmpeg/HLS), AI trim, mux, watermark, thumbnails, manifests.
•	Workflow Orchestrator (Temporal) — ReactionPipeline, RushSLA, ContentTTL, Disputes.
•	Moderation Service — provider adapters, queues, policy decisions.
•	Verification Page Service — public check page + play with short lived URLs.
State: RDS Postgres (primary), Redis (cache/ratelimit), S3 (assets, SSE KMS), Algolia/OpenSearch (directory).
Async: SQS queues per pipeline stage + DLQs; CloudWatch/Sentry/OTel for logs/traces.
 
7) Services (by Responsibility)
•	Auth & Identity: Email/phone login, JWT, device registration, rate limits.
•	Attestation: AppAttest (iOS) / Play Integrity (Android); mint short lived capture tokens.
•	Messaging: Mysteries (requests), participants, open/send states, blind open, group flows.
•	Media: Pre sign S3 PUT; verify SHA 256; FFmpeg transcode ladders; mux split/PiP/audio; watermark overlay; HLS key server.
•	Payments: Stripe: escrow/capture/refund; Connect Express; transfers to creator/charity; platform fee.
•	Moderation: Scan assets; block or review; panic stop; audit trails.
•	Profiles/Ratings/Directory: creator badges & thresholds; multi axis ratings (w/ shrinkage & anomaly controls); filters.
•	Notifications: APNs/FCM push; reminder scheduling.
•	Verification: Assemble checks and signed metadata; serve a public verify page.
 
8) Data Model (Primary Entities)
users: id, email/phone, dob (age flag), country, created_at, trust_flags.
devices: id, user_id, platform, app_version, attestation_state, last_attested_at.
creators: user_id, follower_counts (ig/tiktok/yt), disciplines[], language, donation_pledge_pct, stripe_connect_account_id, offers_rush, rush_markup_pct.
charities: id, name, stripe_account_id, active.
mysteries: id, sender_user_id, group_id?, type (free/paid/rush), sla_seconds?, price_cents, source_kind (text/image/video), source_asset_id, blind_open, expires_at, status.
mystery_participants: id, mystery_id, receiver_user_id, state (pending/opened/reacted/dont_share/missed), capture_token_id?, reaction_id?.
assets: id, type (source/reaction/composite/thumbnail), s3_key, sha256, duration_ms, width, height, hls_manifest_key?, encrypted, ttl_delete_at, created_at.
reactions: id, mystery_id, reactor_user_id, reaction_asset_id, ai_trim_range?, manual_override_range?, liveness_id, signature_blob, clock_drift_ms, delivery_format.
payments: id, mystery_id, stripe_payment_intent_id, amount_gross, platform_fee, charity_amount, creator_amount, state (escrowed/captured/refunded).
liveness_checks: id, user_id, vendor, result, score, template_face_id, created_at.
moderation_jobs: id, asset_id, provider, result (clean/flag/block), labels[], confidence.
ratings: id, rater_user_id, rated_user_id, mystery_id, criteria (real/funny/insightful/creative/spiritual/aware 1–5), trust_weight, created_at.
audit_logs: id, actor_type, action, target_id, meta_json, created_at.
(Indexing: foreign keys + composite indexes on status/state, created_at, ttl_delete_at; GIN on tags/labels; unique constraints where appropriate.)
 
9) Media & AI Pipeline
Upload intake: client requests pre signed S3 URL; server expects content hash; S3 event/Lambda re computes SHA 256 → bind to sourceHash.
Transcode: FFmpeg → HLS (fMP4), 480/720/1080p ladders; normalize audio; thumbnails.
AI trim: For text/image source, pick 3–10 sec highlights via face/voice cue heuristics (Python worker); persist ai_trim_range; allow client override.
Mux & Watermark: Server side compose split or Pause→PiP; overlay soft authenticity watermark (timestamp, device clock drift, reaction id). Embed signed metadata (capture_token id, creatorID, timestamp, sourceHash) in HLS/MP4 boxes.
Playback security: CloudFront signed cookies/URLs; AES 128 HLS keys served via key service; short TTLs.
 
10) Authenticity & Trust Stack
•	In app capture only for reactions (no camera roll).
•	Device attestation: AppAttest/Play Integrity → short lived capture_token bound to user/device/mystery.
•	Liveness + face match: vendor SDK; blink/turn; bind to template_face_id; periodic refresh.
•	Source binding: compute & display SHA 256 hash (faint edge hash in frames + on verification page).
•	Cryptographic signing: (capture_token + creatorID + timestamp + sourceHash) signed server side; stored in asset metadata.
•	Verification page (public): short URL with checks (attestation, liveness, hash match, signature) + secure playback URL.
 
11) Payments
•	Paid & Rush Paid: create PaymentIntent (escrow) at send; capture on Send; refund/void on Don’t share or SLA miss (with grace).
•	Stripe Connect Express: transfers to creator and charity (pledged %) with transfer_group=mystery_id; platform fee 20% (tips off in v0).
•	Disputes: webhook → mark content, run DisputeWorkflow; gather evidence; timeline & communication.
 
12) Privacy, Moderation, & Ephemerality
•	Ephemerality: reactions auto delete 7d, source auto delete 14d (S3 lifecycle + Temporal ContentTTL + DB hard purge).
•	One tap delete anywhere; audited.
•	Moderation: CSAM hash matching; extremism lists; nudity/violence classifiers; panic stop kills distribution and triggers refunds; adjudication queue.
•	Mature content: age gate; still fully scanned.
•	Data minimization: store only what’s needed; strict PII handling; GDPR/CCPA export/delete endpoints with SLAs.
 
13) Ratings & Discovery
•	Ratings: six criteria (1–5). Only strangers & payers can rate to reduce bias; Bayesian shrinkage + time decay + anomaly detection; device throttles.
•	Directory/Search: by discipline, price, SLA, language, donation badge; show rating snippets and verification badges.
•	Search backend: Algolia (SaaS) or OpenSearch (self hosted) with write buffer queue and backfills.
 
14) Notifications & Real Time
•	Push: APNs/FCM (new mysteries, reactions delivered, SLA reminders, payouts).
•	Real time minimalism (v0): push + fetch.
•	v1 WebSockets: SLA countdowns, group readiness, basic live indicators; only where it adds real user value.
 
15) Public API Surface
GraphQL (selected types):
type Query {
  me: User
  mystery(id: ID!): Mystery
  searchCreators(filter: CreatorFilter!): CreatorSearchResult
}

type Mutation {
  createMystery(input: CreateMysteryInput!): Mystery
  openMystery(id: ID!): MysteryOpenPayload
  requestCaptureToken(mysteryId: ID!, attestation: AttestationInput!): CaptureToken
  submitReaction(input: SubmitReactionInput!): Reaction
  dontShare(mysteryParticipantId: ID!): Mystery
  rateUser(input: RatingInput!): Rating
}
Webhooks:
•	/webhooks/stripe (payments)
•	/webhooks/moderation (providers)
•	/webhooks/liveness (vendor)
•	/verify/{slug} (public verification page)
Idempotency: all mutating calls accept Idempotency-Key.
 
16) Infrastructure & Environments
•	AWS accounts by env: dev, staging, prod.
•	Compute: ECS Fargate services for API/media; autoscaling for media workers.
•	Storage: S3 (SSE KMS, private buckets), RDS Postgres (encrypted), Redis (ElastiCache).
•	CDN: CloudFront; HLS signed cookies/URLs.
•	Secrets: AWS Secrets Manager; never in code.
•	Security edge: WAF (OWASP rules, IP reputation, geo), least privilege IAM.
 
17) CI/CD, QA, and AI Agent Workflow
AI first dev loop:
•	GitHub Actions workflow “AI Coder” (manual input to start; optional Issue auto trigger later).
•	You type a plain English task → workflow asks OpenAI → AI writes files → opens a Pull Request.
•	Branch protection requires status checks to pass; you approve to merge. No local coding required.
Workflows (YAMLs):
•	ai-coder.yml (manual) and ai-coder-issues.yml (issue trigger, optional).
•	ci_api.yml (NestJS tests + coverage ≥80%)
•	ci_media.yml (FastAPI tests + ffmpeg smoke test)
•	ci_web.yml (Next.js build)
•	e2e.yml (API+media end to end on ephemeral containers)
•	deploy_staging.yml (auto on merge to develop)
•	deploy_prod.yml (manual approval required)
Testing strategy:
•	Unit tests (business rules, pricing, ratings math).
•	Integration tests (media pipeline containers; Stripe webhooks using test clocks).
•	E2E (Detox for mobile; Playwright for web).
•	Security tests (attestation bypass attempts, URL signing, WAF rules).
•	Chaos/regression (kill media workers mid job; Temporal resumes).
 
18) Security, Compliance, & Risk Controls
•	In app capture only; enforce origin signature; reject camera roll reactions.
•	Attestation freshness (token TTL 5–10 min); re challenge suspicious devices.
•	Signed playback; HLS key server requires policy checks.
•	Rate limits per user/device/IP; anomaly scoring for velocity and geo patterns.
•	Audit logs for auth, payments, deletions; dual control for refunds/payouts.
•	Compliance: GDPR/CCPA export & delete; subprocessor registry.
•	Incident runbooks and kill switch flags for moderation/payment subsystems.
 
19) SLOs, Metrics, Observability
SLOs:
•	API p95 < 200ms (excluding media jobs)
•	Upload pre sign p95 < 150ms
•	99% reactions available < 2 min after Send (v0 target)
•	Push delivery: 99.9% within 30s (non Rush), 10s (Rush)
Metrics: business (opens, sends, dont_shares, SLA misses, conversion, payout totals), media (transcode time, error rate, queue lag), payments (escrow/capture/refund latencies), moderation outcomes.
Observability: OpenTelemetry traces → Datadog/Grafana; Sentry for errors; CloudWatch logs.
 
20) Roadmap (v1 / v2)
v1: richer directory & creator profiles; disputes + mod console; web client (send/view); creator/admin basics; unlock after react; selective WebSockets.
v2: AI auto sync & montage editing; commercial rights upsell; brand briefs/B2B; advanced analytics & rating trust; web portal advanced.
Excluded from roadmap (per decision): kinship graph & closeness %, vouch power, star friends, business/personal vouches, VouchWeb, kin based events & invites.
 
21) Repo Layout & Local Dev Quickstart
mystery-reactions/
  apps/
    api/        # NestJS GraphQL API
    media/      # FastAPI + FFmpeg workers
    ios/        # Swift/SwiftUI
    android/    # Kotlin/Compose
    web/        # Next.js landing
  infra/
    terraform/  # AWS IaC
  tools/
    ai_coder.py
    requirements.txt
  docs/
    architecture.md
  .github/
    workflows/  # ci/deploy/ai-coder
Local (Docker) quickstart (to be generated via AI task):
•	docker compose up api media db redis
•	web: npm install && npm run dev
•	Mobile apps build from their folders (Xcode/Android Studio).
 
22) Secrets & Configuration
•	GitHub Actions Secrets:
OPENAI_API_KEY, (optional) OPENAI_MODEL
Later: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, STRIPE_SECRET_KEY, APNS_KEY, FIREBASE_KEY, etc.
•	Runtime env vars (by service):
DATABASE_URL, REDIS_URL, S3_BUCKET, CLOUDFRONT_DIST_ID, STRIPE_KEYS, LIVENESS_VENDOR_KEYS, MODERATION_VENDOR_KEYS.
Never commit secrets. Use GitHub/AWS secrets managers.
 
23) Appendices — Acceptance Criteria (v0)
Messaging & Capture
•	 Open triggers consent sheet (toggle “Ask me every time”).
•	 3 2 1 → on screen recording badge; visible stop/send/don’t share.
•	 Blind open mode works (recording starts immediately after open).
AI Trim & Delivery
•	 Text/image: AI selects 3–10s; manual override saves range.
•	 Video: reaction duration ≥ source duration; overflow allowed; not billed.
•	 Server mux: split & Pause→PiP; audio only fallback.
•	 Watermark (timestamp + drift + reaction id); thumbnails.
Authenticity & Verification
•	 In app capture enforced (origin signature).
•	 Attestation token required; liveness pass required (blocking).
•	 Source SHA 256 displayed in frames; signature embedded.
•	 Verification page shows green checks & plays via short lived URL.
Payments
•	 Paid: escrow at send; capture on Send; refund on Don’t share.
•	 Rush: SLA timer per participant; auto refund on miss (with grace).
•	 Connect splits to creator + charity; platform fee 20%.
•	 Disputes webhook flows to review.
Privacy & Moderation
•	 Reactions TTL 7d; source TTL 14d; hard delete pipeline verified.
•	 One tap delete purges S3 + DB + search indexes.
•	 Moderation blocks illegal/harmful content; panic stop works; audits logged.
Ratings & Discovery
•	 Ratings UI (six criteria) available only to strangers/payers; anti abuse throttles.
•	 Directory filters (discipline, price, SLA, language) return consistent results.
Notifications
•	 Push on new mysteries, delivery, SLA reminders, payouts.
•	 “React later” reminders visible and accurate.
Web Landing
•	 Next.js page live (hero, pitch, waitlist form).
•	 CI builds on PR; deploys on merge (to staging).
 
How to Use This Document
•	Paste this README.md into your repo root; it’s the source of truth.
•	When the window gets stuck or we lose context, copy this back to me and say:
“Resume building according to the canonical README.”
•	To build with AI only: use the AI Coder workflow. Example first tasks:
1.	“Create /docs/architecture.md summarizing this README.”
2.	“Scaffold /apps/api NestJS GraphQL with Prisma + /healthz + CI + tests.”
3.	“Create /apps/media FastAPI + /presign + FFmpeg worker + smoke tests + CI.”
4.	“Create /web Next.js landing + build CI.”
5.	“Add Stripe test mode escrow endpoints + webhook in API + tests.”
6.	“Add iOS/Android shells (recording placeholders) + unit tests + CI.”
7.	“Add Docker Compose + root README quickstart.”





