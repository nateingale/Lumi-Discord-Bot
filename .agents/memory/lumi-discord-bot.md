---
name: Lumi Discord bot constraints
description: User-stated safety and compatibility requirements for the Lumi Discord bot.
---

Preserve Lumi's established identity prompt, message triggers, typing indicator, message splitting, and 12-message in-memory history unless the user explicitly asks otherwise.

Read Supabase credentials only from `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. Never display, print, or log secret values. Do not make an authenticated OpenAI API request merely to test changes. Do not add unrelated features.

For long-term memory, keep `lumi`, `personal`, `server`, and `global` as separate scopes. Personal rows belong only to the exact Discord author; server rows belong only to the exact guild and may be written only from channels visible to the server's default role. DMs and private channels must not create server memories. Lumi/global rows must contain only information appropriate to their broader audience, and Discord IDs must come from the message context, never the model.

Short-term conversation history must be isolated by Discord user in both DMs and shared server channels while preserving Lumi's 12-message history.

For image vision, accept only validated, bounded Discord image attachments. Send their URLs only in the live OpenAI request; never retain attachment URLs or image bytes in short-term history or Supabase memory. Keep durable image-derived facts subject to the existing selective memory and scope rules.

**Why:** the user explicitly requires multi-user privacy without replacing Lumi's existing memory system; guild-wide retrieval has no per-channel permission boundary, and image attachments must not become a stored archive.

**How to apply:** Filter database rows by scope and exact identity before sending any content to OpenAI. Keep IDs out of prompts and model-controlled output. Keep image URLs/data out of stored history and memory. Verify with local mocks or dummy settings, preserve Lumi's existing behavior, and check that logs do not expose secret values.