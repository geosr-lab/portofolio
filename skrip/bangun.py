"""Bangun situs portofolio dari konten/karya.json.

  python skrip/bangun.py            -> docs/ (yang terbit; hanya status "publik", media "privat" dilewati)
  python skrip/bangun.py --privat   -> ../99 Arsip/pratinjau-privat/ (semua karya, hanya untuk dilihat di laptop)

Berkas media diambil dari ../02 Siap Terbit/publik/<id>/ (atau privat/<id>/ untuk pratinjau privat).
"""
import html
import json
import shutil
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
SIAP = AKAR.parent / "02 Siap Terbit"
PRIVAT = "--privat" in sys.argv
KELUAR = (AKAR.parent / "99 Arsip" / "pratinjau-privat") if PRIVAT else AKAR / "docs"
DATA = json.loads((AKAR / "konten" / "karya.json").read_text(encoding="utf-8"))
if PRIVAT:  # karya privat disimpan di luar repo supaya tidak ikut ter-commit
    DATA["karya"] += json.loads((SIAP / "privat" / "karya-privat.json").read_text(encoding="utf-8"))["karya"]
P = DATA["profil"]
SITUS = "https://geosr-lab.github.io/portofolio/"
e = html.escape


def tampil(x):
    return PRIVAT or x.get("status", "publik") == "publik"


def media_tampil(m):
    return PRIVAT or not m.get("privat")


KARYA = [k for k in DATA["karya"] if tampil(k)]


def cari_berkas(kid, nama):
    for sub in (["publik", "privat"] if PRIVAT else ["publik"]):
        f = SIAP / sub / kid / nama
        if f.exists():
            return f
    raise SystemExit(f"Berkas tidak ada: {kid}/{nama} (cek 02 Siap Terbit)")


def salin(kid, nama):
    tujuan = KELUAR / "berkas" / kid / nama
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cari_berkas(kid, nama), tujuan)
    return f"berkas/{kid}/{nama}"


def label_privat(x):
    return ' <span class="lencana privat">privat</span>' if PRIVAT and (x.get("status") == "privat" or x.get("privat")) else ""


def halaman(jalur, judul, isi, deskripsi=""):
    awalan = "../" * jalur.count("/")
    pita = ('<div class="pita-privat" role="note">Pratinjau privat: berisi karya yang belum boleh terbit. '
            'Jangan diunggah.</div>\n') if PRIVAT else ""
    kunjungan = "" if PRIVAT else (f'\n  <script src="{awalan}assets/kunjungan.js" data-goatcounter="geosr-lab" '
                                   'data-situs="geosr-lab.github.io" defer></script>')
    aktif = lambda s: ' aria-current="page"' if jalur.startswith(s) else ""
    teks = f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(judul)}</title>
  <meta name="description" content="{e(deskripsi or P['ringkas'])}">
  {'<meta name="robots" content="noindex">' if PRIVAT else f'<link rel="canonical" href="{SITUS}{jalur.removesuffix("index.html")}">'}
  <link rel="icon" href="{awalan}assets/ikon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{awalan}assets/gaya.css">
  <script src="{awalan}assets/tema.js"></script>
  <script src="{awalan}assets/portofolio.js" defer></script>{kunjungan}
</head>
<body>
{pita}<header class="kepala">
  <div class="wadah kepala-isi">
    <a class="merek" href="{awalan}index.html">{e(P['nama'])}<span>portofolio</span></a>
    <nav aria-label="Menu utama">
      <a href="{awalan}karya/index.html"{aktif('karya')}>Karya</a>
      <a href="{awalan}cv/index.html"{aktif('cv')}>CV</a>
      <a href="{e(P['geosr'])}">Alat GeoSR</a>
      <button class="tema-tombol" type="button" aria-label="Ganti tema (otomatis, terang, gelap)">Tema: <span>otomatis</span></button>
    </nav>
  </div>
</header>
<main id="isi" class="wadah">
{isi}
</main>
<footer class="kaki">
  <div class="wadah">
    <p>{e(P['nama'])}. Bagian dari <a href="{e(P['geosr'])}">GeoSR</a>. Kontak lewat GitHub <a href="https://github.com/{e(P['github'])}">@{e(P['github'])}</a>.</p>
    <p><a href="{awalan}kredit/index.html">Kredit dan data kunjungan</a></p>
  </div>
</footer>
</body>
</html>
"""
    f = KELUAR / jalur
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(teks, encoding="utf-8")


def kartu(k, awalan):
    jenis = " ".join(f'<span class="chip">{e(j)}</span>' for j in k["jenis"])
    return (f'<a class="kartu karya" href="{awalan}karya/{k["id"]}/index.html" data-jenis="{e("|".join(k["jenis"]))}">\n'
            f'  <span class="tahun">{k["tahun"]}</span>\n'
            f'  <h3>{e(k["judul"])}{label_privat(k)}</h3>\n'
            f'  <p class="acara">{e(k["acara"])}</p>\n'
            f'  <p>{e(k["ringkas"])}</p>\n'
            f'  <p class="hasil">{e(k["hasil_singkat"])}</p>\n'
            f'  <p class="chips">{jenis}</p>\n</a>')


def beranda():
    unggul = [k for k in KARYA if k.get("unggulan")][:4]
    isi = f"""<section class="hero">
  <h1>{e(P['nama'])}</h1>
  <p class="lead">{e(P['ringkas'])}</p>
  <p class="aksi"><a class="tombol utama" href="karya/index.html">Lihat semua karya</a>
  <a class="tombol" href="cv/index.html">CV (bisa dicetak ke PDF)</a>
  <a class="tombol" href="https://github.com/{e(P['github'])}">Kontak lewat GitHub</a></p>
</section>
<section>
  <h2>Karya unggulan</h2>
  <div class="kisi">
{chr(10).join(kartu(k, '') for k in unggul)}
  </div>
</section>"""
    halaman("index.html", f"{P['nama']}: portofolio teknik sipil", isi)


def galeri():
    ada = [j for j in DATA["jenis"] if any(j in k["jenis"] for k in KARYA)]
    tombol = "".join(f'<button type="button" class="saring" data-saring="{e(j)}" aria-pressed="false">{e(j)}</button>' for j in ada)
    isi = f"""<h1>Karya</h1>
<p class="lead">Saring menurut jenis karya. Setiap kartu membuka halaman karya dengan ringkasan, peran, perangkat lunak, dan gambar.</p>
<div class="saringan" role="group" aria-label="Saring jenis karya">
  <button type="button" class="saring" data-saring="" aria-pressed="true">Semua</button>{tombol}
</div>
<p class="jumlah" aria-live="polite"></p>
<div class="kisi">
{chr(10).join(kartu(k, '../') for k in sorted(KARYA, key=lambda k: -k['tahun']))}
</div>"""
    halaman("karya/index.html", f"Karya: {P['nama']}", isi)


def media_html(k, m, awalan):
    src = awalan + salin(k["id"], m["berkas"])
    ket = f'<figcaption>{e(m["keterangan"])}{label_privat(m)}</figcaption>'
    if m["berkas"].endswith(".mp4"):
        poster = f' poster="{awalan + salin(k["id"], m["poster"])}"' if m.get("poster") else ""
        return f'<figure><video controls preload="none" playsinline{poster} src="{src}"></video>{ket}</figure>'
    return f'<figure><a href="{src}"><img src="{src}" alt="{e(m["keterangan"])}" loading="lazy"></a>{ket}</figure>'


def halaman_karya(k):
    a = "../../"
    blok = []
    if k.get("masalah"):
        blok.append(f"<h2>Masalah</h2>\n<p>{e(k['masalah'])}</p>")
    if k.get("langkah"):
        blok.append("<h2>Yang dikerjakan</h2>\n<ul>" + "".join(f"<li>{e(x)}</li>" for x in k["langkah"]) + "</ul>")
    if k.get("angka"):
        baris = "".join(f'<tr><th scope="row">{e(x["label"])}</th><td>{e(x["nilai"])}</td></tr>' for x in k["angka"])
        blok.append(f'<h2>Hasil</h2>\n<div class="tabel-gulir"><table class="angka"><tbody>{baris}</tbody></table></div>')
    media = [m for m in k.get("media", []) if media_tampil(m)]
    if media:
        blok.append('<h2>Gambar dan video</h2>\n<div class="galeri">' + "".join(media_html(k, m, a) for m in media) + "</div>")
    unduh = [u for u in k.get("unduhan", []) if media_tampil(u)]
    tautan = k.get("tautan", [])
    if unduh or tautan:
        t = [f'<a class="tombol" href="{a + salin(k["id"], u["berkas"])}" download>{e(u["label"])}</a>{label_privat(u)}' for u in unduh]
        t += [f'<a class="tombol" href="{e(x["url"])}">{e(x["label"])}</a>' for x in tautan]
        blok.append('<h2>Berkas dan tautan</h2>\n<p class="aksi">' + " ".join(t) + "</p>")
    if k.get("catatan"):
        blok.append(f'<p class="catatan">{e(k["catatan"])}</p>')
    sw = ", ".join(k.get("perangkat_lunak", []))
    isi = f"""<p class="remah"><a href="../index.html">Karya</a></p>
<h1>{e(k['judul'])}{label_privat(k)}</h1>
<p class="lead">{e(k['ringkas'])}</p>
<dl class="fakta">
  <div><dt>Acara atau tempat</dt><dd>{e(k['acara'])}</dd></div>
  <div><dt>Tahun</dt><dd>{k['tahun']}</dd></div>
  <div><dt>Peran saya</dt><dd>{e(k['peran'])}</dd></div>
  <div><dt>Hasil</dt><dd>{e(k['hasil_singkat'])}</dd></div>
  {f'<div><dt>Perangkat lunak</dt><dd>{e(sw)}</dd></div>' if sw else ''}
  <div><dt>Jenis</dt><dd>{e(', '.join(k['jenis']))}</dd></div>
</dl>
{chr(10).join(blok)}"""
    halaman(f"karya/{k['id']}/index.html", f"{k['judul']}: {P['nama']}", isi, k["ringkas"])


def cv():
    ids = {k["id"] for k in KARYA}
    def butir(x):
        tautan = f' <a href="../karya/{x["karya"]}/index.html">Lihat karya</a>' if x.get("karya") in ids else ""
        return (f'<li><h3>{e(x["judul"])}</h3><p class="acara">{e(x["tempat"])}, {e(x["waktu"])}</p>'
                + (f'<p>{e(x["keterangan"])}{tautan}</p>' if x.get("keterangan") else "") + "</li>")
    sw = "".join(f'<tr><th scope="row">{e(s["tingkat"])}</th><td>{e(s["daftar"])}</td></tr>' for s in P["perangkat_lunak"])
    isi = f"""<div class="cv">
<h1>{e(P['nama'])}</h1>
<p class="lead">{e(P['peran'])}. Minat utama geoteknik: fondasi tiang (beban aksial dan lateral), penyelidikan tanah, uji laboratorium tanah, dan stabilitas lereng.</p>
<p class="kontak">Portofolio: <a href="{SITUS}">{SITUS}</a><br>GitHub: <a href="https://github.com/{e(P['github'])}">github.com/{e(P['github'])}</a></p>
<p class="aksi layar-saja"><button type="button" class="tombol utama" data-cetak>Cetak atau simpan PDF</button></p>
<h2>Pendidikan</h2><ul class="riwayat">{''.join(butir(x) for x in P['pendidikan'])}</ul>
<h2>Prestasi</h2><ul class="riwayat">{''.join(butir(x) for x in P['prestasi'])}</ul>
<h2>Pengalaman</h2><ul class="riwayat">{''.join(butir(x) for x in P['pengalaman'])}</ul>
<h2>Karya pilihan</h2><ul class="riwayat">{''.join(f'<li><h3><a href="../karya/{k["id"]}/index.html">{e(k["judul"])}</a>{label_privat(k)}</h3><p class="acara">{e(k["acara"])}, {k["tahun"]}</p></li>' for k in KARYA if k.get('unggulan'))}</ul>
<h2>Perangkat lunak</h2><div class="tabel-gulir"><table><tbody>{sw}</tbody></table></div>
<p class="catatan">Surat referensi untuk pengalaman di atas tersedia atas permintaan.</p>
</div>"""
    halaman("cv/index.html", f"CV: {P['nama']}", isi)


def kredit():
    isi = """<h1>Kredit</h1>
<h2>Huruf</h2>
<p>Archivo dan Plus Jakarta Sans, lisensi SIL Open Font License 1.1, disimpan lokal di <code>assets/font/</code> (salinan lisensi ada di folder yang sama), sama seperti GeoSR.</p>
<h2>Gambar dan video</h2>
<p>Gambar, foto, dan video di situs ini dibuat sendiri atau oleh tim lomba saya. Tidak ada pustaka atau aset dari CDN.</p>
<h2>Data kunjungan</h2>
<p>Jumlah kunjungan dihitung dengan <a href="https://www.goatcounter.com/">GoatCounter</a>, layanan analitik sumber terbuka tanpa cookie, memakai akun yang sama dengan GeoSR. Yang terkirim hanya alamat halaman tanpa kueri, judul halaman, halaman asal, dan ukuran layar. Browser yang meminta Do Not Track tidak dihitung.</p>"""
    halaman("kredit/index.html", f"Kredit: {P['nama']}", isi)


def main():
    for sub in ("karya", "berkas", "cv", "kredit", "index.html"):
        x = KELUAR / sub
        shutil.rmtree(x, ignore_errors=True) if x.is_dir() else x.unlink(missing_ok=True)
    if PRIVAT:
        shutil.copytree(AKAR / "docs" / "assets", KELUAR / "assets", dirs_exist_ok=True)
    beranda(); galeri(); cv(); kredit()
    for k in KARYA:
        halaman_karya(k)
    if not PRIVAT:  # penjaga: tidak satu pun berkas privat boleh masuk docs/
        nama_privat = {f.name for f in (SIAP / "privat").rglob("*") if f.is_file()}
        bocor = [f for f in (KELUAR / "berkas").rglob("*") if f.name in nama_privat]
        teks = " ".join(f.read_text(encoding="utf-8") for f in KELUAR.rglob("*.html"))
        assert not bocor, f"Berkas privat masuk docs/: {bocor}"
        for k in json.loads((SIAP / "privat" / "karya-privat.json").read_text(encoding="utf-8"))["karya"]:
            assert k["id"] not in teks, f"Karya privat {k['id']} disebut di docs/"
        assert all(k["status"] == "publik" for k in DATA["karya"]), "Karya privat harus di karya-privat.json, bukan di repo"
    print(f"{len(KARYA)} karya -> {KELUAR}")


if __name__ == "__main__":
    main()
