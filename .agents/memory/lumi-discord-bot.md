---
name: Lumi Discord bot constraints
description: User-stated safety and compatibility requirements for the Lumi Discord bot.
---

Preserve Lumi's established identity prompt, message triggers, typing indicator, message splitting, and 12-message in-memory history unless the user explicitly asks otherwise.

Read Supabase credentials only from `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. Never display, print, or log secret values. Do not make an authenticated OpenAI API request merely to test changes. Do not add unrelated features.

**Why:** the user explicitly specified these boundaries while requesting persistent memory for Lumi.

**How to apply:** Treat these as acceptance criteria for future Discord bot work. Verify with local mocks or dummy settings, and check that logs do not expose secret values.