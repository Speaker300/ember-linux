# Ember Linux — Colour System

The palette is built around a single warm signal colour on a cool, near-black
base. Warm tones are reserved for focus, selection and the mark; everything
else stays quiet so the desktop does not look like a theme demo.

| Token | Hex | Use |
|---|---|---|
| `ink` | `#14171C` | Window and desktop base |
| `basalt` | `#1B2027` | Panels, cards, sidebar |
| `graphite` | `#262C36` | Borders, inactive controls |
| `ash` | `#A6AEBB` | Secondary text, disabled labels |
| `frost` | `#F4F6F8` | Primary text on dark surfaces |
| `ember` | `#F26A3D` | Primary accent, focus, selection |
| `ember_deep` | `#D8432A` | Pressed states, gradient ends |
| `amber` | `#FFB35C` | Hover highlight, secondary accent |
| `sand` | `#FFD9A0` | Warm highlight, logo core |
| `teal` | `#3FA796` | Cool counterpoint, informational links |
| `success` | `#4CAF6E` | Success states |
| `warning` | `#E0A526` | Warnings |
| `danger` | `#E5484D` | Errors and destructive actions |

## Rules

- Use **one** accent per screen. If ember is the focus colour, do not also use
  teal for buttons.
- Text is `frost` on `ink`/`basalt`, never pure white.
- Body copy uses `ash`; only headings and primary labels use `frost`.
- Orange text on dark is allowed at 14 px and above. For smaller text use
  `amber` or `frost`.
- The mark may be rendered in one colour (`frost` or `ink`) when colour
  reproduction is limited. Do not recolour individual facets.

## Contrast (WCAG 2.1)

- `frost` on `ink`: 16.6:1 (AAA)
- `ash` on `ink`: 8.0:1 (AAA)
- `ink` on `ember`: 5.9:1 (AA, large text AAA)
- `ember` on `ink`: 5.9:1 (AA)

## Colour files

- `palette.json` — machine-readable tokens.
- `palette.gpl` — GIMP/Inkscape palette.
- `palette.css` — CSS custom properties for web assets.
