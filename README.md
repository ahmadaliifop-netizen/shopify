# SANAYA — Health and Beauty

A premium, editorial Shopify Online Store 2.0 theme built for the SANAYA brand: quiet, warm, teal-on-cream, in the spirit of gethywell.com.

## What's included

- **Design system** (`assets/theme.css`): SANAYA color tokens (teal `#2D515F` / cream `#F7F4ED`), Fraunces (serif headings) + Inter (sans body/UI), generous spacing scale, hairline-based components, subtle scroll-reveal and hover motion.
- **Header**: sticky, shrinking on scroll, mega menu (desktop) + full-height drawer (mobile), cart/account/search icons.
- **Homepage** (`templates/index.json`): hero, value strip, featured categories, bestsellers rail, brand story, new arrivals grid, "build your ritual" editorial feature, testimonials, journal teaser, newsletter.
- **Collection page**: filter drawer, sort, responsive product grid, pagination.
- **Product page**: sticky gallery with thumbnails, variant swatches (variant-aware price/availability via JS), quantity stepper, accordions (Details / Ingredients / How to use / Shipping), "Pairs well with" rail, mobile sticky add-to-cart bar.
- **Cart**: AJAX slide-out drawer with free-shipping progress bar, plus a full `/cart` page fallback.
- **About, Contact, 404, Search, Blog/Article** templates, all on-brand.
- Colors, fonts, logo, cart type and free-shipping threshold are all editable in **Theme settings** (Shopify theme editor) — no code changes needed for basic re-tuning.

## Install

1. Zip this repository's contents (not the repo folder itself — `assets/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/` should be at the zip root).
2. In Shopify admin → Online Store → Themes → **Add theme** → **Upload zip file**.
3. Publish, or preview and customize first via the theme editor.

## Content still needed from the merchant

- Upload the SANAYA logo (teal + cream/inverse versions) and favicon under **Theme settings → Logo**.
- Upload real product/lifestyle photography — every image slot gracefully falls back to a placeholder until then.
- Create the `main-menu` navigation (Shop / Skincare / Beauty / Wellness / About / Journal) in **Online Store → Navigation**; nest links under "Shop" for the mega menu.
- Create collections with handles matching the homepage preset links (`skincare`, `beauty`, `wellness`, `all`), and a "Bestsellers" collection for the bestsellers rail.
- Create `/pages/about` and `/pages/contact` and assign the **about** / **contact** alternate templates.
