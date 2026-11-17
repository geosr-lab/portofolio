"""Sajian data di halaman karya: grafik SVG (garis, batang), tabel, dan denah tiang.
Semua digambar saat situs dibangun (tanpa pustaka grafik); warna dari token CSS, jadi ikut tema terang/gelap.
Setiap grafik disertai tabel datanya di <details> supaya bisa dibaca pembaca layar dan disalin."""
import html
import math

e = html.escape


def angka(x, d=None):
    """Format Indonesia: desimal koma, ribuan titik."""
    if isinstance(x, str):
        return x
    if d is None:
        d = 0 if float(x).is_integer() else (2 if abs(x) < 1000 else 1)
    s = f"{x:,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def langkah_rapi(lo, hi, n=5):
    """Garis bantu sumbu dengan langkah 1, 2, 2,5, atau 5 × 10^k."""
    if hi == lo:
        hi = lo + 1
    kasar = (hi - lo) / n
    p = 10 ** math.floor(math.log10(kasar))
    langkah = min((m * p for m in (1, 2, 2.5, 5, 10) if m * p >= kasar), default=10 * p)
    a = math.floor(lo / langkah) * langkah
    b = math.ceil(hi / langkah) * langkah
    return [a + i * langkah for i in range(int(round((b - a) / langkah)) + 1)]


def tabel(t):
    kepala = "".join(f'<th scope="col">{e(str(k))}</th>' for k in t["kolom"])
    sorot = set(t.get("sorot_baris", []))
    badan = ""
    for i, b in enumerate(t["baris"]):
        sel = "".join((f'<th scope="row">{e(angka(c))}</th>' if j == 0 else f"<td>{e(angka(c))}</td>") for j, c in enumerate(b))
        badan += f'<tr{" class=sorot" if i in sorot else ""}>{sel}</tr>'
    judul = f"<caption>{e(t['judul'])}</caption>" if t.get("judul") else ""
    catatan = f'<p class="ket-tabel">{e(t["catatan"])}</p>' if t.get("catatan") else ""
    return f'<div class="tabel-gulir"><table class="data">{judul}<thead><tr>{kepala}</tr></thead><tbody>{badan}</tbody></table></div>{catatan}'


def _bingkai(g, isi, lebar, tinggi):
    legenda = ""
    if len(g.get("seri", [])) > 1:
        legenda = '<ul class="legenda">' + "".join(
            f'<li><span class="sw s{i}{" putus" if s.get("putus") else ""}"></span>{e(s["nama"])}</li>' for i, s in enumerate(g["seri"])) + "</ul>"
    return (f'<figure class="grafik"><figcaption class="judul-grafik">{e(g["judul"])}</figcaption>{legenda}'
            f'<div class="gulir-grafik" tabindex="0"><svg viewBox="0 0 {lebar} {tinggi}" role="img" aria-label="{e(g["judul"])}">{isi}</svg></div>'
            + (f'<p class="ket-tabel">{e(g["keterangan"])}</p>' if g.get("keterangan") else "")
            + f'<details><summary>Lihat data</summary>{tabel(g.get("tabel") or _tabel_otomatis(g))}</details></figure>')


def _tabel_otomatis(g):
    if "label" in g:  # batang
        return {"kolom": [""] + [s["nama"] for s in g["seri"]], "baris": [[lb] + [s["nilai"][i] for s in g["seri"]] for i, lb in enumerate(g["label"])]}
    return {"kolom": ["Seri", g["x"], g["y"]], "baris": [[s["nama"], x, y] for s in g["seri"] for x, y in s["titik"]]}


def garis(g):
    W, H, L, R, T, B = 640, 360, 62, 16, 14, 46
    xs = [p[0] for s in g["seri"] for p in s["titik"]]
    ys = [p[1] for s in g["seri"] for p in s["titik"]]
    gx = langkah_rapi(min(0, min(xs)) if g.get("x_nol", True) else min(xs), max(xs))
    gy = langkah_rapi(min(0, min(ys)) if g.get("y_nol", True) else min(ys), max(ys))
    X = lambda v: L + (v - gx[0]) / (gx[-1] - gx[0]) * (W - L - R)
    Y = lambda v: H - B - (v - gy[0]) / (gy[-1] - gy[0]) * (H - T - B)
    o = []
    for v in gy:
        o.append(f'<line class="kisi" x1="{L}" x2="{W-R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="lbl" x="{L-8}" y="{Y(v)+4:.1f}" text-anchor="end">{angka(v)}</text>')
    for v in gx:
        o.append(f'<line class="kisi" y1="{T}" y2="{H-B}" x1="{X(v):.1f}" x2="{X(v):.1f}"/><text class="lbl" x="{X(v):.1f}" y="{H-B+18}" text-anchor="middle">{angka(v)}</text>')
    o.append(f'<line class="sumbu" x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}"/><line class="sumbu" x1="{L}" x2="{L}" y1="{T}" y2="{H-B}"/>')
    o.append(f'<text class="lbl judul-sumbu" x="{(L+W-R)/2}" y="{H-6}" text-anchor="middle">{e(g["x"])}</text>')
    o.append(f'<text class="lbl judul-sumbu" transform="translate(14 {(T+H-B)/2}) rotate(-90)" text-anchor="middle">{e(g["y"])}</text>')
    for i, s in enumerate(g["seri"]):
        d = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in s["titik"])
        o.append(f'<polyline class="seri s{i}{" putus" if s.get("putus") else ""}" points="{d}"/>')
        if s.get("titik_tampak", len(s["titik"]) <= 30):
            for x, y in s["titik"]:
                o.append(f'<circle class="titik s{i}" cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.5"><title>{e(s["nama"])}: {angka(x)}; {angka(y)}</title></circle>')
    return _bingkai(g, "".join(o), W, H)


def batang(g):
    """Batang mendatar; satu atau beberapa seri per label."""
    label, seri = g["label"], g["seri"]
    tinggi_baris = 26 * len(seri) + 12
    W, L, R, T, B = 640, 168, 54, 8, 40
    H = T + B + tinggi_baris * len(label)
    semua = [v for s in seri for v in s["nilai"]]
    gx = langkah_rapi(min(0, min(semua)), max(semua))
    X = lambda v: L + (v - gx[0]) / (gx[-1] - gx[0]) * (W - L - R)
    o = []
    for v in gx:
        o.append(f'<line class="kisi" y1="{T}" y2="{H-B}" x1="{X(v):.1f}" x2="{X(v):.1f}"/><text class="lbl" x="{X(v):.1f}" y="{H-B+16}" text-anchor="middle">{angka(v)}</text>')
    sorot = set(g.get("sorot", []))
    for i, lb in enumerate(label):
        y0 = T + i * tinggi_baris + 6
        o.append(f'<text class="lbl{" tebal" if lb in sorot else ""}" x="{L-8}" y="{y0 + tinggi_baris/2:.1f}" text-anchor="end">{e(lb)}</text>')
        for j, s in enumerate(seri):
            v = s["nilai"][i]
            y = y0 + j * 26
            x0, x1 = X(min(0, v)), X(max(0, v))
            cls = f"bt s{j}" + (" sorot" if lb in sorot else "")
            o.append(f'<rect class="{cls}" x="{x0:.1f}" y="{y}" width="{max(x1-x0, 1):.1f}" height="20" rx="3"><title>{e(lb)}, {e(s["nama"])}: {angka(v)} {e(g.get("satuan", ""))}</title></rect>'
                     f'<text class="lbl nilai" x="{x1+5:.1f}" y="{y+15}">{angka(v)}</text>')
    o.append(f'<line class="sumbu" x1="{X(0):.1f}" x2="{X(0):.1f}" y1="{T}" y2="{H-B}"/>')
    o.append(f'<text class="lbl judul-sumbu" x="{(L+W-R)/2}" y="{H-4}" text-anchor="middle">{e(g["x"])}</text>')
    return _bingkai(g, "".join(o), W, H)


def denah(d):
    """Denah susunan tiang: daftar konfigurasi, masing-masing baris × kolom; tiang 'hilang' digambar putus,
    tiang 'pendek' berwarna lain, angka per tiang opsional (peta panas)."""
    kartu = []
    for k in d["konfigurasi"]:
        nb, nk = k["baris"], k["kolom"]
        s = 22
        W, H = nk * s + 28, nb * s + 28
        nilai = k.get("nilai")
        if nilai:
            datar = [v for r in nilai for v in r]
            lo, hi = min(datar), max(datar)
        o = [f'<rect class="cap" x="6" y="6" width="{W-12}" height="{H-12}" rx="3"/>']
        for r in range(nb):
            for c in range(nk):
                cx, cy = 14 + s / 2 + c * s, 14 + s / 2 + r * s
                kode = f"R{c+1}C{r+1}" if d.get("kode_rc") else ""
                kelas = "tiang"
                if kode in k.get("hilang", []):
                    kelas += " hilang"
                elif kode in k.get("pendek", []):
                    kelas += " pendek"
                isi = ""
                if nilai:
                    v = nilai[r][c]
                    t = (v - lo) / (hi - lo or 1)
                    isi = f' style="--t:{t:.2f}"'
                    kelas += " panas"
                    judul = f"<title>{kode} {angka(v)} {e(d.get('satuan',''))}</title>"
                else:
                    judul = f"<title>{kode}</title>" if kode else ""
                o.append(f'<circle class="{kelas}" cx="{cx}" cy="{cy}" r="{s*0.32 if not nilai else s*0.42:.1f}"{isi}>{judul}</circle>')
        if d.get("panah", True):
            o.append(f'<path class="panah" d="M2 {H/2} h8 m-3 -3 l3 3 l-3 3"/>')
        cap = f'<b>{e(k["kode"])}</b> {e(k.get("ket", ""))}'
        kartu.append(f'<figure class="denah-satu{" pilih" if k.get("pilih") else ""}"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(k["kode"])}">{"".join(o)}</svg><figcaption>{cap}</figcaption></figure>')
    leg = f'<p class="ket-tabel">{e(d["keterangan"])}</p>' if d.get("keterangan") else ""
    return f'<div class="denah{" besar" if d.get("besar") else ""}">' + "".join(kartu) + "</div>" + leg


def _self_cek():
    assert angka(1234.5) == "1.234,5" and angka(0.48, 3) == "0,480" and angka(12) == "12"
    assert langkah_rapi(0, 82.68)[-1] >= 82.68 and langkah_rapi(0, 82.68)[0] == 0
    assert "<svg" in garis({"judul": "t", "x": "x", "y": "y", "seri": [{"nama": "a", "titik": [[0, 0], [1, 2]]}], "tabel": {"kolom": ["x"], "baris": [[1]]}})


_self_cek()
