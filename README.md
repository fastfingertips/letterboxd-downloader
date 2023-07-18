### ![commits](https://img.shields.io/github/last-commit/FastFingertips/letterboxd-list) ![visitors](https://visitor-badge.laobi.icu/badge?page_id=FastFingertips.letterboxd-list)



## Simple Usage
<details><summary>Single/batch scraping using list addresses</summary>
Define the list addresses, press Enter for each new address:
<br><code>[>]: https://letterboxd.com/crew/list/best-movie-posters-of-2021/</code>
<br><code>[>]: https://letterboxd.com/crew/list/2021-most-popular-films-by-bipoc-directors/</code>
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/</code>
<br>Send "." at the end when your lists are exhausted. Alternatively, you can use "." at the end of your last list address:
<br><code>[>]: .</code> 
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/.</code>
<br>To automatically approve the specified lists, you can use ".." double dots:
<br><code>[>]: ..</code>
<br><code>[>]: https://letterboxd.com/crew/list/drawn-into-2022-ten-animated-features-to/..</code>
</details>

<details><summary>Scraping by specifying the list name</summary>
To use the list search mode, your entry should start with the "?" question mark.
<br>Following that, the text that follows should be the parameter you want to search for, such as "Crime Movies" or "Samurai Movies".
<br>An example query:
<br><code>[>]: ?crime movies</code> It will find and continue to scrape all lists containing "crime movies."
<br><code>[>]: ?crime movies!10</code> Here, we set the scraping limit by using "!". It is set to the first 10 lists.
<br><code>[>]: ?crime movies!10.</code> If you use a period "." at the end of a query, it will automatically approve all the added lists.
</details>

https://github.com/FastFingertips/letterboxd-downloader/assets/46646991/2d44bc2d-1bb3-498f-963f-976d82dbfe6a
