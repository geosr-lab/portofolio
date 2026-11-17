/* Pasang tema pilihan pengguna sebelum halaman tergambar supaya tidak berkedip.
 * Nilai di localStorage "tema": "terang", "gelap", atau tidak ada (ikut pengaturan sistem). */
(function () {
  try {
    var t = localStorage.getItem('tema');
    if (t === 'terang' || t === 'gelap') document.documentElement.setAttribute('data-tema', t);
  } catch (e) { /* penyimpanan diblokir: ikut sistem */ }
})();
