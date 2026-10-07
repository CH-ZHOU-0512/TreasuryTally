"""Local decorative blockchain geometry, not transaction or verification evidence."""

from urllib.parse import quote

CHAIN_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100">
<defs>
  <linearGradient id="chain-light" x1="0" y1="0" x2="1" y2="1">
    <stop stop-color="#AFA88F" stop-opacity=".22"/>
    <stop offset="1" stop-color="#8B969F" stop-opacity=".04"/>
  </linearGradient>
  <linearGradient id="block-face" x1="0" y1="0" x2="0" y2="1">
    <stop stop-color="#555B5D" stop-opacity=".12"/>
    <stop offset="1" stop-color="#34383B" stop-opacity=".02"/>
  </linearGradient>
</defs>
<g fill="none" stroke="url(#chain-light)" stroke-width="1">
  <path d="M950 110 L1075 170 L1220 120 L1360 185 L1510 130"/>
  <path d="M1075 170 L1095 355 L1230 420 L1390 360 L1510 470"/>
  <path d="M1230 420 L1130 555 L1270 620 L1460 565"/>
  <path d="M1095 355 L925 440 L840 620 L950 785 L1125 835"/>
  <path d="M50 730 L210 675 L350 755 L440 910 L620 975"/>
  <path d="M210 675 L245 500 L385 430"/>
  <path stroke-dasharray="3 9" d="M950 110 L925 440 M1220 120 L1230 420 M1360 185 L1390 360"/>
</g>
<g fill="url(#block-face)" stroke="url(#chain-light)" stroke-width="1.2">
  <path d="M1110 190 l92 -48 92 48 -92 48z M1110 190 v104 l92 48 92 -48 V190 M1202 238 v104"/>
  <path d="M1310 455 l64 -34 64 34 -64 34z M1310 455 v72 l64 34 64 -34 V455 M1374 489 v72"/>
  <path d="M130 780 l55 -29 55 29 -55 29z M130 780 v64 l55 29 55 -29 V780 M185 809 v64"/>
</g>
<g fill="#B5AEA0" fill-opacity=".16">
  <circle cx="950" cy="110" r="3"/><circle cx="1075" cy="170" r="4"/>
  <circle cx="1220" cy="120" r="3"/><circle cx="1360" cy="185" r="3"/>
  <circle cx="1095" cy="355" r="3"/><circle cx="1230" cy="420" r="4"/>
  <circle cx="1390" cy="360" r="3"/><circle cx="1130" cy="555" r="3"/>
  <circle cx="1270" cy="620" r="3"/><circle cx="925" cy="440" r="3"/>
  <circle cx="840" cy="620" r="3"/><circle cx="950" cy="785" r="3"/>
  <circle cx="210" cy="675" r="4"/><circle cx="350" cy="755" r="3"/>
  <circle cx="245" cy="500" r="3"/><circle cx="440" cy="910" r="3"/>
</g>
</svg>"""


def chain_background_url() -> str:
    return 'url("data:image/svg+xml,' + quote(CHAIN_SVG, safe="") + '")'
