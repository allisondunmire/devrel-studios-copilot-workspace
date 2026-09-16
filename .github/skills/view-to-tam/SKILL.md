---
name: view-to-tam
description: >
  Use when the user wants to analyze YouTube video performance relative to a product's
  Total Addressable Market, including requests like "view to TAM", "TAM analysis", "how
  did this video do", "video performance", or "view ratio" for a developer-focused video.
  Identifies the product or technology from the video title and description, researches
  the TAM via web search, and calculates a view-to-TAM ratio with a performance rating.
---

# View-to-TAM Analysis

Evaluate how well a YouTube video reached its Total Addressable Market (TAM).

## Workflow

### Step 1: Identify the video

Fetch video metadata using the YouTube oEmbed endpoint:

```
https://www.youtube.com/oembed?url=<YOUTUBE_URL>&format=json
```

Extract the **title** and **author**. Then web search for the video's current **view count**.

### Step 2: Identify the primary product/technology

From the video title and description, determine the **primary product or technology** the video is about. Examples:
- "Build a Unity Game with GitHub Copilot" → **Unity**
- "What's new in .NET 9" → **.NET**
- "Azure Cosmos DB Conf 2024 Keynote" → **Azure Cosmos DB**
- "Getting started with Azure Functions" → **Azure Functions**

If the video covers multiple products, pick the **most niche/specific one** as the primary TAM — this gives the most meaningful ratio. Note the others as context.

If the video is about a broad topic (e.g., "AI", "Cloud", "DevOps") rather than a specific product, note that TAM estimation is less precise and flag it.

### Step 3: Research the TAM (dual audience)

Always calculate TAM for **both** audiences and present both. Let the user decide which lens matters.

#### 🏢 Business audience

Search the web for the product's enterprise customer base:

```
site:6sense.com "[Product Name]" market share customers
```

Extract the **number of companies** using the product from the 6sense results. Include the 6sense URL in your output so the user can verify.

Apply the Business TAM formula:

```
Business Users = Companies × 250 (median employees) × 7.5% (developer ratio)
```

This represents the enterprise/business audience — the users Microsoft monetizes through licenses, Azure consumption, and support contracts.

**If no 6sense data exists** (new or niche products):
- Flag that no 6sense data is available
- Offer proxy-based estimates:
  - GitHub stars/forks for open-source projects
  - Official Microsoft/vendor reported customer counts from earnings calls
- Clearly label these as proxies with wider confidence ranges

#### 🌍 Community audience

Search for the broader developer community using the product:

```
[Product Name] number of developers users worldwide [current year]
```

Use developer survey data (JetBrains State of Developer Ecosystem, Stack Overflow Developer Survey) and official reports to estimate the total developer population using the product. This includes hobbyists, students, open-source contributors, and indie developers — not just enterprise users.

**Important:** Do NOT conflate different products. VS Code and Visual Studio are separate products with separate user bases. .NET and C# are related but distinct. Use the specific product's data, not a bundled figure.

### Step 4: Calculate the View-to-TAM ratios

Calculate a ratio for each audience:

```
Business Ratio = Video Views ÷ Business Users × 100
Community Ratio = Video Views ÷ Community Users × 100
```

### Step 5: Rate the performance

| Rating | Ratio | Meaning |
|--------|-------|---------|
| 🔥 Exceptional | >10% | Viral within the ecosystem |
| ✅ Good | 3–10% | Solid reach for the audience |
| ⚠️ Underperforming | 1–3% | Below expectations |
| ❌ Poor | <1% | Not reaching the audience |

**Context factors to note:**
- Video age: Videos less than 7 days old may still be climbing. Flag this.
- Video type: Conference keynotes should aim higher than tutorials.
- Long-tail content: Developer tutorials often accumulate views over months/years.

### Step 6: Project future performance (if video is young)

If the video is less than 30 days old, include a projection table:

| Scenario | Views needed | Ratio | Rating |
|----------|-------------|-------|--------|
| Current | [actual] | X% | [rating] |
| Good | [3% × TAM] | 3% | ✅ |
| Exceptional | [10% × TAM] | 10% | 🔥 |

## Output Format

Always present results in this structure:

```
## 📊 View-to-TAM Analysis

**Video:** [Title]
**Channel:** [Author]
**Views:** [Count] ([age of video])
**Primary Product:** [Product name]

| Audience | TAM Source | Est. Users | Ratio | Rating |
|----------|-----------|------------|-------|--------|
| 🏢 Business | 6sense ([X] cos) | [Y] | [X%] | [rating] |
| 🌍 Community | Dev surveys ([source]) | [Z] | [X%] | [rating] |

[Projection table if video < 30 days old]

---

**📊 TAM Methodology Disclaimer**
*Business estimate: [X] companies using [Product] ([6sense link]) × median
company size of 250 employees × 7.5% developer ratio = ~[Y] estimated users.
Community estimate: [source data] for total developer population using [Product].
These are approximations — company size distribution, developer ratios, and
survey methodologies vary. Push back on any of these assumptions and I'll
recalculate.*
```

## Edge Cases

- **Multiple products in one video**: Use the most specific/niche product for TAM. Mention the broader ecosystem as context.
- **No 6sense data**: Flag it, use proxies (GitHub stars, official reports) for business audience, and widen the confidence range.
- **No community survey data**: Flag it and present business audience only.
- **Bundled product figures**: Never conflate separate products. VS Code ≠ Visual Studio. .NET ≠ C#. Use the specific product's data only.
- **Brand-new products**: Note that TAM is pre-maturity and will stabilize. Use the best available proxy.
- **Very old videos (2+ years)**: Views are likely at their ceiling. Rate as-is without projection.
- **Conferences/keynotes vs individual videos**: Note that conferences should aim for higher ratios due to concentrated marketing push.
- **View count unavailable**: Ask the user to provide the current view count from YouTube.
