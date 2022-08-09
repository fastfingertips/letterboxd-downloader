### ![commits](https://img.shields.io/github/last-commit/FastFingertips/letterboxd-list) ![visitors](https://visitor-badge.laobi.icu/badge?page_id=FastFingertips.letterboxd-list) 
Attempts to extract data from letterboxd with bs4<br>

## Türkçe - Basit Kullanım
<details><summary>Liste adresi belirterek tekli/toplu çekim</summary>
Liste adreslerinı tanımla, her yeni adres için enter'ı tuşla:
<br><code>[>]: https://letterboxd.com/crew/list/best-movie-posters-of-2021/</code>
<br><code>[>]: https://letterboxd.com/crew/list/2021-most-popular-films-by-bipoc-directors/</code>
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/</code>
<br>Listeleriniz tükendiğinde son girişe "." gönderin. Veya son liste adresinizin sonunda "." kullanın:
<br><code>[>]: .</code> 
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/.</code>
<br>Belirttiğiniz listelerin otomatik olarak onaylanması için ".." çift nokta kullanabilirsiniz:
<br><code>[>]: ..</code>
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/..</code>
</details>

<details><summary>Liste ismi belirterek çekim</summary>
Liste arama modunu kullanabilmek için girişiniz "?" soru işaretiyle başlamalıdır.
<br>Sonrasında gelen yazı aramak istediğiniz parametre olmalıdır örneğin "Crime Movies" veya "Samurai Movies" gibi.
<br>Örnek bir sorgu:
<br><code>[>]: ?crime movies</code> Tüm crime movies içeren listeleri bulacak ve çekim listesine eklemeye devam edecektir.
<br><code>[>]: ?crime movies!10</code> Burada "!" ünlem belirterek çekim sınırını belirledik. İlk 10 liste olarak ayarlandı.
<br><code>[>]: ?crime movies!10.</code> Eğer bir sorgu sonunda "." nokta kullanacak olursanız eklenen listelerin tümünü otomatik onaylayacaktır.
</details
