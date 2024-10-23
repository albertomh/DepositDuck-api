# Frontend

## Bootstrap & 'speculum'

DepositDuck uses the `speculum` frontend toolkit. This is a distribution of Bootstrap 5
customised to use the project's palette which lives at [albertomh/speculum](https://github.com/albertomh/speculum).
`speculum` also includes ready-to-use minified versions of Bootstrap Icons, htmx and Alpine.js.

`speculum` static assets are hosted in a public Cloudflare R2 bucket with CORS enabled to
allow GET from `localhost:8000`.

## Jinja2

The [jinja2_fragments](https://pypi.org/project/jinja2-fragments/) package is used to render
blocks of HTML from Jinja2 templates ready to be used by htmx.

The `get_templates` dependable returns an instance of `AuthenticatedJinjaBlocks`. This class
enhances `Jinja2Blocks` (from `jinja2_fragments`) by using Pydantic to validate that a
`TemplateContext` has all required attributes before being used to render a `TemplateResponse`.

To see the context available to a page in the frontend, add `<pre>{% debug %}</pre>` to a
Jinja template when running locally and `settings.debug` is true.

## Naming conventions

Element IDs should be in `camelCase`. Classes (mostly from Boostrap) should be in `kebab-case`.

## JavaScript

Pages should be built in a HTML-first way, progressively enhanced with CSS and JavaScript.
Small scripts are defined in `depositduck/web/static/src/js/`. Run the `just build_js`
recipe to have `esbuild` bundle all files into `depositduck/web/static/dist/js/main.min.js`.
Namespace custom functionality under the `window.depositduck` object, eg. `window.depositduck.dashboard.welcome`
