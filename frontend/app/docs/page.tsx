'use client';

import { useState } from 'react';

const SECTIONS = [
  {
    id: 'quick-start',
    title: 'Quick Start',
    content: `
## Getting Started

ContentForge helps you create consistent, high-quality content for your brand in minutes.

### 1. Create a Brand
Head to **Dashboard → Brands** and set up your first brand. Define your brand voice, industry, and target audience.

### 2. Generate Content
Visit **Dashboard → Generate** to create blog posts, social media captions, email newsletters, and Pinterest pins.

### 3. Publish & Export
Use **Dashboard → Content Library** to view everything you've generated and publish directly to Pinterest or WordPress.

### Demo Login
- **Email:** demo@contentforge.local  
- **Password:** demo123
    `,
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    content: `
## API Overview

The backend runs on FastAPI at <kbd>http://localhost:8000</kbd>.

### Authentication
- \`POST /auth/register\` — create a new account (returns JWT)
- \`POST /auth/login\` — log in (returns JWT)

Use the JWT as a Bearer token in the \`Authorization\` header on all protected routes.

### Content
- \`POST /content/generate\` — generate text content
- \`POST /content/generate-image\` — generate image via ComfyUI
- \`GET /content\` — list your content pieces

### Brands
- \`POST /brands\` — create a brand
- \`GET /brands\` — list your brands

### Billing
- \`POST /billing/checkout\` — create a Stripe Checkout session
- \`GET /billing/subscription\` — get current plan
- \`POST /billing/portal\` — open Customer Portal

### Referrals
- \`GET /referral/info\` — your referral code + stats
- \`POST /referral/track\` — validate a referral code

### Admin
- \`POST /admin/send-tips\` — trigger weekly tip emails (admin only)
- \`GET /admin/email-queue\` — view email log
    `,
  },
  {
    id: 'brand-voice',
    title: 'Brand Voice Guide',
    content: `
## What is Brand Voice?

Your brand voice is how your company sounds when it communicates. It’s the combination of tone, vocabulary, and personality that makes your content uniquely yours.

### Tips for a Strong Brand Voice

1. **Know Your Audience** — A B2B SaaS brand speaks differently than a lifestyle DTC brand. Tailor your voice to the people you want to reach.
2. **Be Consistent** — Use the same tone across blog posts, social captions, and emails. Consistency builds trust.
3. **Keep It Concise** — The best brand voices get to the point. Cut fluff.
4. **Inject Personality** — Humor, empathy, or authority can set you apart from competitors.

### Example Voices

| Brand | Voice Description |
|-------|-------------------|
| Acme Corp | *Professional, witty, and concise* |
| Bloom Beauty | *Warm, encouraging, and playful* |
| TechNova | *Authoritative, forward-thinking, no-nonsense* |

### Using Brand Voice in ContentForge
When you set a voice in **Dashboard → Brands**, ContentForge prepends it to every generation prompt. This ensures your AI-generated content stays on-brand every time.
    `,
  },
];

function Markdown({ text }: { text: string }) {
  // Simple markdown-like rendering: headings, bold, lists, code, links, tables
  const html = text
    .replace(/\n## (.*)/g, '\u003ch2 class=\'text-xl font-bold text-gray-900 mt-8 mb-3\'\u003e$1\u003c/h2\u003e')
    .replace(/\n### (.*)/g, '\u003ch3 class=\'text-lg font-semibold text-gray-800 mt-6 mb-2\'\u003e$1\u003c/h3\u003e')
    .replace(/\n\n/g, '\u003cbr\u003e')
    .replace(/\n- (.*)/g, '\u003cli\u003e$1\u003c/li\u003e')
    .replace(/\n\d+\. (.*)/g, '\u003cli\u003e$1\u003c/li\u003e')
    .replace(/\`([^\`]+)\`/g, '\u003ccode class=\'bg-gray-100 text-sm px-1 py-0.5 rounded\'\u003e$1\u003c/code\u003e')
    .replace(/\*\*([^\*]+)\*\*/g, '\u003cstrong\u003e$1\u003c/strong\u003e')
    .replace(/\n\|([^\n]+)\|/g, '\n<tr>$1</tr>')
    .replace(/\n<tr>\|[^:]+\|[^\n]*<\/tr>/g, '')
    .replace(/\n<tr>\|([^\n]+)\|<\/tr>/g, '\n<tr><td class=\'border px-3 py-2\'>$1</td></tr>')
    .replace(/\u003ckbd\u003e([^\u003c]+)\u003c\/kbd\u003e/g, '\u003ckbd class=\'bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono\'\u003e$1\u003c/kbd\u003e');

  return (
    <div
      className="prose prose-sm max-w-none text-gray-700"
      dangerouslySetInnerHTML={{ __html: '\u003cul class=\'list-disc pl-5\'\u003e' + html + '\u003c/ul\u003e' }}
    />
  );
}

export default function DocsPage() {
  const [active, setActive] = useState(SECTIONS[0].id);

  return (
    <div>
      <div className="md:hidden mb-6">
        <select
          value={active}
          onChange={(e) => setActive(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          {SECTIONS.map((s) => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>
      </div>

      {SECTIONS.map((s) => (
        <section
          key={s.id}
          id={s.id}
          className={`${active === s.id ? 'block' : 'hidden'}`}
        >
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{s.title}</h1>
          <Markdown text={s.content} />
        </section>
      ))}
    </div>
  );
}
