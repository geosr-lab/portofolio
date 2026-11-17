/* Penghitung kunjungan GeoSR lewat GoatCounter (https://www.goatcounter.com, sumber terbuka, tanpa cookie).
 * Tidak memakai skrip GoatCounter: satu permintaan gambar ke alamat penghitung yang didokumentasikan GoatCounter
 * ("pixel"), berisi alamat halaman tanpa kueri dan tanpa # (data formulir dan tautan berbagi tidak ikut terkirim),
 * judul halaman, halaman asal, dan ukuran layar.
 * Dipasang oleh skrip/bangun_situs.py hanya bila "goatcounter" di konten/situs.json terisi.
 * Tidak menghitung bila browser meminta Do Not Track, bila halaman dibuka di luar alamat situs (localhost,
 * pratinjau), atau bila halaman sedang dirender di latar (prerender). */
(function () {
  'use strict';
  var ini = document.currentScript;
  if (!ini) return;
  var kode = ini.getAttribute('data-goatcounter'), situs = ini.getAttribute('data-situs');
  if (!kode || !situs) return;
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1') return;
  if (location.host !== situs) return;

  function kirim() {
    var asal = '';
    try { if (document.referrer && new URL(document.referrer).host !== location.host) asal = document.referrer; } catch (e) { /* halaman asal tidak sah */ }
    var data = {
      p: location.pathname,
      t: document.title,
      r: asal,
      s: [screen.width, screen.height, window.devicePixelRatio || 1].join(','),
      rnd: Math.random().toString(36).slice(2)
    };
    var kueri = Object.keys(data).map(function (k) { return k + '=' + encodeURIComponent(data[k]); }).join('&');
    var img = new Image();
    img.referrerPolicy = 'no-referrer-when-downgrade';
    img.src = 'https://' + kode + '.goatcounter.com/count?' + kueri;
  }

  if (document.visibilityState === 'prerender') {
    document.addEventListener('visibilitychange', function sekali() {
      if (document.visibilityState === 'prerender') return;
      document.removeEventListener('visibilitychange', sekali);
      kirim();
    });
  } else kirim();
})();
