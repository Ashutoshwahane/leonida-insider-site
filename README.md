# Leonida Insider website

Independent GTA VI companion app website. Static HTML, CSS and JavaScript with local fonts and real app previews. No account system, payment handling or tracking scripts on this website.

## Preview

Run `python3 -m http.server 4173 --bind 127.0.0.1`, then visit http://127.0.0.1:4173. Source pages are intentionally noindex.

## Build and validate

```sh
python3 scripts/prepare-publish.py --origin https://leonida.ashutoshwahane.dev
python3 scripts/check-site.py
```

The build creates `dist/` with production canonical/social URLs, accurate structured data, a sitemap and crawlable robots.txt. The 404 stays noindex. GitHub Actions publishes only `dist/`.

## Editorial policy

Use primary sources and original commentary. Clearly label planned features and speculation. Never invent ratings, testimonials or verification claims. See the public About and editorial policy page.

## Independence

Not affiliated with or endorsed by Rockstar Games or Take-Two Interactive. References identify subjects discussed; their owners retain their rights.
