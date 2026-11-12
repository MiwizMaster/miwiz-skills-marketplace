# MIWIZ ENGLISH CONVERSATION × ACTIVE 5
## Product & UX Specification — Embedded Miniapp
**Version:** 1.0 — Design baseline (pre-Codex)  
**Date:** 2026-11-11  
**Status:** Proposed UX specification; not an implementation claim  
**Target:** Mobile-first miniapp embedded in Miwiz, extensible to web

---

## 1. Executive summary
The miniapp enables learners to conduct meaningful English conversations with an AI discussion partner that also corrects language in detail. Following each conversation, it converts the real conversation into a curated lesson, two audio assets, five Miwiz Active 5 practice decks, and an optional personal error deck. It links practice outcomes to later conversations, forming a learning loop.

**Core proposition:** **Talk naturally → Correct precisely → Curate useful language → Practice with Active 5 → Reuse in conversation.**

**Decisions already confirmed:**
- Learner chooses the topic; can use English, Vietnamese, or mixed language.
- AI replies conversationally in English, with actual opinions, substantive responses, and respectful disagreement where appropriate; it must not merely interview the learner.
- Option B: after **every learner turn**, give detailed correction/explanation, **three style variants (Formal, Neutral, Casual)**, and **IPA**.
- After ending, give strengths, improvements, useful language and a conversation-based model dialogue.
- Convert session output to **1 lesson + 2 audio assets + 5 Active 5 decks**, with an optional cross-session Personal Error Deck.
- Design and approve UI before handing implementation to Codex.

**Current-status caveat:** The canonical definitions and APIs of Active 1–5 and the existing Miwiz card/player/data infrastructure have **not yet been verified** in this specification. Mapping in §7 is a design proposal, subject to matching the actual Miwiz Active 5 method. Do not replace existing Active 5 semantics without approval.

## 2. Target users & jobs
**Primary:** Vietnamese-speaking learner with intermediate English goals, interested in substantial professional and everyday topics.  
**Secondary:** Other Miwiz language learners with different levels; future other languages.

Jobs-to-be-done:
1. Discuss a topic as a genuine conversation with context and continuity.
2. Understand and correct my own mistakes immediately without losing the thread.
3. Learn multiple register-appropriate ways to express my ideas and pronounce them.
4. Turn what I said into high-quality personalized learning material quickly.
5. Practice, retain, and reuse previously difficult language.

## 3. Scope
### 3.1 In scope for V1 UX
- Entry point inside Miwiz; session library; topic selection; conversation view; text and voice-entry affordances (voice dependent on actual integration capability).
- Detailed feedback per learner turn with original → natural correction → explanations → 3 variations → IPA, plus separate AI conversation response.
- Full session end review.
- Curation preview and controls for lesson, two audio types, five decks, personal error deck.
- Generation job lifecycle and error/retry states.
- Content review/edit/approve; publish to appropriate user-owned Miwiz location.
- Lesson view, links to decks and audio; practice-entry and progress summary.
- Data permissions, deletion, session visibility, and accessibility states.

### 3.2 Out of scope for V1
- New proprietary speech scoring engine; pronunciation scores unless audio-specific evidence is present.
- Rewriting existing Miwiz Active 5 player or card algorithms.
- Public social publishing or third-party LMS integration.
- Assuming real-time streaming, TTS voices, backend service names, or direct API access without discovery.

## 4. Experience principles
1. **Conversation first, but Option B remains explicit.** A learner turn yields both comprehensive feedback and a real AI response. Keep UI scannable via collapsible sections; do not silently omit the promised 3 variations or IPA.
2. **Distinct roles:** Language Coach vs Conversation Partner visually identifiable.
3. **No invented corrections:** If the learner's message is already correct, explicitly affirm it and provide enhancement alternatives; distinguish errors from optional style improvements.
4. **Meaning fidelity:** All variants preserve user intent; register changes do not imply stronger factual positions.
5. **Context-aware adaptation:** Target slightly above demonstrated proficiency, never classify CEFR with unwarranted certainty.
6. **Safe generation:** AI-generated content is previewed and accepted before publication; no automatic public posting.
7. **Platform consistency:** Inherit Miwiz navigation, typography, tokens, authentication, media tools, flashcard schemas, and data permissions as much as possible.
8. **Mobile-native:** thumb-friendly controls, compact cards, expandable IPA, no huge blocks that bury dialogue.

## 5. Information architecture
```text
Miwiz
└── English Conversation (Miniapp)
    ├── Home / Sessions
    │   ├── New conversation
    │   ├── Recent sessions
    │   └── Learning progress (summary)
    ├── Session
    │   ├── Topic & level settings
    │   ├── Conversation timeline
    │   │   ├── Learner turn
    │   │   ├── Coach correction (expandable)
    │   │   └── AI conversation response
    │   └── End session
    ├── Session Review
    │   ├── Strengths & priorities
    │   ├── Vocabulary/chunks & errors
    │   └── Model dialogue
    ├── Generate learning materials
    │   ├── Curation & settings
    │   ├── Generating status
    │   ├── Review & edit generated assets
    │   └── Approve & save/publish
    └── Learning Collection
        ├── Lesson / dialogue / IPA
        ├── Conversation audio
        ├── Shadowing audio
        ├── Active 1–5 decks (existing player)
        └── Personal error review (optional)
```

## 6. End-to-end user journeys
### Journey A — New conversation
1. Open Miniapp from Miwiz; view recent sessions and **Start conversation**.
2. Enter topic or select suggestion; optionally choose discussion context (Everyday / Professional / Debating), target difficulty (Auto default), input (Text / Voice if available).
3. AI begins with a substantive opening or a natural question.
4. User submits English/Vietnamese/mixed turn.
5. System returns a **coach feedback object** and a separate **AI conversational reply**; feedback appears in collapsed/expanded groups while response stays readable.
6. User continues, can review earlier feedback in place, bookmark useful chunks, or end.
7. End confirmation -> Session Review.

### Journey B — Generate from session
1. From Review, tap **Create Active 5 lesson**.
2. Curated language preview; adjust quantity (e.g. 8/12/15 chunks), level and desired focus (errors / work topics / everyday), view coverage.
3. Choose assets: Lesson (default on), Conversation audio, Shadowing audio, Five Active 5 decks (default on), Personal Error Deck (optional).
4. Press **Generate draft**; show independent step statuses and partial success.
5. Review content using tabs **Overview / Lesson / Audio / Active 1–5 / Errors**. Edit source chunks, incorrect items, distractors, transcript, style, title; regenerate one component as needed.
6. Explicit **Approve & Save to Miwiz**. Default private; only public sharing after separate user action and platform support.
7. Open saved lesson / practice.

### Journey C — Follow-up learning
1. User opens saved lesson, listens to audio, practices decks using current Miwiz card player.
2. Practice results flow to a progress model through existing app capabilities.
3. New conversation may gently reuse difficult chunks if permissions and available progress data allow.

## 7. Active 5 mapping — provisional, pending canonical confirmation
**Do not implement card-type mapping until actual Active 5 definitions are verified.**

| Stage | Proposed intent | Example for “Urban Development” | UX/card interaction |
|---|---|---|---|
| Active 1 | Meaning recognition | “traffic congestion” → “ùn tắc giao thông” | Meaning choice |
| Active 2 | Context usage | “Many ___ projects are underway” | Contextual choice |
| Active 3 | Listening & retrieval | Hear “massive construction site” and fill blank | Audio + gap fill |
| Active 4 | Sentence production | Rebuild “I prefer staying at home” | Word reordering |
| Active 5 | Dialogue reconstruction | Reorder/complete conversational turns and variations | Sentence/dialogue ordering |

**Content contract per practice item:** item_id, source_session_id, source_turn_ids, chunk_ids, stage, instruction, prompt, accepted answers, distractors (when appropriate), difficulty, IPA (if applicable), audio refs, rationale, review metadata. Canonical Miwiz schema takes precedence.

**Generation quality requirements:** exact meaning, grammatical correctness, unambiguous answers, plausible distractors, pronunciation consistent with selected accent, no answer leakage, no duplicated cards, coverage across stage types, and editable draft prior to saving.

## 8. Screen specifications
### S01 — Miniapp Home
**Purpose:** start or resume learning.  
**Layout:** Miwiz header; title “English Conversation”; primary CTA “Start a conversation”; topic chips; recent sessions cards (topic, date, duration, pending review/generated status); mini progress summary; lesson library shortcut.  
**Empty:** welcoming explanation + start CTA.  
**Actions:** start, resume, view review, open lesson.  
**Mobile:** single column. No implementation-only options surfaced.

### S02 — Session Setup
**Fields:** Topic (free text), optional starter prompts, setting: target level [Auto/B1/B2/etc optional], discussion style [Balanced/Professional/Debate], accent [American default], input mode [Text/Voice if supported].  
**CTA:** Begin conversation.  
**Defaults:** Auto difficulty, balanced discussion, American IPA. Save preferences only with consent/application settings.

### S03 — Conversation Room (core)
**Layout:** persistent header with topic, session status, overflow actions; scrollable timeline; sticky composer with input, mic when available, send; End session accessible but not dominant.  
**Message groups:**
- Learner bubble (original text, optional waveform/transcript edit if user submitted voice).
- **English Coach** panel: visible title “Your improved version” with corrected sentence; expandable sections “What to improve” (errors/why), “3 ways to say it” (Formal/Neutral/Casual), “IPA & pronunciation” (optionally IPA for all variants and highlighted words), “Try again” (non-blocking).
- **Conversation Partner** bubble: a coherent English response with opinion, reasoning, illustration, or respectful challenge; optional follow-up question, not mandatory.
**Behavior:** do not force learners to repeat; default display corrected sentence + concise coach summary and let them expand complete detail. Always generate the detailed components, accessible on tap. Preserve timeline continuity and scroll position when expanded.
**Error-free message:** “Your sentence is natural and correct”; note enhancements rather than fabricated corrections; still show three registers and IPA.
**Voice:** distinguish transcript error vs learner language error; only pronunciation coaching from usable audio; do not assign pronunciation scores based on text.
**Loading:** per-turn coach and partner generation states, retry only failed component; do not duplicate user turn.

### S04 — Session Review
**Sections:** executive feedback (strengths, focus areas), corrections summary, top 5–10 chunks with IPA, structures, model dialogue (two speakers and actual discussion positions), session stats (counts only; avoid unsupported proficiency claims).  
**CTA:** Create Active 5 lesson; secondary Return to session / Save review.  
**Empty:** minimum 1 valid exchange for creating learning assets; otherwise explain insufficiency and allow manual selection.

### S05 — Generate Material Setup
**Top:** draft name, originating session, number of selected phrases/chunks.  
**Content picker:** all candidate chunks with source quote, reason (new vocabulary / repeated error / useful professional expression), checkbox, edit/reject; avoids duplicates.  
**Asset controls:** Lesson; two audio assets; five Active 5 stages as a **single complete package** by default; optional Personal Error Deck.  
**Options:** conversation length (short/standard), number of chunks (8/12/15), register priority, IPA accent, preview output language.  
**CTA:** Generate draft.  
**Guardrails:** warn if fewer than the configured minimum of quality chunks; allow generation with reduced coverage only if appropriate.

### S06 — Generation Status
**States:** queued / generating lesson / generating cards / generating audio / validating / draft ready / partial failure.  
**Display:** independent asset progress, errors with retry; exit without losing draft. Avoid fake percent completion.  
**CTA:** Review draft when ready.  
**Do not claim generation is complete until server confirms each asset.**

### S07 — Material Review & Approval
**Tabs:** Overview; Lesson; Conversation audio; Shadowing audio; Active 1; Active 2; Active 3; Active 4; Active 5; Personal Errors (if on).  
**Actions:** preview real player, edit card prompt/answer/distractors/IPA, replace audio, regenerate this item, hide/delete draft item (no effect on past sessions), approve & save.  
**Quality badges:** not default decorations; only real issues like “Needs review” when validation flags.  
**Approval:** explicit ownership and visibility; private by default. After save, navigate to learning collection.

### S08 — Learning Collection / Lesson Detail
**Content:** source conversation link, curated model dialogue with speaker turns, sentence-by-sentence IPA toggles, vocabulary/chunk sections, play conversation audio, shadowing mode, Active 1–5 entry points, progress and review dates if available.  
**CTA:** Practice Active 1; review errors; resume next conversation.  
**If no practice tracking integration:** show only available progress; do not invent streaks, mastery, or scores.

## 9. UI content hierarchy and design direction
- Platform-native visual system: use Miwiz existing brand tokens; avoid cloning screenshots from another application.
- In conversation room, primary visual emphasis is conversational content. Corrections should be easy to discover but not overwhelm the viewport.
- Use distinct icon/label treatment for **Coach** and **Partner** rather than enormous panels with nested paragraphs.
- Per correction: 1) Natural version, 2) Why, 3) Three styles, 4) IPA, 5) replay/try again (only when supported).
- Avoid printing full IPA for every long sentence in the collapsed view; retain it in the expanded state to comply with Option B.
- Important language notes: semantic colors rather than only red/green to support accessibility.
- Minimum touch targets ~44×44 pt, scalable text, screen-reader labeling, dynamic keyboard resizing, smooth long-transcript rendering, and offline/reconnection states.

## 10. Data model (conceptual; adapt to actual Miwiz DB)
```text
ConversationSession
 id, owner_id, topic, language, input_mode, settings, status,
 started_at, ended_at, review_id, generated_collection_ids

ConversationTurn
 id, session_id, order, role(user/partner), original_text,
 transcript_text?, input_audio_ref?, reply_text?, created_at

Correction
 id, user_turn_id, corrected_text, is_error_free,
 errors[{span,type,reason_vi,correction}],
 variants[{register,text,ipa}], pronunciation_focus[],
 level_estimate?, coach_feedback_version

SessionReview
 id, session_id, strengths[], improvement_areas[],
 key_chunks[], key_patterns[], model_dialogue[], created_at

LearningCollectionDraft
 id, session_id, owner_id, title, curated_chunk_ids[],
 selected_asset_types[], generation_status, validation_issues[],
 revision, created_at

LearningAsset
 id, collection_id, type(lesson,conversation_audio,shadowing_audio,
 active_1..active_5,personal_error), canonical_miwiz_ref?, status,
 metadata, revision

Chunk
 id, source_turn_ids[], original, natural_expression, meaning_vi,
 ipa, register, difficulty, tags[], selected

PracticeResult (via existing Miwiz mechanism)
 id, owner_id, learning_asset_id, item_id, result, attempt_at
```

**Relationships & invariants:** session → turns; user turn → correction; session → review → 0..N collections; collection → distinct learning assets; chunk source lineage preserved; no leaking private discussion into public collection; stable IDs and versioning for regeneration.

## 11. API / integration contracts (logical, not concrete endpoint claims)
- Miwiz Auth/SSO: obtain user identity and permitted session scope; do not create a second password flow in miniapp.
- AI Conversation: session create, send turn, receive separately structured `coach_feedback` and `partner_reply`, end session.
- AI Review: generate/update post-session review and model dialogue.
- Content Generator: source chunks → lesson/decks/audio draft with job ID, per-asset state, validation results.
- Existing Active 5 Engine: accept mapped deck payloads only after confirming canonical schema, IDs and semantics.
- Miwiz Content Library: save collection and assets with private visibility and provenance.
- Media/TTS: synthesize dialogue and shadowing audio, return playable URLs or managed references.
- Learning Analytics: read practice outcomes to recommend review and future conversation prompts, with permissions.

**Backend concerns:** idempotent generate/retry, request correlation IDs, timeout/error handling, draft save, version conflicts, content moderation where required, transcript/recording consent, cancellation policy, deletions and retention, and cost/usage metering for AI/TTS.

## 12. States and edge cases
1. User sends only Vietnamese: coach provides English natural expression, full 3 registers and IPA; AI responds substantively in English.
2. User sends correct English: explicit affirmation, enhancements, 3 versions and IPA, no fictional grammatical “mistake.”
3. Long discussion: virtualized timeline, progressive loading, pinned current reply and accessible historical coach panels.
4. Ambiguous meaning: AI makes a transparent best-guess and notes alternative; should not silently change intent.
5. Voice recognition error: transcript editable; do not label ASR errors as language mistakes before correction.
6. No viable chunks: show why generation cannot create useful decks, allow manual selections/short lesson.
7. TTS/card/lesson partial failure: keep successful drafts, retry failed asset independently; approval must flag missing selected assets.
8. User exits during generation: job persists; return to draft/status, no duplicate generation on re-entry.
9. Re-generation after edits: preserve prior approved version, new version/draft, and practice records.
10. Network lost: retain typed input locally only as platform policy allows; do not report send success until ack.
11. Data privacy: session and generated contents private by default; explicit separate approval for broader publication.
12. Mixed devices: resume via user-owned session/collection if platform supports cross-device sync.

## 13. Acceptance criteria (UX signoff)
- AC01: Learner can start conversation on a self-chosen topic without a forced questionnaire.
- AC02: Learner can write Vietnamese, English, or mixed; AI continues in English.
- AC03: Each learner turn has correction panel with explanation (or explicit correct status), Formal/Neutral/Casual variants, and IPA accessible.
- AC04: AI supplies a substantive partner response not limited to questions.
- AC05: Topic and scroll/context survive corrections expanding/collapsing.
- AC06: End session gives strengths, areas to improve, chunks/IPA, and a source-faithful model dialogue.
- AC07: User can preview/select chunks and assets before generation.
- AC08: Generation status and partial failures are visible and recoverable.
- AC09: User can inspect and fix card content before approval.
- AC10: Approved collection links to 1 lesson, 2 audio assets, and all 5 Active 5 decks when selected and successfully generated.
- AC11: Content default visibility private; no automatic public publication.
- AC12: In Miwiz, saved assets open in existing learning experience with provenance to original session.
- AC13: No claims about pronunciation accuracy based solely on typed text.
- AC14: Active 5 stage mechanics align with the **verified** existing Miwiz Active 5 definition before handoff to Codex.

## 14. Deliverables for design phase
1. Mobile wireframe: S01 Home.
2. Mobile wireframe: S02 Setup.
3. High-fidelity mobile conversation: S03 including expanded/collapsed coach, mixed-language turn, correct-English turn, loading/voice states.
4. Review summary: S04.
5. Curation and asset selection: S05.
6. Generating/partial failure: S06.
7. Asset editor and approval: S07 (at least one screen for each audio/lesson/cards UI).
8. Saved lesson and Active 5 entry: S08.
9. Clickable prototype: S01 → S03 → S04 → S05 → S06 → S07 → S08.
10. Design tokens mapping to Miwiz, UI component/state inventory, responsive/a11y notes.

## 15. Decision log & implementation gates
**Locked from user:** Option B full detailed corrections, three registers and IPA; conversational AI with own opinions; post-session Active 5 learning content; embed as Miwiz miniapp; UI approval before Codex.

**Needs verification with real Miwiz implementation before code:**
- Actual definition and question types of Active 1–5; supported answer modes, audio, IPA, card-level metadata.
- Miniapp embedding mechanism (webview, route, iframe, SDK), auth and navigation contract.
- Existing lessons, TTS, audio hosting, asset-library and publishing APIs.
- Existing practice-result/progress interfaces.
- Theme tokens, typography and mobile safe areas.
- Privacy/data policies and whether user audio is stored or transcribed.

**Recommended signoff sequence:** (1) approve information architecture and user flow; (2) approve key wireframes and visual style; (3) confirm technical mapping and backend contracts; (4) produce Codex engineering spec and task backlog. No coding before UX signoff.

## 16. Suggested V1 screen priorities
**P0:** S03 Conversation, S04 Review, S05 Generate, S07 Approval, S08 Lesson/Deck entry.  
**P1:** S01 Library, S02 Setup, S06 Status.  
**P2:** Voice feedback depth, personalized error deck analytics, cross-session retrieval refinement.

---
**End of design baseline.**
