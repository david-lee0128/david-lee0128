// Draws assets/activity.svg: the last 16 weeks of contributions as an animated bar card,
// in the same One Dark colours as the streak card beside it. Reads the public contribution
// calendar, so it needs no token. Run by .github/workflows/activity-card.yml every day.
//
//   node scripts/activity-card.mjs <github user> <out.svg>
import { writeFileSync } from "node:fs";

const [user = "david-lee0128", out = "assets/activity.svg"] = process.argv.slice(2);
const WEEKS = 16;

const res = await fetch(`https://github.com/users/${user}/contributions`, { headers: { "User-Agent": "activity-card" } });
if (!res.ok) throw new Error(`contributions page: HTTP ${res.status}`);
const html = await res.text();

// each day is a <td id="contribution-day-component-<weekday>-<week>" data-date="YYYY-MM-DD">,
// and its count is in the <tool-tip for="<that id>">: "3 contributions on ..." or "No contributions on ..."
const counts = new Map();
for (const m of html.matchAll(/<tool-tip[^>]*\bfor="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)/g)) {
  const n = /^(\d[\d,]*) contribution/.exec(m[2].trim());
  counts.set(m[1], n ? Number(n[1].replace(/,/g, "")) : 0);
}
const weeks = [];
for (const m of html.matchAll(/<td[^>]*\bdata-date="(\d{4}-\d\d-\d\d)"[^>]*>/g)) {
  const id = /\bid="(contribution-day-component-(\d+)-(\d+))"/.exec(m[0]);
  if (!id) continue;
  const w = Number(id[3]);
  weeks[w] ??= { start: m[1], total: 0 };
  if (m[1] < weeks[w].start) weeks[w].start = m[1];
  weeks[w].total += counts.get(id[1]) ?? 0;
}
const recent = weeks.filter(Boolean).slice(-WEEKS);
if (recent.length < WEEKS) throw new Error(`only ${recent.length} weeks found; the page layout may have changed`);

const total = recent.reduce((s, w) => s + w.total, 0);
const now = recent.at(-1).total;
const best = Math.max(1, ...recent.map((w) => w.total));
const day = (iso) => new Date(iso + "T00:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });

// One Dark, as in the streak card
const gold = "#e4bf7a", green = "#98c379", rose = "#e06c75", bg = "#282c34", grid = "#3a3f4b";
// the streak card keeps its 495x195 shape, so in its 420x180 box it is 165 tall and 7.5 down; match it
const W = 400, H = 180, Y0 = 7.5, CH = 165, X0 = 24, X1 = 376, BASE = 140, TOP = 80;
// square-root heights, so quiet weeks still show next to a busy one (each bar keeps its exact count in a <title>)
const step = (X1 - X0) / WEEKS, bw = 13;

const bars = recent.map((w, i) => {
  const h = Math.max(2, (BASE - TOP) * Math.sqrt(w.total / best));
  const x = X0 + i * step + (step - bw) / 2;
  const last = i === WEEKS - 1;
  const t0 = (0.25 + i * 0.06).toFixed(2);
  // grows from the baseline: scale(1,0) to scale(1,1) around y=0, which the group puts on the baseline
  return `<g transform="translate(${x.toFixed(1)} ${BASE})"><rect y="${-h.toFixed(1)}" width="${bw}" height="${h.toFixed(1)}" rx="2.5" fill="${last ? green : "url(#bar)"}"${w.total ? "" : ' opacity="0.35"'}>`
    + `<title>${w.total} in the week of ${day(w.start)}</title>`
    + `<animateTransform attributeName="transform" type="scale" values="1 0;1 0;1 1.06;1 1" keyTimes="0;${(t0 / (Number(t0) + 0.9)).toFixed(3)};0.85;1" dur="${(Number(t0) + 0.9).toFixed(2)}s" fill="freeze"/></rect></g>`;
}).join("\n    ");

const lastX = X0 + (WEEKS - 1) * step + step / 2;
const lastY = BASE - Math.max(2, (BASE - TOP) * Math.sqrt(now / best));
const clip = recent.map((w, i) => {
  const h = Math.max(2, (BASE - TOP) * Math.sqrt(w.total / best));
  return `<rect x="${(X0 + i * step + (step - bw) / 2).toFixed(1)}" y="${(BASE - h).toFixed(1)}" width="${bw}" height="${h.toFixed(1)}" rx="2.5"/>`;
}).join("");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${total} contributions in the last ${WEEKS} weeks, ${now} this week">
  <style>
    .t { font-family: 'Segoe UI', Ubuntu, sans-serif; }
    .fade { opacity: 0; animation: in .8s ease forwards; }
    @keyframes in { to { opacity: 1; } }
  </style>
  <defs>
    <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="${rose}" stop-opacity="0.85"/><stop offset="1" stop-color="${gold}"/></linearGradient>
    <linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <clipPath id="bars">${clip}</clipPath>
  </defs>
  <rect y="${Y0}" width="${W}" height="${CH}" rx="4.5" fill="${bg}"/>

  <g class="t">
    <text class="fade" x="${X0}" y="44" fill="${gold}" font-size="28" font-weight="700">${total.toLocaleString("en-US")}</text>
    <text class="fade" x="${X0}" y="63" fill="${gold}" font-size="13">Contributions, last ${WEEKS} weeks</text>
    <text class="fade" x="${X1}" y="44" fill="${green}" font-size="22" font-weight="700" text-anchor="end">${now}</text>
    <text class="fade" x="${X1}" y="63" fill="${green}" font-size="13" text-anchor="end">This week</text>
  </g>

  <line x1="${X0}" y1="${BASE + 0.5}" x2="${X1}" y2="${BASE + 0.5}" stroke="${grid}"/>
  <g>
    ${bars}
  </g>

  <!-- a light that sweeps across the bars now and then -->
  <g clip-path="url(#bars)">
    <rect x="-60" y="${TOP - 4}" width="60" height="${BASE - TOP + 8}" fill="url(#shine)">
      <animate attributeName="x" values="${X0 - 60};${X1}" dur="1.6s" begin="2.2s;sweep.end+3.4s" id="sweep"/>
    </rect>
  </g>

  <!-- this week, pulsing -->
  <circle cx="${lastX.toFixed(1)}" cy="${(lastY - 9).toFixed(1)}" r="3" fill="${green}">
    <animate attributeName="opacity" values="1;0.35;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="${lastX.toFixed(1)}" cy="${(lastY - 9).toFixed(1)}" r="3" fill="none" stroke="${green}" stroke-width="1.5">
    <animate attributeName="r" values="3;10" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" dur="1.8s" repeatCount="indefinite"/>
  </circle>

  <g class="t" font-size="11" fill="${rose}">
    <text class="fade" x="${X0}" y="158">${day(recent[0].start)}</text>
    <text class="fade" x="${X1}" y="158" text-anchor="end">Now</text>
  </g>
</svg>
`;
writeFileSync(out, svg);
console.log(`wrote ${out}: ${total} in ${WEEKS} weeks, ${now} this week, best week ${best}`);
