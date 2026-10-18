/**
 * Profile view counter for github.com/phoenixak, replacing komarev.com
 * (GitHub's image proxy kept getting refused by it). Started from komarev's count.
 *
 * GET /phoenixak.svg  → +1, returns an ink/vermilion badge
 * GET /phoenixak.json → current count, no increment
 */
const ID = "phoenixak";

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === `/${ID}.json`) {
      const row = await env.DB.prepare("SELECT n FROM counter WHERE id = ?").bind(ID).first();
      return Response.json({ views: row ? row.n : 0 }, { headers: { "Cache-Control": "no-store" } });
    }
    if (pathname !== `/${ID}.svg`) return new Response("Not found", { status: 404 });

    const row = await env.DB.prepare("UPDATE counter SET n = n + 1 WHERE id = ? RETURNING n").bind(ID).first();
    return new Response(badge("profile views", (row ? row.n : 0).toLocaleString("en-US")), {
      headers: {
        "Content-Type": "image/svg+xml; charset=utf-8",
        // GitHub's proxy must refetch on every view, or the number freezes
        "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate",
      },
    });
  },
};

// flat-square badge: ink label, vermilion value (Verdana 11px ≈ 6.6px per char, like shields.io)
function badge(label, value) {
  const w = (s) => Math.round(s.length * 6.6) + 12;
  const lw = w(label), vw = w(value), total = lw + vw;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${total}" height="20" role="img" aria-label="${label}: ${value}">
<title>${label}: ${value}</title>
<rect width="${lw}" height="20" fill="#141310"/><rect x="${lw}" width="${vw}" height="20" fill="#C2341B"/>
<g fill="#F4F1EA" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">
<text x="${lw / 2}" y="14">${label}</text><text x="${lw + vw / 2}" y="14">${value}</text>
</g></svg>`;
}
