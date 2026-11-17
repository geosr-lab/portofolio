"""Uji tata letak di Chromium (Playwright), meniru tests/verifikasi_tata_letak.py di repo GeoSR.

Setiap halaman di docs/ pada lebar 375, 768, 1280, 1440 px, tema terang dan gelap:
tanpa gulir mendatar, tanpa elemen bersaudara yang saling menimpa > 2 px, tanpa elemen keluar dari kartu,
0 galat konsol, 0 permintaan lokal yang gagal, dan semua tautan lokal menunjuk berkas yang ada.

Jalankan dari akar repo:  python tests/verifikasi_tata_letak.py  [folder lain, mis. pratinjau privat]
"""
import functools
import http.server
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse, unquote

from playwright.sync_api import sync_playwright

AKAR = Path(__file__).resolve().parent.parent
DOCS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else AKAR / "docs"
LEBAR = (375, 768, 1280, 1440)

JS_CEK = r"""
() => {
  const salah = [];
  const de = document.documentElement;
  if (de.scrollWidth > de.clientWidth + 1) salah.push(`gulir mendatar ${de.scrollWidth} > ${de.clientWidth}`);
  const pilih = 'a, button, h1, h2, h3, p, li, dt, dd, .chip, .tombol, .kartu, figure, table';
  const tampak = (e) => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 1 && r.height > 1 && s.display !== 'none' && s.visibility !== 'hidden' && !e.closest('[hidden]')
      && (s.position === 'static' || s.position === 'relative'); };
  const nama = (e) => e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).trim().split(/\s+/).join('.') : '');
  for (const ind of document.querySelectorAll('body, body *')) {
    const anak = [...ind.children].filter(e => e.matches(pilih) && tampak(e));
    for (let i = 0; i < anak.length; i++) for (let j = i + 1; j < anak.length; j++) {
      const a = anak[i].getBoundingClientRect(), b = anak[j].getBoundingClientRect();
      const x = Math.min(a.right, b.right) - Math.max(a.left, b.left), y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (x > 2 && y > 2) salah.push(`timpa: ${nama(anak[i])} / ${nama(anak[j])}`);
    }
  }
  for (const k of document.querySelectorAll('.kartu, figure, .fakta div')) {
    if (!tampak(k)) continue;
    const r = k.getBoundingClientRect();
    for (const e of k.querySelectorAll('*')) {
      if (!tampak(e)) continue;
      const q = e.getBoundingClientRect();
      if (q.right > r.right + 1 || q.left < r.left - 1) salah.push(`keluar kartu: ${nama(e)} di ${nama(k)}`);
    }
  }
  return [...new Set(salah)];
}
"""


def main():
    halaman = sorted(p.relative_to(DOCS).as_posix() for p in DOCS.rglob("*.html"))
    pengendali = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS))
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), pengendali)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    dasar = f"http://127.0.0.1:{server.server_port}/"
    gagal = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for skema in ("light", "dark"):
            for lebar in LEBAR:
                ctx = browser.new_context(viewport={"width": lebar, "height": 900}, color_scheme=skema)
                for h in halaman:
                    pg = ctx.new_page()
                    galat = []
                    pg.on("console", lambda m: galat.append(m.text) if m.type == "error" else None)
                    pg.on("pageerror", lambda x: galat.append(str(x)))
                    pg.on("requestfailed", lambda r: galat.append("gagal muat " + r.url) if r.url.startswith(dasar) else None)
                    pg.on("response", lambda r: galat.append(f"{r.status} {r.url}") if r.url.startswith(dasar) and r.status >= 400 else None)
                    pg.goto(dasar + h, wait_until="load")
                    for s in pg.evaluate(JS_CEK) + galat:
                        gagal.append(f"{h} @{lebar} {skema}: {s}")
                    if skema == "light" and lebar == 1280:
                        for href in pg.eval_on_selector_all("a[href], img[src], video[src], video[poster]",
                                                            "es => es.map(e => e.href || e.src || e.poster)"):
                            u = urlparse(href)
                            if href.startswith(dasar) and not (DOCS / unquote(u.path.lstrip("/"))).exists():
                                gagal.append(f"{h}: tautan putus {href}")
                    pg.close()
                ctx.close()
        browser.close()
    server.shutdown()
    for g in gagal:
        print("GAGAL", g)
    print(f"{len(halaman)} halaman x {len(LEBAR)} lebar x 2 tema: {len(gagal)} masalah")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
