/* Sakelar tema (kunci "tema" sama dengan GeoSR, jadi pilihan ikut terbawa), saring galeri, tombol cetak CV. */
(function () {
  'use strict';
  var urut = ['', 'terang', 'gelap'], nama = { '': 'otomatis', terang: 'terang', gelap: 'gelap' };
  var tombol = document.querySelector('.tema-tombol');
  function pasang(t) {
    if (t) document.documentElement.setAttribute('data-tema', t); else document.documentElement.removeAttribute('data-tema');
    try { if (t) localStorage.setItem('tema', t); else localStorage.removeItem('tema'); } catch (e) { /* penyimpanan diblokir */ }
    if (tombol) tombol.querySelector('span').textContent = nama[t];
  }
  if (tombol) {
    pasang(document.documentElement.getAttribute('data-tema') || '');
    tombol.addEventListener('click', function () {
      var kini = document.documentElement.getAttribute('data-tema') || '';
      pasang(urut[(urut.indexOf(kini) + 1) % urut.length]);
    });
  }

  var saring = document.querySelectorAll('.saring'), kartu = document.querySelectorAll('.kisi .kartu'), jumlah = document.querySelector('.jumlah');
  function terapkan(j) {
    var n = 0;
    kartu.forEach(function (k) { var ok = !j || k.dataset.jenis.split('|').indexOf(j) >= 0; k.hidden = !ok; if (ok) n++; });
    saring.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.saring === j)); });
    if (jumlah) jumlah.textContent = n + ' karya' + (j ? ' jenis ' + j : '');
  }
  saring.forEach(function (b) { b.addEventListener('click', function () { terapkan(b.dataset.saring); }); });
  if (saring.length) terapkan('');

  // Perbesar gambar di halaman karya tanpa meninggalkan halaman; tanpa skrip, tautan tetap membuka gambar penuh.
  var lihat = null;
  document.querySelectorAll('figure > a > img').forEach(function (img) {
    img.parentNode.addEventListener('click', function (ev) {
      if (!window.HTMLDialogElement) return;
      ev.preventDefault();
      if (!lihat) {
        lihat = document.createElement('dialog');
        lihat.className = 'lihat';
        lihat.innerHTML = '<button type="button" class="tombol">Tutup</button><img alt=""><p></p>';
        lihat.querySelector('button').addEventListener('click', function () { lihat.close(); });
        lihat.addEventListener('click', function (e) { if (e.target === lihat) lihat.close(); });
        document.body.appendChild(lihat);
      }
      lihat.querySelector('img').src = img.src;
      lihat.querySelector('img').alt = img.alt;
      lihat.querySelector('p').textContent = img.alt;
      lihat.showModal();
    });
  });

  var cetak = document.querySelector('[data-cetak]');
  if (cetak) cetak.addEventListener('click', function () { window.print(); });
})();
