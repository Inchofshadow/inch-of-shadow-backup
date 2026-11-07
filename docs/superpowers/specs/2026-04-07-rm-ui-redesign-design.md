# Release Manager UI Redesign -- Design Spec

## Goal

Redesign the Release Manager web UI from its current glass-morphism dark theme into a sleek, modern dashboard aesthetic. Improve visual hierarchy, navigation, and usability on the three most complex pages (Release Detail, Engagement, Promotion) while applying a strict design system across all pages.

## Approach

Custom CSS redesign with a CSS variables design token system. No new dependencies. No framework. Modularize the existing 6400-line `style.css` into multiple focused files.

---

## 1. Design System (Foundation)

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-base` | `#060608` | Sidebar, deepest background |
| `--bg-raised` | `#0c0c10` | Content area background |
| `--bg-surface` | `#121218` | Cards, panels |
| `--bg-surface-hover` | `#1a1a22` | Hover states on surfaces |
| `--accent` | `#c9a84c` | Primary accent (champagne gold) |
| `--accent-hover` | `#e8d48b` | Accent hover/active state |
| `--text-primary` | `#ffffff` | Headings, important text |
| `--text-secondary` | `#a0a0b0` | Body text |
| `--text-muted` | `#606070` | Labels, captions, inactive |
| `--border` | `rgba(255,255,255,0.06)` | Subtle dividers |
| `--border-strong` | `rgba(255,255,255,0.12)` | Emphasized borders |
| `--success` | `#4a7c59` | Done, live, positive |
| `--warning` | `#b8860b` | Upcoming deadlines, caution |
| `--error` | `#8b3a3a` | Overdue, rejected, destructive |
| `--info` | `#5a6e8a` | Neutral informational |

### Typography

- **Headings:** Space Grotesk, letter-spacing: -0.02em
- **Body:** Inter, line-height: 1.6
- **Scale:** 12 / 13 / 14 / 16 / 20 / 24 / 32px (tokens: `--text-xs` through `--text-3xl`)
- No arbitrary font sizes outside this scale

### Spacing

- **Base unit:** 4px
- **Scale:** 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64px (tokens: `--space-1` through `--space-8`)
- All margins, paddings, gaps use these tokens only

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `4px` | Badges, chips, small elements |
| `--radius-md` | `8px` | Cards, inputs, buttons |
| `--radius-lg` | `12px` | Containers, modals, panels |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(0,0,8,0.4)` | Subtle card lift |
| `--shadow-md` | `0 4px 12px rgba(0,0,8,0.5)` | Elevated panels |
| `--shadow-lg` | `0 8px 24px rgba(0,0,8,0.6)` | Modals, overlays |

All shadows use dark blue-black tint, not pure black.

### Effects

- Glass-morphism used sparingly: sidebar and modals only
- Remove ambient background blobs -- replace with solid `--bg-raised` or subtle radial gradient
- Hover animations: max 2px translateY, 150ms duration
- Transition default: `150ms ease`

---

## 2. Layout & Navigation

### Sidebar (persistent left)

- **Width:** 240px expanded, 64px collapsed (icon-only)
- **Background:** `--bg-base` with subtle right border (`--border`)
- **Top:** Inch of Shadow wordmark/logo
- **Nav groups** with small uppercase section labels (`--text-muted`, 12px):
  - **Releases:** Dashboard
  - **Tools:** Artwork Resizer, Video Resizer, SEO Copy
  - **Outreach:** Engagement, Promotion
  - **Analytics:** Stats Dashboard
  - **Bottom:** Settings (theme/palette)
- **Active state:** `--bg-surface` background + `--accent` left border (3px)
- **Icons:** Simple line-style icons for each nav item
- **Collapsed mode:** Icons only, tooltip on hover
- **Collapse trigger:** Toggle button at bottom of sidebar

### Top Bar (contextual)

- **Height:** 48px
- **Position:** Top of content area (not full-width, sidebar-adjacent)
- **Left side:** Breadcrumb trail (page hierarchy)
- **Right side:** Active release indicator -- small artwork thumbnail (32px) + release title. Shown when a release context is set. Clickable to go to release detail.
- **Styling:** Minimal, `--bg-raised` background, bottom border (`--border`)

### Content Area

- **Width:** Remaining space after sidebar
- **Max-width:** 1100px, centered within content zone
- **Padding:** 32px top, 48px horizontal
- **Background:** `--bg-raised`

### Mobile (<768px)

- Sidebar becomes overlay drawer, triggered by hamburger in top bar
- Content goes full-width
- Top bar simplified (breadcrumb + hamburger)

---

## 3. Release Detail Page

### Hero (always visible, top)

- **Layout:** Artwork (200px square, `--radius-md`) left, info right
- **Info block:**
  - Release title (`--text-3xl`, Space Grotesk)
  - Type badge (Single/EP/Album)
  - Genre tags (pill chips)
  - Release date + countdown text ("12 days away" / "Released 3 weeks ago")
  - Distribution status badge (draft/submitted/approved/live/rejected)
- **Below info:** Full-width progress bar (prominent, 8px height, accent gradient)
- **Quick actions row:** Edit, Validate, Export Metadata -- compact buttons aligned right

### Tab Bar (sticky, below hero)

Tabs:
1. **Overview** -- metadata, description, tracks list, links
2. **Calendar** -- release calendar grid
3. **Checklist** -- all checklist categories with per-category progress
4. **Distribution** -- distributor info, UPC, status, dates, notes

- Tab bar sticks below hero on scroll
- Active tab: accent underline (3px), bold text
- Inactive tabs: `--text-muted`

### Overview Tab

- **Metadata section:** Artist, copyright, catalog number in a clean 2-column grid
- **Description:** Full-width text block
- **Tracks table:**
  - Columns: #, Title, BPM, Key, Duration, Genre
  - Compact rows with hover highlight
  - Inline edit button per row (pencil icon, right-aligned)
  - "Add Track" button at bottom
- **Links section:** External links displayed as icon + URL rows

### Calendar Tab

- Full-focus calendar grid (same data as current)
- More visual space since it's not competing with other sections
- Task pills color-coded by category

### Checklist Tab

- **Category cards** (not collapsible sections):
  - Each category is a card showing: category name, mini progress bar, completion count ("4/7")
  - Click a category card to expand and show its task list inline
  - Tasks: checkbox + label, completed tasks muted (lower opacity), not strikethrough

### Distribution Tab

- Clean form-like layout: status, distributor, UPC, Symphonic ID, dates, notes
- Status shown as a colored badge
- Notes displayed as a text block below the fields

---

## 4. Engagement Page

### Top Area

- **Stats cards row:** 3 cards side by side:
  - Today's progress ("3/10" with circular or linear progress indicator)
  - Total active follows (number)
  - Streak count (consecutive days)
- **Release selector:** Compact dropdown, inline with stats row (right-aligned)

### Platform Tabs

- Horizontal tab bar below stats: **Instagram** / **TikTok** / **YouTube**
- Each tab label includes its count: "IG: 3/10"
- Active tab: accent underline
- Switching tabs loads that platform's contact queue

### Contact Cards

- **Layout:** Card-based, generous padding (`--space-4` minimum)
- **Left:** Avatar placeholder -- circle with first-letter initial, background color by category
- **Center:**
  - Name (16px, `--text-primary`, prominent)
  - Category badge
  - Genre tags (small pills)
  - Location (`--text-muted`)
  - Last engaged date (`--text-muted`, relative: "3 days ago")
- **Right:** Action buttons -- "Done" (accent) and "Skip" (secondary), minimum 36px height
- **Bottom:** Collapsible notes/context area (click to expand)
- **Transitions:** Completed cards fade + slide out smoothly

### Progress Feel

- Progress bar at top fills as contacts are completed
- Count updates live
- Empty state when done: "All done for today" -- clean, satisfying

### Filters

- Compact row below platform tabs: category dropdown + search input
- Simple, not multi-select -- complex filtering is Promotion's job

---

## 5. Promotion Page

### Campaign Stats

- **Metric cards** (not a cramped bar): 5 cards in a row
  - Targets, Sent, Replied, Played, Rejected
  - Each card: large number (`--text-xl`), label below (`--text-muted`), color-coded
- **Progress bar** below cards: full-width, accent fill, percentage label

### Target List

- **Row styling:** Each target is a mini-card (subtle `--bg-surface` background, `--radius-md`, padding `--space-3` vertical)
- **Left:** Name (`--text-primary`, 16px), category badge, label boss tag
- **Center:** Email/DM badge (clearly sized), genre tags
- **Right:** Status dropdown (larger), notes icon, remove button
- **All interactive elements:** Minimum 36px touch target
- **Row height:** Generous -- no cramped feeling

### Add Targets (slide-in panel)

- Triggered by "Add Targets" button
- **Slide-in panel** from right side, ~400px wide, overlay with backdrop
- **Panel contents:**
  - Search bar at top (sticky)
  - Filter row below: category, genre multi-select, location multi-select, email-only toggle
  - Contact list: checkbox + name + category badge + email/DM badge
  - Scroll-to-load (no pagination buttons)
  - "Add Selected" button at bottom (sticky)
- **Close:** X button or click backdrop

### Bulk Actions

- When targets are checked: floating action bar at bottom of viewport
- Bar content: "[N] selected -- Change Status / Remove"
- Styled as elevated bar with `--shadow-lg`

---

## 6. Other Pages (Design System Application)

These pages get no structural changes -- only the new design tokens applied.

### Dashboard

- Release card grid inherits new spacing, radius, shadows, typography
- Sidebar replaces top nav
- Remove ambient blob background
- Slightly larger cards for breathing room

### Artwork Resizer & Video Resizer

- New design tokens applied to all form elements, buttons, checkboxes
- Focal point grid and platform groups get better sizing
- Upload zone gets updated border/background styling

### SEO Copy Generator

- Design tokens applied
- Result cards inherit new card styling

### Stats Dashboard

- Metric cards inherit new card styling (consistent with Promotion stats cards)
- Tab navigation uses same tab style as Release Detail
- Chart.js colors updated to match new palette

### Palette/Theme

- Moves to a settings section accessible from sidebar bottom
- Updated to reflect the new token system

---

## 7. CSS Architecture

### File Structure

Split `style.css` (6400 lines) into modular files:

```
release_manager/static/
  css/
    tokens.css        -- all CSS custom properties (colors, spacing, type, radius, shadows)
    reset.css         -- minimal reset/normalize
    layout.css        -- sidebar, top bar, content area, grid system
    components.css    -- buttons, badges, cards, inputs, dropdowns, modals, tabs, progress bars
    pages/
      dashboard.css
      release-detail.css
      engagement.css
      promotion.css
      artwork-resizer.css
      video-resizer.css
      seo-copy.css
      stats.css
      settings.css
    utilities.css     -- spacing helpers, text alignment, visibility, flex shortcuts
```

- `base.html` imports all files via `<link>` tags (or a single concatenated file for production)
- Every value references a token -- no raw hex colors, pixel values, or magic numbers in page CSS

### Migration Strategy

- Build new CSS files alongside existing `style.css`
- Switch templates to new CSS once complete
- Delete old `style.css` after migration verified

---

## 8. JavaScript Changes

### Minimal JS Changes

- **New:** Sidebar collapse/expand toggle
- **New:** Tab switching logic (Release Detail tabs, Engagement platform tabs)
- **New:** Slide-in panel open/close (Promotion add targets)
- **New:** Floating bulk action bar show/hide
- **Updated:** Remove blob animation code
- **Updated:** Toast positioning adjusted for sidebar layout

No JS framework. All new interactions are vanilla JS event handlers, consistent with existing `app.js` patterns. New code can be added to `app.js` or split into page-specific files if `app.js` grows unwieldy.

---

## 9. What Is NOT Changing

- Flask backend routes and logic -- no Python changes
- Data models (JSON files)
- Existing functionality (checklist toggle, validation, SEO generation, etc.)
- Chart.js for stats (only color updates)
- Fonts (Space Grotesk, Inter -- already locally hosted)
- Accessibility features (aria labels, keyboard nav, skip link)
