### ![commits](https://img.shields.io/github/last-commit/FastFingertips/letterboxd-list) ![visitors](https://visitor-badge.laobi.icu/badge?page_id=FastFingertips.letterboxd-list) 
Attempts to extract data from letterboxd with bs4<br>

## English - Simple Usage (AI Translation)
<details><summary>Single/batch shot by supplying list address</summary>
Define list addresses and press enter for each new address:
<br><code>[>]: https://letterboxd.com/crew/list/best-movie-posters-of-2021/</code>
<br><code>[>]: https://letterboxd.com/crew/list/2021-most-popular-films-by-bipoc-directors/</code>
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/</code>
<br>When your lists are depleted, use "." send. Or "." at the end of your previous listing address. use:
<br><code> [>]: .</code>
<br><code> [>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/.
</code><br> You may use the umlaut ".." to automatically approve the lists you specify:
<br><code>[>]: ..</code>
<br>code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/..</code>
</details>

<details><summary>Capture by giving the name of the list</summary>
You must enter "?" to utilize the list search mode. The sentence should begin with a question mark.
<br>The following text should be the search parameter, such as "Crime Movies" or "Samurai Movies."
<br>Here's a sample query:
<br><code>[>]: ?crime films</code> It will search for lists including all crime movies and add them to the shooting list.
<br><code>[>]: ?crime films!10</code> We set the firing limit with "!" by providing an exclamation point. It is set to be a first 10 list.
<br><code>[>]: ?crime films!10</code> If a query concludes with "." Dot will automatically approve all newly created lists.
</details>

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
</details>
