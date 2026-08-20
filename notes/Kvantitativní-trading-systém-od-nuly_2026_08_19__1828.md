> From: https://claude.ai/chat/e1963d8d-7005-4107-b7d8-02e362cf5fe2

# you asked

message time: 2026-08-15 18:16:35

je mi 17. chci vybudovat aos trading system. mam minimalni zkusenosti s kodovanim. ale od ledna do dubna jsem na tom uz delal. mam lenovo thinkpad x1 yoga gen 5 na kterem pisi kod, na starem ntb "ghettoserver" tam delal dlouhodobe vypocty prootze na hlavnim nemma moc misto a prehriva se a na raspberry pi 4 b taky a tam pak bude kod ktery bude posilat samostatne prikazy. ma filizofie je quant. muj vzor je jim simons. chci stahnout spoustu ruznych dat od ohclv, pres sec, insider trading az po meteo, pozary, finBERT, apod. chci hledat vzorce mezi nimi a jak najdu alfu tak budu jeste testovat ruzne strategie na zaklade jejich vyhod, a pote vytvorim trading prostredi - risk management, break even, if scenare - vypadek proudu, burza neodpovida apod., pravidelne zalohovani atd. spoustu sve prace mam v chatech s tebou na jinem uctu, v deniku, v txt souborech a na githubu ale rozhodl jsem se ze to udelam od znova. chci s tebou probrat strukturu (do budoucna chci pokrocile veci jako triple barrier, k-fold cross validation a podobne veci od marcose lopeze de prada a treba ai system - neco jako osobnosti, co zastavaji nazor - jeden pro koupi instrumentu, druhy proti, ti se shodnou a predaji vysledek manazerovi penez a ten rozhodne, a do uplneho budoucna se to automaticky bude prizpusobovat a tak ale to je ve hvezdaach.) a ted udelame mvp. delal jsem to v pythonu ve vscode to asi bude nejlepsi ze?

---

# claude response

Super ambiciózní projekt, ale rozumně poskládaný — líbí se mi, že máš jasnou vizi (Simons/Lopez de Prado) a zároveň víš, že teď je čas na MVP, ne na multi-agent AI výbor. Pojďme na strukturu.

## Rozdělení rolí strojů

To, co popisuješ, dává smysl:

- **ThinkPad (dev)** – psaní kódu, výzkum, backtesting menších věcí, Git.
- **Ghettoserver (compute)** – dlouhé backtesty, stahování/zpracování velkých datasetů, případně trénování modelů.
- **RPi 4B (execution)** – tenký klient, který jen posílá/přijímá příkazy k brokerovi. Nic těžkého tam neběží, jen spolehlivost a uptime.

Klíčové je oddělit **kód od dat od configu** a mít to všechno v jednom Git repu, který klonuješ na všechny tři stroje — jinak se ti to za měsíc rozjede na tři nekompatibilní verze.

## Struktura repa (návrh)

```
quant-system/
├── data/                  # .gitignore - lokální, nikdy do gitu
│   ├── raw/               # syrová stažená data (parquet/csv)
│   ├── processed/         # vyčištěná, feature-engineered data
│   └── cache/
├── src/
│   ├── ingestion/         # stahovače - ohlcv, sec, insider, meteo, finBERT...
│   │   ├── ohlcv.py
│   │   ├── sec_edgar.py
│   │   └── base.py        # společné rozhraní pro všechny fetchery
│   ├── research/           # notebooky/skripty na hledání vzorců, feature eng.
│   ├── backtest/           # engine, triple-barrier labeling, walk-forward CV
│   ├── strategy/           # jednotlivé strategie jako pluginy
│   ├── risk/               # position sizing, stop-loss, breakeven logika
│   ├── execution/          # broker API wrapper, order management (běží na RPi)
│   └── utils/              # logging, config loader, retry logika
├── config/
│   ├── settings.yaml
│   └── secrets.env         # .gitignore, API klíče
├── tests/
├── scripts/                # jednorázové/cron skripty (backup, health check)
├── pyproject.toml
└── README.md
```

Důležitá zásada: **ingestion, research, backtest a execution jsou oddělené moduly s jasným rozhraním** (např. každý fetcher vrací stejný typ DataFrame se standardizovanými sloupci). Díky tomu když za rok přidáš 20. datový zdroj, nic ti to nerozbije.

## Stack

- **Python 3.12**, VSCode je v pohodě volba (máš tam skvělou podporu pro Jupyter buňky přímo v `.py` souborech přes `# %%`, což je super pro research fázi).
- **uv** místo pip/poetry na správu závislostí — rychlejší, jednodušší cross-machine sync (`uv sync` na všech třech strojích ze stejného `pyproject.toml`).
- **Data storage**: začni s **Parquet soubory** (rychlé, kompaktní, žádný server navíc). Až narazíš na limity, přejdeš na **DuckDB** nebo **TimescaleDB** (Postgres) na ghettoserveru.
- **Git** + `.gitignore` na `data/` a secrets — kód sdílíš, syrová data ne (moc velká, moc rychle se mění).
- **Config přes YAML + .env**, ať nemáš natvrdo API klíče a parametry v kódu.

## MVP scope – co bych řešil jako první

Vzhledem k tomu, kde jsi (data → hledání alfy → strategie → risk mgmt → execution), bych navrhoval takovéhle pořadí, abys měl co nejdřív něco funkčního end-to-end (byť triviálního):

1. **Jeden data zdroj** (OHLCV, třeba přes yfinance nebo Alpaca) → uložit do parquet.
2. **Minimální backtest engine** – i primitivní (vektorizovaný pandas backtest na jedné strategii typu moving average crossover), jen aby fungoval celý pipeline data→signál→P&L.
3. **Jednoduchý risk management skeleton** – position sizing, stop-loss — i kdyby byl naivní.
4. Až tohle jede end-to-end, **přidáváš další datové zdroje a sofistikovanost** (triple-barrier, k-fold CV, další strategie).

Tohle je důležité proto, že s minimální zkušeností v kódování je snadné utopit se v budování "dokonalé" infrastruktury, než vůbec uvidíš jeden reálný výsledek backtestu. Lepší mít ošklivé, ale funkční MVP, které pak refaktoruješ.

Chceš, ať ti rovnou vygeneruju startovní kostru repa (složky + `pyproject.toml` + pár prázdných modulů s docstringy, kde co bude), abys na tom mohl začít stavět?

---

# you asked

message time: 2026-08-15 18:31:17

jak to vysperkovat do budoucna? (jsem perfekcionista a mam tendence se nechat unest) uz jsem to mel napr napojene na telegram co rikal updaty.

---

# claude response

Dobrá sebereflexe, že to říkáš rovnou — u perfekcionistů je tohle přesně ten moment, kdy MVP tiše umře, protože se člověk zamotá do "vysperkování" dřív, než má cokoliv funkčního. Takže: pojďme si udělat **parking lot** — seznam nápadů, které si zapíšeš a k ničemu z nich se nevrátíš, dokud MVP neběží end-to-end aspoň měsíc.

## Nápady do budoucna (seřazeno podle toho, kdy dávají smysl)

**Fáze 2 – jakmile MVP jede a máš první backtesty:**
- **Telegram bot** – notifikace o obchodech, denní P&L summary, alerty při chybě/výpadku. Tohle je nejlevnější "wow efekt" a zároveň užitečné (viz níže, proč právě tohle bych nechal jako první).
- **Logging/monitoring** – structured logy (např. přes `loguru`), health-check skript, co běží jako cron na RPi a hlásí, že žije.
- **Automatické zálohování** – rsync/restic z RPi a ghettoserveru na cloud (Backblaze B2 je levné) nebo aspoň na ThinkPad.

**Fáze 3 – jakmile máš víc než jednu strategii:**
- **Triple-barrier labeling, purged k-fold CV, walk-forward validace** (Lopez de Prado) – tohle je metodologicky správný krok, ale je zbytečné, dokud nemáš vůbec žádnou strategii k validaci.
- **Feature store** – centrální místo, kde máš vypočtené featury (ne surová data), aby ses nemusel pořád přepočítávat.
- **Experiment tracking** – MLflow nebo jednoduchý CSV/SQLite log všech backtestů (parametry, výsledky), ať nezapomeneš co jsi zkoušel.

**Fáze 4 – jakmile máš risk management a chceš to nechat běžet:**
- **Dashboard** (Streamlit/Grafana) – vizualizace equity curve, exposure, drawdown v reálném čase.
- **Alerting na anomálie** – ne jen "obchod proběhl", ale "něco je špatně" (např. burza neodpovídá, data nedorazila, drawdown přes limit).
- **Circuit breakers** – automatické zastavení obchodování při extrémních podmínkách.

**Fáze 5 – to, co zmiňuješ jako "ve hvězdách":**
- Multi-agent systém s "osobnostmi", self-adapting logika, atd.

## Proč zrovna Telegram bych nechal jako první "sperk"

Není to jen hračka — psychologicky ti to dá zpětnou vazbu bez nutnosti sedět u počítače a kontrolovat logy, a zároveň tě to donutí mít pipeline dost stabilní na to, aby vůbec bylo co reportovat. Je to malý, ohraničený úkol (pár desítek řádků přes `python-telegram-bot` nebo jen webhook), takže neotevírá appetite na velké refaktorování — na rozdíl od např. triple-barrier, což tě může vtáhnout na týdny čtení teorie.

## Praktické doporučení proti "unesení"

Založ si v repu soubor `IDEAS_BACKLOG.md` a kdykoliv tě napadne vylepšení, zapiš ho tam a **pokračuj v tom, co jsi dělal**. Pravidlo: nic z backlogu se nezačne řešit, dokud aktuální fáze není hotová a odzkoušená. Je to jednoduchý trik, ale funguje — dá ti to pocit, že nápad "neztrácíš", takže se ho nemusíš bát pustit z hlavy hned teď.

Chceš, ať ti tenhle backlog rovnou založím jako soubor v repu spolu s tou kostrou, co jsem nabízel předtím?

---

# you asked

message time: 2026-08-15 18:36:25

pojdme opravdu zacit s kodem. pojdme projit jaka data budeme stahovat a pak mi na ne napises kod na stazeni. ja zatim udelam slozky. ps: nazev projektu je predbezne hermes, faze fenix. mam rad symboliku. mas lepsi napad? neco z mytologie co symbolizuje vedomosti, informace, silu, vsevedoucnost, naskok, nadrazenost; faze fenix jelikoz jde o obnovu

---

# claude response

Hermes je fakt dobrá volba (posel, obchod, jazyk/kód – hermetismus = skryté vědění), ale když jsi zmínil vševědoucnost, náskok a nadřazenost, napadá mě silnější symbol:

**Ódin** – obětoval oko za moudrost, sedí na trůnu Hlidskjálf, odkud vidí do všech světů (= vševědoucnost), a má dva havrany, **Huginn** (Myšlenka) a **Muninn** (Paměť), kteří každý den obletí svět, sbírají informace a hlásí mu je. To je doslova metafora pro tvůj ingestion pipeline → centrální rozhodovací systém. Dost by mi dávalo smysl třeba data pipeline modul nazvat `huginn` a paměť/feature store `muninn`.

Jiné varianty: **Thovt/Thoth** (egyptský bůh vědění a písma), **Mnémosyné** (matka Múz, ztělesnění paměti), **Prométheus** (ukradl oheň = neférová výhoda/náskok nad ostatními). Ale Ódin mi sedí nejvíc k tomu, co popisuješ. Fénix fáze zůstává skvělá jako první iterace (obnova po předchozích pokusech).

Teď k datům — pojďme to nescopovat na "všechno najednou", i když vím, že seznam v hlavě máš dlouhý (OHLCV, SEC, insider trading, meteo, požáry, FinBERT...). Pro MVP potřebuju vědět pár věcí, ať ti napíšu kód, který sedí na to, co reálně budeš používat.

---

# you asked

message time: 2026-08-15 18:38:14

Q: Jaká třída aktiv na start?
A: cokoliv az na krypto

Q: Zdroj OHLCV dat?
A: yfinance (zdarma, jednoduché)

Q: Jaký timeframe tě zajímá primárně?
A: cca hodiny, asi spis vyssi kvuli poplatkum

---

# claude response

Dobrá volba — hodinová data jsou fér kompromis mezi granularitou a poplatky/šumem, a s yfinance je to nejsnazší na rozjezd.

Jedna důležitá věc dopředu, ať tě to nepřekvapí: **yfinance u hodinových dat dává historii jen zhruba 730 dní zpět** (Yahoo limit, ne yfinance bug). Pro delší historii bys musel na denní data nebo později přejít na placený zdroj (Polygon apod.). Pro MVP a hledání vzorců na hodinovém rámci to ale stačí k rozjezdu.

## Plán pro tenhle skript

- Univerzální funkce `download_ohlcv()` – vezme seznam tickerů, interval, období.
- Ukládá každý ticker zvlášť jako **parquet** do `data/raw/ohlcv/`.
- Základní ošetření chyb (ticker neexistuje, prázdná data, rate limit) – ať ti to nespadne v půlce seznamu 50 tickerů.
- Idempotentní – když skript spustíš znovu, přepíše/doplní data, nezhroutí se na existujícím souboru.

Píšu ho tak, aby seděl do struktury `src/ingestion/ohlcv.py`, kterou sis říkal, že založíš.

Instalace: `pip install yfinance pandas pyarrow` (pyarrow je potřeba pro parquet).

Pár věcí k domluvě, než půjdeme dál na SEC/insider trading data:

1. **Seznam tickerů** – zatím jsem tam dal 3 placeholdery. Máš už nějaký watchlist, nebo chceš stáhnout třeba celý S&P 500 seznam (dá se to udělat automaticky z Wikipedie)?
2. **"Cokoliv až na krypto"** – počítáš i s futures/komoditami hned na startu, nebo to necháme na fázi 2 (yfinance futures kontrakty jsou trochu jiná disciplína – rolling kontraktů atd.)?
3. Jakmile bude OHLCV sedět, můžeme na řadu vzít **SEC EDGAR** (insider trading, filings) – tam je API zdarma, ale je potřeba trochu jiná logika (rate limiting, user-agent header povinný).

Dej vědět, až budou složky hotové a případně odpověz na body výše, ať jedeme dál.

---

# you asked

message time: 2026-08-15 18:52:36

cely projekt musi byt zdarma. zadne placene zdroje dat apod. posli pak tu kostru repa a ty moduly. pojdme probrat ty data. jaka vsechna mam stahnout a odkud?

---

# claude response

Souhlas, žádné placené zdroje — a upřímně, free zdroje jsou na quant research víc než dost, placené (Polygon, Bloomberg) dávají smysl až ve fázi, kdy víš přesně co ti chybí.

## Datové zdroje podle kategorií (vše zdarma)

**1. Market data (OHLCV)** – máš, yfinance. Jako záložní/rozšíření: **Stooq** (`stooq.com`, denní data zdarma přes CSV, delší historie než Yahoo, žádný klíč netřeba).

**2. Fundamentální data** – **SEC EDGAR Company Facts API** (`data.sec.gov/api/xbrl/companyfacts/`) – kompletně zdarma, žádný klíč, strukturovaná XBRL data (rozvahy, výsledovky, cashflow) pro každou veřejně obchodovanou firmu v US. Přesnější než yfinance `.info`, které je nespolehlivé.

**3. Insider trading** – **SEC EDGAR Form 4 filings** – nákupy/prodeje insiderů (CEO, CFO, board). Zdarma, ale vyžaduje povinnou `User-Agent` hlavičku s tvým jménem/emailem (SEC to vynucuje).

**4. Institucionální držby** – **SEC EDGAR Form 13F** – co drží velcí hráči (hedge fondy nad $100M AUM musí čtvrtletně reportovat). Zdarma.

**5. Short interest** – **FINRA** – zveřejňuje short interest data zdarma, 2× měsíčně, jako CSV.

**6. Makro data** – **FRED API** (Federal Reserve Economic Data) – úrokové sazby, inflace, nezaměstnanost, GDP... Zdarma, potřebuješ jen zdarma API klíč (registrace na fred.stlouisfed.org).

**7. Počasí** – **Open-Meteo** – zdarma, žádný klíč, historická i forecast data, jednoduché REST API.

**8. Požáry** – **NASA FIRMS** (Fire Information for Resource Management System) – satelitní detekce požárů v reálném čase i historicky. Zdarma, klíč zdarma na registraci.

**9. Text pro FinBERT (sentiment)** – tohle je nejkomplexnější kategorie:
   - **GDELT Project** – obří free databáze globálních zpráv, aktualizovaná co 15 min.
   - **RSS feedy** (Yahoo Finance, Google News) – zdarma, jednoduché.
   - **Reddit** (přes PRAW, oficiální free API) – např. r/wallstreetbets sentiment.

## Priorita pro MVP

Bych to bral takhle, ať nezačneš stahovat 9 věcí najednou:
1. OHLCV (hotovo)
2. SEC fundamentals + insider trading (Form 4) — nejvíc "alfa-relevantní" a je to jeden ekosystém (jedno API, jedna autentizace)
3. FRED makro data — jednoduché, rychlý win
4. Weather/wildfires a news/sentiment — fáze 2, až budeš mít funkční pipeline s "nudnými" daty

Teď kostra repa:

Teď doplním klíčové soubory – config, base rozhraní pro ingestion, stub moduly s docstringy (ať víš, co kam patří) a projektový config.

Teď utility na config/logging a base rozhraní pro ingestion moduly – tohle je důležité, aby všechny fetchery (OHLCV, SEC, FRED, weather...) vracely stejně tvarovaná data:

Teď stub moduly pro zbytek fetcherů (zatím jen kostra s docstringy a TODO – kód napíšeme jeden po druhém podle priority, kterou jsme probrali):

Chybí ohlcv.py (ten z minula) a IDEAS_BACKLOG.md + README — doplním a zabalím:

**Rozbal do svých složek (nebo použij tohle jako vzor a vytvoř si to sám).**

Co uvnitř je:
- Funkční `src/ingestion/ohlcv.py` (z minula)
- `src/ingestion/base.py` – společné rozhraní pro všechny fetchery (jednotný tvar dat, jednotné ukládání)
- `src/utils/config.py` + `config/settings.yaml` – centrální config, ať nemáš tickery/parametry natvrdo v kódu
- Stub soubory pro `sec_edgar.py`, `fred.py`, `weather.py`, `wildfires.py`, `news_sentiment.py` – prázdné, jen s docstringem co tam bude, napíšeme je postupně
- `IDEAS_BACKLOG.md` s tím, co jsme probrali
- `README.md`, `.gitignore`, `pyproject.toml`

Jakmile budeš mít složky a rozbalíš tam tohle (nebo mi řekneš, že máš vlastní), pojďme napsat **SEC EDGAR fetcher** (fundamentals + insider trading Form 4) jako další krok – to je podle priority, co jsme si řekli, logický další kus.

---

# you asked

message time: 2026-08-15 18:57:58

dopln to o celkvou strukturu co jsi navrhl. navrhni jeste spoustu dalsich dat a pak nejaka vybereme. ber i opravdu nestandardni, hlavne at je free, nezapomen

---

# claude response

Doplním kostru o `scripts/` a `tests/` (v návrhu byly, ale prázdné) a pak ti hodím velký seznam dalších datových zdrojů – včetně pár fakt netradičních, co lidi běžně nepoužívají, ale jsou legálně zdarma.

Kompletní strukturuje teď plně podle původního návrhu (`data/`, `src/` se všemi vrstvami, `config/`, `tests/` s příkladem testu, `scripts/` s health-check a backup stuby).

## Další datové zdroje (vše zdarma) — rozšířený seznam

**Makro / vládní data (mimo FRED)**
- **BLS** (Bureau of Labor Statistics) – zaměstnanost, mzdy. Free API.
- **EIA** (Energy Information Administration) – ropa, plyn, elektřina. Free API, skvělé pro komoditní/energetické tickery.
- **USDA** – zemědělské komodity. Free API.
- **World Bank / IMF / OECD API** – globální makro, pokud chceš přesah mimo US.
- **Census Bureau API** – ekonomické indikátory (retail sales apod.).
- **Federal Register / regulations.gov API** – nové regulace podle sektorů, free.

**"Attention" / pozornost jako proxy signál (netradiční, ale populární v quant researchi)**
- **Google Trends** (přes `pytrends`, neoficiální ale funkční free wrapper) – vyhledávací zájem o firmu/ticker koreluje s volatilitou.
- **Wikipedia Pageviews API** – kolik lidí si čte stránku o firmě, zdarma, žádný klíč.
- **Reddit / StockTwits API** – sentiment/objem zmínek konkrétních tickerů (StockTwits má free tier přímo pro finance).

**Politika a "kdo co ví dřív"**
- **Senate Stock Watcher / House Stock Watcher** – obchody kongresmanů (veřejná free data, hodně sledovaný "signál" posledních let).
- **OpenSecrets API** – lobbying výdaje podle firem/sektorů, free.

**Skutečně netradiční fyzická data**
- **OpenSky Network API** – free, real-time i historická data o letovém provozu (soukromá letadla firem = signál před M&A/eventy).
- **USGS Earthquake API** – zemětřesení v reálném čase, free – relevantní pro pojišťovny, těžařské firmy.
- **NASA FIRMS** (už zmíněno) + **NOAA Drought Monitor / hurricane tracking** – zemědělství, pojišťovny, energetika.
- **EPA AirNow API** – kvalita ovzduší, free.
- **Sentinel Hub / Copernicus (ESA)** – satelitní snímky zdarma (limitovaný free tier) – teoreticky i "parkoviště retailu" analýza, ale narychlo dost pokročilé.

**Inovace / firemní aktivita**
- **USPTO API** – patenty, free – proxy pro inovační tempo firmy.
- **GH Archive / GitHub API** – aktivita na opensource repozitářích, free – zajímavé pro tech firmy s open-source produkty.

**Doprava/logistika jako ekonomický předstih**
- **BTS** (Bureau of Transportation Statistics) – US letecká doprava, zpoždění, free – proxy pro airline/travel sektor.
- **Cass Freight Index** – měsíční report zdarma (ne API, ale pravidelně publikovaný), proxy pro nákladní dopravu/ekonomiku.

---

Je toho hodně, záměrně jsem šel do šířky včetně těch nestandardních, ať máš z čeho vybírat. Doporučuju nepřidávat víc než 2-3 nové zdroje najednou (viz tvoje obava z "unesení").

---

# you asked

message time: 2026-08-15 19:02:29

Q: Které kategorie tě nejvíc zajímají jako další krok po SEC EDGAR? (Select all that apply)
A: Makro (FRED/BLS/EIA), Attention data (Google Trends, Wikipedia), Kongresmani/politika (Senate Stock Watcher), Fyzická/netradiční (lety, zemětřesení, požáry), klidne bud kreativnejsi, jen nezapomen ze nemam neomezene uloziste, zalohovat budu na stary tower, ten ma komponenty z roku 2010 ale mam moznost tam dat stare disky, ted je na jednom ubuntu server s 256 gb a je ready.

---

# claude response

256 GB na starém tower serveru je vlastně solidní budget, pokud budeš chytrý na formáty a agregace — hlavně **žádná syrová satelitní imagery** (Sentinel Hub bych z výběru rovnou vyškrtl, jeden rok snímků by ti sežral desítky GB sám o sobě). Pojďme nastavit pravidla, ať se do toho nezamotáš, a pak pár dalších kreativních nápadů v mezích rozpočtu.

## Storage strategie (než přidáme další zdroje)

- **Parquet se `zstd` kompresí** všude, ne CSV — u tabulkových dat je to typicky 5-10x menší.
- **Vysokofrekvenční zdroje agregovat, neukládat raw.** Např. OpenSky (polohy letadel) neukládej jako "poloha každou vteřinu", ale jako denní agregát (počet letů firemní flotily, průměrná doba letu). Syrová data by tě zabila v řádu dnů.
- **Retenční politika**: posledních cca 90 dní raw, starší agregovat do měsíčních/týdenních souhrnů a raw mazat. Tohle si můžeš dovolit u téměř všeho kromě OHLCV (to je stejně nejmenší objemově).
- Hrubý odhad velikostí ročně (při rozumné agregaci): OHLCV (desítky tickerů, hodinově) ~pár set MB, SEC filings text ~1-2 GB, makro (FRED/BLS/EIA) pár desítek MB (jsou to řídké časové řady), attention data (Trends/Wikipedia) pár desítek MB, congressional trades zanedbatelné (řádově tisíce řádků/rok), fyzická data (earthquakes/wildfires/flights agregovaně) stovky MB.

Realisticky se s rozumnou agregací vejdeš do jednotek GB/rok, takže 256 GB ti vydrží roky i s rezervou na modely/backtesty.

## Pár dalších kreativních nápadů (v rámci vybraných kategorií)

**Makro navíc:**
- **Baker Hughes Rig Count** – týdenní počet aktivních vrtných souprav, free, klasický predictor pro energetický sektor.
- **AAII Investor Sentiment Survey** – týdenní free průzkum bullish/bearish nálady drobných investorů, oblíbený kontrariánský indikátor.
- **CBOE Put/Call Ratio** – free denní data, měří strach/chamtivost trhu.

**Attention navíc:**
- **Internet Archive / Wayback Machine API** – frekvence změn na firemních "press releases" stránkách jako proxy za PR aktivitu, free a dost neotřelé.

**Politika navíc:**
- **FEC API** (Federal Election Commission) – kampaňové dary podle sektorů/zaměstnavatelů, free, signál politických tailwinds pro sektory.

**Fyzická/netradiční navíc:**
- **GDACS** (Global Disaster Alert and Coordination System) – free API, širší než jen zemětřesení/požáry (povodně, cyklóny...).
- **NOAA Space Weather** – sluneční erupce, free – hodně niche, ale relevantní pro satelitní/telekomunikační firmy.

## Návrh pořadí buildu

Držel bych se plánu ze začátku a nepřeskakoval SEC EDGAR (fundamentals + insider trading), protože je to nejvíc "alfa-relevantní" a máš to už rozkoukané ve stubu. Pak bych šel:

1. **SEC EDGAR** (fundamentals + Form 4 insider) — další krok teď
2. **FRED** (makro) — nejjednodušší API, rychlý win, malá data
3. **Senate/House Stock Watcher** — taky jednoduché, jen scraping/CSV
4. Zbytek (BLS/EIA, attention data, fyzická data) — až po prvním kole backtestů, kdy uvidíš, jestli vůbec makro/insider signály něco přidávají

Sedí ti tohle pořadí, nebo chceš začít jinde? Jinak jedeme na SEC EDGAR fetcher.

---

# you asked

message time: 2026-08-15 19:21:02

klidne vic nestandardni ps: myslim ze bylo i neco na insider trading, nebo snad lobbying, proste mocne velryby na trhu. ps2: jeste napad byl sledovat letadla zastupcu pro potencialni spojeni firem, nebo hlidani google a wiki vyhledavani. lowkey ted jsem jeste neudelal zadnou slozku ani kod. dej mi zadani co delat

---

# claude response

"Velryby" je přesně správný pojem – pojďme přidat pár skutečně ostrých:

## Whale tracking (nad rámec toho, co už máme)

- **Form 13D/13G (SEC EDGAR)** – ještě silnější signál než 13F. 13F je čtvrtletní a se zpožděním, ale **13D se musí podat do 10 dní od nákupu >5% podílu ve firmě** – tohle je klasický "aktivistický investor se chystá tlačit na změnu" signál (Icahn, Ackman apod.). Free, stejné API jako zbytek EDGARu.
- **Form 8-K** – firmy musí zveřejnit "material events" (akvizice, odchod CEO, atd.) do 4 dnů. Rychlejší než čtvrtletní reporty, free.
- **FINRA dark pool / ADF volume data** – kolik objemu se obchoduje mimo standardní burzy (dark pools). Free, se zpožděním, ale ukazuje, kde se pohybují velcí institucionální hráči nenápadně.
- **Lobbying**: **Senate LDA (lobbyingdisclosure.house.gov)** – oficiální free API, přesnější než OpenSecrets pro raw data.

## Firemní tryskáče (tvůj nápad, potvrzuju že to funguje)

Tohle je reálně používaná technika (Quiver Quantitative to dělá komerčně). **ADS-B Exchange** je lepší než OpenSky pro tohle – nefiltruje "citlivé" lety tak agresivně a má free historická data. Princip: sleduješ tail čísla známých firemních letadel (dají se dohledat přes FAA registry, free), a když firemní tryskáč nečekaně přistane u sídla jiné firmy → potenciální M&A signál. Je to legální a veřejné (transpondery vysílají pozici veřejně), přesně tenhle typ "legální insider info" má Simons rád.

---

## Zadání – co reálně udělat TEĎ

Rozumím, že "structure v hlavě" ≠ "kód na disku". Tady je čistý postup od nuly:

Projdi si tyhle kroky jeden po druhém a nespěchej – klidně si dej pauzu mezi krokem 4 a 6, ať to sedí. Napiš, kde se případně zaseknou (chybová hláška, cokoliv), a jakmile budeš mít krok 7 hotový (první commit), pustíme se do SEC EDGAR fetcheru (fundamentals + 13D/13G + 8-K) jako dalšího kusu kódu.

---

# you asked

message time: 2026-08-15 23:16:23

nejaky ty knihvny jako pandas a pyarrow urco mam ale tady je vypis: PS C:\HERMES_FENIX> python -m venv .venv
PS C:\HERMES_FENIX> .venv\Scripts\activate
(.venv) PS C:\HERMES_FENIX> pip install -e
Usage:   
  pip install [options] <requirement specifier> [package-index-options] ...
  pip install [options] -r <requirements file> [package-index-options] ...
  pip install [options] [-e] <vcs project url> ...
  pip install [options] [-e] <local project path> ...
  pip install [options] <archive url/path> ...
-e option requires 1 argument
(.venv) PS C:\HERMES_FENIX> ps: jak bude vubec vypadat hledani alfy a jeji testovani v ramci strategii? ps2: nerozumim tomu zkopriovani .env

---

# claude response

Dvě rychlé opravy a pak k zajímavější otázce.

## Oprava 1: pip install

Ťukl jsi jen `pip install -e` bez tečky na konci. Ta tečka znamená "nainstaluj balíček z aktuální složky":

```powershell
pip install -e .
```

Pokud by to házelo další chyby (možná bude), stačí nouzovka:
```powershell
pip install pandas pyarrow yfinance requests pyyaml python-dotenv
```

## Oprava 2: co je to "zkopírování .env"

`secrets.env.example` je jen **vzor/šablona** – ukazuje, jaké API klíče projekt bude potřebovat, ale samotné klíče tam nejsou (jsou prázdné). Je bezpečné ho mít v Gitu, protože v něm nejsou žádná citlivá data.

`secrets.env` (bez `.example`) je **skutečný soubor s tvými klíči**, který si tam později doplníš. Ten je v `.gitignore`, takže se nikdy nedostane do Gitu/na GitHub – kdyby sis později projekt sdílel nebo ho dal na veřejný GitHub, tvoje klíče by nikomu neunikly.

V PowerShellu prostě uděláš kopii souboru pod novým jménem:
```powershell
copy config\secrets.env.example config\secrets.env
```

Teď je to jen prázdná kopie – nic do ní zatím psát nemusíš, until narazíme na FRED/jiný zdroj vyžadující klíč.

---

## Jak bude vypadat hledání alfy a testování strategií

Tohle je dobrá otázka na zastavení, protože "stahování dat" a "hledání alfy" jsou dvě dost odlišné fáze s jinou logikou. Nakreslím ti to jako pipeline:

Tohle je **výzkumná smyčka** – fáze, kde hledáš, jestli vůbec nějaká data mají prediktivní sílu. Klíčový krok je "statistický test hypotézy": bereš jeden feature (třeba "insider nakoupil v posledních 5 dnech") a testuješ, jestli koreluje s budoucím výnosem přes stovky/tisíce případů – typicky pomocí tzv. **Information Coefficient** (korelace mezi predikcí a skutečným výnosem) nebo jednoduššího "quantile test" (rozdělíš akcie do skupin podle feature a podíváš se, jestli top skupina outperformuje bottom skupinu). Drtivá většina hypotéz v tomhle kroku neprojde – to je normální, i Simons měl slavně říkat, že jim fungovalo jen pár procent nápadů.

Jakmile feature projde i **out-of-sample** testem (na datech, která model/test "neviděl" při hledání vzorce – jinak se jen naučíš šum), teprve pak má smysl z něj stavět skutečnou strategii:

Pár klíčových pojmů z toho, co teprve přijde (Lopez de Prado terminologie, aby ses v tom orientoval, až na to narazíš):

- **Triple-barrier labeling** – místo prostého "vzrostla cena za 5 dní?" definuješ tři hranice (profit target, stop-loss, časový limit) a označíš obchod podle toho, která hranice se dotkne první. Realističtější než fixní horizont.
- **Purged k-fold CV** – běžný k-fold cross-validation u finančních časových řad podvádí, protože sousední dny spolu korelují (data leakage). Purged verze mezi trénovacím a testovacím oknem vynechává "nárazníkovou zónu".
- **Walk-forward validace** – trénuješ na období 1, testuješ na období 2, pak posuneš okno a opakuješ. Simuluje to, jak by ses skutečně rozhodoval v čase, ne se zpětným pohledem.

Zatím to nepotřebuješ řešit – tohle přijde na řadu, až budeš mít první surová data a první jednoduchý test hypotézy (třeba "predikuje moving average crossover budoucí výnos o něco lépe než náhoda"). Teď zkus dokončit setup (kroky 4-8 z minula) a dej vědět, jak dopadlo stažení dat.

---

# you asked

message time: 2026-08-15 23:20:55

PS C:\HERMES_FENIX> python -m venv .venv
PS C:\HERMES_FENIX> .venv\Scripts\activate
(.venv) PS C:\HERMES_FENIX> pip install -e

Usage:   
  pip install [options] <requirement specifier> [package-index-options] ...
  pip install [options] -r <requirements file> [package-index-options] ...
  pip install [options] [-e] <vcs project url> ...
  pip install [options] [-e] <local project path> ...
  pip install [options] <archive url/path> ...

-e option requires 1 argument
(.venv) PS C:\HERMES_FENIX> python src/ingestion/ohlcv.py
Traceback (most recent call last):
  File "C:\HERMES_FENIX\src\ingestion\ohlcv.py", line 21, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
(.venv) PS C:\HERMES_FENIX> pip install -e .
Obtaining file:///C:/HERMES_FENIX
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Installing backend dependencies ... done
  Preparing editable metadata (pyproject.toml) ... error
  error: subprocess-exited-with-error
  
  × Preparing editable metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [55 lines of output]
      Traceback (most recent call last):
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 167, in prepare_metadata_for_build_editable
          hook = backend.prepare_metadata_for_build_editable
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      AttributeError: module 'hatchling.build' has no attribute 'prepare_metadata_for_build_editable'
      
      During handling of the above exception, another exception occurred:
      
      Traceback (most recent call last):
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 353, in <module>
          main()
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 176, in prepare_metadata_for_build_editable
          whl_basename = build_hook(metadata_directory, config_settings)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\build.py", line 83, in build_editable
          return os.path.basename(next(builder.build(directory=wheel_directory, versions=["editable"])))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\plugin\interface.py", line 157, in build
          artifact = version_api[version](directory, **build_data)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 547, in build_editable
          return self.build_editable_detection(directory, **build_data)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 559, in build_editable_detection
          for included_file in self.recurse_selected_project_files():
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\plugin\interface.py", line 182, in recurse_selected_project_files
          if self.config.only_include:
             ^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\functools.py", line 1001, in __get__
          val = self.func(instance)
                ^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\config.py", line 715, in only_include
          only_include = only_include_config.get("only-include", self.default_only_include()) or self.packages
                                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 293, in default_only_include
          return self.default_file_selection_options.only_include
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\functools.py", line 1001, in __get__
          val = self.func(instance)
                ^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 281, in default_file_selection_options
          raise ValueError(message)
      ValueError: Unable to determine which files to ship inside the wheel using the following heuristics: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection
      
      The most likely cause of this is that there is no directory that matches the name of your project (hermes).
      
      At least one file selection option must be defined in the `tool.hatch.build.targets.wheel` table, see: https://hatch.pypa.io/latest/config/build/
      
      As an example, if you intend to ship a directory named `foo` that resides within a `src` directory located at the root of your project, you can define the following:
      
      [tool.hatch.build.targets.wheel]
      packages = ["src/foo"]
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.

[notice] A new release of pip is available: 24.0 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip
(.venv) PS C:\HERMES_FENIX> python src/ingestion/ohlcv.py
Traceback (most recent call last):
  File "C:\HERMES_FENIX\src\ingestion\ohlcv.py", line 21, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Dvě věci se semlely najednou – pojďme to rozmotat.

## Proč `ModuleNotFoundError: No module named 'pandas'`

`pip install -e .` (editable install balíčku) selhal kvůli konfliktu v `pyproject.toml` (vysvětlím níž), takže se **vůbec nic nenainstalovalo** – proto pandas chybí.

## Rychlá oprava – obejdi to teď

Nepotřebuješ `-e .` install vůbec, aspoň zatím (to je jen pro to, aby šly dělat `import src.neco` napříč projektem, na to zatím nesaháme). Nainstaluj závislosti přímo:

```powershell
pip install pandas pyarrow yfinance requests pyyaml python-dotenv
```

Pak zkus znovu:
```powershell
python src/ingestion/ohlcv.py
```

Tohle by teď mělo projít.

## Proč `pip install -e .` padal (oprava do budoucna)

Hatchling (build nástroj) neuměl poznat, které soubory má do balíčku zabalit – v chybě je to napsané docela jasně: *"no directory that matches the name of your project (hermes)"*. Projekt se jmenuje `hermes`, ale kód mám ve složce `src/`, ne `hermes/`. Potřebuje to explicitně říct.

Do `pyproject.toml` přidej tuhle sekci (klidně na konec souboru):

```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

Až to tam přidáš, `pip install -e .` by měl projít bez chyby. Ale není to naléhavé – klidně to zatím přeskoč, funguje ti workflow bez toho.

Dej vědět, jestli teď stažení OHLCV proběhlo (měl bys vidět pár řádků logu a v `data/raw/ohlcv/` tři `.parquet` soubory).

---

# you asked

message time: 2026-08-15 23:27:40

PS C:\HERMES_FENIX> python -m venv .venv
PS C:\HERMES_FENIX> .venv\Scripts\activate
(.venv) PS C:\HERMES_FENIX> pip install -e

Usage:   
  pip install [options] <requirement specifier> [package-index-options] ...
  pip install [options] -r <requirements file> [package-index-options] ...
  pip install [options] [-e] <vcs project url> ...
  pip install [options] [-e] <local project path> ...
  pip install [options] <archive url/path> ...

-e option requires 1 argument
(.venv) PS C:\HERMES_FENIX> python src/ingestion/ohlcv.py
Traceback (most recent call last):
  File "C:\HERMES_FENIX\src\ingestion\ohlcv.py", line 21, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
(.venv) PS C:\HERMES_FENIX> pip install -e .
Obtaining file:///C:/HERMES_FENIX
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Installing backend dependencies ... done
  Preparing editable metadata (pyproject.toml) ... error
  error: subprocess-exited-with-error
  
  × Preparing editable metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [55 lines of output]
      Traceback (most recent call last):
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 167, in prepare_metadata_for_build_editable
          hook = backend.prepare_metadata_for_build_editable
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      AttributeError: module 'hatchling.build' has no attribute 'prepare_metadata_for_build_editable'
      
      During handling of the above exception, another exception occurred:
      
      Traceback (most recent call last):
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 353, in <module>
          main()
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\HERMES_FENIX\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 176, in prepare_metadata_for_build_editable
          whl_basename = build_hook(metadata_directory, config_settings)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\build.py", line 83, in build_editable
          return os.path.basename(next(builder.build(directory=wheel_directory, versions=["editable"])))
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\plugin\interface.py", line 157, in build
          artifact = version_api[version](directory, **build_data)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 547, in build_editable
          return self.build_editable_detection(directory, **build_data)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 559, in build_editable_detection
          for included_file in self.recurse_selected_project_files():
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\plugin\interface.py", line 182, in recurse_selected_project_files
          if self.config.only_include:
             ^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\functools.py", line 1001, in __get__
          val = self.func(instance)
                ^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\config.py", line 715, in only_include
          only_include = only_include_config.get("only-include", self.default_only_include()) or self.packages
                                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 293, in default_only_include
          return self.default_file_selection_options.only_include
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\functools.py", line 1001, in __get__
          val = self.func(instance)
                ^^^^^^^^^^^^^^^^^^^
        File "C:\Users\dubul\AppData\Local\Temp\pip-build-env-rwz5s8t4\overlay\Lib\site-packages\hatchling\builders\wheel.py", line 281, in default_file_selection_options
          raise ValueError(message)
      ValueError: Unable to determine which files to ship inside the wheel using the following heuristics: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection
      
      The most likely cause of this is that there is no directory that matches the name of your project (hermes).
      
      At least one file selection option must be defined in the `tool.hatch.build.targets.wheel` table, see: https://hatch.pypa.io/latest/config/build/
      
      As an example, if you intend to ship a directory named `foo` that resides within a `src` directory located at the root of your project, you can define the following:
      
      [tool.hatch.build.targets.wheel]
      packages = ["src/foo"]
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.

[notice] A new release of pip is available: 24.0 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip
(.venv) PS C:\HERMES_FENIX> python src/ingestion/ohlcv.py
Traceback (most recent call last):
  File "C:\HERMES_FENIX\src\ingestion\ohlcv.py", line 21, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
(.venv) PS C:\HERMES_FENIX> pip install pandas pyarrow yfinance requests pyyaml python-dotenv
Collecting pandas
  Using cached pandas-3.0.5-cp311-cp311-win_amd64.whl.metadata (19 kB)
Collecting pyarrow
  Downloading pyarrow-25.0.1-cp311-cp311-win_amd64.whl.metadata (3.0 kB)
Collecting yfinance
  Downloading yfinance-1.6.0-py3-none-any.whl.metadata (6.7 kB)
Collecting requests
  Using cached requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
Collecting pyyaml
  Using cached pyyaml-6.0.3-cp311-cp311-win_amd64.whl.metadata (2.4 kB)
Collecting python-dotenv
  Downloading python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
Collecting numpy>=1.26.0 (from pandas)
  Using cached numpy-2.4.6-cp311-cp311-win_amd64.whl.metadata (6.6 kB)
Collecting python-dateutil>=2.8.2 (from pandas)
  Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting tzdata (from pandas)
  Using cached tzdata-2026.3-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting beautifulsoup4>=4.11.1 (from yfinance)
  Downloading beautifulsoup4-4.15.0-py3-none-any.whl.metadata (3.8 kB)
Collecting curl_cffi>=0.15 (from yfinance)
  Downloading curl_cffi-0.16.0-cp310-abi3-win_amd64.whl.metadata (17 kB)
Collecting lxml>=4.9.0 (from yfinance)
  Downloading lxml-6.1.1-cp311-cp311-win_amd64.whl.metadata (3.6 kB)
Collecting multitasking>=0.0.7 (from yfinance)
  Downloading multitasking-0.0.13-py3-none-any.whl.metadata (16 kB)
Collecting peewee>=3.16.2 (from yfinance)
  Downloading peewee-4.3.0-py3-none-any.whl.metadata (10 kB)
Collecting platformdirs>=2.0.0 (from yfinance)
  Downloading platformdirs-4.11.3-py3-none-any.whl.metadata (5.5 kB)
Collecting protobuf>=3.19.0 (from yfinance)
  Downloading protobuf-7.35.1-cp310-abi3-win_amd64.whl.metadata (595 bytes)
Collecting pytz>=2022.5 (from yfinance)
  Downloading pytz-2026.3.post1-py2.py3-none-any.whl.metadata (22 kB)
Collecting websockets>=13.0 (from yfinance)
  Downloading websockets-17.0.1-cp311-cp311-win_amd64.whl.metadata (6.5 kB)
Collecting charset_normalizer<4,>=2 (from requests)
  Downloading charset_normalizer-3.5.1-cp311-cp311-win_amd64.whl.metadata (46 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 46.7/46.7 kB 2.4 MB/s eta 0:00:00
Collecting idna<4,>=2.5 (from requests)
  Using cached idna-3.18-py3-none-any.whl.metadata (6.1 kB)
Collecting urllib3<3,>=1.26 (from requests)
  Using cached urllib3-2.7.0-py3-none-any.whl.metadata (6.9 kB)
Collecting certifi>=2023.5.7 (from requests)
  Using cached certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
Collecting soupsieve>=1.6.1 (from beautifulsoup4>=4.11.1->yfinance)
  Downloading soupsieve-2.9.2-py3-none-any.whl.metadata (4.6 kB)
Collecting typing-extensions>=4.0.0 (from beautifulsoup4>=4.11.1->yfinance)
  Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting cffi>=2.0.0 (from curl_cffi>=0.15->yfinance)
  Downloading cffi-2.1.1-cp311-cp311-win_amd64.whl.metadata (2.6 kB)
Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas)
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting pycparser (from cffi>=2.0.0->curl_cffi>=0.15->yfinance)
  Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
Using cached pandas-3.0.5-cp311-cp311-win_amd64.whl (10.0 MB)
Downloading pyarrow-25.0.1-cp311-cp311-win_amd64.whl (27.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 27.9/27.9 MB 8.0 MB/s eta 0:00:00
Downloading yfinance-1.6.0-py3-none-any.whl (148 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 148.0/148.0 kB 2.2 MB/s eta 0:00:00
Using cached requests-2.34.2-py3-none-any.whl (73 kB)
Using cached pyyaml-6.0.3-cp311-cp311-win_amd64.whl (158 kB)
Downloading python_dotenv-1.2.2-py3-none-any.whl (22 kB)
Downloading beautifulsoup4-4.15.0-py3-none-any.whl (109 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 109.9/109.9 kB 2.1 MB/s eta 0:00:00
Using cached certifi-2026.7.22-py3-none-any.whl (136 kB)
Downloading charset_normalizer-3.5.1-cp311-cp311-win_amd64.whl (206 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 206.7/206.7 kB 3.2 MB/s eta 0:00:00
Downloading curl_cffi-0.16.0-cp310-abi3-win_amd64.whl (2.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 14.0 MB/s eta 0:00:00
Using cached idna-3.18-py3-none-any.whl (65 kB)
Downloading lxml-6.1.1-cp311-cp311-win_amd64.whl (4.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.0/4.0 MB 18.3 MB/s eta 0:00:00
Downloading multitasking-0.0.13-py3-none-any.whl (16 kB)
Using cached numpy-2.4.6-cp311-cp311-win_amd64.whl (12.6 MB)
Downloading peewee-4.3.0-py3-none-any.whl (179 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 179.5/179.5 kB 3.6 MB/s eta 0:00:00
Downloading platformdirs-4.11.3-py3-none-any.whl (23 kB)
Downloading protobuf-7.35.1-cp310-abi3-win_amd64.whl (439 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 440.0/440.0 kB 6.9 MB/s eta 0:00:00
Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Downloading pytz-2026.3.post1-py2.py3-none-any.whl (508 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 508.3/508.3 kB 7.9 MB/s eta 0:00:00
Using cached urllib3-2.7.0-py3-none-any.whl (131 kB)
Downloading websockets-17.0.1-cp311-cp311-win_amd64.whl (213 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 213.3/213.3 kB 6.6 MB/s eta 0:00:00
Using cached tzdata-2026.3-py2.py3-none-any.whl (348 kB)
Downloading cffi-2.1.1-cp311-cp311-win_amd64.whl (185 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 185.1/185.1 kB 3.7 MB/s eta 0:00:00
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading soupsieve-2.9.2-py3-none-any.whl (37 kB)
Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45.6/45.6 kB 751.7 kB/s eta 0:00:00
Using cached pycparser-3.0-py3-none-any.whl (48 kB)
Installing collected packages: pytz, multitasking, websockets, urllib3, tzdata, typing-extensions, soupsieve, six, pyyaml, python-dotenv, pycparser, pyarrow, protobuf, platformdirs, peewee, numpy, lxml, idna, charset_normalizer, certifi, requests, python-dateutil, cffi, beautifulsoup4, pandas, curl_cffi, yfinance
Successfully installed beautifulsoup4-4.15.0 certifi-2026.7.22 cffi-2.1.1 charset_normalizer-3.5.1 curl_cffi-0.16.0 idna-3.18 lxml-6.1.1 multitasking-0.0.13 numpy-2.4.6 pandas-3.0.5 peewee-4.3.0 platformdirs-4.11.3 protobuf-7.35.1 pyarrow-25.0.1 pycparser-3.0 python-dateutil-2.9.0.post0 python-dotenv-1.2.2 pytz-2026.3.post1 pyyaml-6.0.3 requests-2.34.2 six-1.17.0 soupsieve-2.9.2 typing-extensions-4.16.0 tzdata-2026.3 urllib3-2.7.0 websockets-17.0.1 yfinance-1.6.0

[notice] A new release of pip is available: 24.0 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Instalace proběhla v pořádku – teď zbývá jen spustit skript:

```powershell
python src/ingestion/ohlcv.py
```

Měl bys vidět pár řádků logu (`Stahuji AAPL...`, `AAPL: uloženo X řádků -> ...`) a v `data/raw/ohlcv/` se objeví tři `.parquet` soubory (AAPL, MSFT, SPY).

Pošli mi výstup, ať vidím, jestli to prošlo, nebo jestli yfinance/Yahoo hodí nějakou chybu (občas má rate-limity nebo mění formát odpovědi, tak radši ověřím, než budeme stavět na tom dál).

---

# you asked

message time: 2026-08-15 23:30:03

jo mam tam ty parquety. co dal?

---

# claude response

Perfektní, první článek pipeline žije. Rychlé ověření, než pojedeme dál (30 vteřin, ať víme, že data nejsou prázdná/rozbitá):

```powershell
python
>>> import pandas as pd
>>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
>>> print(df.head())
>>> print(len(df))
>>> exit()
```

Měl bys vidět tabulku se sloupci `timestamp, Open, High, Low, Close, Volume, ticker` a řádově tisíce řádků (730 dní × ~7 hodin obchodování denně). Pokud to sedí, pokračujeme.

## Další krok: SEC EDGAR fetcher

Podle plánu, co jsme probrali – fundamentals + insider trading (Form 4) + "velrybí" filings (13D/13G, 8-K). Napíšu ti fetcher, který:

1. Stáhne mapování ticker → CIK číslo (SEC interní ID firmy) – jeden free JSON soubor od SEC.
2. Pro daný ticker stáhne **fundamentals** (rozvahy, výsledovky – strukturovaná XBRL data).
3. Stáhne seznam **posledních filings** (Form 4 = insider trading, 13D/13G = aktivističtí investoři, 8-K = material events) s daty a odkazy.

Pro MVP zatím neparsuju detailní obsah Form 4 (kdo přesně kolik koupil – to je uložené v XML uvnitř filingu, trochu složitější parsing), ale dostaneš **frekvenci a časování** insider aktivity, což už samo o sobě je feature k testování. Detailní parsing dodělám jako další krok, až tohle proběhne.

## Co udělat

1. Ulož soubor jako `src/ingestion/sec_edgar.py` (přepiš prázdný stub, co tam už je).
2. **Důležité**: otevři `config/settings.yaml` a řádek `user_agent: "Hermes Project your-email@example.com"` uprav na svoje skutečné jméno a email – SEC podle svých pravidel identifikuje, kdo dělá requesty, a bez smysluplného User-Agentu tě zablokuje (HTTP 403).
3. Spusť:
```powershell
python src/ingestion/sec_edgar.py
```

Měl bys v `data/raw/sec_fundamentals/` a `data/raw/sec_filings/` vidět parquet soubory pro každý ticker, a v `data/cache/` soubor `sec_cik_map.parquet` (to je ten cachovaný seznam ticker→CIK, stáhne se jen jednou).

Pošli výstup/chybu, ať to spolu doladíme, než půjdeme dál.

---

# you asked

message time: 2026-08-15 23:32:20

(.venv) PS C:\HERMES_FENIX> python
Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> > import pandas as pd
  File "<stdin>", line 1
    > import pandas as pd
    ^
SyntaxError: invalid syntax
>>> >>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
  File "<stdin>", line 1
    >>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
    ^^
SyntaxError: invalid syntax
>>> >>> print(df.head())
  File "<stdin>", line 1
    >>> print(df.head())
    ^^
SyntaxError: invalid syntax
>>> >>> print(len(df))
  File "<stdin>", line 1
    >>> print(len(df))
    ^^
SyntaxError: invalid syntax
>>> >>> exit()
  File "<stdin>", line 1
    >>> exit()
    ^^
SyntaxError: invalid syntax
>>>

---

# claude response

Malá záludnost – ty `>>>` na začátku řádků jsou jen **symbol promptu**, který Python sám vypisuje, ne něco, co máš opsat. Zkus to znovu, ale piš jen to, co je za `>>>`:

```python
import pandas as pd
df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
print(df.head())
print(len(df))
exit()
```

Zkopíruj tyhle řádky jeden po druhém (Python interaktivní shell si sám doplní svoje `>>>` před každým). Pošli výstup, ať vidíme, jak vypadají OHLCV data.

---

# you asked

message time: 2026-08-16 13:44:52

(.venv) PS C:\HERMES_FENIX> python src/ingestion/ohlcv.py
2026-08-15 23:28:41,599 [INFO] Stahuji AAPL (1h, 730d)...
2026-08-15 23:28:48,622 [INFO] AAPL: ulozeno 5082 radku -> data\raw\ohlcv\AAPL_1h.parquet
2026-08-15 23:28:48,630 [INFO] Stahuji MSFT (1h, 730d)...
2026-08-15 23:28:49,917 [INFO] MSFT: ulozeno 5082 radku -> data\raw\ohlcv\MSFT_1h.parquet
2026-08-15 23:28:49,919 [INFO] Stahuji SPY (1h, 730d)...
2026-08-15 23:28:51,176 [INFO] SPY: ulozeno 5082 radku -> data\raw\ohlcv\SPY_1h.parquet
2026-08-15 23:28:51,177 [INFO] Hotovo. Uspesne staženo 3/3 tickeru.
(.venv) PS C:\HERMES_FENIX> python
Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> > import pandas as pd
  File "<stdin>", line 1
    > import pandas as pd
    ^
SyntaxError: invalid syntax
>>> >>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
  File "<stdin>", line 1
    >>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
    ^^
SyntaxError: invalid syntax
>>> >>> print(df.head())
  File "<stdin>", line 1
    >>> print(df.head())
    ^^
SyntaxError: invalid syntax
>>> >>> print(len(df))
  File "<stdin>", line 1
    >>> print(len(df))
    ^^
SyntaxError: invalid syntax
>>> >>> exit()
  File "<stdin>", line 1
    >>> exit()
    ^^
SyntaxError: invalid syntax
>>> import pandas as pd
>>> df = pd.read_parquet('data/raw/ohlcv/AAPL_1h.parquet')
>>> print(df.head())
                  timestamp       Close  ...    Volume  ticker
0 2023-09-18 09:30:00-04:00  177.021896  ...  22986329    AAPL
1 2023-09-18 10:30:00-04:00  177.809998  ...   7649414    AAPL
2 2023-09-18 11:30:00-04:00  178.544998  ...   5913851    AAPL
3 2023-09-18 12:30:00-04:00  179.115005  ...   6522049    AAPL
4 2023-09-18 13:30:00-04:00  178.960007  ...   4692584    AAPL
[5 rows x 7 columns]
>>> print(len(df))
5082
>>> exit()
(.venv) PS C:\HERMES_FENIX> >>

---

# claude response

Data vypadají naprosto v pořádku – správný časový rozsah (2023-09 až teď, což sedí na 730 dní zpět), timezone-aware timestampy, správné sloupce. OHLCV vrstva je hotová a ověřená.

Teď SEC EDGAR:

1. Otevři `config/settings.yaml`, najdi řádek:
   ```yaml
   user_agent: "Hermes Project your-email@example.com"
   ```
   a nahraď svým skutečným jménem a emailem, např.:
   ```yaml
   user_agent: "Jan Novak jan.novak@email.com"
   ```
   (SEC to nekontroluje jako přihlašovací údaj, jen to musí vypadat jako smysluplný kontakt – jinak blokuje requesty.)

2. Ulož `sec_edgar.py` z minulé zprávy do `src/ingestion/sec_edgar.py` (přepiš prázdný stub).

3. Spusť:
   ```powershell
   python src/ingestion/sec_edgar.py
   ```

Pošli výstup – u SEC dat je o něco větší šance na zádrhel (403 při špatném User-Agentu, nebo ticker bez SEC záznamu), takže radši projdeme výsledek společně.

---

# you asked

message time: 2026-08-16 13:54:44

(.venv) PS C:\HERMES_FENIX> >>python src/ingestion/sec_edgar.py
>> : The term '>>' is not recognized as the name of a cmdlet, func
tion, script file, or operable program. Check the spelling of the 
name, or if a path was included, verify that the path is correct a
nd try again.
At line:1 char:1
+ >>python src/ingestion/sec_edgar.py
+ ~~
    + CategoryInfo          : ObjectNotFound: (>>:String) [], Com 
   mandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
 
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Stejná věc jako minule – ten `>>` na začátku je zbytek z předchozího výstupu (PowerShellu), ne něco, co máš psát. Napiš jen:

```powershell
python src/ingestion/sec_edgar.py
```

(Mimochodem, obecná rada: kdykoliv vidíš na začátku řádku nějaké znaky jako `>>>`, `>>`, `$`, `#` – to je vždy jen prompt/značka terminálu, ukazuje, že čeká na příkaz. Nikdy to není součást toho, co máš opsat.)

---

# you asked

message time: 2026-08-16 13:56:18

(.venv) PS C:\HERMES_FENIX> python src/ingestion/sec_edgar.py
(.venv) PS C:\HERMES_FENIX> python src/ingestion/sec_edgar.py
(.venv) PS C:\HERMES_FENIX> (NIC SE NESTALO??)

---

# claude response

Pojďme to ověřit rovnou – zkusím ten samý scénář nasimulovat, ať vím přesně, co se děje, místo abych jen hádal.

Našel jsem to – potvrzeno. Skript padá na `ModuleNotFoundError: No module named 'src'`, protože používá `from src.ingestion.base import ...`, ale když spustíš soubor přímo (`python src/ingestion/sec_edgar.py`), Python nevidí kořen projektu, jen složku `src/ingestion/`. Proto neumí najít balíček `src`.

(U tebe se ta chyba pravděpodobně taky objevila, jen se možná ztratila v terminálu nebo jsi nescrolloval nahoru – zkus se podívat, jestli tam něco červeného nebylo.)

Oprava potvrzena – `-m` řeší import problém (druhá chyba, co vidíš, je jen kontrola, že jsi v `settings.yaml` skutečně nahradil placeholder emailu, což už jsi měl udělat).

## Řešení

Spouštěj to takhle (z kořenové složky projektu, `C:\HERMES_FENIX`):

```powershell
python -m src.ingestion.sec_edgar
```

Rozdíl: `-m` řekne Pythonu "spusť tohle jako modul uvnitř balíčku", takže si sám přidá kořenovou složku projektu na cestu k importům. Přímé `python src/ingestion/sec_edgar.py` to neudělá.

**Tohle si zapamatuj jako obecné pravidlo** – jakýkoliv skript ve `src/`, který importuje z jiných `src/` modulů (jako `from src.ingestion.base import ...`), musíš od teď spouštět přes `-m` s tečkovou notací (`src.ingestion.nazev_souboru`, bez `.py` na konci), ne přímou cestou k souboru. Zatímco `ohlcv.py` je samostatný a nezávislý (funguje oběma způsoby), `sec_edgar.py` už používá sdílený `BaseFetcher`, takže potřebuje tenhle způsob spuštění.

Zkus to a pošli výstup.

---

# you asked

message time: 2026-08-16 13:57:56

(.venv) PS C:\HERMES_FENIX> python src/ingestion/sec_edgar.py
(.venv) PS C:\HERMES_FENIX> python src/ingestion/sec_edgar.py
(.venv) PS C:\HERMES_FENIX> python -m src.ingestion.sec_edgar
(.venv) PS C:\HERMES_FENIX>  kamo proc to nic nedela? nahaze ani error tak co se deje?

---

# claude response

Tohle mě dostalo, ale mám podezření – **nejspíš pořád běží ten původní prázdný stub soubor**, ne ten kód, co jsem poslal. Připomeň si: `sec_edgar.py`, co jsme vytvořili úplně na začátku (v kostře repa), byl jen prázdná šablona s komentářem "zatím prázdné, napíšeme spolu později". Pokud jsi ho **nepřepsal** obsahem souboru, co jsem poslal o pár zpráv zpátky, tak se spustí soubor, který doslova nic nedělá (jen komentář) → proto žádný výstup, žádná chyba, nic.

Over si to:

```powershell
Get-Content src\ingestion\sec_edgar.py | Measure-Object -Line
```

Pokud ti to ukáže něco kolem **5-10 řádků**, je to pořád ten prázdný stub. Pokud kolem **190+ řádků**, je to správný soubor a problém je jinde.

Pokud je to skutečně jen stub – potřebuješ:
1. Otevřít `sec_edgar.py` z mé zprávy výše (ten s `SecFundamentalsFetcher`, `SecFilingsFetcher` atd.)
2. Zkopírovat celý jeho obsah
3. Ve VSCode otevřít `src/ingestion/sec_edgar.py` ve svém projektu, **smazat celý dosavadní obsah** a vložit nový
4. Uložit (Ctrl+S)
5. Zkusit znovu `python -m src.ingestion.sec_edgar`

Napiš mi výsledek toho `Get-Content` příkazu, ať víme jistě, co se děje.

---

# you asked

message time: 2026-08-16 14:02:49

jo ja to neprepsal lol. musis mi takovy veci vzdycky rvat capslockem haha. (.venv) PS C:\HERMES_FENIX> python -m src.ingestion.sec_edgar
2026-08-16 14:01:54,357 [INFO] __main__: --- AAPL ---
2026-08-16 14:01:54,358 [INFO] __main__: Stahuji CIK mapping ze SEC...
2026-08-16 14:01:59,572 [INFO] __main__: AAPL: staženo 25046 fundamentalnich zaznamu.
2026-08-16 14:02:01,206 [INFO] __main__: AAPL: nalezeno 692 'whale' filings (13G/A, 13D/A, 13G, 4, 13D, 8-K).
2026-08-16 14:02:01,403 [INFO] __main__: --- MSFT ---
2026-08-16 14:02:04,539 [INFO] __main__: MSFT: staženo 32536 fundamentalnich zaznamu.
2026-08-16 14:02:06,716 [INFO] __main__: MSFT: nalezeno 789 'whale' filings (13G/A, 13D/A, 13G, 4, 13D, 8-K).
2026-08-16 14:02:06,897 [INFO] __main__: --- SPY ---
2026-08-16 14:02:09,210 [ERROR] __main__: SPY: fetch fundamentals selhal - 404 Client Error: Not Found for url: https://data.sec.gov/api/xbrl/companyfacts/CIK0000884394.json
2026-08-16 14:02:11,908 [INFO] __main__: SPY: nalezeno 0 'whale' filings (13G/A, 13D/A, 13G, 4, 13D, 8-K).
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Haha fair, příště to zvýrazním víc. Ale výsledek je skvělý – **funguje to přesně jak má**:

- **AAPL**: 25 046 fundamentálních záznamů, 692 "whale" filings
- **MSFT**: 32 536 fundamentálních záznamů, 789 filings
- **SPY**: 404 chyba u fundamentals – **a to je správně, ne bug**

## Proč SPY selhal (a je to OK)

SPY je ETF (fond sledující S&P 500), ne skutečná firma – nemá účetní závěrky, rozvahu ani insidery v tom smyslu jako AAPL/MSFT. SEC EDGAR fundamentals a Form 4 dávají smysl jen pro **jednotlivé firmy**, ne pro fondy/indexy. 0 filings u SPY je taky logické – ETF nemá "insidery" co nakupují akcie.

Tohle je dobrý moment na malou úpravu konceptu: v `config/settings.yaml` bych **oddělil seznam tickerů pro OHLCV** (kde SPY jako benchmark dává smysl) od **seznamu tickerů pro SEC data** (kde chceš jen skutečné firmy). Chceš, ať to takhle upravím, nebo to necháš být a SPY prostě přeskočíš ručně při přemýšlení nad fundamentals?

## Co dál

Máš teď funkční dva ze tří naplánovaných kroků (OHLCV ✅, SEC EDGAR ✅). Podle pořadí, co jsme si řekli, je na řadě **FRED** (makro data) – je to nejjednodušší API ze všech zbývajících, takže rychlý win. Chceš pokračovat tam, nebo si nejdřív chceš data z SEC/OHLCV prohlédnout/proheatovat (rychlý pohled do Pandas, ať víš, s čím pracuješ), než přidáme další zdroj?

---

# you asked

message time: 2026-08-16 14:09:48

vic rozeber napad rozdeleni seznamu tickeru. jak si mam prohlednout data? to bych udelal. rovnou pak rekni co mam udelat pro FREDa

---

# claude response

Tři věci, pojďme na to popořadě.

## 1. Rozdělení tickerů – proč a jak

Problém je, že SPY (ETF) nemá SEC fundamentals ani insidery, protože to není firma. Řešení: v configu rozlišíme **"equities"** (skutečné firmy – tam chceš OHLCV i SEC data) a **"benchmarks"** (indexy/ETF – tam chceš jen OHLCV, pro srovnání výkonu tvých strategií proti trhu).

V `config/settings.yaml` nahraď sekci `ohlcv` tímhle:

```yaml
universe:
  equities:
    - AAPL
    - MSFT
  benchmarks:
    - SPY

ohlcv:
  interval: 1h
  period: 730d
```

A v `src/ingestion/ohlcv.py` najdi na konci souboru blok `if __name__ == "__main__":` a uprav ho takto (OHLCV chceš pro obojí – equities i benchmarks):

```python
if __name__ == "__main__":
    from src.utils.config import load_settings
    settings = load_settings()
    universe = settings.get("universe", {})
    tickers = universe.get("equities", []) + universe.get("benchmarks", [])
    download_ohlcv(tickers, INTERVAL, PERIOD, OUTPUT_DIR)
```

A v `src/ingestion/sec_edgar.py` uprav stejný blok (SEC chceš jen pro equities):

```python
if __name__ == "__main__":
    settings = load_settings()
    tickers = settings.get("universe", {}).get("equities", [])
    download_sec_data(tickers)
```

Tohle je obecný vzorec, který se ti bude hodit i u budoucích zdrojů – ne každý zdroj dat dává smysl pro každý typ instrumentu.

## 2. Jak prohlížet data

Nejpohodlnější způsob ve VSCode: soubor s `# %%` značkami, které VSCode automaticky rozpozná jako "buňky" (podobně jako Jupyter notebook), a ty je spouštíš jednotlivě tlačítkem "Run Cell" nad každou buňkou, aniž bys musel spouštět celý skript.

Ulož jako `src/research/explore_data.py`, otevři ve VSCode. Nad každým blokem, co začíná `# %%`, uvidíš malé "▷ Run Cell" tlačítko (nebo najedeš kurzorem do bloku a dáš `Shift+Enter`). Otevře se panel "Interactive Window" s výstupem – tabulky se dokonce zobrazují jako pěkně formátované, ne jako plain text. Je to nejpohodlnější způsob, jak si "osahat" data bez psaní celého skriptu pokaždé znovu.

## 3. Co udělat pro FRED

1. Jdi na **fred.stlouisfed.org/docs/api/api_key.html**, zaregistruj se (email + pár údajů), klíč dostaneš **okamžitě** zdarma, žádné čekání na schválení.
2. Otevři `config/secrets.env` (ten skutečný, ne `.example`) a doplň:
   ```
   FRED_API_KEY=tvuj_klic_sem
   ```
3. Rovnou ti píšu fetcher, ať máš co spustit, jakmile klíč budeš mít:

**Shrnutí kroků:**
1. Získej FRED klíč (odkaz výše) a vlož do `config/secrets.env`
2. Přepiš `src/ingestion/fred.py` tímhle souborem
3. Uprav `settings.yaml` a `sec_edgar.py`/`ohlcv.py` podle bodu 1 (rozdělení tickerů) – volitelné, ale doporučuju udělat hned, ať nezapomeneš
4. Spusť: `python -m src.ingestion.fred`

Vyzkoušej `explore_data.py` na datech, co už máš (OHLCV + SEC), a dej vědět, jak to vypadá – a pak spusť FRED, jakmile budeš mít klíč.

---

# you asked

message time: 2026-08-16 14:23:39

--------------------------------------------------------------------------- NameError                                 Traceback (most recent call last) Cell In[3], [line 2](vscode-notebook-cell:?execution_count=3&line=2)       1 # %% Zakladni statistiky (min, max, prumer, atd.) ----> [2](vscode-notebook-cell:?execution_count=3&line=2) df_aapl.describe()  NameError: name 'df_aapl' is not defined

---

# claude response

Tohle je klasika – buňky jsou na sobě závislé (druhá potřebuje proměnnou `df_aapl`, kterou vytváří první), ale ty jsi zřejmě spustil rovnou tu druhou buňku, aniž by před tím proběhla ta první.

**Oprava:** jdi úplně nahoru na první buňku (`# %% Nacteni OHLCV dat`) a spusť ji jako první (Shift+Enter nebo Run Cell). Teprve pak spouštěj další buňky pod ní, popořadě shora dolů.

Obecné pravidlo pro tenhle typ interaktivních skriptů: **buňky sdílí jednu společnou paměť (jeden Python proces) a musí se spouštět v pořadí shora dolů**, protože každá další často pracuje s proměnnou, kterou vytvořila ta předchozí. Pokud si chceš "poskočit" rovnou na nějakou buňku uprostřed, musíš mít jistotu, že jsi předtím spustil všechny, na kterých závisí (typicky ty nad ní).

Zkus to znovu odshora a dej vědět, jak to dopadlo.

---

# you asked

message time: 2026-08-16 14:24:30

--------------------------------------------------------------------------- FileNotFoundError                         Traceback (most recent call last) Cell In[4], [line 4](vscode-notebook-cell:?execution_count=4&line=4)       1 # %% Nacteni OHLCV dat       2 import pandas as pd ----> [4](vscode-notebook-cell:?execution_count=4&line=4) df_aapl = pd.read_parquet("data/raw/ohlcv/AAPL_1h.parquet")       5 print(df_aapl.info())       6 df_aapl.head(10)  File c:\HERMES_FENIX\.venv\Lib\site-packages\pandas\io\parquet.py:671, in read_parquet(path, engine, columns, storage_options, dtype_backend, filesystem, filters, to_pandas_kwargs, **kwargs)     668 impl = get_engine(engine)     669 check_dtype_backend(dtype_backend) --> 671 return impl.read(     672     path,     673     columns=columns,     674     filters=filters,     675     storage_options=storage_options,     676     dtype_backend=dtype_backend,     677     filesystem=filesystem,     678     to_pandas_kwargs=to_pandas_kwargs,     679     **kwargs,     680 )  File c:\HERMES_FENIX\.venv\Lib\site-packages\pandas\io\parquet.py:253, in PyArrowImpl.read(self, path, columns, filters, dtype_backend, storage_options, filesystem, to_pandas_kwargs, **kwargs)     240 def read(
...
--> 939         handle = open(handle, ioargs.mode)     940     handles.append(handle)     942 # Convert BytesIO or file objects passed with an encoding  FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/ohlcv/AAPL_1h.parquet'
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...

---

# claude response

Ne chyba v datech – je to o **pracovním adresáři**. VSCode Jupyter interactive okno běží podle výchozího nastavení ze složky souboru (`src/research/`), ne z kořene projektu (`C:\HERMES_FENIX`), takže relativní cesta `"data/raw/..."` neukazuje tam, kam čekáš.

Oprava: přepíšu skript, ať si cestu k datům spočítá sám nezávisle na tom, odkud se spouští.

Nahraď tímhle svůj `src/research/explore_data.py` a spusť buňky znovu odshora – první buňka ti teď vypíše, jestli cesta k `data/raw` sedí (`Existuje složka data/raw? True/False`), takže hned uvidíš, jestli je problém vyřešený.

---

# you asked

message time: 2026-08-16 14:27:58

![image](data:image/webp;base64,UklGRlZbAQBXRUJQVlA4IEpbAQCQuQWdASqwBTMDPm02lkgkIyIhJFJaMIANiWdu/l6/0eS3/qtZD/e/cB169L+gp+Qfy7/O/2bzgQc+n+gP+Qfzz/mf4DvTf6bzqfFv9J7Fn91+pnqnpAPzj/1PXn/df+r/Sf6X18foX+x/9n+y9xH9G/sn/R/vv+i///feejX5run/6jrvY5+Jv0A8tWd/Y8cZ4hvsvQA/jP/P5jvIq50f8U8x3zTtBL5P6Cv4t/Gf+1/e/yH8Bj7APgR/RP/neK1RLN+6Nan3v9f/5epniReAZa/wvf79GH+U9Qj/C/3T1of/D1s/4X0Fft3+1HvKf+f94Pdx/ifUA/qfo8/97///9v4MP7d/3v///yfgO/o3+m///tXf/j94fhh/0Ppa/+n1AP/x7ZH8A//nW3+af1f+0f3f9oPg18w/Uv8l/c/89/v/8D6S+P73F+4f5T/rf5P5K/oX/N/xPgu9E/d/+R/lP9P7BfyX7efqf7d/kv/N/mvmb+9/8T++/5n9qPQ/83/bf+H/fv9H+0nyC/lH9D/2H9z/yH7MfEn8P/z/8v/ov/F/qfGO0j/L/9L/J/6j/vfv/9Avrp9Q/4f+A/zn/s/znon/3P+C/zX/t/f////Q/6J/bf97/fP8z+1P2Afyf+r/7r/Afvf/pP/////uL/W/+b/Sfv/6Kf3f/Zf+n/T/lv9gf8+/vX/d/yf+p/cH6Vf6v/0f6X/Yft/7bv0b/P/+j/Q/7P9wPsH/nX9w/7f+M/1P7gf/////fl////b8Mv3t////r+JD95////38eyTpfI2GbJ5HYtbTaFPfYabQp7gaEdBFuYd694qUpy3czDap2WgbAyT/cst2Q0Um9huRz+eFeHmLH8DhT2XD7eovzcwxRw8gdTS8jyBg4QKZVBdU2mbvlJriGl9NaDqfz25G0FBwTuBQ31mLwUpsaDN0xiAXZnBRWXR0oxlUyQmWYGmPdXgiBTLRy/mPj0uyCqwtlbRJjlC+LKkZxe2LgTxdHoYf8IAGeS95HP0rVTA+UpmV5CfQ9YKYmMKiAn8+oWrgPT/OXyR08IXrQ5aDTKmSURAvQzvM/O4z6DwDrG9egRX/uc5phx/ETkwWCKOvHcwPQiOpGEERlpqrbLTlrFXVzIVFCEzthzpsruje2zQNqJBCA3/T7E2Ur13C5NsIltJCKm/xcfjXBuNutbqssrxJC1SWibGAwncFqEvoAtE6XJMSjXycNPciJXt9cwlb46I5WJ79wHOlMoR33aJ5QSzIh2DL2ScReilB6/B8nJO/Nf09whh0K4Yw4QwJhe2EMCYXthBf2+4qEA31S075QijgR0FFQnUX2Yl1z5Vtsvjmy94b8gi7paHXbJNl73nzPct10vYUaq+zddIoQN8AajBAtEUtnIGv0FovhROuCgaV2ICqWe6six7Tzul+V+zZtHEi1EAGvKjfCDXEnbRj7+foc8OhHerClaMfHn2lWA7oOnitw8Mh4RBCkUAK1Z1Pfv5+zoIUigBWrOp78eTDrSgb2g9J3dWHSwPf1l7IPSwPfvsezTRC458KIn6u8EFqyAN0Sk2DMd5zaSFGUlyqUYbLThd1Q8l35X7+fs6CFIoASpPbZM18bymzJ1rOMhVljwqqfUFlOcNCI2KlPa/jyRSQpSYijCtsVztLAQhCKzKCEVmUEIrMoIRWZQQij50R3SZ0dovjupDMA13PtftaL9PqSInSNfQMuDUlY+CzDrF6ty8Q69CCnea6XKWnqazKXVul48wgUmsB/PTLVMPycB8fCImLUuj1pfSQfEZfqyv2a6cTsQWEyLaXiEe1k4qXqDqe2IdzBofh6Yop5QFX5jzigY3rnAWDSG6sS8LGgYIGydBhgTC9sIYEwrJcNXMV3kJewYgMRo4XjV97+kfOYiNh9o5lx5bqUHNrEC/5Wea1dAtkf5VdixqG3cbTdlQcIYEwvbCGBML2whgTC9sIYEt1R8I9CXONXPQw/Ip7NKOKmr9dYWyvMWm6KZ/QFb2HKfOhLPBTuM+mOiCm5tccQ7HtWQSeDZ6oPhLq1nsdqJoFMLCCzMY2+TYJyMeM+OaRfYUXMSvBaj+xQqKanYlKvWWMCbgG92Py9QAmMRsu3ggFsZVHyATNhzyaQgGsVGL1EMwJheoo5JsBZcPUL+lymAxjkQnr9D2cyqZRfndKbpGGxxM1SYAVSqU3VlgbLV3no80BLBewnnqJgPW3xGh74KMBhRhsFjHprqQi3sFcqY1zmfNopjtmTo2Ufe6zb8RW1Hfbc/BAObL/jZLrGImFXN9vZcx6PKQj+YpE1oZsZxeYwD28ngBfFrF79qbe+UaqxAwAk+RuPgn9j2Ta6dDSwNoOaYf4tPM86wwdohgTC9rgPwuNnOqaQFt4xfIj45lMWTmaXIR6hhgtcAEvTnBVSnHVCfcHXHYi0aLS6bMZJNY8Zs0zsZIacETQO7rOK0iwR7eLQRz+1+fJva+ZInakhsIzjAj8DQGKcAep4i7WUVtSJAJwJheqeymcx6+7uZgANRUTYakRaRBz7QM80JUfeUcgrOFCmK3tFpgo6d14aNUvRS44dVXs9aZAhzBjCIn9CuXbOTfhFf+cuFiDtLc6x9mURKvxSLrAZGxDe2SmWKN30UhhmdmvwfgN9CVBNBE6qBwVjSJJZo9G2lOmR8Ejm0/b33sy0iSQolCXGn4z86rIqNKblW+uqbN4DIPbsn2vIClG5itcq4ZSsQja2JB8cF8opf38ggwMPa86/tR7mRp7fUk30qfZoRhxHrggrbOI+p3h4sFKXdB2+uuaPL+Hl12SRLfEXGk7ZHCGrVD3s+sCb0GFacHxsSxBn3/YV/o/hANKww5Ur4VWIfSTfbjBv1ONs9/DHt0C1ATp8rPiD8y/XOFCuGMNxYdRt9oMuMtY63tlXeJaMH5vQPU/HilSsTWG/6rqv4sU4TkKZFArCphnybu5Tslrx9sRriNii0k/5ugLV0MJzFGsKVcxTCNglUi+H4QXJIfKdmjp2hWSyoI7NKn6jmWXYPiyv6MTOyjwYLNQlkyyffyjz6Bts1s2V4oZ7q+PEN+6kPOfQvXzFD1LquK1/UMrg9NJEW4fD1sOlT9KTgiBkhKFAQO8rXwUya6jEvqAw5vlJ57QVWXWFDCzHbRcloPzD5vhZg0S6P4xyq/D1gaeRgRmKX96AIf+sj9EvBnDC9iCH3cwysvJzGZZbd+hdfR/p80u138B9b793J/UU0363Qj0KvOtPR7BUHtkLVCcI+EGOD9F9CN09+PQ8HPDZb9S12tpVxN6as3vgTC9sMflLXA1GALmXN9KeSMLDTTdw43PJKfqlsdQvf4mpUNmHqFbiUYKTkkoOlcSxYsflOLdZlhy0HOBJbeeRxGhhnLWolo9G1SNwngGm/wZ0+n9ksJNngvksdtut81wolGUiSbqMp5grktKW0X7umy+rE2vFCl+ISsYSABN+0FbTbM9UjV4UFXA3zPHqkElMYLBCzIIKFxchtDjyGwMlu17BkFvO3UIq0esq3VCa+1DoNxRWh12ywyhXAGkBi4ZWfSVF/pJZ+tVAW6XVREwvbCBUwm98CYXthDAmF7YQwIMf3k4vsC6bcSbl7fL6lU5AZfQx2D7CiOS8ha0RZmDD7ufySxoruKyc8nyqvngvwIbcyD980K4lFBOD2beMCncafjg2EoSllfJLIIXhAA/NAqzIOtsdJyN7TlUtpr5LPxz68ODceNwW06Aqhw3hN5HeRjZaWWJsw14lQY5s9grBjur8SBr7HeRanjJhfnZoUtkHP4AQpu+bJU70QKWF/eaUcfLQyn2g6SqQpVETC9sIYEwvbCFqaz7uZwQqnmZEkm98CYXtfeNeHCGBML2whgTC9sIXoG3MMQ6iSxkWHlpy4602TW4xZo9mNKbq4Pl8ATEMaKF5wg53xmM8Q8VToCyYggNlBbGrmEuTWG27RRdUjr6sklngUSau1X+OvlQHT+CO+rlu7oEP9Sd99S2fHGU01b8UeNsAbyMctlhlCuGMOEMBY74umpAmysu7tS+eUjRsfEm98CYXAOHDGHCGBML2whgTC9r7x1dQiUfMsBUKsixRK/4AHkVN/RxMAJeWcxzj6SAIndpgAkYCdj97F5IYIAjRs5c2sqjknEyGAkRShZQMPuYKF1UHK2yUT+GMCabFW6AYKiVB9UMCdHR7SgjGz0Dk3hXrnFV+lfNm61GpW+n4/xanbwxlP/RFKTiV81nn3iZaTx1QGrz9LTMFYD11H8ySQAs0sJclA7h8oo5dqk61RNlk3A+m1FaFRY5s7rXcpdPhw0+ggKGlbRX7bMAQ0xCbKOHGy6Ytnt6LxlhlCuGMNxSPckQ54ijQvUzCKGUo1hhDAmF7YQKmE3vgTC9sIYEwvbCGBBj+RNHVnxaDAv4NuuvyM0xRSSY1NFRwmBJDe7NwJiGNFC8x/l7/R7MaU3Vwg4BfFKUEBNofMbpkBKsmWUFz0aqwaJSMBmwYgQ/PdiWwkB39Uj/xYvA/8ziywONcsGCCBaBhs3z8DtMxq9be5m0QM0/d+OCYJ+fi/UMCdG7CtaPEOo5wcPRXzqkgrm4CEG4Ap4F7c2gqAzC4UpS9YFePTVojRn+jtbzW+9x3w/mTkJBI+D+NN0sIg6mqnUpZWZ5znhSfTtDkFeNcn4WiGArXp8b97k6ykn71mUVobk5/ANrBjf6OzP8grGN6CVtUHCGBML2O5ZxJvfAmF7YQwJhe2ECg/TiLl7FNOsMEFgeSaDSt3plcMAfX2fOFHfPF5Oxsc8Je4NelgMyBqLTtocT4GyU+GXT9E+4q6oVFuMqlk+5Mty2pLzYR06q/2repndE7xugllc9knju/9Pwxq8VtoYHqcK+wLswws1ahb6bPz0ld9ZgX4wtwGK0A3vXB6sB3deD4w5Yf6zXl6Z6EEbZstfmUTe8W6+7Sn7ARqMlniFuvsZ3nB50KJb8iQy76a0O1zWNTq4i7UIdiewjTXVREwvbCBUwm98CYXthDAmF7YQwIMplBKz3R9iy/CvnbOtyb3V7f4RxEC72+NnMvglY+1YsU/090hRcRQr4vXCZ/4yS0h3qW29Cnofc2CLcMlAy2X+RzYom/69obPjhVHv5aN+agexDxK4S7Wu+BI9RxOPakTDr2uv8u8X+b/jhGfdHGrgrPKAQX+IOJY3D9e27DYrhVqe32ILNd3Y/eQUY1KVoDXslHdiorO8izLinfDR9NTJCPCk8fU0XaeiOHU138ln0hhVrwNIg7IPyn20/iHrLa9SQl8jawAUk+iYO6YcVhoddssMoVmosiOu2WGUK4Yw4QwJhb+lu5JBDrRF++Wt+F/2QdklrVxrNHLzs/S0YOlv9vdXt/hYNZH9wYK7Z2ihzMV0zeyUBJ0HkIQ7n4kn6iSMJtJvkAH9hO3wT3X8L6y6WGv4WrWXxT1lLREh6jM89jhs9a423CZxp+bw9L1KmNEVa3R/lGX1IZdA4uPaMHuFYm09mkEYgWyOek42q2h8WsJE7Xuvf4CB74odOyVz+YBLr0h2+E4FavrLMtBcv2LTWCx8i1Z5ez1vNKd60r/7xZg57KEPeo4gXU+ZKQ8ShI6XQX98zKQChLAyxxe+PVm8esKW4mbWCkQPuunetJr0O93uTHqawpTB0xcGdKABGX+e0/+zw1GzATactDrtlhlB353KFcMYcIYEwvbCGBL8FTqi4hePC39tqIlC+fTGlXMiGmSzUwvdCXQfPSH30drTLcQEZ0Z8WNYzGZo8cOk2/krAZ4SWH9dkHmXDJvE81CxgTqtSm85xJe8y5lWbUhKQ8b5IWyjtZ9ZkHYivmfb6wBbI4+gIQLoj03F/WTxKOe0DthLqjl0s+M20kErVlplgFPrPUAOfmwVOPNloPLMbzobPzwKLXbR/HNIjeCkbX+0g1SRX+qt7oac9QXu3SekeGDTptdi1VZPkxNdCoDTjVlSBrou6XC58G8FjuEeOaYVfGuJddJARPBB+k/C+jUC2sodJvfAmF7X3jXhwhgTC9sIYEwvbCF6Br1gAqrRPNyi6tvKP1DX8urbiaNTIHqf792Mf5WVGfw5cXlXfT3fkZa/IvoaBZUuw+r/+nWdaCbAH4TVwbNhTYk1Z1iod6mJGoeZy7X4Jj0uHMopmXSHkoqHcgJp+W0YZqNfbftVRR0pujeq+EBmhtWpL/XL3bJbu3+69E8B5z0XW7MmsYrrbVeWCWcd73WezMx/M3rZQjSd2Mj4cR12ywNDT7BTDoh4GwfjiFqyY7ZYZQrhiWuHDGHCGBML2whgTC9r7mEleU9tYubyVIWQon1ED8IH8BgassXcqynx/rQcP2BsGdH30xBFJaXKIoYHJUxxhqhRQd5pqAV2UyE3Zw7leUHeTLVOjb5xwQdteYlP65FFuUrbvFNNOnqUrdwMV9CF22+UcQ5ldxqOrPT6jZv77qNxHneOZ+i6nMiloddonLKotAP/kQ5UEEKPZF1URML2vvGvDhDAmF7YQwJhe2EL0PJUgV/I5MAH91AUsTgkBgyj6Esv5tX0DHaC9BToa9a0hGxUDddwPrKCZmIWaQK3FmL+ZHAINPfsliakRv2fSQThi34DIQN/sTgbtpPkBcuv2f3QV4QSd6p+oLRT+6vkhwoGSiv4ys+D5+Wvv3cd9OjJD0YxpmSaz7gRp7rsNNlVuwPlEyqlAcovqLvPtYYp3ssuP5QKy8ZNqPZzBiHvBUI8BD+7WaVXfr+cYS70+X0P216XzOs6/HB+NTy+c37VOJSAd2mD2tYcnMRAMwjbcJMi7YZqfi055YiWAx0E0eqYzKeZc8ZhPkqmmsr6TJIhGzwX5HbLDKFcMYbiPTuTgC6f+g18fhkMAsT7diOu2WGUKzUWRHXbLDKFcMYcIYEwuAcvHht5MrFPa3ZiNGrBWT1lcyUxYVSlaqsS7oUe9X0OPVW/Pi/SBa+1Z9R0zvStacYYPLYEvYLm4cmBw9zRnO8KNc3BOCp08ZCcNtx1myASbf9vI6WFvPU3lAXU3yjYuF29vgfXZltUYy1dyXQl/tN8okR2sZWOL2whgTC9sIYCvcTKN3p5fPJ9I40hVLAw6Kg4QwJhcA4cMYcIYEwvbCGBML2vuXDWWUaVGU4z0OeEOnPiqH737ijxlPgMufs1RA7RHfqOCOdKT5X24b0Li/8OEUo2zRFhDY2y1YEJDlReY4K8/iA8ztCt6ElABGE4Q3/3iwPy0ZBR0a5KnJQZfctoNzJzfifbWXXsN4+QNBC6hqT2D+Msf9Td3fsx9kuV71CAZsoaC0UJn6X7GODq/QeonkK/RNSU7z53N+XaeHjW/e7qmKXOT2w7Se1loH80zPhIarMX/1PmFIm8c8jjIz3pYiDLmx1FWlWLHVkYdIF0zOPGZLO+xDUWGUK4Yw4O9DEVaPqxRCS+FCuGMOECphN74EwvbCGBML2whgQbiri//hGpw/P4w2cyyQF0/Pl3uk9KtCH57EGucrIIO/sBiD0AFgRAUXa1Ju/P856jJ9ytc00Rr+VzWSrXnzIb1mol/9nh9jjeFfA0HPW9tavkdDjQyM+yP1++yjcX3IQ3pr14RxooKsXiI91JGXZRu1IQ9SM6iktXfcVl9h7BEo/YHekqrYfPAj+L+vvfpcqR9++DTKSwXv1B1e578PiXhdfkHtVAZ5RQrLz+Q/QYcKB5xB0YP9qzH4EHd6mUYU3rIlxOUa541n7F/+nJ7j02C026OEOZRjcO5TTeTJ4qFddssMoVwweo8eAAVqy8eWQTJE74dssMoVwxLXDhjDhDAmF7YQwJhe19yzktx/XserYnlRD1V+CdplDo9Vei2neCK0AX6MgPoZcmKW8SvsmLXgSLSXNw0omP4exVmwzh66+MfuMO57lKV9CYNTqQd+X70odvbcr+L9W91rXTCBouNtoPvLE0Q97LeBCYZaI/I69hMuSzOBfuwH8KarTb1sT0HBJ6Q/om012Zdj1QA0NIaktn4sOzFSxxv2f6bKz0dt+pLzcaPMXlAKV09qUaGHeSYpGhPkeDjvgTC9sIYEwvbCGBML2whgQbgr5eF7YQwJhe2EMCYW/k2Kpr7D8EirLfGpv5GnoXwcGLm7gifTGw/PL5XI/svf6iCvhlm9wBnLZY34cQCX4EwvbCGBML2whgTC9sIYEwvY7lnEm98CYXthDAmF7YQKmhalqDhd67ipjHVyUDG2BFXxPckX1f9jjUX5p+0RDvdeCuGMOEMCYXthDAmF7YQwJhe2EMCYXqQWRCHIQBqIWgTSwI81HonZMoVHvDbMHhcA4cMYcIYEwvbCGBML2vuWcmwwGgb8/2XxhEGownn1a9y5qeFlGH+O3q02pVczCjPfsjvPnh1wIAO+izjq+cJqSa6Q5cztX49HRVGGkDs7bCGBML2whgTC9sIYEwvbCGBML2wha8bNaGbm59lCTbQDr0+jyw7wi1flA+O4adk8fyswwVO6vbNL6wyhXDGHCGBML2whegZecblM5CZuwCjzbAQ35qMSP8EJ2xSz9Ayh2PjN/HadzlhOvXoEm2KW0d3Ao7toeWHgydA7XdAQNpoysaXlsxWaJmk6zhfU104dPh+eekAuFMqUb8fEZW1K+rYqGekmHwGCPCMry7wLVq6enWVwtlf1k0HRhtkchdRZbI8/TkqMlJ/wm7ksSteSK/E8oaX1jdQg9jGClkaPtDYiZ0E9S+wWnfiyEifwlEAgDLgxFMK8wmw1ykA7YiS7hfh7bfTjsF65CWN2y3Rv85z5eF7YPAA0OfHDbNBuVkJVTXbfHig8MEwddssMoVwxhwhgTC9jmo6r1ZFq2bcvcOGjUJWEBipcL2whgS2xXaXu+RcEuEJ5tLetUcx9/khfEZR6HIty6On0LlZ2h2hYU8fGap/PoMMREA1YE6zYtSOogmn3KmJ3J7ILVmr/RnrKIPOiGEu5jN55mhRw0oKJmsgFsYiJrOIu4tGu7pQ9sn5o/raMlERWZGR9dxLwFBOIaX01oLpvPbkasyegeYxHDhjDhDAmF7YQwJhe19zCF2kuuGC4f9nNCcDPq7Qez1/ZTRFqn1HvN0qJq2oyS6rIZLJE7y9ASBAlBcc1aIfjG3LVuT5Mmt7hD9DyFwSAkYxi7iwZAqXHifiYVnpNZM1cURQee+IesbtAE9+8VBOJvuXsrhxUcxaWc0wmghSKAFapajyaz1KfykUAyUHv3M9FZxHENL6a0HU/lOXYMCYXthDAmF7YQwJhb+TTgWMzocz4ThxaIXegf6rr9az7I0nDdBDgkd2mI9GPf+CLKE6V7cfBKk+Mg2qRI99i4geqDtdyD7/uDojzO4aeRWA1cWogBUb2rVD8IwAgj+9vm4Z79+JI6DiZFLQ60ryovsK+OviPdn6MGODBa0pdJsqEB7IQ2N0QEN/IuruBPLF2V+DPNKa9YCqj12/YaLBNdZ7G0m8HyYMLR2RZ9Y767X29WrhHusLVDT3PdSxlwd9J4iJ/QI71TN/Pb4WXmnin4K8QqV5f+agzAmF7YQwJe7bvU7xmUFaHXbLDKFcMYcIYEvxSL/Def/pgK5jqViZMPrAQDJ5nAW1YNcvt6vwsADpRvLZgwfz+brVqnyqFfFtIcftR4nVPxR3KzOuylHwDS6+94oSoCGG2VJ7MkhuZZ/O0b+M8wlmEpfkJeK8QE/BR/t8Hf18Bi+2LxARWfhPf9/Y+QPQNB4E44EZzgv9LCo8AvCXxZRtxXPLI+a3FRsHIvkoTzqzjToNBX3o8eGClg8KkolO31hFGPd8/YXP4ySwEedCZp8mgX7yXPMicI+ri+jo/53LA180sTr9bCGBML2wgRoe/he2EMCYXthDAmF7X3jguy18JNtLTu1BsbA3hoqF0pbsUhO7ip94Mn4u+sxDyTPvBvJABoDCxqKJI+2UdZ04ZwC40bcp3jdaCUS/9CWFlfQR9+PPgqrxDpnqsGgUmSU2b8iflHEhlTWB7VbPBWpnvqkPrkCA2wtF4VqS21fEfmFihb8sD/9G6H8qKAc3xhzf0I//DU2WOvZ4n68rk4ZKKwj6VP8KUQeOcmANG4AOIAEGiCLlEQ/YCvhkVjKRdrOg9ZX8zgYdoGV6GgIsBlgYoTsHngeDK6teENjnqgNsfi3tGLy+Av/8x2OolQAXIbbxoApU0OMWe3eQdrQkwZk+AjktinPp8bWpsikvQPm9L3shsUYIy8L2whgTC9tMj1qoiYXthDAmF7YQwJfikZarXg3adXtBKtR1FfgHngT+e6EzKXavIXoB2mhQFmQD567QJNJg0R5WnWvfSEtxfjXYzbqXjbwPOe87PsMMBP7lAoZS7bLDKFtWWL/i4hMemM73CCmUknQey5PEB8l2I9HXNAdaTUSe9wWs+JUmuQoB7FUuFZXikuux0ce8OME7sXTZStHWaO1uoWnG7LxCyoy57reVLXQe/ZkyYoKtCA3lWGGBML2whgNLEflZcn1puvDKFcMYcIYEwvbCGBBuNkNl2XgS6g/TuDb3+JSsm5Fbgd6BAMikXcOnTSq1Eg6Wn2YZ+y8c1K8QwsHFkGXp1SOLTWWUvSKJkjYV5CG+Lf70EL3/Dt3cnoZeLqQ5GAva3VJvMxSr1q2+zE0RX/c5gKYTrlTQ1ZP0mOpFmxmkK3qUKw7maApMdoc/W3t4h55dWvyTNPzwCAlzcVdO/G9U1miM2j+SNjiHHQuaMRg/V3dcANEOhqDvOlktDyMuhIeRPUfgMqvvTo0eEMywxom8hvz8P+fRddYab3wJhe2EMCDcFfLwvbCGBML2whgTC4B2wIyWI0k3SHIP/J/UX4r1IQ3xeuEx1yL6v+zXassZJbAePGw2YVw5K68UMiln60LcQtRureVVBQcyJvFYFtMapIi06REDfjT2PO+mxMy5l0ZApVQ5Y4QleoqKvyxVveWFq+UpkovNuqXSnG2ixY6nQr336dfWvvAfS7s+TmMz7cg41FozUvCkNsUsso7ZYZQrhjDfdfr2AApFPdXJXENL6a0HU/ntyNoD+QyZrX0/wqa5jYiE8xfbFnIDCYjdpXQCbnP/wOHhuilMgLiXXm4nl3wgrsxMkVeG7yp4OxbdbD1XQpEhgiudJldu761w5FfXbKi+brr1k+FMPqlnnRRVBArQEuZrOVV/yMgmugdxt0a9RkwEx9PZ3xh9iBnlFWQvG/wE8PEyRoUyvrMnRb10IPxxjRZP/sp1FMJeMhMbp4jhk6QUMfEiueKrfNIJNhDLzsYX81ZrrUxbG74rH1yzz35Z9qan+2a5xwfVavdS1wlD5qQLOhpsK8hDfF64SALGch++HMKh8yEfdcb7mlYqYiG6ob2A9eFbVUAQefUzOOoc5Y5zYiLdBfkXrD+nT7AHsdwsYs05gqwyrZLu45+6eYMhjU51LwdiL+/dPEirAuUCU8f9yIH4iwLv0maasoHIgnFM/RKh9+zUr9Wxy18mPCr2jgbtyu1rJRSI1OjqHEpQDJykR3OrdKcJKeOiU8IUifkfRFceYsjJDL+OQnEVPjs0EEJQ/LTbEGi1sNiNX07XrbxHQ5oh44l+ocmFXXjIbDwDqbYlgLVHD7vzSKFSI7gWL5WzD9fSzbo+33hbuBATS/iHA7PnDb/CxMfJy87NUGmF19nb3V7f4WJj5NS1LbD7gkeJJVYc2GUG/r//Ik+WMTRzhYubsKTllnK+7PJY6lP4SNdV7Hm8lTaS0vLXsyPNyXed1ABCrsvX0tS009KNURGIwVro7mrBaWTN4fzIvevx70/yCqtk3BFV+HF9OrK2QO6FKDamHwJHx20e+2s/g6y5CW2yDtzrAeaxuN1ke3hRCDWBbPviT+7Z/EF0ZW31Ljbt/Wcb64zCpA271o6DllfXQqp15BzlVgFmAIxrOskjITn7WFuv8CcISLtlhOhoeE4qh//sFxlkQp+NC6QBqLx7SrnwVwxhwhgTC9sIYEwvbCGBBuLH51ZJ+SBt//nU7GeJO9OGZKCbYz25yD0sD1TlkenNG/RXukK1m53ATC9sIYEwvbB9X4tXNE/bhk7vSkx2xrneUfC/SXNnkYW5WJpxOQhjSmvMf5e/0ezaFN1cIOhwJiG0Kbq4QdDgTENoU3Vwg6HAmIbONC4XSPO4LhQe2vMA4vU9VPhI8UTYOVFLg49SmIWRRPYdWZKMNoLKhEjer2aWzsuJg/n7Od/hBHvXMc428TFbL0/SdOB2CpBxin37bpazrKodMv7clV6aqLGIjp9akwXm2i2Ee9kO+tO1QsPSixWGlONkw++w8HPDoFKqdp+2L4NpQgu6f86Gz9vQktK9OS1csPXtdP+dDZ+3miWlbgYWKgEUMsN7w/6SK3Vkk5HL1inbG/5L3ZVuvRVef0W2U/hwLihobLVt1CCy+k7yC/NPOfEpHHSZGUqN4QjhRML2whgQbi1b71zX67LLKOoh+85KHJ0ilNE3idCnDq/8ON//Dql+FQKJJxEO46N27Gh5L18wTLq+6vGUp2uFYr0c8020Kk2UqZ1TiUofurz87XoXxxowIcBerA/oCFQ6G//iHKI1/OrBfCquDgmJKFU6CV8L6vN7rZPzF+yeJWr8EHhwBmNZ5HIiav7NJJZTd4aXLlLivzaKoWqva4iCT1m2ZPJINZcdlzrsBPjXBtUus+sRVYoBf8biSyppjXvsgqTOX8UQZG20z3pgXCQe0zJK4mDDDyHQH+MZd0U82/LMc0G1B8LEwNqKm6ksOOGVzCN9/lW/3WlmZiKLn8lR2F1J4pEt5rK/2sD69PXm7IEl9xUe+gIzS45yNfLvDcE6ohCwd2b2PL9BPsErjgWKvRHZr+EWMhdVETC9judUZH+wIO0eOKpePBobfSdTI8ESEFrkQGnuF76AVEQ/Fj15RzLtd/4/hv4N/X5Vks+ow99V/orB/1O58jbmzNIKo4ei9pEJXU8IHPDHIBOd389mqBgSRX+i26SsXHicrFFVTloWS5MssoVjyJhmtEiDgnnDetAg+MSH/WQ8KqerS9KFxt/JmCxrSQw+dW/2YF3Fj5MaTt7RXVt63BNY4hL97RHQE5t0qPmlyZPgi9OAUS6UMpPwKnMI8VrgvS4UNvg5GVGU9inEWVzZlxkXIm0B8d9pK/fYdcmCXuLMjrR0Bj0k9h0Rs08ZhHXbJkZebRkpH9xJcxLUudaE32ufJuFvqWhSCs5mXlL/3UL+pU+CDsWtxWMBf4ke8el52F7M/KeAkJyV+fqwizkcvHtUf0vlshwxWINUKbSO7OUL+TskE0LH1hpuOA7HxPOrLvLZhe2EMCDcNScRlZL2Cf/gdNDsho5gxroq8X7bdyTLwQR3tNfLOwJlQCTLNeKzg8Zy6CJyH/eIBGrq0ELemCkiwCZqmfQ7IDlU6rahq0zOh2H/h/dsA+BnCp+nB/QOd5GCrvk8dOIaIZoPsfLh8G30aWjpfLDtlkHgfSuIZ12yzbOp8UyoPdG20iFYKDgnb2uGMOEB0F0xlnSu6OF6+gJsuHdoh5PdJMTfbZQwfPUuHchSPQC0SSIA6gQSwYoEMCYXthDAmF7YQvRB4AjqHjdEoOS4q+pT6zkJRynoFoWlDE0N2+BhJwa30yXzvv40uqiSPybkdssMoVwxhwhgTC9sIYEwvbCGBML2wd7lnNa7+x9Jk+Z4jQNGPRxtKQUt1NXIahJiCNX86evkS5Y/w/kdNmfYXaJ80YZr7Sbh13/oPKW54kJ7DiEFqoPWEOELizVG8p6mEXY/yStsxlMOs9Faw9LhBxXqhHvkJTgwRx9q+HPG/c1syPEu/o86Xzc4A9lf96jPGI3QxxHWSiWnkWQ5ypJhRqob3KDuBDkKBDMHD9y1Ls8hNmUUgnb4yYNRHl30iYMMrB7aa48DBmi34aDbP2jkzg4itjXr6bdHuwSX7nqI5hljnzbfVxVOR15rUBpSmmDw8bJy87P0tPV19nb3V7f4WJjwJ7d9RGqwfeYfZFIXyflfpwkCIwL7TaHvnP9jEXif6tT1tz99IJc4Kb+1+KM/33gZmdIipOu3Q54xYtFG60mpN2kqMn2XFasluOEFRCuXw9vfzykX067/nWsEiVGJhuhTqxQ3W2FbWj9BGhav4kyM8CyMaqzDv4r9w/mOU9wU2Q50lRGVj/KSFsDoAIDin5UYkt9txJZLjcx1Rt+90TFmXIcK4p6tOeqVzZbhe4dDjZz5VNvGVeM1HD+y6dBQvbXjJuhwI3ZOTzEbTMWXSIqsExJSnZ772JLNdQ4H+57diNuqwefpI5+W6ojF21lcI97fuhwWFMhJenLfyumvrnxto0v4fscjYGhdF02Pn71WkxIefkDf+Rsr84O1abUJJi8rO+Do4H32EVibh7AwJhe2EMCYXthDAmFvVMpfM7NwqJ6TB2h0ILcqN/pztQDEbEclzQRbsooxB0c7vtgpR889lVpu+eF02ZYroGFWC01ZnFKwQTl52aoNerr7O3chXRmNOfk8u/GFY7CNoyDIMMwKi59TMxR4h7dHuWX1DGaiF2+gYbVezlvYKiQwH976rxrY9jpN3Mfh52UihbUiaeq2lbvVRh9OW4rCkjJ3117+Wb0R7Upr3DehHz+1+xNXJH4Taig9gCPe5HBbPPpPZuz2oAn27kOQn8QzWz62d+Zy9WwBvexNR4s4KMFBZkRormBayu8fItlPH+xJUXVREwvbCGBML2whah+Ypu6mwsIXG6szf/hxIdGYiWUHqHrdYHV4SNV8rZnJuHZSSQFfNoKkyAUl+t+BciSaJkTXPe7R4UCet0c60Q75u4TdWevNhLTD0jnOhJGtajIs4hQY0rokqINa+WhZgCwLaHf+Wml5/jDk+AEA4DsMDFokdcfQdDRYGCqtV0d5dVEQazN45AbCxyG9qJpxv3diYrz3rbpcBlD3aUqGITiQKS/iWtg5RW821axVkp9VYbjd0/i6RyO/WpD1dGb5oPGoq/DY+mPXApBiNoc6nv38/Z0EKRQArVnUSRtT+wo0hOGSTl+OMD4OUTnqsbg2bdXbCEyL4FIMRtPO/IvqBYpzZ7VIuizR4oFjNGP98/ledwl2EZUymtaNpvMHoey8ms2GF6f/iZBZf6OMHkF6w0z0gzrPvHH71yEuryNXIYw4QwJhfgGGBML2whgTC9sIYEwvbCGBML2whgTCrnC51MnoTwgmez7wQNj503qjhF8tnxJ1D5Z5dfkr3mP3g4QNcl2I3ZMqcHps9unhomsWbjWLT77HTJWO0WXOwQEGkUm+SDl+Uo2PHTF9YXLeVKMbv3RCMPADrtHXAIsfZeoVTtldAe13CCW/SmK9Rqxr+iwFqqjGCZRtTcqK5Zy4jrKXvF+OppbsE+FsJ8AWYoWCbsz3yxziUy+aSuHrAf5tZx2afAnE8YTFhYzzPu+5tLVQJhe2EMCYXthDAmF7YQwJhe2EMCYXthDAmF7YQwFl/tmLGRVR8qgRuwbE8nUE4JOwKvRDandPlCvKxJU+lC7k70twXV8reXlgTBEsNtVll6k949219lgQYcPgK4lSpeh8acORRD6BOveuRcG2P29VLuihzoeF4UX0wUIspDNrR81Ro/Z1waqoU/NR+oVQFlq3l8TyBR+OExaubzr2uuRfV/2OOJfqHUhDfF64TP/Ivq/7HHEv1E+Qhvi9cJn/kX1f9jjiX6ifIQ3xeuEz/yL6toxxqJaV6clr4YeyZ/f86H/Y41EtLHyEN8XnZAgAA/tUA4Ft9hRph3Yv6j4v4uvXV3ckX7Qrn5jms09PSZ4/+mtyuX8ZW6CcqbArrOLIKqMGghpSMOavUzdj5w9kbj/JQqCkbf/UdfzDYyYx/mugXnD3E6xmZGAs2e5i6Vql/7tr7WmyYnEQyGLqVDwTMaDWJOxklHueYjnzCRnsCFjUSw0/jedxSgf59fcpQsbmSi3Toftrhj+hDVycPrRC0mtda5U8yfr4rQNY/LctfZlUfeJcTcFvpKjk44JJKwxk55Sqm54vjydKjNnpgBvmm57GOuLZs5Dib/UyKRgYkdbGvF6gzEyRa0VztYfqrkg4I1Dwb+jni6v+zJugzvAH6YpwoCg3Y+znWokprmPtE4Or+qmQr7YkcGket1Xk3RUqMUucgSsgRmyxsaFHPlTEBcGD+Wd7qqj1dP88hMUCjb2FuHxWB6CDzASjZDFSIETCoIAtQ9T42KIORImLLBL0qcUQ1I6wHo5Mius/8RqA/GnuOcLkVpq/3QHxiEIH5+v8WbmqtMVLVEu2nczbB3dRg1nyg0tMUHPllwTnDlog8Fa6ZvOH2b6zMHcqYqweh9Mm9oLP2vnIJGwFKWcF4rUx6ZshFy7vXmB9TeqKry9uVPZ+LTNimIL3nu+sxVISlSBE+UF3hD2NNARVKMDa1sPYFQPzsjLH3SGdmX0SNN7fMz6USDlafv+NgE2vT736u/i1R3srmSISKFD/bFlBl4axoE6ygv6eUKRJ4EwYuqTCy3BQq1yUqrbkwwARTx+TZwvntcdAzEMsodz6NjTrS+Ye7stUcxYehIEJn+5xrPLS0NGyYzN5m/b3jiqgi1adE0A+2VeIafVzQaLr5zuLiphWeF54ftEN/tTlYcXglk4rTx+CYE947v8ht0BOZEqpWlhZsSRcQO1tWUixuiFNYMjlgemyzyhEUIyOxgmWcynC7DGLw1YWyQjbG8V1b6dBwsaieBNpcL75TH08ZYXYcl4WjAhgwf0z1Vl+zAur/sUzXCWYT5bNhuOQR1weG9E0goMFT45z+9jL9uSH/KKX9Fv/kt/5+dI+bgMiLbn7A795u66i7EImWio1iuOSBZ+b1RpkS9yk32eR8/FsWFabCwfQuDJUxBUkV4RQA+z++8As73Yfi2ZqQ4GJTRJFgeim1k/aUk1sbKKp9cycJUgDCtYBiSFJaP2RG6FAwkECAzTdG24nbO/mgHYwBdjuED0cJ0gj8vGeDxyTzN8nWLl5D//xffezNi9O1f/gyNGnZ1nN9V1RmeWVo3BT8rrjgmWFS7+2c8AitHalaNQ0OzYRls5uy35f9ST1paQEkR9KIWajlGdOgXD5L8yUIU6FkZgk5emgekkynbAkwj4y5LDvmZEM1SrNwIcTW4Y7X8fmi8aDSHWDVWvV634Sf85ZXkVDOoPOWCU23FZaNL749m8cmD6OApQt3WF5sP5yzjD5uH2ZQD+qRvN3UcUJ9OUfTu9eqMGngaynHKH5xn/miUJA3F+kO0Uc343/Tal6V2phb7KWqQx+VDyv4YM98zI/YRQXLpyNw/ikfRl5ROgkDfD5vAxNyur5XpH1ZUYXqwA4AsXouLOCwuDlxKKkSS5Z+MNLiH7Y1n0E29wOSsXGTciKF6WgqcMw+GsUj358ztG3E9PPxha3hQ40Smq0r+Ou5am44fwka7SR1wCOwg/AMYFyu8a8PipkYfmb8Vgu1RiRIwSJuml5TZkP6ZLmsVcufDEZKQURveDy2xv1oiDvO4ulqqpntBkawGpQe8uzlQHvyfx5KUY/Z6xYkVEtMQrdFso5iHRh1WZzoYkL909oLoC1QnW7uVUzRUBGwbgA65W+zdhOyF5AXC8j8xrtWxcNp+uJgLZXL6/JToLQze2BdX1kijTf61M0Eyn9FoaZ5+0dPcuDIruJpTe+iIYsiPiZsrVaHlVRuk+YJZvrf1t8EUTXe0J/OcGbVfbwcrp8sm0i9DZwjrVrUiEFcWReUdXHxQ7JxEqoUpJlLKFMst6Q9iJqSuLFFiA3aEobuyP83olV/W0Qul+wqkg4YEHTwnSLu4CJgfkMyEH8JBMMFuZ5ChPRRbtTlcKJtWYegspgBQYERp4wm7/B+wqPq1EhfIk1oNOCXI+yY76qqga7lYTQc9fd0HxyCFsl+9dT6KNtCA5Fye8pc3hFEirt7i1NFgRQq9CDwaQEvC1j/m1c15zt/2DKeNG+UyeJV5JdVsZlVThH4CeayJAQaDj72PP7YW0+Kotwg8YnXrsRhcfLzeYYx5Lsc5pXKAeXTUtT1PoUJaZzxBEndIAYpU5DVV+g3fG4IXIujIwr3jqJYX2PRGbh5PRP7Xjbh8bsJHgZ3nYqjY923uEPW1uJrRjb3hEXz+OfV6VTznFcEDQ3nMoHeYHmH98nog3X5eeT2FdCValX9WpByl9PAclw2zYmJltiZUzeJigwtINYQoagHbuglKQkzDyDeALPpIyfXh/GgPxJ+nSpk9MyCBuoR8G802Bch8au7fES1+6le12laH5+drns0kfev+m9PGTQutX7YWyc9DnW0tFsJlO5syjJROlQkiMz7CvokSUxpJ+gY0gNBd4wPPHaRkY0B7BMSkAiH9Yhf+hPe+4kJvnbc/Rg37fczlXCJTqO/9SfXDMBcXTAncXj0j6jtHCJHFUnXpkDFAEsc66kk9JZqlF8fU0NlwzCZt7r7WpHkYmwEGg75MJ8Te/v5TBDMHfQLzwdeWi33iqJNur4C8X348mQFxpuItcYYgj5XNRA6k4fG8xCGcFAJdU0qDCje5Bdv6SrWs6iZJPBXAXkD6hKcSrIJvDq4jgktCLN1ih4JcaMiFrc7mO3qgbksUcbqnpGnSQxcKPmBhDvRILhkEBdNdUc4+zSnJzJxGjtWbBl+iU/cdUW4qmeyo6c6aypoDtvHnXaOyYWqB7ApS9ouKodDlpOCzTLZRSGuTvIEl3iu1D24q7oEmDPOIKlT59wRNPPb/JAIGfHhb17N8Bnd71tLVZhV4IvkRKp3bXQT4fyBPG2VdQsOmM263VFGrE4h9nw2etTp3IXCBH3d6wiG8IXRY1poPMDJ79M1QyQPR57FdDk1Q4rpEKVSmRmdh/pAA5kOudroTxhUbnobksS90PamLHq6cVV/j8jsHh64kSxLSGjUtx2QgCkAZlMnWB9WYFk6iXRGR81yaCIe+IgsNVctny61c0eb426pocS+U4f1eBJ+lMJoWBfLN6BlHi/haesr3F2vJxlj2n3smZRIEswuJGObGQLABtMFgH5oyhLUF9KMhYEnkbLcS99aXnH+vlAVtmTvhlqqaVYWCbg1tfmRzXD9EHEQwYwlDPR7cz6ZJmKfbYiJsj3yBHrA0BgF2XNrYOD11poRCu3gKLuwj281grSULoukDJS69oWDoYQG2C/EZOKtTpojPV33sHBPoeZWOarZwYJEYF6DcgnIc/H133XW1qtG+24ZZc0GkJNhGb9OoymZjYWIkkoaLCJSFCkh3s1jFRw6bGSl9h4nS/uc28BSDFKpLs3KYIMNqJNVE2CH6z3sU9QAcGJzrygLpstoTaq335wlnl+2zN8tq4PjzV+SZEgOrRXJ/SLNTrjB1pRflgNBBsSEWE4MAO9RJcaE0lCvFkI5sEzpShASWYLUnHVBX0MbjmFUfVA0EkU5fZT/d1d6CWcTFakaJMueJ5FgKPaoLqCf8PWcP9V1fFgYoyFKKGS7rzlws7P/TkbXuC6Yqi/Z3tQ7ALB91c68q8C5B3vGWgiIuksl3YYgsXaCa5sxH4s3bSnTd+g27zyOJUtvXFFBkOlNgC04bgwWgi4RqiIDIKoqjG2Rtr5EJOZpWlWmKVEXuXQ6rBdTOf++pWLZLMO7Sr0KaDX9VbKnqh7rVvKr629BC1rCitMYwJWM2aNg+fzp0oTxvBd+bhw5dJ1MF6as9A+Vl3OBD6BxwiiS2Q0nR8EZPP9D7sxNiDB5CyKfwySQbpLLimYcWshiK5oitUUuyfyeoQVjBHiQCLtON5b5aBV9zRqajpoHekW7EvrJ+6JfWUGwMV9qAoLdiX1lBsDFfagKC3Yl9ZQbAxX2oCgt2JfWUGwMV9qAoLdiX1lBsDFfagKCrkH8UX8EziZUERXtb0ikiUVeGK+1SXH7pMUeB0N9xUotoxta6tSASvUNTeF1u5SYUD9rMFc6PgfwAvPAjIC8VFr2wzmMPjDPOoVAfPV4XKftr4kbXRPtWVEnY1UIhL9pMLSbcvq17KrWhiakbf+1EpFn98YyVWpDncXSsVDIGdXtnrwXDxEjpq7aoqv5Gw66Q1eEvxTHdLBKUF+KS6OWuCgpcuXOmC9j/tYJpL29s+jy3HTjFBUD4Qu7gDrQfBhzWXpgjPiCGXcuvfzUddjVcrM9LD+5K1gdERRlY/kWYW9ovAqm6D/k84XQgk7fp94zTOsPhtm65hl27i1MLpVgnJm6tM0deH3pN7PbZDKPhG5sJZajG8qV5wzXDMjiuo94ZwT2m8+fy0TFGROVay3Hehqfh3UOOQ2xD6nvGopkwBCfilYdDcQEsKgFEqS1yYAViaGu2DruY1gAD3o+S1y1mdej+buA2av3X8MqWunQ3FniL3TaAQUDwRso75jN+2FL9PJa7RgQsxHRNq9xyAHEFWrIVAhxh3BiQpIP+oJssUVS5YtrhU0rEcSJvyxOHuve/2lXg/1H03dJ1roianAITVUMsDPPyiq8TpXIVxSgpUbqiUhxQjRiUqJhaJK+EnJtU7QQ2MdxXJKqDq+t+AxvO+Y9czIUQV5t8+iBITho9xxgyiTvhqouy7BiE7Zwz67vJxmG28VfFSHJ5QZaZp7mkSYVTI//zzOnoQ5TBOOoPyOJ1F9nHpuEw8fs9Q5Yjt4dAKob4SZdMcCz3mqZXROR8Z+IBt4H5zjUEQ/v99lzuwnYYaUknJrRO3uaWr30/0BuL1YHM/7o67wkfcJLo1JLOZp1KYvRWI9SI0qL9dJ8c0MeUrUjRaV9Xop8dK+r0U+OlfV6KfHSvq9FPjpX1einx0r6vRT46V9Xop8dK/6n9GfKOTHdafKCGTW7zOPWj6od+KoOqkZsOxo5wP7oaF/3TekS09ojsezY/08hT3Ppz6YAhDuWSVsKuxhJG6OW3CuFLfLNwXYI2xhsHFPTuCTDwOFAWi5eADJaTpGkusJk9AEo9qmQ3UhA/Y+gVX7+U5t9+kuJIIlBeGEb8/RTNpOEY0jCWdSKNOeXdfbywH99W7L5UaPhaTjnekUXkx/xVZ6ZFWCwuh4gnWIbrwpbJP27g45cQwdMIOv3TPjsz1aVDBzEnRvXKkMdf9TNhWRDv8gAL7lvZ6aYenK11tNZJ9Knpucw2j63gIqZbQLIg05wQSyYzZcRD4HWWT5w1A7zP40P7rmZ2Z7b1sxy4A9Mfpcbg/mTSAO2XWs5kOUU13uqhPByj+3aBMMCFR3m3av49zOhKuziN88uLI6KnvbY+MnmlKYLcewF/u6m/zvF9imO6xl4Ty/9WFCjb67BO9zmzioj7zSWxlmgm24obF5dhi/twj2VaCaCWad5MelPX3r0Gge6b56QSA5q7i4H+PQaHu8MHsC+ZzP+VKHVn2m6bsYVWaZnqpzFJissFjzzbjvE5MWLzVlMAWBUC8meXUByrVdILZcF9GYk8cftpFtS2mHXctAT7OeG1gEMvXiAHX/yW4IeTbmYDuVx3h92mO8KKzCU2gHnfVtEhaQQkkGWSUN+lotSZARyh9C0qlu0oCa/Clf7vfvrCkTy2sdSYNL8ipYbp3PHcsdXKuBBEYDtn8W9qhHmv8IE6fA/FeNLdE7uZ/Nqvn5o9LWkCFw+0Bi1dKfm7oEDTnYY0dH/Gh/bj6VRYzWY7fIv13MnXws9H8+PM7QH/hU5YYvw4dJAArjguCdp4KE/M7ApoxyRr+FOftCfQEtg2nc4QjyuBL88SbGznqDhZMnZ2dHa3FduknPV2rXSFpbiTID6FTLqUDiGbVfht7FrGa7mNjSP2zfvox/5eIkXfD8oX8iiI7y4Acl1H92roL7OfGk6RivT402alpibPZEUHBCgm9lnY+IEyr50dP6Wu8at6MGxNhAmhXzKH/TtA3rwa+QTIciLU9KNv1VbCWLevcsGPqP7hms30PXC1VY1W55/rX/St2i33Hspbib2HPxqNVPCrReoTbJxm7DgyLYlD/VTjhEhJHNXz1+r0nNaKV1K4M5cuaM7iCLgyqiKtdjCtqpYXVz6OOqmHhbKMHGTrV28Cd8GBXIbe5uocbRG3nTadiVLuPrU/bbIpZAVgIgIDk94nxjcnm7HyhJ+GkI8rKS8f6tLIruqzK9Xgp8Bm9SapccOcSgJVoGUGQ8az0g6hqj/vKYxfQ5EmUzN5Dws1HNXHaLfGj+KtHwQ0au3kSdr2YkSp9l2j7189XYfJmbdHZYCHUkLqYv8uHkSTdEZHLNgNBo5TT5TAwbQLir+yP2cU0yGNri4/o/mV5ydHlVNdOma5fG8MrAnkCWeIKfJITShARRC/ig8CZd5aPvGi4GFc7Pd1GDbWJE2O6oR2GTal5bWVbFrCmsA/uV2rVjo6Bj1ukGwlNpmBCcP+76f80O7A31rwuQNW+c3dWsnvRlbhdhpM/4duVOvQ2eWA8u0dpCgfHYhxO8W8LFt39XeIynTmSNh2o8NA+qfNrHCXmgwQ4mW5tIft/80NIJ2hMARorzfEtP/CXj6hCb4E/qKPsJflKrddGYNaTR4vTwC/ZlfuKYL/JvTGWGfTMqQFEqOPhQ8NnTBDU1YnHWvTn/NqSjcY0BFRAFWB9LiiF3pRQ52SqhrgcAodHtHTWIbNNCl20dfLyQU2p+fUA3JTFPLngyMFoinybvZOzkiNOXUIzI26nu1FtyMflQ43Sxbk/cKpfk+0LfjmkHZcr+uyYdDQ/Favfi9hngqTLvtsGHdeX1NouDzsEThXiD/vzrcT3bNxTf+ttdRB4Xfk0cDh/rNeyvoAyGlsnb6eYNaGEwQvzaSxvBitp6Wg1i1bDzB2JqBLQD/MEMT9svXU2wUWaw0CIhhNMc70Gmgo2EhW05UXhegD6EfyDfbfApe8s0478RdXJF8lUwuG8AfHqdJXw6Cwq59ILBRAJHVw08Mtvg7XJP/GRVT8WURKJRM0p4uraXeQ9FVrk21qu/ng2AHOdBcUT0fuFs9kZjqhyk/N4DDc1kIg9npi93bMPdIqtSPgljebHn57cvAxNcx+kEzKYMxPf1l7y2UiBlT4esLbO+ukHMxL7t/JAoiMdRtV4vIxTTNwvHXnZqMSQxDJFt+bT8iI99Oj/fURZkUbQJpissv5LWNxUBHXfiNxS35w0RK2oNodqkXJpAk9K1hXsbm/w4BsI3tOb1G7MpZDKaWxsLVsuvTIbrhD601RZwZHjvk+jBJpfznH1URDj17a+np0ie6OJwybaogWjYZa6Vu+sdnruBahhanHYA6U6Zm2RJuwiHDgTpHEIgmoEl3jkPfhfqVdzTqogAAXUlGjVqKK7HnBi2sXPdO3LhMs3o3rYguyRkaL2l5GwOC6jqMAh3ukp72++EYIo6T0xrMEmmGUB2m14d/ReLy7Ao1ryfbjMWzVaFkRaEvcEBCtOm/UZMUlduqpPoOLPT3Fp3/V5yc1jTBHeBD39MYKWEzbO+0VoyKy22kU3odXDUzP7mlhOwN9/iPMQk2Led+0KO3u/B3AyOdrhgFIe0mxUq9abrnXZzZE2gD9eHwwwiL4CxyczzkcTctheUDGoWuxMSejjzbRmmhyn6JAzSs4oYpfY7QqT6XsizyKkiWqw+5qNbp0ir3FfXqoXqKBi5OZGoca2YNayWNqPGLObOlToYuuhuJIr+UZOSoDi58ukWY3TsVqJHgO33hI/X9Z0qR23LoI7kv64xLGUGENUId0FpFSBi7dLR/rN6B9mzmVnmucRPcM+p4vUvkY8h/Iqyeqx6Qj7cVC0XFp3Ab9MTTZZLMpvzCP+noLeuPjGHZlZvYiGkJwrVhNOe9d8OWJgP3ChMWzV9P8T+o00WNkjT3aMrjoHgk7Cv4X4ag6neiL7mEaK+ecbBi0z7FD6fIVrmPM6Pq7l6TRp/Cq5uSDo58Xdyp6AovQcS6yU8SZGot2m7UG7t1aIhLND5PcMsnFLY5WY9ClQ7D4SIBNS87jksTnt6aiG2NrtvpzMuI2rZCHBi6OMfHKLxIgJED0z5QbgluUcZBBBDwIsDxsfgJlPhj/XNWVLwyPHHwJ89J5IiQUFnxU0q2VCru0v66u9AF+t145Jv5yEr8XU7YgSf9nwKDlGT2aSMhRtO9nec9ZmPZ9baCN3X6RoWZYhtxps5N3SQP4fId/Wxpee65BNHTPZ1ic/2mmPHr9RMQ7CbztVBojqXzDmpkhY9DUB8IqApmZ/aaPM1x22dX4UaeN/x62CePnGXMHLFWAHMoMb0pqOkQ8byAMlEkTbcXqPpgk4L/ULAGrOpb3KN4T5f+D7mvG2UMx1+AC5lJfdXWI4Ni3+DeG0XhMg1HzDFU7yNKjbFHW+cmGu4iAp00svJM/z7XB1sPJBXLC8aHoeZ2DOjaRs7b5lNpoOziH1MisYQ8JhvytEOiGLzO/MCaltiYBUAwDiBt9JNtZW8e7xJM0sytf6kh+aSoccFJb9r/9fqIMZ9f4R0kFlpL+5hbv3DyY76wpdPr9JovMyszkteCyx0cTroNoAPONMNO6nUL79oKR/mvpMS3Vu9yIXGfuj69EJ9OZyasbJTsOZExNAkeJQDlnmmhs4x6t5Iut8ZAPbw2uGEic4JVJuz13YoVCgxbkI5N5av6LIbHqmYODVOBxVOfZnXVG1yh0JOq1o+yc7fCT7ZtzmmqlrfUF+ed5l+pTF33h+37dOGh6TjG5rkKX1ZG5l+Pxu97v4uOvOjS/CF5GZxm5yAi85+SZZrjCsfMP3Qh7l8v6jPGj1vlMycoJMSCsPYVOe8iXXPe4cBNB+ECGFzeshXRKzQCtnTRoUbvB2PRIFsOeTrmg5ESrR2QhqUGa/hh5UPymcHAIsmK8YJDZr7Lao0VzP7X+glrr97GQwdNZoNeZ/RALGhQuptNQhqUYNOqbaEo9vhTZ9VXKgjb9Vf+OF3xKE3tS/VFGUz75Y2LbAMZ/ufW8HadGLjYSb3kdMWZJ3/rgYKMo9JQlz4Jb1IcR1s4uJSfv0rEyRHuUaoc8OOb65sOooPESNhNbs0CNgNFJCQyl+IWqairw/3QJHNK+yAHdVmUBWa3JDt0oaWSbza1qHK55cRe4L1HKLj0HIL7A9J6x5/U0pFhbBSGQLsJb941hdWSL51CN1KyEzuzSxq+Y7P/4Bwk4wuNQ+x9ZMeT6yFgQzYqnyHyrC+HOApfN6KFd+KUOJY9guJBXzGhDsPKSFAbO8BmchuNC4JjSdVs82psiTEalTCrxYmGtd2AIjdlrF1dvd0B/7+HRWQQx+cuSc7Shsk55XoZteGqFIOdNYyujZn2uBWv4I8KQEEjuKbdd72VRoPiItPkczTZjJbvZknSMvlXD80tT5Gxm/bZAEy4wo2HtNOIOycn3rv7fRAIwtQkj36Z6k564MfrNjl242TbNQDmrMquPPnpbzdE79/pFpFsl/pA2ZEMEc4YiD072njF6BJ+HFvShYhDHhR2/Xlpn4Uz4bTpEiDeNBMIozUPMgHsppU5X0Wtgg63I22Ojklnhy0FTvFCQwclNeULU6ibkkk0IbrTf189WY18104NTL+8qhnIyuWGDJPv5oeR8ELVey26yhmDW99sEQd7D8yYXy71oQGbHVTL9T7nmLYNugTRWtnK4MIE14V7b8XwnggwnGStwtRzCAx4pGkjCj/TNUdH4HxyhLReXEZd7pIXXSPuwtPGP0j/FYW1xQqpr2z2nmWPetVaJnpOtdnRNZoRhN3w9KxBIVDi4XsSVW3rQlwc1PEQMVcLTH+3mmeGSn5rNJOdOSZDm6sOi0h1Syoq3OsM/n+qZjrPaXTWowCxi5Bts3PCbOWdPCHhRQohIWwW21NdxQRKtEts28pR0R9fmrdaw2MtnXLrzOB5K9p/iEtu/UeNS8ZogL5iPXIHM4VD17UjpIibQrhuYCFpZII1afeV5is7GskHD1oF3Cz5qUUrI1BLh42hXuRzm+FFPeMitAhCtzdmInfuZFFvGM9R2lsNxUE3krMuZHtlJyPTq72xnLt2l/9a942PRHvvM/3jYX9YdHlJiRqNWOSX8Vk0+LVQPvagOXDytuFwHOYI6UxoIZtcJGoMTve083WYI/pfdzDOLtuJRbs+D6g/Wyq2S3gGvzSuv4UjwAFMlAgoXllgxH8fjA2PQyW53qKFGMYE78Q2gXEUs9CwzUA47j/q38DyJugXzuCPP2f5ZBy0bRVK1qXgBmb51WVePtY8dzZcGDtBCUECfcxkRgPJEx800WjFBKdqpezgka1Pfdsq8hKhSQdbzyF0bjSMXT8mt0XJzaibAryxBQEprCdzYtoSaD2gxiGKQTA3Qd5m80aGacYtSLekhidGELMJU2g1Th/jYBrFMDzD4wGPstejKl4sWlHn7E1ePCABLtUMkXo4E9zFVUXLT2ooxs0+/iwj3gnXt0GDg6cuZhg9ei0YFz1Dx6QOsnw7o6GvaOitycKOTw15YIq8UJq8Ey0mOcjVN7SS1s96YW1OgI14GGsqVGcrBO4oGitFrAXoYjWAVd9q5apUkLd7U3a/RgGJNx845zm2tjLDTUulKL8QVDTssXaQE/tcWKUX6XFdmPn7yCoFC7KNuAjtrG7LnWC1FBfF09OtuuwnyF+EhPkHZ2jtFG26tof00D8KxwJpWF6fgM72R9ZgTUYUAiJNfjEfk78Soqxv12fWmbWe2yTCEStNrasYAmcJd0O5MWrz7avL/YYGlTuqnzRKWdW5ySwss8TMykDyLXtJYCmLkiFXWUznuEg1AQtHMfk7XvuW44dk41E5FMVek+HV0uRBd8ivxCxf8YcwKxfL4kYyn0AkvQ0V/NEeHiFLw1a4ZVaNIMxkjGfY+TFE3WOTtbfCWooEm9z4b/YdUONLKUWevJMKAYO2p1aBbXMMfnE2ObDvRxzMQN2B8dyNp7Ms2lYQlRMFqgr72yroJyo8m5Kf00GQL5I0IkrJ+5fuYHunH7aem3hg1ig9KLyT/IvhpeUANIhDssexpXIy7devElelhWgI8Bo6vRPWg3ARIdmGe4Y0BtNPvbwBT1mVD7vUg+TMO1R7CkSWZNwHY+a8Czya1GnZjh1K9rfEcDJCJ+862i0spOi2bBO7s5+lOHoeWI50FiDbhJB8VVm7maf7MV/OV2x776hIZVfP5wUe5tYf8ZiAGHLycfsPwQfnhVTwFJvzt6oka/m9I32Ys8r/WghcPEx9MewJ4TEeCw4CpSwwhKVLqJdxv6gMj4OosSloOBk/JwNwGiWuRURqu/wywbaAxo5OiCRRQAk74V3vuz6ICBR8Y9Vys/CZFo8k+0XJiYDXHuUOdCklb4aMsXRQBV3t12yWFVCQGzE6pXPVkAxzQDshtC3Jjh0rWfmf81BGo70O1sXt0xAjjUoGf1GFQxy1De2C1GWc2C+0MnKDVBaxTxJEdcwwAzf9ESqFmldxGwrrVjmmwZZDwc4mquHvo5kfMqlXRHFajyfUMCq9k1zK60a6klYA5qtBJ51RHEQB4SkWjcbhrmWFmfS/ghRnpgkAniw3AA+pnafylXwsrP2kzp5Zex44HdGyKlDG5CyeVgq/NYlxfUMC3ZkNgqHokKnfEUujmonvm4C/F1KfPUp67Ff7/1xNOgu6WwViT7OU+TCd5vqkqHp/bAMiYtBmy+w1gkHa9f7grfjQ0qzd6/ckzjGNfr7YlL1CI9HsJhBtPwIiNNWpES5OkvqXUkiRiSFdAVe24U1pIcyLH9sL7FvX7x1rcEWb0QKcgG0IlBY56n6sfpV44WzqcEYYn/z2PCU9U4KmkLJmMw6XZyq6Y+fUnsYu8sfMIELIX0JrOxLEZEbNSjitszbLnltcQGt5Q8/9wKZI2KBN0fStyaMG/58JCMW1zH/zkIgTQ8xmhSUzL8t9WFLJlc4f3z8tFlFj3+qwGjhMdtrFtAmmYe4ajZvYd7zmimYM3OD0Vg76cMpy+kyYxohI1+4QbBeFPk5cjK8FYz7LNSLt9bRXa6Fetd4zzISBt/tyZ/4xsCmaaMfPIPTdttACFDUCdIdxHUPUhA1IB1SYckg/MbNt68WkhM61nqodNB3SoPMXuOYhY0pp4vpN9ZZEKHJxxO9o6/2QKVPQ7BubsMHibPavmJOozK6b7/bugEp1F9udF2J3cc42bkUzquMHeB3QkZgM+fSTgS9vH0wRdXyVO8gOU8G6Yh5wrFhhgoU3BjE0qK3L3S9VZGw8I9Wo6hX4cTTY32bFPMAG5hWtFFna/P2LsY4gduCpRfmDtN7h3gV7PRjGcjAKbWWs2f4Xr/4b1YUo8XfdO5tv3LQu3gg42gRimWiIT8W7b0KYCw0LDrK2I9t858hKOKZLKOeR2ontrOll9aLiubxBuiT+OZlql+EKyEwt4zwp0nainjZEJnuMjQZA6j06CkY3jZeR7jCgsYN2+BZMtcjqJlNFnlfXAcN5s/vBYtYiTx95fql8JH6qMEgfwzJajnJQxAA8gKbiznUdxUZ4BruIrKyIMwPLsn7Cl6nLmt1hfyJYp54eusC2qLXpdhVL+XlJJT+uPV+jI2o/Bq0naR9XkxCD7r/8BqCEdN4WI7nFOjHN9gbsOqFjmbQo+cz1Ug0nF6UpvrVLvczaasx57G5kQR04ZegtSM+Km6jG4UVLhkVcLI40k9QC5rh8Rtn4F8ojwwHSa0pdeR6byOeAl80uJU0rqB0nSpdKEa7rYF0Hnsij2aMePdh4lNtgs81nN/BN8f5FpuGBoYtcWAMdLs5uXLrGcGIT3xQDtmxeevH1I88RhW9dZC77Ag7gFAL7KUCuDhpWkhlDQShSYJioibSOIxk+zCG8i1HIWyyvCpKXpKJCNsFcaGeEm1lLs04eTOZ70o1DcbDAbHzZ2oSIZtpllB3wHqULzjlyRwoGN5AL1gOvMKCZ+zH5nhMSM9nedbJFPCEyxdLMZNzJOS96LG+JwkfcgU8am+MuY4hcOvzG2eEvrSPKzqXPmS4UTS4tZP8MxPmQuxsnxpIVPt2E9GdnAFPjPhzwYj1g9uw6OK26HLPNwVO298xQzxIrrTdWbWTzciGElolSOJPBqQCayCgcOOdQxfPE+grJl5WPm8AvCb3S/Ew3Ryo9AxQ0VusRiIJZqJV2iraJ8m/hSYEtCOM20i0m5MpEf64X+4A/Z9IcQygAiVd1VUOFquo7tzyEcrI9MNFPOQ7vjHK67wVdkOuOR1c0MVZXfgz48SJGXgRWhO8kOtzCBpLq5BcsR84WOYOfY3sqj502Mt5jxlnWKxgFj0rkPLt2m5QJfsz8cImYJ2gi/AOfuzJmGodsUz8ep3X0qTZfSmFOLMzFaW48rRraVCNskbGvOxZmmK46tJU850HsHLL3lJbfpDeHI5kVPR/1m4fWHrrcV35Q0B/eO18t2BY8x+X5VzylwfXOhG+ZKyba+K+u6mzsGln/g7wnuJwf0GMgQldq67NRA+FprhErGqKmZQCV9rd/fIFDC1Q7CPtpj9wscabUmBVwUuf4j4+DZzJ0cbpTaDGVcL91GkOhusanf/rWd6NFYuqFFyOV34NenBcc26KnTPiyGjOv/PQxTx7GNXfiloDfXBvalqje8StPq+ws+WipJWlqFi8Evn/MEP1CTqEeHVkM4VUbN8vGGwUs7etEpgLtWSfpc23kRzK8v4h8+DavkHjjCM4GpjTGplg8rUbTLP9lU7VzPHgmh7OxKRHtQ1S6aD3ZyVYB1RDI2jcwMfp0CCCPqFQCpsKqnrFCdCToLY90R2MDKuEUX4aE1WgN/LnJjKMedrKHdxrRcy0OHAXb6ICqzOBmUChMAbxw8Y6xVOXC+y9pX5N1wPEKudLCaP5BLHG29SVpLD/ViVVTPpnF1yUo48KU0GyNqfSqsFjuJMRrO7n6uDeSgCB9PfSHZ09bOk0DaxYZ4zRhqe+CkNIsxq6pkyR3KPZ1cNExuKNvPsAQTikGzzueq/R3aJQ8q15WYjWXp4vwqvosSzm3Xga4lhTfxMinAXE4/zp3OgIaw8Q1cTLIjg4pZH4pnzrz6KmVpBTqUy0IPFro0m3XVkWiHVxeed/EPWwEd87yILjcEvooewa1yDxX2iFgWeoN4NBYkQCQq+KkpA9Pb3RGppV61GTq3jJsTh8omFTUPAbSB/MPO0Ug33Wu7j5+Bk1aBXUuyf9sPQp/MbkNE1lLQ3WBP7RTWHYncUNqjyJqOHu5yU30RP71U0vderyuP+X92QEUl8nkajfUAiup3rb/q7cpLV5j6dOh9hyajTxIVsv3y+0xo9YI81LQPyILyz5ZwacjTaldoyc9OViAWx4TdVElVpHXdq3WTKT4RR3iDadRgqS17iw33DiMkMb0pq74Hp7b8LpQE82ejDBnrBbDXXANppd0XFVoHcQFtjoJ99TgmrfUhtaKiQOTICDoc1Q78uiQjjUdaTcTvjZv5bK3zNFKGUygITBCBKiC2Di0lffIvpxQWFcuxhax0e3muDKRSpBp3EQET88VrQZPW56jvAf9cKzbkj7aUq8AfU54yW8OYXInCMxpzZ7lB/HeHQrqShJtCbut2F8uOgWyfCCJItMXwUocoWcXSts5iUoMh/2BCJ/fIp+uxE95/7Q3HPxiYDTOUK/dfcvPDUJ4KHEeYE916qjeY+UCidzrq5igzvNo906xGbpXCHINQh1QqJ6Ao9A0bIT1wmqJMET2RTWMzH4XOy2UEgzeSbkaYyzoL13Ely4qMnCsUl01KIGO2CJvHTz5IzOthd6lgEfqsLz9hGDuJ5iSXcW8gYNKihHKG3J7C82055NAi0O66l37bhTztep6+zAZDR/10HP+F6t9dDrZOCozFYIy5LDoMp0eWz5HDwVFP9+0hfoqF1dhTCCG3Dx6clj4C47dl9kZK8TRP1lKmBCYtDPUVcacA1GK35H22biYVCaXSjGcj98NOmvUfW7I6o+wOKvNjp8iO7iTKlyW3/lpxc5sP2nvkGO7isbt9hVWtpS+NHCIVYX8CQ0BnTfBrbT+DPy7uEeHF5zbsL8R4qKZH0Y2jBKorbMLzxJB224hPMYy2B4TmG5zNPsI+TI3bJL2v11UHcB1Nx3s92wb8tmz3/KbBvuOuM9CU4/g8Ufa6onKp420jWfmOIzsETl7zQW9DQGhtNcHqsyp2beiTMVeY4WF03ny50cHxeIj1v0hdhIOye24QH49hqrrgjfTWwepEeu0adLPEarlveW42x93+pV3mO1jOrivF19sa0N0gwtlzRIDPQcpHX5ywDHpxbO/SsgCzAgdVZQjNzmiKYCeJBFVWT1rf8WBthtouCUE79uGqfMsQV9/oO7QoQ5VaNJUO+JIr2CDGgvDIubZaFzcC9+VxV8/5HWfp877WIyMnfrN+/xkELkvBAbJ4civFU5G+oTKQSggc318NuALAX/SluXgWyuigEyBLhf9IIV4nmvygoka/RY6PvOoI3E4sF7UBVLCiZ9w30YKv+UlNRaasLPxpNNfeZOcpsKRDwAuz/q422Ov5oOsDsfr8xXzaIp4oKAiSXmfaFCk0eIPeISlaxVLAnvpfTd/GmzzJX2ebrbJGjy4Och6vp/JBfZ2vO2NxuZDG0WfOLPFsYrnmbGRR8d50mnQXdImMpRweXsCu+/26psQiZPZOyFwNfKkINf4X2FTfyFOykXQJWOdHmtmw671X8gHpv3KsmwBEUvkr4c7ccfP0JfUVN8H+O9PWQ6oF+YdccMJHtEKFnmoOaPcsb67fSWEKowF2XtuSGuOUy2tOcc7TFI1M9yORFuFTNPG+bXm8hAvlZ/QWHFjC3eL/9QQ3c91LToT0qsSV+L2PFblbW5nr/JXab2iwRMMYZmLL94UTFGxL8X/5XV0gelWRFdkBSKHvBqQ/j+/ONevGRbHBSNYsaSEtAg6RFf1YVWVbmk+Z1iNcGq6gRDb1dCj4v6Bb9HguuQQR0fydKVDgjk5tJ19jONEfZzl8zyZMZYfn1Yfu4VVBoGAhO3Ekr7g1MLxYI4jNQr+RJu/uCkIOj9J5CynVlhxlMLkLa5jzhD3il3BBizUYtxZ+M3hCUr4xk/Pof8xJvFerZIbGrTZHId8WuUl5ikwPdSPuFfevm7tm/5fz+8rUK+33lHoBRV3mG71PfAAnKWCLlaRE2iz3wBvb6G5FEnWLYjVtTpg8wb08VmlObl/gueF2PTEw2vKPW78krpEVM30OrDzSzdLnMlUIgTR0HS3yyTttJQ543w1d7uUZzDUyJ9zVb6A2OpRbZZMnozG/xFQURVoYRgAUy4Pnj311Xb6B8RdXiVF2lu5+19BMWU1OR7qLL03WIrVQwIxnRUKQyzYlpQEb7D5ypMkCGPr/1NN10XGzB915aOZzibePo0eqkugFd9vV/tBVlwBiX7J4n1ac0ZXNnRhzCWzHUH+/J23qLJC+LFczKlPygAz1s7OU9JL3qXn/TbXcvYEkByzS/fjkXpkry1IJXpVyrMa84TKbf/kZgaH9miR1LzuqUWbyIiSJUrg4eojs9zo/iWGr0r5HsPl4uff9oRcfSwRNy5EiynjVT8B6WWZk7StPUMy7xZcSPpIW+EYylLbrMQSrJCbIXSCbunC1QEfrvGlzki5C9BBLMBrP6FMnbNypCsRj++W0ZhvoeLBBR9djdzI7JCQPseudxDcpOzkEQgE3Z61Ru2yC2ULGSlkcFpwDtqWEG4iC+8LiZqQVpTulrRl0Pm3IYcXs8sWaufrvSbVHcTKTJiHjgHnW7i2u2zJhYJOAnd2aiV8JszvyX29oTX5f6OFWP2Jtquw/BZX4BVAjkvA26+yIIdG1LmxQBGEZpIJBVtQvaJk2w+/ZFJFyqlM76Uq+kn6xrCLp7qNxnw1a/4akEfVoX/NHEwvj6sWYj+c8XvBLGiEyhACd6Vv+73QYhPPGTBCHKGxqTPiYiVoAYXqjkFqJtVWdnnIcM9OEhQCgunWjTKiwy9poplhIB2i1FqKXQOy0vDDmLdWYCaOlWSYRCc5p3485a09HaEvtuNrRBgWepX12V0WLB8vz4EdfH1vh/jxQfGToYRL+xF7btkA8neBLKW//WJdiuql45hUmJAR7yi4C+Tl84lo7dbxV4xqyKDFnaH6LWXFtGtn9e4YOf4seFKQM1ULsqtDFzgVjxNtVnRNdhKQPb8Z3KBFLeuYKX78zoBgtS0eqyJzi9AM5i6/49/mqTndpp/TnsBxQraqzNqsT8XaLwzv7v+YUYkT9J4nbRXIU/IE+U/BW1FnVS4jkM8offQOlEHVviu25qtlJ6m78/v4IOIwYabe2nS4L6rkQEzjfTb0KMFsGExZ2sJIiX/rKO0o3aRg7A+9fOJXvVfPfQuEVVpiA5Nyt1Sl73GpMkuqE6/4+kWkBDuyRSpliMD+iY78b1E6OPkHE1guJ24TkeeTSQ11KPEAwvLdQzWf8yGOQXLNuPtEGq3VJ5+G3xAUQj6z4LL73GNz77P6/JD+mCw7GTo+wLwnf3ru/eq2NvSuMwIRuMprvkxVciCaIZu74JckDFFYOr7H6C0TZcM7p7mBTHhpPEypTH8zOib/tZvIKq+M2ZbPcur7sPcejkKkJmKgphnchwe7jPXsQ09bZ7UochmbF8a5ElPDgYjLw5h2wSWKQ03tLsb5aNuoAKu0o1eia3kIMIRkeaz/cQyVQr7pFpOCLP3Ktj0KnT/mAXCPeyMNtrklvTKSFml2WpKXBfDU0Sw65lIXnxce6Z76mPCLbZw/eiWU3ge3q1fFJnttgBqMNQUL0vRCRxdbjX/8ooOuSwr3Gou4Mr+sh9VqeVcpg8g9iJ9xeqaN9yZ5AAuBq8DjneMlszJarX4lEZ8dWDytQ5ZzgP4fcjIQzeDNFTCynM6hujj1juLCkNLTZTTKUJU9ItwYxPQeNN1MUvaC3CJdLoQ+2vkDg+7FF4uXB1NYbgpFsqMD78o25Cd84vH9JA88LPxDAdeZNGGKmNBZkGcYyhKiAhyPYMoIe0NtJZ1C5FnALrF+Vj6T0N5btKVzwnJcYjPREwyHjBzPQp4myoO5l3r2ggFaa4zf2HGA6uUY1haUPkjJX1oi93s5QpHv1vjCB1G+TGeb6ORSmU9soNRgp4ZGZsc2hGSuqsg704q4j2pLQ97uB+Nukf4RQETtKXl+P05Mr82peCn6rSyFiCsJU8DNx0oJ+BesRSB7BGfhf6pvsMVtrrm3hJb/ZyKvlCOa/0VEAPwsAuF5tnWaE2r/U7IaPilo2pdxJG4FfzIu00ShCLzrROR4LvhkjG1ga6fRJTPBY4aqfYB3bc093+CdIiBrrjGPV33rqZgIXR9+AE3uMJX56oOt3nl5QZAdaf9C9kTFsmFBWybPFfbVok5QiRajb5QdrtfzFicD6TUld/Bs0g24cZYwhkaPvzlUpAN/7nWqh4pXcx1T+uoB5pr/QJHj7iWLU9kh9evDL1/zwfwn1CGmsc7VTAE5QDaSq2+HKslp5QRuLYvAvFWfMvFkRy4Uz9/jBFBXBC+UANb9w2tEM/+5FmlvRkrttmIcNcGgAqjq9XK3UmtsmoEJevMgEkzIopQsakvw7lgsyZJiOWLFLjYYCnKGG0h7z6gbraL8nmk+C+ohr05L9i98h+geFxK9Iue9M2wZzg2PGcmHtEpL6+Oumv60/kzWUvGjgmU7JQnL0FZFAfzXtACsmTG91lyooMe0LbJNH8mp0aWikNdtIatYsohGdyrztCwEqFOggSwroFY7x1GU8d4Ah9gcZEmmF1MoKB5K+w1LOTD7HHNNoDT5SHzFvOOY/HOljCaX26glTXCf3HAn3YqhR3PJv+dknLwf/yYtmNQd3Qp/SZZp2YYKrVdJ/XpTauS2wbHRTW00jHiEyZ3bf/bnyVXXoj8QoQQU+1acdnJoamKIXoGKL5bsmSQ8QUx0ROcUa47U1cQiXXWKQDzeMqfuYkJlct7N7Th58EZvaUH8C/Ks7O5Juk2w1nliM3e0fw0lDNxK8i8cy7aYSZq3LucKmS0Tftxwfmtupt1s8d4nzaBWQCXMD5Nfz5BYk9h0s9vptewaoMOAbrfCWXpMCpcQRAKnky3ncae1mx4fs93kJy3v+twamkJwKpvVir4NSOOl6A5WZ9VGTVuiGFjd648HAJy86hd1s66OkOpZ5o0AT9QiZgxHKcCRgyGP/pbF/t03U4mZ0QaZ2JkMaq+F83H3E50SkAioRvj9ztsF9wTvpVj1b18PZyb7Bvnp+BJZwi/NSDU/k5q85h8fRSAocXCr6dP65mkn09NqymuE3p0Mvn3mPXBRtZlEsb1Vwh0IXfLqVANaxrNokiOwng1OUFKW8lUFnsh+vcgM+Z8aA0UWhOcn8AgnFK74lkIhXaDdvs2oXB69fJDz9ni5oaMiUFjriyBDxlgIM9fZOIsBvU5ZEifBJyauh9H7xg9NzWOtiZSwR+QnNUzJxFkHSfGFxbkm/tT5WroEq1ViFCaSOBtQnaprZgfJOv4IplbE9fLRRdS5GDBNPX17ZBT+p2nc0OtJjEdBRZbxtkX+ABsYlvgd7ZdLuaULNk1sfUYnk9e2pRvyyUkpbgAt2tkqPsMOZL+PLFl+W/ltE7E9DB0ca8ffz3PdUb4hwhguigaydpzZUWSz/oKb/BaU0w22msHHRu7yYpaCY/StuGiQmVX+p/gzwV5PcFNXGTnpq75OZgB+k2LrCQuOkI4NjOQ+hKQe+N2D1pQIMsnbizkpuCE2cluZpLsWKtq0WchgIFx7r6Ok8tvh5gsi4IJlA/KysMSVA/QVcAa8nuCO6WeRC7VGTgY9o3fMDD7xfBmK/5RO4FLHYRWcROz92/WpWy9jOS52NGhGwEmvqBxyXUp/VKlL/4bobvPGGzDoAZAQoMzLCOCs4vV8+CAjuzJE+APpNeGrU5UwqJoq2FmjO/km8kR/JM0iV02nVnmiQPoul3D2lLdLRQl9t1J+bIyNHwanq7yBfcQAfyCrJLHq+ub7pYZDGUap8aoU/xFpu45zYihWNL3i6M6NjA3aFzJ8NQI9NzozmVdFFUdtNjmPtyeNRRUeMJB2IjmkRz17cx7d487ymtBruALW3c39/lf7aQBr94pcmoXxMwYjnxdyIfB0RzzFrXRjdZOOsqJzkNGO/2JraV86S4oiFby3P8qRgh7JaBFj6aJ/Bo5RqHUKdpO+QFlgq2VpQnjlN68azZ2XzBoNLUBoahweAJ+hcx+k0AtGFrUz2Tag/ayHQGelXC06sWNMeStp1q6p30d8ODIKoQZY1fivOdngRRGTvqmzpaWFSuJJwrLFNqCf90GOsH1YwPnPOxRl3hNjrLgUsslznffVE6p6/l76QmZ/25veIYr4Njd70YhIgwY0HF2xoWSMlEF8Z2WfIzihbXaJqa/2NipIxyziaRIVJSw9sZrI1i6ZLsbY7I418L/erf1zYbjJRK7rOYAeHqnyZ1pGnIwSXbeKQMUf14c2PEAYTyLhxR7mwNjDsphQ+VQXkZv0g9sTCYDBLMFRJqSCIsui92S8UQCg2OqQYJ4qO1rW1KKpL8fFGXYqpL3eO5tiiJ000UIV8UCTWDoymrxH50nykp864fTtjXZQ6OQ7iUQYViqU6t8yNIzpaR+/Jz+34NfCnorNiIe9UIkVlj+PS8DznojZ6cEfncvv4HKwGop0spLB8moVGuG0yWvol/dPd+7fTSgyylo593G9cW3MaKB3uqjuGizMZrS56LqlpTYIbivJ2Kwg0oBVLyYgJboT2FYunZudM3H1rG9vyuqN9p1n0oxPAEFqteiHbQgi4WhrCXBotsg7FoYCxx9n2Fm4rvX8+e5z0r3UloODoiAm4O+q8GziyAtja8cfeRhR8TiynGeCdrVzBphhDyLgEZqOSieH+3Jmj1Nt2n+Skuo2+JChaJwz6C9jgnoYbuSM1kN0ESSH+QTpCiGCkdVRQdTiQNgF+sDmaKt/lXEc5XSRk+0Kqc3tN79OWjk9kXGF+WuGkqQoCSnXyNqG1//4hBg/aKVUBlSGGc3xagNGfHQqRFcHeGCOx4IcKiSUz+WSWq8N6AVTORcAG1dgC/lYul2He2QQ2Cg9xxlD+kYJP+l9NZY5JxR5JcLAdRucxv8cmc6O0YQRXoSF7GF+JyBuGJLwjJ+3MFrQMGHhl5rdFZgechRY/cWPsyTMULW/eSD5ySqE24Pp3YxvOKHKWyxO+lqptsBtLkt1nGROJN/H9ilZK5n2i/z5nks1xKxplA1n1/qYzoR7riT0vt+f/0JbJzBwAjXrjLtJvoIKzpvn0b1v3bFE6d86VpUAcDoFS8XOopOSLdPr4YXEEGZww8fwJbuijmHU97MRWEr/yFFXc57EPaFSBEVKyMKGBz4LfLTVfDcmeMZVSi2ZytvS9yML7wjN3LeW/CGhbCHGNdRBzCc21FDZF/fiMFI7OwRdQKY/oz3mXtDBxkvVMJqiaCjfwVnUelhwNkBQYJmtDhzNxsc5zBrqCuLeSNxnz2ikbHZa9X1Om3Rxm81L/BHT62xxj7H+URj5DX6ioz5P/09l+DT0uwL/YU7bBFIHEdNXUeSWvjvw8cnGJ7arHUUEbwhsGbDzsM7OCXof5O0tg2BI8kmYqRcXasB7JBBN/rdzLzzzkU6qaWcaIHAVu4U0XPH8X+jnUkMG7Au49AJHQ4sbuHyAyeZoYIgV01oPGBst8beeDPSivw2OcdNGKdm5+r4H6GNV6E1T2ezohrqOKFWMWmZQ9ypiDOKF0effpvNmVCGKKBVNLul7AW3sDIg4G9E94ao6ZUYmMaZseiNRjSESYvom+0IggxSfLhOp7cwOA4/TAZ0JP9qwjL+Epq6sibeQfDzS+bZswrrsLWmodSKa/gSUPs55d2QkYr2ujDsiguOJEvDtERRmzz72FQnJ9zFJAEslCvY1/sWicKzxRjVGK6P4DlYC8FJfmiSLvwpCqdQmtBEYj7+UC9/kFGQIU7nLU+FwIiAu9nLJoo+tGT7PX+cGiFeBSdFrrq+0Xc1xJEgHqnsKwl6PNz33Fwv5lcGbd10CQtvO6zFK2EpyxqxSWvnlA6y5iTgwU2SycWwTnH/h0H+eshXP1ymd8PpKCcXbFEw4p8tFdxdAMDKfW8Rz1ya/bKbPRebDA8w+IDmUdQHBfLVNVh5aSKGrzbLLd8S1G6+nw7YA7okJMCCpSY1qwEIEy0u+METXHf2oGYE0+Ve8059Z5JlLqXFeS0mp81zmRKoLJp3o2KQ4KqIu/Fz+lR7E3nkTtsH8NDyn4E06UQJr9jKQcZEbaburm6SpYfRCiyHRP8jOX0WcpLuevx/4bj9IyHRLCp6em5Pm221TJFMECjODDmEGjZArOJK+5pmDkgCnSUroTqw6ZJkVC/+2egrfZd8NLFFK7BGlRsdPKrdpZyQwHBvwJmj5kr2nf0PHBZ2iQtxxzYlXBcZ2+QuyA1Xcm3BN37q/4u2+tCpSiad4PBg6698aAm8axqNDa5WIgJGImPO4aM9cgnPEMMNkiBkrHUAS8Cu1u6/tCZHna1rdNm5MpkwJX7P1UQ+bTg/lHINTBZjBQvSZfZDfRvou1G91DThis3sk5VP+Y5mvqrif96daY/vCT+01LZhiu3OdP+qf1CcSrrmkeZ5YycssatLTqdx8mKHBHkBihqDCrsm34dFLshl1P0EUy61vEdsclWLNRD/U8CP0Eu4qcuxEwHOwZhe83cpysyzVM8AKCxENGrupcy04i6HuItCL9HEA0+HW3ovTOW7rni+6sbXb1ZMUVCqebf4sxT/qHo6Etdqpllmqo2pp+L5vf0FPlsDFLNI514SEL75ldpeOKmoK4xRUSCpIO3ja6adV5rcDqFn9p92UtvAtEAYUvW+SWObIkjy4FaoyiLfmKoQSI0vVy/hKpGPorGEkQomZwaZRSpqXqP79uqUbzslw+w6mUKBcllgNacM3XhUcekA/DXEA1JT/aBH9wW57VT6Op/UphpLvM0hKyFyeBD0esDUvZngghShMu9f+TOnHuYofM1FYujLkX89OYt3ODpZYBwENsAgrbtxZet7jy0DVCsKOqlonq2n5ftwVVAEgQuF0zNvLA2AQuaVxLdBi4u2kWUfcmmCSV1Qgj/Zbx8wrcfQVcmu6YoxTBwjCrf1siUavW7NCled+qEB509hxVrW7Sg/pA1aX6pXdmTchtCepuEBRs9fQU8yXBskuzTc9cPsjnUJRyiL2Jfyvjz2UH225YI0oXpOv9o60rAxFLnhFUDxJ2/62+auGt0eRsJkAV6uH+4v6uW+ScFtPDGP+m8Lf21+HnNAsFRcWjBq9SXczuOUQ8WDCbDZ075JSk/2ubvX75rpxD2sq+UgVFbOp058sQX4PcGBM1N+vm/QXbxrnYlqxBfUaAP2mVFA8bPdr64CFlNGGzJdf1r6wk6wAEMzY2WPnEdqzAqOnT2lo/RIulLUJUtCI9ohL/1dFkjKpoDjTTmGu/PVxmRcCk1kBKQvLS1VIq9JnhXzRGpvYVBRPNroaBHTlPW6iSIJ7su5MvYlIs7ysssBo6saqYtFgIQ1qax6nQ17D7gjMNFfBNlR/Gcb5JMxhUToAKZC7A9ZaZrb1t4w9NN3BbI2/aWDmSDYrcqCTfV3/6aRofSp2daduUS6Ql+fPWpw8kpFk9B3KDVQnIEsHcP+BSMQb7EB9fXuvXMfGxEMZicesGpFE8shRPKn5RhhpxYLEFtmrSXerG7USFcgNG40uPTRfRlQrr2HnqoXp2iY+hUesZSO8toBOxAQvg+hC3yP/6Um8HC/BkYdy3ficj2c6Y1c8cI3vdCFv5CIx1DBut+R2zSkeZTwOsDjTSogCC6qXqBccWvP8hWva90IBYnW8/6RX+qJ5LfWYtybEDxIQScH8ly98ZjjVRe5xsWh/Hfk9rFlXMXBRuRJ5cSRsum8FeO/aDkCxMWmKcLMt4jm9kvFJw7DwGy2obSz9aDOhWJk/PCKxowLxtq+XgwK42uTcn7dngH8bsTUo0LFrljnxptaow6GzSOu+XVIi1gVjI1k03xhVQY79DDsuW0cLefU2jSFXZsgcoYNa6wYR+uLqRb64HehwRfCd5pYh5jYPlVXJjOEnyiscWXrm8fpjwHDmdwjDKzAj4WUZfqKmT2W0bE5ExWivvF/TETqwiqFH3kijc3x6SJlL+Ay+0W+GAJRNMXteZKg6yooKXduHF0ubcOT9uAlsgXyooHuYyroTxCPHQVtkFX3urHnVwxB4jEWCyEUtBLFrzNMTdhxo53Yzrqp8x3ujLXN5/sjtdhkz8IQdJrfeXCx41MF3gWFj8MbT1dk3wirIaN2OKhhxdIWcyJTuHcv42LiTcywA1OFoBlyy1j1mhk4xH2vt0+n3iwQ7QQoyZkC1BXmXiyq1PslQ2i4QfKtFj8grPWRsNnAlHGYCDJHlyVQKwT/sV9zhhM+1IiO0DzF+wXgQE9dLRMkTPf3f1TUsyvdLW3LXAfR57HkD9zoIwhQOEpqC+LiAGm2nnJ/j3Cg35Dgm7PPHkU/c39+RJK2aF4WJ4pROVDt9ibg6sFYq3qld0JIIDIjS28fhEeF7S0sHPFGcdoinIMh+DzHvSyLqaQr/EZFCJ8QVyyAxz1+mUQ+m7xWBXwI2JaRc55lO/sqqswjEPzo7AvydlkoE4osPnU4V630xeRrhMIzjALeFNxmJX6EnyzX7hkmlIvwsw08Dde7JXahMuJqKckRd2h3hXKVDpBAfjMdUPnAxzdAYk545KHLEXyncx9LMZlqfcUIswOtdU5pgvtiYui2WcY16hOIzCHTzcO+AjhD64EWtKgQ2fIxQ/xz+Hi3zvYhM+6fHaLWwWmMm4w80SeKXRGpxLrsnn5/J/CNBDPjDlDZKtodHOLbc3BIhXn1rXoFng8fEQYU4QmqWCPPLvNDmkTVR/RoTle7SeXQU6zqAZ1o7c/xA64Zt5nWMJwlejDcWOqE8ZHLWN/bRY9r+wEcAnnnSZ1JgXvTFHVV3/LFCHLdBb/w7/im2h49syYRheCjKndzaB/I+TldQpn0S5FW2oAyNGn6fXS0pQOb5BCfxf+wQ6vRp343CT+hoGyIrGxpWED6LNjKGKJTKaxEGDPqiBF3rEl9D23sOqOY98gRVLuxGbGGTyG9sknQ+xq0x9bMes+hpI7ESxVcPjHab8BmdA49bJDFXp3FaOenitbsjkvWvwHlSG/PJPtnYB7DqqI86SC3T7tN8iJ3d5jm8e/JLgQbI0Jxa14MO0JwKgk1lz2++wqLkGYb/k510nTfy0t6eysb06zWeOjxAM1l6+M6WLpOUd2on1lMT1gL5oEMkPwW6cKxnD2vMvMXSdaGYfXZuqlkdQoR9mtSmYjwF88n+vflPRWRR4e3wgVoDh0RMDcbKIDnGKRdzV97u5NesbCFUMWmyZMQ4VkP/v2Ldq66XL9LyFEQQWwUn/UAvRB+6zJ6B/pDS4TzmJhtiXhLi2PrIjgJ3QFs4t0DeKradfTAOtMOF/AUbj8UosaToJRqSg9kbPue3tcLjGz4pIruUGyDgU0l+SvsXecSQOPvpQJuLVPuxWIZUJVlTXw4yxa/NWGKcXfh19Gv5GS85CwqDzHABcx40SZSIAV2uR/YBZmXtg1ZoVcAgUqbtjHtwesqP/GRaG1xStXAn5gtwl9oXDBESY/HbjJ+zk601rp0GEvFmdhz/G8lly2p9cfEMvTvfI1HewWgrNd6E0wuUt+3DdEljF7o8RKffAPI1OQJgXuuyEzd7idJYppFVuHTDuVYYJcaDuyh8MReVne2gxi0VULQShOhdx3LKrNZj9WKbLKYhc54bu66woCjwpSffOezTm9l2JJT7BhDH96zm62qzvqojaVMs50Jvv9NG8S13BxWkS4WTbvsY6wq1aT8Nu4iV9eOuC3Fy2Y0QR5GUQiBtDft1YBExjXn0tSa3JPRfuEcq1blNLpDt9deHqmJAD90a9xTX119o/yAGg7J0p9otmGv/fUfXpTgR2BdmDvJ8qlruYEdismeCubGtmXx2EUSHTj+ha0AftWct6Wb2MkZ4xVo2x1aYCGb7Ik4VuR/Ny5pagsRm38ZaPYdz+BSZQPVd42UtCUOuOJzvzNIgOn5bXS6wZeZm9/LMbVMoe2gNTCtik3BhuBFU8CYq2vM9F2twDPYEDEabGfuQ8jSkqQONcs2s0+TS6bP7RmWAtgrZoK43thlJo7W1GH4/5fQiy1pd3D+I9fXBCU0KPpwIFb99+F0dpyJ978pPRISwx6jBmod9aCfGDahHCKeVipZDlT4XpOcdu2yDwq1NHcXgz9mKoAn0rtw+53J/5L8ne+DYVFBOWf7yoNxfDUqbH2f/FWUlpmHa73VDUJQnm5JU4G23zZb3J+AFN9JJRYKWTgu1QnafmUn2lQqF/Flo/2wc1uaRQ3BL4fQGpwWkzQdvefaLynk5MGiq3qJl6opekV5CpOmIj+Wie0j7/UpbQ9YA7/ClJInuDGhBwE4TSwL8URdZ6SdV1X1ZMvPAULM9JudKr+3gaT5eom+DE4UuWETD3xjhym6iA8ienHDZR+/9yTlC72nY4kqbFFih3Fn7CLzv/iD/YuisjE2WOmYEMgkTDUNpDgYeYFoNBrKQfgBBzRNJ9dq+Z89YCKP35C5TkwPoS9WoyVPdXsQzGf4+/HBnRkmGWM9CwUkL07e9gR++JyMUKnrDTwfomC95xsUM/yO4b3KwqAk0f0swHSUetf/1diblPXARyC3LgKz5+qZgXcX8SCp+OVrOl9LFaJMop3tPECz01Dj940eFeGSemNs4KxPBnQobUc4tzYcEnyu9jiKgzIKDQlkLvNWYE2gwwDxDLCXgtGOzHxpqB6NQANrvgnZEC7IM9OrZ3Qi4B/Tj/trHtVmXdNVzGwYaVrf9qbe3Y4iSyuk7NiuZ/YdGumay8pbRMIZdnXAkwiicJL3VRzU6Dw0K/lLEvZjCJBr3We10SN2U/YtXMJkYWUZVS/zfNBS2TbEFwR0ajZxHP7T2/UMjtAs8PeXede8Qp1/PIHYjITY9BCbtDPafSaINE2Gim5Q4NORXzK7KcnbMrdZoD7n7KzVMtBP0LcAW/WkbuIIrXuYqEchEP8kE96E0wLvhuKEXrT0j15EeCFi8xWZUYfPbTxu8TKMTyicMUH8Zh/nHidoToA1t6ZNIIHGk1YrMC6RrTTWxKVt9l3fXOUzgCvehZoQ3dFGLz0L1Yo4rcaEBODVD6qvE6SPoZJ2Uuw3z5chRH8EW5//FXcXmx0ohiXfSFt+JxmN2YN5kxc7OVcVGKKCHcm+1wvdJZWwAv7evjouaFvlGKNPPdniH8KkCEf/4J0tD1upTUuYr8u7eHSl5bbUKyHqz3kq+wqNDZ0CePFJtkUU6CsSSX2wSouoA86wO4gTX6nRVuIygOr7mCJHyGCtehTN9+AYfVJXOi0nQVJz1i006mIln9jROqwMuDYQnVXjFFCuS0VwrKxl4EycHdfUiK4WiaA7T2bp0ibmBnraMKGGXb5jlCy4b7Fxn59QLTeqYqLvRd6MocT2n3r46QFHXQgsdcVyney6ZSRydJ8+H8F5UMhRTMTBPiWG3QhGMsEqK2XJYZ+7dg+SbKNLhgDP6l7Z0yEz3F7UxPKXDEI9gqWacU4xQoWPsTS+apopvh8rYnlYRTnMS+aWwWTVP94tHKWiAs+AQn8aA8FoA4J4eU2LzrCrU2OCru6DaEnu2KXF1bIj+RBh2RhCGmYroqOpMj73q9fCg69/UtuewgiMZbLlZq06U9v1oyv1O8zhBdNp2aiRgIH+i/bV3CWC/apGjNIGAcZ7tGolUTRiGzbQNAYfScG4vfMefm+L41xjypWCSjGZXJ0CxBmMxukO2WcPUm8xPYd2XnHbuILraA/7r/ugufAJo9/QMNdKl7iJGJXpR7Qql/byp8f0LcyvUXb+2VPT5MVZpvc5dPlt4tCpPJaimfBNn3QzzGJPwlVlgm5KmPBdWigSl+m9TqvR5DBXelTr9ysoo+noYj2we6qQ0qsiBc84WNrnmjWYbU1sEr8mYRCxpMvu1t4dxq6lugzLFRPWpiB4PzU4RNQ5UUMrHtFOS+Jfc+4jTbHp7PJYm6jrrQBTWTADXFBVbcuxrE+v1RHMQI44IjMohC2FOYmd/eCl5r7AcAA5Ue4SpsoRLyLjTe8ju9KspYAd+zJQUeszUi1kVa8c1EUU+lNF/xkUGjup0bbQBXK81iMw2KE5b8IPA4dWQY90KX4GzC0M1sW0FfJ4ZsjYysvtUtaYihmLi0wIypYX316MgLuXVyKhr3CCDc7yB1oAbhtPkY58n0chPjHlUmkcY+QjD/dFluTnrb0x2axFv7AE96QykSLQ9FrL6hoOfK6kfeuEImtt0e7+YCxZHqb2pwrMVYhI6iipFECmWQFVM9bIo/VsW2K/K7obQn6rPCFt8KNIySTKy+Nk49NzyYM4VRllxV4JNVjGtIAuuuLDQZ7ZfEEcSlHrOmx2l+LLaVSvhrtnrQWHXqNmef53dJO0M6ggsy4/q8ahuh+yO1iCafs9V2/N/HMJT2ia+hV4G5RKGEjY9F3PGpJZut2d1Rx2t6a2j+kzk2yvctpvJsnH+a+AiORR25pdxKM43v18Bb2shHP30EEgBTxChWILE9G+juhIVOzib6HKbvkb2+/TSU69l2t9/ZTEFYNhIvHMf73erUuw9C85NDAHPjwShLnNp1pZwMcSRcQ/YoXNBiAP6Kn1t5RjLLQZL6nBqVFbSZw6/gAmNrJzDCACCB0cJSQK7/0G7OZdD4k8eFuz09wLI/rqjI6FD84R7KX7yOGkBYJHlcqzCJr7Qo2IiglvEY1h7NGM1fBzVT0bNdSlWiIuESX6iDlYPGwbUhi2lEJckD1pDJI6HyEOWsfhva5/ZZmmZT8SBqoKiOBccIjxF3qIm2kL+dJw5ZJF5dMoVGkCns04ibK5z8bnATZOUMDx0H074BkeMfa2lrtePS3bDvQRmjkMXqUgk4ai6QOaigVyh+b69heeqsogOgI0wfbq0dOGxCmOPmiDyJb3I4P003PB6TYvbHUolUhi4j1WvxdeSjiDSCW/EHNkoruzVy8hCcn1xM8+Okwfq0/98oS3jSZoMX7roaJ72pJr4E0mmaua7fMmwnDLLXaififorAAr7D8AkdudqVCQ0zNLuSZS+ayKyTLb9/zIj3ye3YHiIUHer9hRbAYL3Y4567Sn7tFjVXfsr6ffR1rHzyLf7ZZNTSgbvwPYvr3iL9kJf/pCK1/uMmn6gxEZKQcmOxDp7wYEQAaRMpE0pPzgfmwzF1QDjRPtUtzJEfvgJ1U8wgKcvBOOc2kwKm8Lpcc/RpkVnFyyH37pM5z+iayMgNnb6eAjZwQ1zYcWT1ITzEhLRAzN6CFWj+eRUn9RZRC9mw2wlu8RKEpYiGTXTgwb6Kgy1rLVJDP5+/1j86DPl9pnbZs+kP9bfLPvcyHmyZpgFr0F0OYdHrMBqVzQKZlrsea6qTg+Mo3eIiXhuWhmnjUshqyUbh0/yIX9HeC20E9WcoHWkPtA1vUFbxcg/nkv9fucJPVeIG7S/Yr1TXzBf/f1y1EF8dUL69NtCeXtLCvyjuNyC5M4Bu6TMvfvx11VpnRQcY+1kochRXVKWyrd8iRrwvAAQV8TuVco6o8/hz4evfh23w6JRiy7UPF4s5MI6FNbbgby2588X+9d7g0FPC3rw5x5mJ8X2VW72/4PMHjKikmXEDaFjPYclcEp+SkInU5cAFVQzRAKKyjkCe3CCZez7ma1fz3f0cOiji0pVmxHlbUHWM84qiibChy8xTijLD24VptagJhrqFcabgRLn/2DmJCZ80gXqFcTnd1hAdOvjBJppt99qp7xmV9n0aNBCmvwAEkRg42qLUzk5g+ocXYwHitW73Y+u7CkHZWTcafAE7lymYbmCg+ZkqedOT6DpghjA0MwoGmvJErS1ruz0mpdt+m5higRzvT9xmUqonyv/mIR0Jon46s7xDR8/FU4wXsnJEYijs5WK6sJJagQLNDuQqCTS/JWHT+Dg9I5gssm8xR14TxqFpUU9jxGVshGmNbB/9gTzg5thXC+GrXneuiCv4kiVWVnf/18Idh4BpucX0EHqCLpQpdKb+S6C04QLfYVMOzBcRbwisyU/LSdjOerEjpFBwMWeR9J8p0+bxbn3SzTmducmNoG+HtBUJ2xcdaz7Cahx1Znnu8GoThGTWZaSeH9HSBKKT5F8kLVVa9p737EFthijofwwper6QzASsgQqLSlHkgpNyu9ZAvCz2SViGAK+B+VRIO6vYRVYpY9C6VlBuoefAq3Dch83Y0lrBnYHW6NvcZJFozOdjnWn8Agz+rQl3p2cn6wrruh0+MK0pqkcblRYM1KjZEFb5X5Ott9kgf7v5QrxEuHSG6qvqtBPMzffOfpX0ga//G8Su3lr7a4lcEOSzjKXsmxn0g14dR4w4ImLk5BCjqH+x5XqHEXsKhXvJFDzQJxUCo8FMl1jOKIW95oxmCNzJvCbamR6tSE6HutVt+QW7RhKvKHOPmSgtyl7zXFEQQe3Uq/Rw9XSqJZTyI86XXE4qTQy2Kxj2PaREBZXEmxixQGxFWEalFbJtkglSW5p9iXYNampCV2h79FFl9K8ag9gfahawKw0zGA8LtDOqELXwvWyp2pnNfO2rEcnO8bSmrPTLHaQcOpaXbqgZ6kxJpTNdhcQy+FRpy+5Tg95GS3tVuxQuT+bLDARCFEnIyOC8LbEtbfgGKTl3szgAtCcgpBH/gCOtY34u4+ivhF0K9vnoV0sXpR5LV39p78aNNMKeM+yrrBA7Uof9Yx6qVzE7strQNIJ+zhvx7IpAn7MbysPTlAtbThbVtjBD+Is1NGMsgYJRwBGr9Q8Mug4zeIaFZVLeHsHhKpzRyiF9GCS9f/LSFrGfpiRdeDU3+EcccpEI1XRL9fgdVQV9yqUmcYhkGm5YGa1815bJ6IWx3OWaGveV6zTYbucOCTx+1+naAMNfpC7D2kD65H+48D6Y1O1EyZOG3jOOx3pASqSolcPQh9RM4C9EreDb+dOPWwqpWiMCZAywtMpCkQSKZck/y2fBgOiGTGjGVmRSYZ0zUOAIZxeUtvGFCUorbzY3ZibtY/pnbvRORwsz4ddJfV9swuF9bvgaqcjhhPykqAXMlL87JYZRFpFlFaPxmZ+RCw4QPjj/gis5e6hdS8vujlGOSazNkKKRxMPgid7qhXqWBjhu59TyNj+YvNq8d823I2GOROPIMrWcAUwpug+zB8Q7G6dvxGCgJSSG8g5NyGZlJsuNZPKmEWTVrPJLL7Nty1qp6XDhVKJAJ7IdFnfJwF3xePkjB8D4jyZtswQQctz1tmIijVBrU625M2tJy/7UWoUvAhZSMwFwyR2FplKbVkJ+YoagNHcIKXV0UjbWfIoy/A1iC8e+C4oGW4gasCRFGyDIKVUtoiPqQbNIJNZpK0l5ltimiHcEi9GQY6oFcbi5gTcN9yYsAG+TGDVl39KQaiWMHijKJYA1YIiDCiI/KFpKl1+zq/dCyBb6JNRQrBKywLxXmKtmeegjvpPveAHS3HDD9kiZQ0OgW+BRvV4BnEVSKkbFObHYWPxWSgS1egJNfKbTR53aGmA3Dg9FrcDB9Bs/yZPCmy6Sr7FHdrwjxz9QJpq0KAoK/4Lh14xL2Og8JIPl32bC9ZkpyghYcHEqRjm0jFlcSLmRrsrE43shwZJ8h2TZbmDqAhkgIuMb4M3RqVkdutESQMY/gw51W0YAUaq3PhFiwyrjGUev3rf1Uy4LAbZy7MZ6/y9yny7D7frH15UrswiFmI1AuIQ3rrWqJxmIhjaC6iT+TWYt+1dA1IdYWuUbqEZKC9BsmGfegGktJy1yLfh0ZRWCsvJGFhTCXAnhTYzMnhJpcfCfvwdvUBxv/8q66xNHqWXAtRrmIPE3gqtH2e3p8Yo1ZQAJWC4o+JKQyzTx8Brex/AllPqZ+EN6v6oRrffPf1BAcsjfnF/bT8mOq43za6UykCd3i985wtPrB59oeKM1zY7mjw0hOhSB2l3cUuLQoFJ1GAlxxYhBhzR2I45T+dgjB1Aq6LtQcT80P7xao+myLK610jgmtqM+jtZaVEetqL4d+qwNfZuvtkkCMJNRNRl1izJGF/WHm2RX0ZZnrCH/ZhsFv4G+g5f6bBLueeZhSZG5soBA25wdqcHfEv0EYr5HFRXIsBo193Lqko/evwK46FxvjVWGpVAxibaD8SUNtNj+STKsbE/6DmPdT7IDl/k/8rI3cqm3CFqRvQCDDxjs4SkKZUtS8gOfUFXPERsR7ZmcVIiukmgZ7VQuYQf3vUFHm6kjqVqc8Nh/yG0f+xfYwD/zGHp2wEp3SzlnoAZ2Efqj4+h+ZFBZ5UfM/6f4yRh01fiVfksUZmsk21f8rSVLAycm/QhzcQjfvmEzfCRuFppvKTikIFTJiLYoJRVd7i8l8tAqHYjmYWOSAPIXRkXT+kN8s8jih8FUNGyKvSblNkHdTyJLvHDOa565Pz+fuJwhpOsE6jX4C4RUjl+lk8Myz/suOH0oX08awFh5ORdaGI6mCQbkRYZizlDoWgmVfXm0h4Cf1Ul4ATfqeNchKrltRQzcDcahbi6dikAwHA64bzoknEdbZiCRsNI4EOawHI9PadXRtO4/cmpbK6m+a32pWXxbsJVligF6ndiz6NQwPrc0Tm3KobnWYeXqQ0wU8KqqpEtf8wCygEuwo869L+eop1z5UqkcGf4mojNtkfEB1h8lft9Lfumc7rBYFrj+zSiLaxSBWutbIp6vs9C0veP0+j3eF44xlVsJzgdEQdQ+XoNTipxNOj76T+sU3yEFvvAMvN7/VfInDSMlbOi3TUf0Vx1ZJLchsD/pWILzNwrct7G2HBQXE1yq6ZM2Y382jvueCtCwASwjUxUc9gUosUoJ9UKF85HP2EpEg2If87CwV5oPoXDPNbrswR/SR8U8rwhDdK1F9+bwrtw7v8PuLBCkEUoX3AVctng/SJ0b3U79EhOa82HpVWoUTeHq5Pr+pa560Pw8oCZ+7wEchLAkPodFctcIci5AaM4adSq9r42CNN9BNhLyd2NsetlKJY5HKAxsVW10Q3h8DIxJweqjS8byKOoPfXRaTzqtNyimDezpMG3/24oPyMvzXb8fjYof2vVvN/fAtrvPxM3fE8GGXt6XrIUAjQ/7pwZdcqeSrdngzUiBOjoR3jjGxEmPy5+UXmFUDeq8kJqcZvPKPCkzSSzfWOhxjaBknsTMAKefahwtMZV4JpgNnkAAZB4rXaxxTCgAPNz2YH2iCppmDv75S382JHO2xT6HZorcxt3BrkGvy2h4+tkZRfd2bguZ7EyR+fK04xvcT4ixnr/a0HsnQLA+mN2lHEufubh6JKQvvqlwjp+TKgxU9ZndYT2RKAAzNLy1YAjbYQNDOQTxN8VHNuEVYnMQn9x2S1JrDuMbLFGNnwouJozA1wE44btESDCtNPRFZG/pkARHvQ8xU4T49lSFpmFgMBsK4jS/+9rkD8XXCMBXn3vWMoG1sEgNc55eoJf5lNCeLtvW3avzD5BFfLCQdF/mN3Sj7uhqfXFmiHILNAFB9v/tlzIo7Fg3GphRemKBVnpJXdRvyltV1Ps5ViZa5jMPYsTf5nGcOO6rlnYXNiO1YBura/8xcU03zzrbGpgIST1aZtogoDGxDB0hxqoE2lrdHLopD1mFDXf1RHbVvGIGh8iGZ+Iiqaa5Ecbmf+pV4YlpYJGtdoSvXRwF1VAgApx3WHJ7c0y5JMaop4UP1k1Y3uFp/OqRem+8jisrE5UzUNTY/uJP6ymQjrJ3PIX7Zav/WOowv0xW7HF8WKfvvI+tGFucpRUJUavb3iAkMhUGcFvO/nK5f88mm/eNbq4vHku8YVhNKnC16zWZbCGSX+Ae9+Q+BYvGHKomx10LzvAU4Fhd+n1Pm+O9qq3XimRPiYCX5QX2pnNBgBkEPzWmcJtC7ouK1YLcnxVvhmAxoGD1RCFZDHvqEgQ1Id6z6NFtyF+Pvtt5iQeKtSlAlukmp4V4bOAD/htYl0L1KQye+dlkyC9sWawfoKPqKyin2VEVAO21lw2PuFnTr6fTvaRGkZL+lYqWguT8c4Ft6uNZjVB/dEGVhVLXHw0IKvUvZbHqx5/1o3huGYs9S72IOs3Jg0mjLQOME1Zbnv3EgxVfTUD/evK0v5E4eSrZNSv6fHvhfrcjo0oI21+0Y3DcN9bkILqRuBqkZjB0/jNk13Gu+ILPzWC06qpWFt9EltNa9v66BM/m8wE2gJGJf7s/BSdMAtffbLU2leGm4Is3JcYOcgg3qMTRmZMZdaOv+4ojqI7TAYTbcnCqukkrltxagh+4w5eAzj2o4C9LqkJy1C/9Gu2IA4PuX7BmpoqQmem2Wu1rasWh4fHXTCufI7N1zdmz7CkahVpj37rizeNYFIQMl6RJwnSR7gWMQWLvSIW/yWrul25TEEgVbbiPMHW0rzLgfkYHq7naqiNHWm37wxJHssHwXp7tvhzPRn5sB/F32LWjQQrt/QBc3qbSxBVyWTwBWfz0bjrBfbQoP0/pEYBBR4DRQv0qLiKt727wwlrxWkXWCftY5eI+TBCKoerUsAthHY6icazHQggxx1ho5KA64tZeGkbb0HvanX3Uh3PGQE9RFZ6SA2qPzyuVGkEKolmpnwwevbn6Bro6HvoqSMW4Rt/IRRVYRLdKcoedz0BJUFm05T9DV0lWbQrDKflMJ0HmgEmsoQlBE/Nc04uYDgH+jNxYH9xaG2C6sw3QAbp3rfrLsHsZMERpWtn3UU3jpsNk0WEKc3aV14JNWGpZN3f0QaaL62S4FHWku18edSVa0Pol2AsOd2X3N/3LBvHT/Xz6wPltZSemw9bbSWYL6hWfWVejsZpdlgLHlftHHrj0IHrTLTtglKcHYyCCZRpvpJ/1N1i+snIkPxcNFJCaOcdBY8EPQ48nI6yZ8E7/QG1ilfhbMZmyIc/jrKcF/mZjUQ3apoaniq+jLFj79zWX+jY3FfSvcy8TQj9XQJwsuQPgIjT5LH/ueqliapOUrwnc1WM3xCnNT0ETvJaeQR3r9Ma0ch2xyFV6fkmJ4YWHupi2x67nSMC2J1i92OtlIqNbaq7ZT8kJRAd47KKRK64zT27SbuHPw+Z7uFWd/zwzyFSKtUk9ti0uO9bP9SJqoyiKbYADnJGx2r0OAhajUd+hTFcsqlDVpmfrXV4WTsl6rKi1yrpwJgTR1fG8lTicNIHtsOraIzy+AuFO3E6fEe0U2ichgIgT+1gPxgl3a5WDAgy6Ym4ceW+Id7JAuWwe/CvTd1NVWcYzzmzP58ZpLc9gcMm+OeySlMl+oQP0Y/5Lpp1/WaPxeVic0l0GZArdGF9P/v0FcpTmM7aJxKeV+eLljZtRsV9cvr2R/4xlwnUMYM1uzcLP8kIA95sMrKKbPhvAfTVVDVPcw2AkitL17IfDlDBGs0wirbE6TAkqEdnWHQSQkIdgTzO/gdSkBFFoVN+IqpSKjJWxMtorXL7OeWNOGjMc4qeKmvfephDeXpj6HSHsmK5dvR/HY0Iwxty7IT6FApwGkSe3fNkICSlAvSxq3tnFZQC/IuxmM9h3vaL8iSB5CNUJyftTDiTyuHnE/AFNdaq5cmJ00MLcpBgj/DC4cnpdqp//LtZ/uir/2ot8L4Wg6zz4OHF9yoxYUG9B8GlS8GgfETmAAaSuJrdVW3qOoZwk50FIFABYhAixc4N62c/umj0z9edIiHtOGZ+lFTrPOaW5aMHYe9X7ij92OOvLi3ahp5X4ViCffsHn9iypWP98oimPhuMSkxTLsVB9aRnAl7F+5yYwG8ryrJU3xaipDbdlbMEnTyE+ZTNG2HHTTnN6by1RC0mw2Ud1XWcHcGa6TwLG6dqir/v1Kq4kADsQgOez4P3C0SN7CM1DmZhWqWUZovbcitzdnsVmXQt8ep6m9xPf+Ne2BSUxh7DsBywsy/Gm+4m1Z+pPHLQuMoyK56c8I/ScML6UMo1VYseIes4pxdPrLqHc+xG4Ogjy6yZwgNCRavHSyf2e8fsNlQvhRk8yLCMORl0fzfkyeugN0Tyr9g8DUlQdedicU+guKxwyLnRdN54owZW5nqHmeimWCyGZR4AcqvlWtlFBcT+l0iK8BvGOF+V6sRVaUjDc6/1Ef4Y7fNu0NtGXTktG9zxnpgPIS1ORJRmD0Wvrc4tfI2shceGKYkeedVmSQMMGQZXwYJ+R6Tnr3Wgq3pndtWnZ4uHF9K5NIpH+PmfyCvQk0Ku/zXGhC3M7PieTHvsiAb6J2ntmSfDvAjps4LhZkj8FS15QLytp52iGnwPEn3tLZIlilO3omypeyl92PzKrpBaGEZxyuL/Hf51zmu0R4ovfcwsPBQYaqZrxx/IKPRWxLKGiwl35nBElAdDKxNZoMKTWryC/WXq0wlDzPkvK42iPuIMRoMbJiXLFWnu3ArhKV6aRzlYMYOttt4MvnJqFp4hWbPVH1w4+O3MGL5jrx+nx/EN0ZD/GLybyyBbr0X5kotvQXF2rMjcweDGCiibfDm5dDD+eM/XmX0z0ybQ3ffaBnMezQmyCFeTIW7eWTrjmOtzUpaevut+CM3ssvm7CxTxhTJOH7q7Hm5Crjuf7+kkUmKt+h0Wk9rBaXICZsOStLrGZdN6ZQSSsAiCzXnKAvqK+VQAWzx8El4Ym25lMkN4/I7rBS3cFjEBOmAcW1fXQwghGTIY5VReEJe6j2jUptmSSJ6vmoiX/YeIifausIiYc1eculP9UQDwie7l4UxrjK50+UbS6GqY6frYaahTeBqc6xB/d/uKJDLYpAu4tfKoql4MFG5JAObxr7GJFfbIBlxOb/lPWf+WbaQdpAXoDXnEgZNyULXMKC2Otb72gseLLZjrTgWxHHt2yhx4BTDxoF6FnmFtuFifD4d7p6MmLOy/wD911BJcS6m9nOTdS9thHUayoXeSFgaZ2T8ICFtESTDUJXXk1W3Nq4FR3E5alDmWxAyt4gYm8YvFluX3ORYNRGwbB7l+/c+L3XeASb514wbepmekcYLMeHsOOveMRAEDwu2T7OVPGfJzLc0dKhz70/i0EaNtKxTTl4X8907Fy+tZXYncKxKKz5R97w4uywD4TjBm78B4mguhBnb4x9lOQ/GCCrLqvNQf3zAfXfAHcZz6Qz4VotBRfzExEBXp0Us+XgawdN36weK7dosX171mIxOypieP5V9zHkx0ZrLV66AzcIt+6x7tMVv6f1rOoc3d/MN57lAk695QvlQY1hQPqLW67zQiNdEvZHMZAU42XQnzchOGRzBAo20Q3/qFiZf7SvAxaoM4adgBZqpYyOMVCfVocvMomYrQ5iiSTXdYsZ3Qi2qA5elwDKUhnVl52+i1pM/DzLgfHAFD9udoXQhwwKDvGwLsyZLIxCPjtKDLjCOAX+eNIMuTZ2/LjZxHI5vSSNWjqoPHtxOzyQGPCZ8DgvgsszXKhbPWCtavcrFRxbR/DpWupdzlSODq4DhQSIXU+KULA+W5Mku1maAfP1lJ9nEdbI5CeTgH4c+SrS2BSINwz+6VuHWQtRv8AqHnJG/PXJpmIHBYJZy9pdebjJOSBBAGDNxGsg69t8ov6FkBzSE4vb9c9L0jSiOCzXIz/LRK20mlzRKnKkLlpAKrHvYe9/jjETUeBOAy4oiOS/rfyjPs+1UixDkApnAgY/y4xEN8bIP6UBJPvg951fC1lXT4y8e4pwq7IOv2nKWQaJy8ushCasyAwmZ4549yq3JOli+DUK6k/xe69fEEQpfz0DPGQ3rrWe3N5LQeLIgrh50cX/bQwcY0ZPW6pgtRiJzqDxUZ5pVRzg0u27V4uWXH/JjD9bjAZ/1lAXYmshx8EYpMXkyBU9uboRHaz16phUs/NHtE8E6BEifLx6e+XjrwenFt5o4Bn3lKtQRcshVPc0gcMPRiJTJF9+O/biFwsc1r0IKXctHoVFF188M+Zxo5XRwO4KlOIH9u22L5dgJMAchs9NmbEQNmR5vC7/7xybPkv3cfOPImAY6T761+Fln9hKtuC3ygrqXY/k9+i+vjIw8xzMkPIlVlZ4Fgtmifvyoq6CG5ngTUX0vvy5bbUKpWLYj04LsXbdjJZs2dpBXD5zLC5D6oJydB2JslmGJ1d7HnA5i+ZbYAV9iUPClLgVIqfRNkC6UBtqwgLEYYSf3qgGWp63NU3kifvE8aY+8e/+6/7H9JH8z8qBzBQXgT6+HMKgEyaaxXGVyz947NOxLp6bre/DkMygAteMjAs/a6Yp+aDHyNSXf9eC42pHsuCTH6/dmdDk9r3Auy6L3WXAZatfKHk16Q5EZcMB/PKpsEFjVoiKbUywIf3bxTzI1AaT166MbTUf0TnUiEL/oaUcJE0mBcC/KmOGsAOEGftYI+UQZWGQ+j5BnaQMAipAWhJ3FNm1IZ5s15OR6k4eWo8RdS0CQDti5NJQFrLTkfGULpzlJSjA4Ik5jfeBMf/MxPbagdi2XmrUR+96he0bNZQiuuwBOCONWoOfHwC6M6DqUMiwtycoggaqZyFwtQMxr+oc8LI2UYQYR2TJoPKD89utjGzyQJY9cL1nKkpCImTEz0HqMfFKjRe4Qh4tMofrbCFfr+UbRl7ooKpACExF4qTmUpAVAzgiOzJVwkKp299k0nW9eQxXHpvfa7Xg76q41d3C2T7v7toKKo/tmVQ8VQFaA1qwrG6Z3PZ58qbNxtD9sZuQwPBCaYfs2G9wvZaXLXujiemwJyiTvgTA+oOwhY2Hf6Paxr9ejKg8oJ4I5a677MFCz/dvWhHbHjzs+jOLS+p0Lx9Rg5Ruturr97WnkLC7fLKK6GnnDX6AxmS+t2irajf4UIZwbCcSJcRWBSOz++0He3nnELrFHka+flBEj/PRbXIWoMSS1johNA6TqRPW+a+y6ER8C1Vw1JcmHTPvfQ+ky4EwEPjWwxYUOqm4lK2HinvH/9ojIsGEJamz2j/XRykzwsGdbPxBgjOYkrd9q1zjN6hPbn1mnB5DjfExUbN+Gp0TkCbJtZnuzGU4dZfJ5bIXEYprq+llyt5EYbyOuL+hzPX3ghrlgkscHX1Acx0xbebcXEXFNGzaajeP2Di2H6eamci2by86i/4Fjef9qGjj6IBRV8AdTkXBWKnZAV7BPTEfsqirOmYwEWPiRfqkIXzNYJ7tx/GZZQDWBEYiey/c1rW3k/YTJXI54maWUGeZBOfRgzVOwunBbPeVEbR4Uc5DEJuH+scqjfcWOiFHw1/zzjQLe7xsetftC2sqt3DFrtVlF6CWhje30lu3Z+6fX+r6DSCoK4MfNJ6zhiyJn9EyuUmrN+6WOtNXmOk1Dh+xaj7URcjUByf7tsu/QweTlDUSed34c+xbMvsasYmuwsjPDJlLTqb9yrjZG2K6N8ujZwAckaJFZ/FKDXArgeo0pH2ct8LOsj9kCW9sllY2+6TltEE9jRavfhzCx/W3XRo087nn8EzAyrZohqhyO1Fw/80TA6jMQVC9iA3B3xlHdxPwsXpKVt0mENiJ7jfBVDF+Bhv1s81mi3R3EH82ZMM9bEEcFJtF0JHi8Cqo2q+byxvZF//twhUq8xfTNyQTI1zuOSd9CdoHDUB1pjy4DDEif/dEP/XBdFRUQh7y+5aXnnj0D8RJs5uwF7ZLam6nc5iD0B5vBDsk1f/d7zv0yI26W3sArI8ewm5f4nE820SdiuM/oFW2I4cckj/SUS1R2TsIKcHtzbEfWoSf/g0Wl+vLTLyJKTdUbASiUjGjjJWIVAQ1i9c689oBi23oTPhWXhM6Kg/4QM2nZAGJ7WqY4TNFII/taKCrdk3UaWQ8+RuwE9DSBIhRzI+b+kPMriuRBKsKBaH/d+/IoBp/254PGJVlyd+R3anifV4z1z8g+8GoQo5p6UBHLmHH0hwQ4dpLZbRuzLmaXgDJJlhuBkJd6ik5tXAhV6TO+uqIqKlBb4S2wDAzP3fZfI/kXFjp1N5QiA0ABwaUX4dqHmzESswjZDloJ2XHHdPfsi+U+cPceRCQldsHaMQUiIlKUX7bI7qPV6kgoP8//p/I8k2Ggp+JJsQoHGhRxWDnAvNGbUSGL04o36V6ffQrW3UatWNwhZ1e6b/gefwWxDQhKdL976BwZH+/DBmInBYKmZTSH1THKHhatHRBLBcgCddL8Q0ct5E9jurNqVSCQHQpE5PYusP454zxT/5eUo38QI3PWPFva4NG/TNV3i+dR663SU+SYeWL7d2vXmJx4tpiF9vNKKQGy+HJNKgDv+N0I4CsC0k6DMm76cZmRDe/uyE8FRQju+FvCFvohqIh+11++OFjH151Qn5RZYzToesi/wOuIeUtus59C2eZVaSwEN+1jyCO/onjaaYcUuVpIn0XXj3y3dnvOfG5hp/nIx4gfd4Xs78RUXo5vTz8AsYG0NS6Elli/4XxfskXY6ZWk6v0bK4GrJPihAtjh/6zBdUCF5De4AoB2g9J4tmmIZdfDwsMCkvjq+MKdkOilOixBXvWLkFInRI5XhruZp33ksVD7XhK+XOOpfESAVo8b8AS6AHVf3dxlHrSWaYL7/0NDKcdvJXBA01HhfXk/UW84QIFEf/hpococHZFOIQrYw7w4mhmVzpD+dF2DBCG8oiw2mlMcBEV/IvqhUQ9HQE+0XfiF8DR1FN32j24LRl/x6GnJHJK+Dr0BMblOosyccGKnyqnzzXq9R64x4LmHWjnmMMSWXCz6j3//YNdBaXTzbPawBJqJHvELXkzAk5nW4liJTIPsrjGiPnXeaPoIxM1dNU7v1h3j3SRjClq2bv0ohVW8UQABwgPxg5B0N4BReWGWFbseJv2CNQC3Ux9mwt/8Ydnufkt2CS+L+x7wU7xeUtf1EosqN4GC9+fnuBSjI9a3f7IXX4VhsxRmrJQln7x11zWTWdquIL2CXoyayxpeksZVcQU5vs4ZkXzHcK4Ch+MTwVdFFFphXb89HJQMF5D/ZSr7rOhRU9xzQMmYXv/ACT377R5k033X1rzOYAlInc96Zrq4GMFrKkxtBWhXv07Q8Y1vGm3i945vOrtnrTwPbYspaexC4sdFD1hgthIGmL7R07NgSgfwps7D+nZgzC57fPaAxlcM2HjXtM6w/S28v194XZxRpqZOnrEc7AFWfAjUU2AW4xSj4TzLvgYk31kl5mxGXntCI7AaOvuEVdL3tLypVBNpTF3+yE/0l9A6+Q5QXO6ei9YFP3SobmvGcHw0tYIy6GRWzmksf7TqcRAbw0d208SJPfXHHhOiKWw8zRa2A1I6ApPXn/Z+Wp8Kpz3HoUDg9KRvkc3pqx1gWookWbaNIlmZq0S9rOCS/NwhwYjPhnv9Jp6DqvOcafEF0MqVoe4vYYpvCL1+ibLVBFNcrr73TgKRSWg2t2eX/FpdkzbC9e6XboeAiPqyRwqhIuxWg+nDUDAriLYBRNemxLY7thlr9V7iq48/MGWRLxdYYkQ3/5vdAqSmzt+73lbTis/mQa1B6wz2pOsb6ouXmXj1KcGsTdz4ae8Abx6mpG1nWSnYX98F69a1NolHDth7H+5tKnszzzI+ovJhrC6URO/L/kv4sbtei0HfT7iKMpwPueASlt4wo26aRh8m8Hc1IZ/raJEeIY8y9n9Q2uqvmg79WtoJKoTAxcpdEE1qv1QcuNMT0EkY2m1Kfm0AzR8cNHKq6DSypyMJ3UGVba0iyGIm31ohxu9Oz/btnDnbNf8Ozgv22OZ+G7QwoP6YKtNHE6owlOknKQbMS/7WOMYwmHrx7imuF3KpIodAK7yPz6jnPwkIwV6KBnEGjkGFvy0x7ND0Y37MezDnWHeNCS/Pb8oPLDZICJKmxnz+zKKGlgYbDSCqVYNboDAThFaqTuKa9VWhtTze8tkhLnOEae6j2y4Oesfi83RmKsF7KSijxSuCbH3IR+NgkvmrRbJmOj6fVRDq+RqxgL9nP0ZcaWU95H797K7hQn8cUwPc4sKSO4nwFUd0nK0K3gadzX4swdi1ZZ8cAgPJRIEf2aUwVHb5+7CwcRzwE2F9WH+MzqmTd97WvcXsu2uBrBO+rkSvQiN+GelalyA886IxFU9Uf3Drn55iyumQiB8F2RJmuRQ6UuwuVwSZDZlddVnD132wYGuecKNmyuOKkfyPVX/73RfNrNodF1IYn6TDWutEnJOHGEdMvC4UubmghlK96TuKqffJAx0bnzj3eCDaMjemt1PLoxB1WRKaHM/rIOXG0NsMR8oBHfaOyQ2ApJmlVDtSzOL1H5TpdvFJV7OMxSMAs/zaiFUaQNYo53a6RD1Zj2SE2Epp6dxe5t6NK11WXmS13EFSy4FrmCYocv2sytBSJwSupD7tar+J6DeCwWmH14+eKp8Fv5JirIsUeDuLb0IMVPC+ti+kLUCVOxbkbc8A9/iJR7VYs97uzFZE/s/b5i0SbMkpSxwDNrQbeaHhwvUKMtxxQOgmdeLia5MBhzjiTuAe4A64iM/Qlb4b8cE0rli/jd328appg1UW/Bwq4Wm+DbNwen8fPRCpRgROop3v2gr2W1B9J0qlrBHOUw3gR0cAsfGzh/cPgWusVADmSG7aRjJqM+T2dqj6SSBQaDVtydeE2RnCc3eaQjwE5agxhu2iqlmBpkfHBEEpUqiNWp+dZ9sus9srIAurzDkx9spsdmj5PPRmkPReg4e+8BQhJja3I9HTpQYbMkPeZMR1Sw055GZYm6UaAZ+rrtAgWQ6lkPLyMrWJT3kxuGtYWmZnyxILRtm1hL2J6fZZthAMPg1Q9rAQId+bVf/DUIJWgALdkME034lXoffEa8OqUiGDP83QKkiGqafDkuZH3ECv8H0PeN/hGAvybMaX7QYYKBUAL0IC31ViMIUnOME5/y9dgwI5O/rf1SYsEgHlK2S2ZvLPrfd5gd+g7jPO14jo7A95eWjzw10V1j/L79LRqgelo8GYY/WoHIIbndD8o6LmfT9CuCU3OiP+j7E5hHs8QFjt7MwQ7VpyK1OMvWBN2ONI6zHst1ALEK3WlScjg1WwWsdVpjiuq7IoZR4MCZ4YbHLCipDfr73wu/duH3IKWrxhs32x16QOPGLhK5c/dJYg7KzHsWIQb7oYofuAOb21NY0VN59XjPpRZgiP2Ug9qiZZWwvkazUzni5GsY5u78qyoddEt1FBj6gsojgSnRxajcFv7mJyZsrwzYIfCu0cEymSR+Qa6YIzPm8FT+QRrkfUoc79RYrhkjb9HlgmCAsLetc4v7PX8WfcXIxeZ1+avVpbG38hr4TpMt3pvfP39VInSRh4eL1JYe4+g4xOBLJ5yYI92hmThJH97yghr/xBRQh4dDQppSN3xzlvWKEbnqv/XYDBmt6BJmSM6iY8xMIidV0NwCbx2iU9brdYlwtd3X5LaS+ruLeUHkez6UFqL2FNw1BLf+4NSRfEhUPOYKVocgqGiT5Q+a8bxrZ57IsenFXAutu54SSV3PPLxGXmp1Hy+u8WPf27Ga6xWRzWGb4Ia2PQHGUtd/BOSiUI+5LWwjZYyHc/mCYpyAhnFj4BoUuOXyjVcxaPwjanG4tS3NJNIe/Q4tpaojAfaKDTKJZpo9D/wbKUHLBq6kdUGYyhvSf/lmsmH9c5r4igoAIJhhIcd73zxUL7Fmim7gWFomBj39S5pKZb1u9rkK7pAuS0k8RAMWKBrAfMbvtW3orw5PCuscv6Hd6MIUkqyUEwniiKnUIbHdcsPMyAGvjjV7AUEpkIpjha/NhwxFa68k/bDjKCSM/SHZQvXXd/yqP7O8Rv+TaIItFA0uKQoDv5QmXuiDb9CLyCAkrT5sJfzhjcKViYGYRweVdDUbU1KD97CNzLij3hszvxeRY+xtlOAlkibnbeYtfiuh1iM+fQlqPfyd6pLNVrQQP69FPkkA2d8co+dwE5S0EZSzcmOihYgzqjvvhXirlo998vm0AmoAf4MoQHrfhaUFPsmTMHZWH4w/0QtGdmLLM/eEp8Z5g3GtTLUai2kD9r1CYjBwttgvhIhz/PG15azB0taW44VMLSgaTBSAlHK4g+2fVxonQYJGS3u/tRMlm5KdTQoaSLPBJt7KGHze7eqJAeWuoWaaVyoba0gd9w+P5esabJamlINVNls6nYB5iGQDnZVZaZZPTP/csOI/G9xQMgQkyZt2KZpsOM0iHySGR8xbXGpRLuZgclYpUGSoT2bl/sf1QMPea+uGEcPOGblQwpFuRxbs8dEu6YgQyD3tCWLpkqH5cIn+4/mgzG8vw+B1QMrmmr5vLBeecuFF0IZHWP6boTg8IYR/fzkQfyyu3G1slOrlL1vx59/DrxC4Go7/imDdpYYBvKJNMZ0i+UfJS9+cbYUmKBhZEDYpv6ufZ/OX8rNUW3CNpWNvCA0rbZDYJEiSwh1ImjRnmOQlN3dSuB2wT66asfbU8mPH5r5kGmRqa+kkXb7Qwq8Z6wY731p/3vcBjiSH6mVGZaFwJYEYfGLHCAU7iACTLnT67BgWofaqtHfP/ONYNpOVzssxy2ge5+FkzHqXqUgfnDT3FT5Izcy8sM1ALyC2l4iAY6+TZmYkVDwPjfQQ01njm9JujOwzDqp0ZyfpJ7VdVf92+gYHLY+wv7UuyoVa29j5U/X0lec/frO1uM5+bOjFhIcAAwgQVHNQjZialuPrU/aLcwxsRXiqn64IoHRHIuEP/CgRB7DMyPsKisI/YXCKC2bmyaqv+gBzjVVsXgOP4rFa0GdlKdlJfn0wkrK6HZJsX60XiK1zyxKSTFqLZ0quDeT778iD8UerKA6OCvfaIdORm2HeuDY7U0aRWCQ+6w9OCvSBCtJq6RNTNfqTWwZH4X2zffBpsDOANBvp1AIG6pBPvO18Lg4l/REryo0kXNZ82vj5IONskcZW2Mf7CoJpThRny4mGwRTPyamVK/iHg5jCuz/BMxLILzXCl9Zgbj30OXbBDndWdWkYS1td4h+jeV/h7ELYwO4SnCYV08ayBabHni1dsMnyj14IcwQwMH2Q0ypqpm79P4H015HKtddJE2hqiG0mdIWyqApnZbae+x+tafPQ1pdzdAgWH4EbAt5w5pBvTjHqFlMFqwhZgeE4u96pYzg5Q3fdu+Vx5dYhwPtSAzH5TdGK27g2sYOyZb6rROV/Vx9+REFDLd0TIaSxH61S12keKK1vbW1GawXbPfQQ2Q2WhHN4fIQLEFwJKf017KOIeWpN4otuihglL1QaEouXUTxqJl0/ijQIE/L28TDLKpqBoB4/BncmtMEKRTuJnOs1Q551LNXvGpCyqcNhKMsdgVJcDUwD/BZ2B8A2xWADFm2mDhMtoC6HMkJ5h5pW/ffAHG9kqBq0carinnzokkFKCqzFC0XJALdEmueweO9NBJebrd6hWoC4RPZNRQIIe2g+6EPjMndl2wWHCVSqEkmiSCNKbBW+d7kjt7enH3YsyTYieFyhaev2+16JnL9nuy8ot4oPzj21o2ZDhoRBEr91kGSXqoKC4WXWhvDBQ9eL0SC9RWdi7aSdzJ69qczbZYChzXd6KvBOj0L7ZWPaNa1auWrGjHevYVlSz7m62Eua+6+ouopgysfFABiKuOAX+Kf7uaNsH+xYLkhM32UTGtylMuwD5+ANsEkA/l5CoRgogJRQclhTOXp9Qea6sVhDxPUQzTD4iCEqUjuEAorBz/7cCJail4zUToDTT0qIzdr3Tcz0hqiGBTnceoVxsQtRlubVGO2/6Dmi3Dbp1bNCY5o+kQkHGHE6PbntcM70uUHCjKwZEA74xbDXNPejUSggy21rJ7xffDz/k2FjUqsKdRBXPd7vYinKxDcKxGnDiKcnPLTGrAzWuf+v4hXtwnzKx2/so8ebQg+NGAT36R3bfnuvst5rWxbm0PLcB4LK6gO6o5n2PEe5hVLkTMx3K7FAPE/PDfL5dONhLsWhZSgOCAkD/huqzABsQswdtxgsDmhs0XVI9GUKKPfgbXHzpSS8VN7f2+d0zwDnmg3Rj07yanroVXEhVJ9+RZopbCUz+kPt9tL7svsTotZpGULnUSgt3mw9lHIHaw5MDLkxrfFm4KwvS/iN32mz6TPXldYkUxE8NdSx+17JdQkzLRk+ivWB08A5r+x0TXL02xAO8bhNWOVhq89zz11HwSmlWxFK4VQPcW7zQSU7YlJaOziy0umZ9oVBX6gm41uzg3gdSsS1jIAUGP8QCZCUGgkiyCkXDxsH8Ace4KTgpCA2iC6kvswzLRMQ7tjQ/TiuDwkkvL19alvJRBTdYyQjrXMK7YWDwPMVyazqeeV5JuC8C9RdUkf5qq34QgJCr2FvNWdCGB+z3ULbQNUV/qRJM6FfVkRkyTTBjseJQFJke3s1ezd8NTPUmJj5uzuh2diM5qEirAC3FhIaMlLpzoQOllkt7KmhnQH1IpCLaWyqantnWV8g3y8kP9amTWUwUG80sEf1Al0w+hoCXTN6tR2DhF6l1hjZoWDtByAB1mMQz0G/FLrCgFWDfIiutQuGAda8ePpa7WKTCiMRa9aG4ra4T+WXPo8DDkOmiBmQH6BqMwbQXV3ulyPwXWQWI4L4kP4RW//4/PSQIVChnJFz3i3+8FYvvLXLVRERUfl5L+0wuXKmefM1rFHPNk0kMnTBSwWd7FRouACCzKtTEgdqp0eHI/bgiohibea0jB91Rx0jzZMkBDlx3f5L448x7M0vC+dUwKJTG6cQrOzRHuRIIED+O0IYPjFeTNwfLAZIbMADPvN9TQNDKYSn2sGh7qHrJH2gkb0UI+MoNv2TmRmvyle5043Djt4EqRP6onqPNvsDrBfbfTLTidk3Y55/wjTZdSRZDVm7puRiqyvgGC3v/Kj6lhOOr+bznHnMrwL21WomJYXUW7BSRQ5DWOJOH9m3QPeS+bm4geHQGUxPQayejW1krfQZ+gWQc9CiJ961PeqL3sj4TEZKMY6Xt/wqaCYdX3cUcw8By06w1fxYSEW2WjOetd8shfya0fiG7oNfxEEXDnh5l0UeEFtG+AKZ7zbBo4NMNi7EWVCHUZrTpAAGkLi3XGRFJKAvR3iZEnxr+kADhp3xipzVn9A8zsYouuheKGp9l3BxT4XASj+iBcQtFlaeeMxif//F6CzS7C3FcgCcH1EpuBG8T/lY4nUCstqPgSc7Y+h/uCts7yStasbSe9HomAevNdzh9/QIjzD7mSZNPsT5D9NvjikUfib8qW1X7Kkl0iJ0qHeJiYwTqJYk7/EET3MLbSa9W4Y4trF91usGc0S5nH7e6TQch12eDyFglNNNfyNPzl4lCxIVx55IXFaJUbMg7dME10AaYFUEmTtXg1HOpC1D7X+nBZhaHNP7Qk/NKObOmAbCre34a2c135hFMLsWMYmUJpe+2QyNeZTLkFdKk6qgzZ8aJIsbZxGvxqs09RbsyNm2IVx6j04nnSYROoApfl0/WDRJIgmv8EV48J4R5QG/poU6buW5HSfzemMZGrvBuBXO0kmUeBwMFFSmjMZ/C00GRbifpAksKQXqzA+ya/3pZnPVVmYaPVYGEnlGN0r1NzNPxFicjPdh3YgMRJSpk9BBKZC8/LxiSrXeR4EP3EoW67TkRgxBUyVNUnVPU4Vk2qwMuxrZZGbHGyV9fW4B6IlFFXhrLEguYwAeNcgCkJfRBQQL7tHbjjiB0WePY9g764dVEXxwsmcz1HJ9Gw1AffvmR0dcVkfmeYc7wdof/7o0CWWdyaGj3n267zGbZpH9qtpjtXNNnhxe0S+zGrlKFFDxO2tSAWoEgPRIwnZZW35A1MtAxlkOJLDo2YQcnEhv8m+EOWeO+UKXTCCCNTsk+p2kFL5s/SomdHdiIv51JRDviKO9sn3FauSn+Y2CZUhHEjxgMMgSPDEax6p1WTeHA2HRsk/H1o3Zu4uhaRNCI3Gc3B0TL7WtzlwPQ7jlMH1rvNMMIJACWpApMjnslRqTsHQpPNQJMukc2yJRLKoNCv7jXE3gj2Cfk+0AvbZiMG0COr28MjYQoScfDKxekCvTNuQBwEGSVrkPhcHr175WQeTNdTYFAkRz1R7LzXrZKbyLS4u9oW6iAcqujvacPNM+IYitfk5LrY1id259+8gL+rH5voBKU0GDd+Cl0rtEAorKDuCmj43hIGJe+Ekau+VjRLL1eqE8IF3E8Xf7js2JOxcmdvO0o3DJOXC8eB4uSORbNUYdgs0NsDt+2tySBACIaQnZ50Quwy7PJX6jCMQDvHCCjM0prUx4f/wjNmCB4GQKs9bZ5BdAMpNnBHYv49JK+zxw/7AbB2nWVF3bM8a6xCIDyAIz8YAoEsnK78rApzWiIg5Pr2CSD1Ju9GYRDkKkGEuXOsJbArV7SQGFv/EkrPvWR4xKvNOPE+0l5quk2P8zFVIKH5HATJy4pt2QOBMBIy0Dljd4+8cj7vOpxoIxCo4/Sp3OrnvEII6FCXu0onn7EWPuvYLj3f2nh9hmedI9gqbbVx91M8PMxVXdD34B8WG8x3v20c/C6CTc883YS6YqqS3KDM1Mu3Xr0LRCQt9kJRwygd4bIEIydkJVFwTi2vFeiK2PPy1yJ73z/n4b7Inn3taD5H35C4c5FfPsk5X3zxCjQ1xZAjYratzt8KA6nrr/0oO/rshXMxlbGcRojkv/wBwn72sGZq5tEgCGDf/euYrrMkDSGVkgBp2RJNJ56mgmG0rsDVwG2L005HV7HqYAySSZXAfSg5njvml8X+QZWdconiRXLA+REr1AI78RS+JKIujwhW8ccqLgd367buMBX9Iu4lyAyVECfzcm8rnqy5xl7sG+aiTDjGWO53+evvv0sGhp+GGRIN7+Do2llL/RxfPWvBBJEwnWScWlHc7PVklNaqm275JwdaSXUqMz3IJ/j65GwQGeodzCM2PH22JO5zvbBW1HILI91cW55+GjIPcmuN6OA7SqaQXxEWPODufxAn6AFZ9JW+F7+97RYHTYSC4OEzPJsR64Brhs61iJlymfhz/9U2pNaAGyne7zluCxjQQxIIqIljQG2+6A+P5+WXzBCazM8xWSPoofGWlP5R+hoNOeHL0RZ9vGKoz1V5Rg4KiJIehUb8IbWw0eA9qBatb/bTP/cgmAaobOu7QS1zh6tCa5ctx1qT5wGNYeKzEGB6vEfQryWwJdk/sQFprSqEKTA0WkWjyupmsyYpFJvW2JVZCwSzm+MIwsDppBg334TwavVTlQSRG2v0ZyYFbhFquBclEin5hgusJA55mFKVHuwJCen00NKD1FNBu2Vnym0LuDcGcXU8NWz/rIAuB2oKm9yC1OuxXjrj+/u/va8B42DI9GJpON5KXJXHyDnGEx0nNP2Qq7fEKsyOSDEFrTnH78nrAGyyhtiTfA85h9URqSJdxnWWtMFduzKABHxnr4X+eLhSLlq3NtArzIFaIeWUiUbavMUXWqCS74Ta20uCK6Rr6XwX0dQuUmTj8vcMB4JNfo/doz5atehRPF2lW6aipF96ipy/kRu6BJDPKUhFRJeyylrtJ/6ux5ibCe4kP8szgRnamh9CaMFMU0TeocnecIXz1capVkpz7HQlm1xLDu3WM8E750zqwYLRN+Ty6ztFRL4gj3THMXQvzXFZiT3PxMi52ydG4KV/JghwB5cfy5rQOeKQrC3mgPp0eUaRCw0XPZqZmkHFYcWerXbd6U8gXGLrj2M6q/W06KuNZpFePiCdjVdrOn6+QpEnJYc/uAa0LdaMfvbmRs/QHY1WaUW6agUQZHOitAIEJYoUo2MkqfAAL7IOuctAvjCk52EG6yDEQze4Eu8i3PdCdwtdkppR86H/TL2iCjZELixjjSYygbF39YizW11ox6EvtS8yKJU4SoIAEhANvSb73joAIQ2ceVmVCbXqebS3C8zkC0oaMi8Natteh/AWwzr98Pou4vnJNug92phsCF9h+R5p7eCkrwKHWaEismMBP+9JfX9FSzHY63ZgE6H9j8NFZoGawCDyghSnAGNEKFuLNxBmKFd01VZJRMwfPjLChT9Unqwcu9/PQ4y+6JuCRKq58luLe/SFHDphumEMucuqrZiGEi6tV2VuhsO8veIM3796KaQ54e4FnvvSMlT6Rxvi9GPcz71inwaOA31G/p1M4r96/wy7K+o0uHnu1WWxAtTw1wEaVKJMN1uZu3zY46F29sDM4D5jmJ4DzdDU+0L7G3LyoaSDKteRvrFHpV2RCYJa8zuVxexFoUmTKk/YHZvvEIccnta8p4BnMk5kEDp0UnaidSNPBMyyauNwnLctRDO5wgfN11pqK3EZsJsNSQp97al6dxxMlO3NOONPe/sR7nEOqUIB8sxRL6hVBm9uplb0/epIRjeFxktRcD4eAC6dD1dxU1bhCliKTJc/HU1HZ1gi25gOl8WqKKyLpK+hpk/2KIV1syiCMpDK8bWMTyp8WUI/z89NCsH8UvBYXzEPzzLy80FIqILPJpWoOtlIQWuh3+SwcWRRO1xGFcYygXLWciPdEhMXOwH2fWwVQop6L3cIOGM78nlYnFdvGJGIivkOg8xjgT5rNaQeIVTXdVmqqRE0RO0dE8Q6r5j0g48ivyaJv7KCw/p7vd7y2EZambp1bC2xJzbNw680FGmDtnqTsJiAdrm2N27fatJQd8EJk7aOS4nYodDE66AgoZOWJ0JNaSkg2cNeuif71+QSErDswffcSnu/V9DQGx8j2bBrAg9hZzbLtkcy1ptfOvbnuOXNEZLjQFHBWNgZW5a500iCa0uPQfRmHb4NW6Y5IN23s6DPp9DumHjnJnHphIyqhBbr5scuRcOXSgCJxGLUh+UDhoj6s6iC3m3YtOHcIBRWBEj2ZUjE9OC+v7x9Xv1kN/tJCC+DgsJiGb7l0JNLy22jLMmzsIX5WGmiHQ/tAAoko9vL5eQO4Mk8Q8RjLUWxCnIISZ1JaHqGBje0zHvxWK+rkpsQvnMEW5bm6vtPLxb+nuK9dClLouzkdAIU2zYvGS/e1cPOwVoyuyuTXsPfnaNYVOkCxVPiG3hDcfIMT5/biGvsSDL5ImpaHAaInKxvvgHswYT3p0Ld6CaqGlYI9a08Sp0ZiyHxKRexjzYD78BZPYTGcZtVUV74OjMVdpQWigh6hsjs+Y8pGyewz0T9FiOeiqbgkkRLycgUqwqXVEnbPcj4kJNe2oNbkD1c70UHWaBRMqyHRBI0aV6JehgLDTMacmkYAe6B/DxHwhkgGngnsrE+axKPnbmNBL3Sywp37ogigGt/N7h5qR7LhDRZ35ALpTTpIBCltpKs3TquEQw1HbBd/5eR2rBXEeXUrXvy8/gDnNDtzNWu9bgCopuTij8HJ3fwec0MfTUNjNl+5wCXn6QXBx3NvTFB66Ntt6kE0ACJXLj6u39j6coh9Q29ZTVs0XF9rZv89UPxEifJUqMDamZJ+2VyFBLDKbAAmWyv00tONrYDKgLOhed/rbnZIzXrWZF8eTJJkdBN6s00ICUCsWmE3zNjTNxN6gpIHDXPs+Qu7I4s5cvS+p65qCMdl5fVsEPzrktWKshg8bIB7QD3mxlJO4aekDcq4hy/ANDNujx0XQ8+8UNm0TRpka+VPnzyYiy2l06GPJdRJQjxnNGe264UWPvIOaAzCxJ2hBqu2EB1Kkkfjrrde3Cr3YdVuWJoxCf0HedWftBJHNO2z17KcoLuslkv+xihmDbem5/yOG61GYQxZHGtuA8ZcXnlfPSmx0fAg5kzAHds9PLAxxqvLKqqPjzbUEqwEyAI+m4guHugWkrjBy9/fc4pJmJSlTlZIHVftUIdFQDgmFiGGMSgn6+Jq8RPST6sjS+1cyWe7kR431/FDziTXk7rurcyKZpmk0k3eDi25nWf7OuFe5N5ucn9Xmgxm4CdFeldKauqinUZB8J/JqklVDM1tBdyyRpN6j0WcvUIjTZ0BYJ8Y+oluHfCCILulofCMi40WWc1+TF6BuGzZP7cIBqUn4l1/Cz6gtmNpGajKMIWBeqnP7r4vXuSxAMBggBPcM/L5MFIeYNAJdbKog+DF6nKFDrmwKK7Kmm8+J+XrXp5cCrEiMGiZ3RRhuhppS2c4+jFM7VaSCWJ4b4AQye7AGvSJEgV0NB4OIDa29yE+YfdCLfm4RBzqWoOeSGAK5KitE0aT/pkZKB2O177KGSSn3jFrj/e3s8vT0tK4AQzmrWgfHWlyeFZXpa1w23YtzgitJpbtfbZmdYVh4sCBOFDCIqHRTKQYJMOWAuakGX47COl26uKnFW8Y4PvhvnV6v3J4ZAgJVuXPe9RPXy9Amrcuj4H0Dk+mIGdTPsm8JhS3AaVl5jZNIjGIZg9VwcteIUsCCLzoT5u9ibxMZif2u+7jt9nUDk3FezT/+/4tsvJmmABxC4A+gJfNmBUyY1Utqb8S3ug1DVSf8cO6RhhR5f8ovMk4262Lqf2aABwQotEnP7dxnUHSGH8yfioVRLYjiA0aSaggWTXH71SCyyd6vEJT80xXj5qmLRYOPHnCsNkSbd/ttImOtL6xeCOu09BUsK3vNmUN+YBYNmWFgg5ENtOb3Vi5oeYj5EmxoKNBZm+SKJdC8oGCLTm+MEkWs6NwjXl4a7hn8NCLqN9khSJ7hKCf92+vOuIOIwVLwMiEdRgsVL5qoSikD6tkcVRkXU6neBfNRjn80zs6vcMcmjwJh8+iiSyGpJHBM7dBDfTS9TdwSMmw85/xgCKbhepagEw7NM/S8VpRR9kBGajfBdcRwxHQFdYImBLj59otRlb8gpvVRWLsjh4FCZI3igsGWYO00qyyNOCXu+Vl1z6lF8sn60seT1gq913LGsxXF3VDixpjmpQzi8ZwyNaQIGgWsxMXLLPSiVAis0D0vtGANegfVCIGYZEgQJ3YAEAG8X1j9AQuUVjd2qQDYhpWGkwJQkVHQjf06WZhYPgRx71brddSxTFbRKWf00n7jcAr85pAGhgejyGEXvr/XeGgDIfQ+WQkUIwAZFkZDBsZruTd38eNEb4x89rRn7CjYMysFdRR0de0RKXi8YObUovOcpSS9Jm9P3KcsN4gQAFyhDpyYKkt+TMTNS3zh/Gx9KGuJjwyrbJc+buclyonP9LVG2LfskGnP3GhKG2SupVmj6pV2J/oQUVmRE0Yhqa+iojzvZMG64D3Fo3aHQh38T1zt4J1ptef/DYn9WGaxG7ier7Lt6+SvAQOLrdoD4gxAc1gmIXt+ixiHihw5F4edd4nO63d8QlKHByTOFENbErRl7IlReiej79tjC3oQQKYm8n3AX1nw8pZev3uzGFRJJU4biFFj3m45Cut2JbpzymdqoJcHaaYAfIH2KWAifBvPGFp7VvF1kiIq+lq4z98d5xox0ZMMtsFjDfQZqE873FDVPAEA2E0sisDp5jtMNnwNMkbxqQryG6JsygbW7wUo9YuoAsdXPTmgTuJBbnlWZICBCnMSiop0alR9jjBZmfUzZj9FLdHsPxyRM5ci3r4Va1suL26EpT0NRUzViI6SmYC9kBuj5HXsYo3OVOYJS9rAEIRK/VPEAZ8A2Ko+0kYzH1bJyhO636FPZVGFGE7kRtdGol5oUWwq3UdGr2cMO602rLRl5q0tWGCBni8CjA06oIur3neUguqLF/8/lPu+9geXo3fshpEr1xB3tA5QoQkPKkq/fSQdQQtYe1pXZrdDK/VBXgac1LMEDB62TVXCnVe2YQnd4jSHpbuUxDI9iUodSGfyiwEO2XUMV+RvFnKqXUrzEDhXneJCvZCSKsHRP22e4IvzOeFjHYCmB+Uch1eNhwG/0fI1hW6NP9NtDddpf3v59WiFrKSvSsVZjF6hkxXwCmphm5kyeMi635XZyZDVum5R2iAC3MU0fM67UHYdhTwVqYjCa2etjSJK7qdi3caWwqOfEdrC1UvPYEune7AJe/ZbZpwmKRY+4Gwdj3WFJSgJEu7gq+6V3eOR7uVc/U4tsXGa5hGbED6BoXasBCzsNcD8BFDYFZuCNeKhdiyuVlYgCwBYbBkw6xTs47jGnLmURoWJ0/xq7k8mGEHNfbpmOWf+njCc1fVCvLdKxEfB9ycz+3rM8qHXHro9OV8ile2JkxCqL/2o3Qv+VZAEIsajttJozRdawaGxFhEEygyJxZHOi/pFUcKaVL9piuTUp9bO3Zz7G5R7qjwKCUlFK14/8RFi7slLGPkucPeEsdKtVTNEpksGwtYta1ZoqpYGTsnBtUYrajzDO7DZADUUylpAesn48iESMkFp+jXAmgqtcTmc8UZYD5GOAFMe0BAocJNldJ+ZiICo16jtGuALdwS0Xv17ChMgtMqlBKFeF1itJCi5dUSCceEBohAp+Hjfgv0TSa3zUAMRpqYVlDYNw44NUA4upedNuNViKvt6EeR1lBQehuoEDBMKGoE0fonIFDwSqAmnCwmSZ00qB9mZ5C+7yfHTcV3IPZjarKg+bWzmYjkspiRdTWmgmtFLTC2NEb3WcwSXK1i4YDvZW2nHABV8R4BDT/bMgnHScYX9a9b6H9dxvVh/7lQmnzIjRfP+KEtVziflaObnOUcHZDc5scEGONS3d4MlLJqDsKM8ROeqUVRTgYV2Ym4Dh2jsS7GGjaYUaVX5bjWS86J8UZRkDB/VnegIX0RfCFs7Bo8+YNhdjsQ1O6EOz7KdIL3FuZuGgq0LIjIeWd4uNIlQGSg0eCw2N0771dcpZQRoh7pTWrunT+Go+wq6xGb/Kqu6R5+5GJHkRoxBl/dJfBU0bNSDsZG8iKikbwQRdJ0TOsm923eJWzBvhlhAW53x+YOF263w6Z/2QsZuHTTdBJa6mUSAthtFjxachzPVzMr4/YAWiKUkOR4IrRD47GstWKzSkV2KXhCvTGkNTPYPkn6YVoPscauJ9uj7GfDQcS2e2tMY3ESdu1y25JUgoLzTpu9KDl6Tu70D0GQDmXdUUP0Fxus85KDPtuOcctB9HViWtCZKq8IMb5LL3rcelhKK50gv6ON6Hj8HBRCNL/Ij9nsjbXWrzbOe3JncVtuxAmedLyFofuRBtGT1dtKv2K9jxqkbSuwHKzDWWCAm0NgaRGf6+N7+eZoPgJmshJGNFr4McuWQ5azoIxpqbqlVcR2975Mblx4YVoKP0mskujFksLKTmjJaWMktAyXSVkHgl9GHncVv8fnxKx0vGEbHUwvOd3UZWYz5HR4TSGRSkil52cSJMycCk4CZt2rt2NMiEteuZCfUY/+tcApwK2YbD93K4ZPQCKu8YgfydGPNXjDJewdhvQq6PLuBPvzTP+oyb/roX/FrdNMDoov8Kh9QBJEkqbqV83rntpepn3PmRQOOWuXe6e4nkR+uHkx1oOSmHZp3xYmarV4dswB0mwAQjYrHu6bV43mJwPxLd5e+D6DpLukkWtrKK6Y5Yl/k5IU11SAxMZklVbdXfowaLIj6A//6+/dOgMM8HZ9EYiE7Ey8SwMZIzGQhBvEKYk6aNqYvTkaWaXNUk9xllD3MT647LBFzb3tdbnUnFLEyciBnOaMMJjP1yXs3DA8/lOzK6TdjxEDerdHVckrxUUsbTEDmYCXbhqQF3bMlweTIVp7cp6qFJKs5FBfenonBzEm6oPeI4hMPYevz8JGMYlQpCfTeGVcnLFcPSnHNU9MA5n9/FZacFDQqXFOBD03qXOKUH5HhaoF2tx4sxdfbuDXz2+i2jCBFdoNz+KDLltr6UHMVc/88Nq6a80jnUh/GOgkiBK5d5ekAvv1WeQjK9Lt4CzzQWGSU/pyVdjXWivhXQiXWqBirhs1/+VYHn09iZhhPo3n2dkXkqwkKBaTK/8bfXYiHif4RGDHJ+r0doAZWgXovamwTK8Sz5INIxNA9FTR4e+AhhtIkf7F6pXSOhQMgu2Fz0dsEvHdnhteXiniPw6IuNm0nF4Rp2JtQEevlmOL8picipyocDmS9EoTUE4X98BphFJcnWBbxJVTMDIpxkt5w85qhd65DGzino/c3m6jLmTO+hw8vPPJ7nqhEfeeVtmIGe+L3xamtvUSe0oW+P9JSmDVNwI3Quo8c5y/wLJQtx5Dm06TZ9ApsXzf3Y4dtj8bISH7HZDnQlUOW/7X7+//AzntY1z/kJA9CcC7ySKP+gNBT+RE07UnlTIfz+yyY+b0ZWH9//RrGfgJSQa1OUZdn6drHmqx+1403fhpKdLrH+/4uAaay7Go+WgC3YjgNOj2aIzBVBx4aKIQj4MG12XOut+H54uhklSSaFQvYfAMc1NdwaJ9bflHZGr+6tre2gi2El5Q3PdA4T0hoSTkKi1rg32+K9E51AjA48ZAYbrwr6AOlxAKfz96CUNIsPOP4a2NFz3odP2t7duOzAxlhEBpSbl0ff1etVDzfeHNvpR0yAFvwnIauVnJ8eD4t7NZH2RTknYtLfX7QVP4psmyvW9qjza0MXIwjnwG4w9toyx+0Dip7cXdl0OVwrEoYYb4A6rbsjXquvfdHj3wjL9OPTPUvFg6xzBVnSz9RhNgc3s8q1k4mJapE2Bvtf6+2LQOdtrmIt4UoZX8q27K6+38vX/tsI8XIFZiowUyCH+ZkfjACRS7NjhYe7TSBVYhpeqW9GtUEAHxGUVqu9A96lIZv/6itqPY90ifzeHl2h1yBzgH9rmWtzsIrSuMWktJ+AqOWRU7CdUgmaEVoU2R6rHB7QErrV1aywKpE07iMYs6Uet2WlJCjnf/RPF9hR537Xd1YGsul5J7wgLSljLz6bzrtc+xsi790r4+ZSQfWQ3laIIYgiXaeZ8Uf1BvATIQjakgLwe2la7HJYngr2izO3OKl0B+pQYr8OY8NBrKMsNZZAGnF+0ZyhjTgSA5qJNrqDrJlSLJaIKPCovAdTNnoKZHXYejeObTeSGMjBTIc7vJum25XcpGGwdCsDryjUOC3S5HMRMAGPsLVr83TEtWr9BfM8WkTDpDqV816aXCxYFNe8gE0uWUQ8hOmIwNV9gzMonbUZeMcMmfuFkCnJPF58REsIdMEBZvTOHcxJgCBG4p7KC3czQsblPiv8OhsXEi6hNsQBQbVP1n00VLFJvs+GvH4o8f24MkYnbODG4fykmgXabI3StkmWiaTh714mi1NsSzbFjaXMYAxQbwe8GKiGxY/YsY14gOqqw4IAxfNhkgrm0be/orH6YAeHsdKhHZSr9A6XEKkuWfwrV9YFABZbQQswthdZ+vmaLuhBma88GydRaoWw+yRjikBOyW699ku5GkG15I7GJChghuHMRXaCPecnLqwLpBgm6+2qeUm5nqjApmCq7RkfnmZ4vKB6apEwcxeOPIRVpJzmNlN6F1fsXnJUEGWXwIXfUZfxMJmmpDWLB7NNzZfnJpuzSbxdeWN7bs+j4RV8MipDw+O5HLyo9Yv7IbSERbe4blm1AMw0S+Dl6ZwL9opsQ62IcaJhDUqS6fTJ2me0HDCBhhGueA7+3qbyb5Oi4Skh78MxnGH9WP50Pm6bTeJfYrzJODIHcwIFz7+zl0tM/B2jKVfzJUV9ZcZYTeOPxJXtq9ROHM1MJ/zfhKGJXDV3hXeetiR2IHvgks2vI1WMHCu5mjeYoYN7cGpfhrQ9aiNQzWiAEOfuJK+uzkg5IDEJHMc1hBEe4w/IG5p2QuEEoKk1eSUTfQvjs+ovuJZpYHRSz7ge8yNQhTi8d2FQG7sQrMADw3SsSYOT4ncovu4h4XpCIYQ11aDbFtysX+QYGJAnInjP45grc29loh6S7PKDV644QJB9w9tdkN64Na+W2+U2ApkfEq3rHQdSL6MyM7t/DPd+o/sZvFEOoZVu1E3wn8CtE9R+i0pziXPANo/V8/r6n0pQ2ygpL87QwQkBKSlv466aONg1EAkV2T0xFUuR7+44VidU3g+lb7P73YkhaO3CKzB7WLl/CJsfd9W1RDb6D8ebpNcl9WAcwANrwnk5IGO+RN4HBXVI0CekSqO7DpO3mslIx5CgX/t8v6AqRjSAcdoPEViDclL0cO/OVgqjhEKDzNddZGySRNJFEIEBg7hFsYwzRZU/ytXbdFMpdE3ot7AnSsWKRdq1Zf3CCjvs7ENmQgtzXS+FP8dgdRYKesiZopmkMmfcoiLGf7WAfHiaSHJB7A2QBmF8nvwu6Er/7kklXkJWHGWUBdfAyQszny0l2eM05yENTbHhmZSr/80e0rzHjG5VXBDFXzyG3gNdSXncP85S8/qQanQU6I0GT37B/XXMGcTlmpqRyEIMYQe9JxBzEz+cAW2AB4pamcezRpkQ8OuY4Et1W/+1ND0N3RVpJbh0k/6HE3VI+OXSrjsyi5szK2Qcjj6Te2OxvqrWKmvGczXbynL7EyGYjAJ+xfuqXwyG+QWLXWY3/JMFMGhaBgatML3i9xrj9/PEi5M9xuPA70GiytTFY5n/ncl7q6RkTfk9HeQ2MADrWZ2BjL4ClUXfUYnrrRPmoM0OnLpMLjd7D1Lfy8+2v45oMB5op4G93SXBQb617LWTPbP2N/YaF/x7vLJmBf2EKXWY8aRPdgk7A+i9WZ1P2G+Gl4UtFAqrIm9wJgXSngbuD7mFWjWReBLBsVR2dAX2M0RYVKkJoQdbleMJAlubNhv8x8TKU6lM5dqMWJXiWIgri3o1txH8ob4SJMn/nJu4QRSbfCO9P0SCKZTD9KUHu0KfrAiEFMk7vOFxb0CzwRFbhV6iMmp6WHH3z3BG0jCL6zu4OePlGbHfdThFhM/a+kHTdUdv34QUTPLLULQ3FIxGdYJyWqXYucSiX1Dd+fdAQ7KuugGnH9qTX3ZecKl6VKzkYTzn7ENZ3v2ES9ARNEsRFbzYPy/1tVMO3l7RfZxk/CHk573kQNt2D+mgtOzS31/cEdHUAkQnT5ZkD4Km0valk7froj2cVAEiDnS8NEYkEsn1hcbM3czPGJQBf6FsudrDxQl+W/OzgICCERkV2hn7rkzbLnXyowERi6sOe5YaZKXTrJhYIiCEvrWPTEzWON6g6RSsRC/zyErACG8D/0+Jio6cecWNbZir+EJ+1ThnLQZQFYboYt30SWuWcHN9j46yWdK/RAztpoENwCUw+8X0mpTw/yYy72kLVXGz/2aFo+hZihUKd4MnDPlVaB/wRyoAKX/QKHTS8VogFFYKkcSUp5SMD6kPFBOA3Da9cd5rHCCMXCw0/p/JeCbtrzJ0AYxabQ8nE8mInp7A3yVAttTECq+zURK7NE9pKTIrvgQrOf92WAd8Aa0BiTLG8z+h4tsgP0hE2wAmThzEnC00tMuORe3P40QRllEDSKPcdCsX3eBPkdjiiRoeXGXBQFAyXbqKK/BzDq0tzAe7tqFOdw7YX0sf9izrijl8SjuUj9b7weoAZrBMpIp011szYtNcjZdWuVXOOnOtHDwJUtMdrNF2pRn0azC2Zetcwo9SsTQgz3i7Qi+4np+MI2VFJi+lPRbxiv5O+A8GnLEJNuxpx79eikZ55IcoFfZgkZcjnry13112a/OFZH5vaRI8dCrdOeZcZvf23wSQQKABbYZNq+L7wFv2Jw6PV5QxE7aE8kHVF5ZRgr2ydiZSlSFw36QnMBZDYEoXV2UacEUGcCvmfd9jmgHY4dsgWO//0gG7tuvDo+TGaHRBbUOVMDDDPoA2LHkbsk3T05ZB8rFjedkXTJ6+R0IGeLso+xKgK/EHH/L3u2HtmvvOw+7IOD+DLSXnTRvT9Wwa6yjDQvMfBVVBlBakH7VfeJ7oFgwEmp756oAfxw1toKbcPZvS9YFDNRmTR2ufehBHdMyswUXyyXJDxZbhPUg6y7frj0Cc3pY6R5nAQHWrL8LT0kfT8dw6wzgetz/7AETAdQbbG0UQOp6XUjtNIDlIV4TN3qp6vi/Pk6jamDUHKJq8F/tjuLdaQBDVWW+eubdzbFDkrFXG/zHsMUvwq4Z0bPKOdY5HUspUOczhY1gmNBcnZ1TaaRF2bpPW928VDc/iDona/9I5/ZxSWQahc5D3JBeBqr+Baf6XaJuCIvMklZ0EvtJKIUxFnW7dY+9ueiJghe1qsqaNbVo6CS0Xzs8PqwbePjGLNcG3spnpu2oZyHvmEv5//sFMK3BMh2WtxpAnp+nGCjdRE4M9aoLvuaWUr16lt5Nnw6YR824Ueu6NnJdKMV8y6NTmm1Dce1+TAzbSp6L6ZKW6cCKV8UdevgFBtKxs/bHtPXoKCAi0ohRn0B0NrejEO2SEIpcJMug5A+L+jvoEtv2s3TyEjNbhg87wjUzyt6O4L7XfaZlbxk/EuUnGsCfM3dfOGVS3QXVdlrfr6+LG1EqoDjJMnR80iRpZmmbuRjPSxcUTN7H2MdpRtKC946DM41raxGQVEjYx1S0PcS4nLt2Z2Yzbl7wcISSgliIYO06nO9szr7oxXnjThA0QsD4f/ixZh5VdiPgWsyRbd0CgozBW0kh/kGqXiuUP/X/YhyO02jVDYZGBxjWlc/7TP5r1Zhk4mpLrYjJVuIB7/on9V49uCZgnZCiX1R0T2V2US7zQADv88PZL90kqcEGxINh9vE5Xk36qDf418l8uy/e3QFPjXo4fr6e3VPBCOx2YfXYOBadcq7slVnnIN9+IVW77MU9l8P+kxZiDC/zsF0KEY3PSPXvqHSgAmbeoey5q/h7DSpQFszxc4X16+46ZjHPJZyPZSfeLDgtWdqLEouStkzTTFkc5rHKolQD5RjpoPV0TRbFIYhwA0jGpP1r+MSSeydD7qwI5fjs6PIGyIXF9mI9uNZCedRrBARVGLw5p1tfxe98ZU2D8h8RItuBofvtentMYC3SQNI1bdBWIvxa1+sYnhCAyONh/pphC6afCD3FVLYp/AN8tzMHIIgqsrMgmi5UuoX6B7p/Bow5dfx30NgdHMueoOlfsZeZO6/q8mOx1EQmPuUOD8Y4VSR0ncjr7FU07KJyQLYzu6RGJ0Rd8UU5t27RbR/OV8V9dsbnYCPsi/wQkNwmE26PvEQx/kbOrTpUlyV+D8pDi8unu6vL4Go9y6g7yu+6X0hIqevaTqsDzYk0JkNAnI0n726miJ24vLD/jywDl6ak+WR07WvhJnzG5Cmo3TQ8NAaygz8iV+lo2nTZfHyrKEYgXj5UdXPteEu1jHY9xbIU8cYOAiqvbFpAV7ub/AejWbsPqzDAcSRmFwYYNQXbe9xn7VyePCJ0ZQmBbNngu5EmDMHFEAZ0Rs7OCUGwXHbSYyVKdaDc2xZ+YLqK1iHxnpbxx5me9hBr/eXH6cSxwffR49HnUmpEP970593P7j4dePr+e6tNO7yfG0pdh5EaIbwhUTlRKf46wIMNBXoKeAMuuHT8h4wIcbWI+D8KW5KB975y4Rv2eeg3kBJCpumMoVsoIDvJYC3UXsTpK++qz7UayfgT9kUcnes+D1y1PyLSSOvdrcHffbCMN+1CsRajmeqIjt4MIeH75msVr3jyIL27hnr3gFMtQj/04ntjs0ym+GGUn3jMFnbF/9NPZOMaJcWpzVNgmkmpk+kq5TrYL1YAOHcjGUdqmiOYOxdlkee/QTbJ7JKm+nH+2ixTqHa022mbOjnB90/j9IHi6kkcxzPdHgzHMSMufAmQAEDwbTz+206o4E+rXae7K81vqRq6yL/q47ULmqDx/lDt/Yk/a1av0Sb8C5x7k2jsbiI7JskifwH+P2KgANtDk3f1+VDj3il4+LSxp8JcCS0MoJHlholnOMFdWY8YFs66DHR6fzw7FOrE7poYVOgDZle1e8mPavy+HiEM1HfpjElY5kf5S/O/Datd5G7E3Q0GJSFo76heE0oG7+9GSpRDcJDTaEXYABWcLqbE2monFYk+i+uZxRRQCIUc9hfE2H0ppVmN6vvosFhdJYklEvLI4z/nXVqLluygJhiivIcamG3dHsJ0pR+WMmxa8rkbB1slcCMKo94xYxSqL8EQ+CstUiAPVht6m6RbOQUek3ukf58201iHLichYb6KRVVspcM5J2XVv1cZceGdVmkGLXw4YhO5KNR2XkvUT6Lm5cFIQFysQgImfejyTCOG5G1syXdItFpX9AWcVsv8woG6DDSMec1D5TRSNbqLf7n2/3qKciPEcTBFOPZhoVV63KeCycwtgZCErjmInDvGMMWxRjnom6gai4S+h8AslH3EeMJ+bRwwSP/xcVQoeqZ4sOXoT+vea3dd9P+fxIrLJViRkmIDNvB2WSCvkddLxPOVJ1NHfQAzfs+9qlBBjer8Qtld4zBnUXpr+7MJkkAfby5BxxSOuO2Poxfb4HGpnIZSaczEZAnwfCUeYPqucAoy3Q/uT7kgrtc+zfXgYHngnDMf8GCFRQYjNOseFiiH9P51Jk6ThNZ4tgEWX2QtlqMCrfBynl/JxiriYERWUODTUWU+8m7D14ADiP77L2gMODT/E/mLb+3tJve7CJHf3GATRjibSS+CeJLRTnSPya/O8/QIdwywsVa2Ws/YgB7gc/JJwMFOtK6rGmVaNts4jjP7vaatk/h4oROx4mkoSpKG+drue8sLGsA6wq9FdJFVQecgrPaYt0Z0cv4dE1wuIr3GkRxsLMEvdC27WWCvQyNJhMNP9Hf1kwTDY/h+RwPm4cFp0KFcp0HQrlOfnfflQUOJ+CXZYjHLOQPAV1PpDSf0p9fB3U5CwabA9482tOGLFY5MIGpjvO6V5nj2X8gD3fhywrYSXQHpAqOE9COf1pJ1mKoFzRHZ5SuouY9ZbJ4zg7q5JvEYl3T0SU2St+/GBPrLB5hLZY0gX+XTteems9kUd1wApSRxgPMyVMSiDSSt1cR2GWgWHVKug1AqxYF4AF+ChVqPyCvoyIPtY1NgejdbCJT4a9RBW4yVasBuFBGi0Ik0YMvUp8m4X7u/pHrLvOztLlTgtlIPfJIZg7ahaoBmGRVCKKealWXW7dvO4LDQQJwLRbOYdnh7oKeBC4HahFSmWUuQ/sZ3uFgPbL1z8vu1Pu/E6j2T6+vteVatJEg1BdIYNcSeWwljIgrMSGADACCeOg2SWX/5d2gvLZHNn1Ywr0JZECdgkxKQfJqw4zsJ9w6k87uYFJ8XPTbAFGlA23LlcPCo/g5hjc81KAMmLGvaBu8fePSRGWZ9xI5oXZjWRsZL2NxH6K044aXr5KQhqg7qkgqShCEkDRnpYkKnQL0YW4fllBUho5NP/A0t8d7wM1bFdEGg4u9UEE3fzVGJMMI7oAgdxE0swVVpadXAiFE/tUHmp62jZ+KSz3kzhvOZpSXNrYOzy6hsGIW9fxEjg+D6Edanruzxo5/IW6VD3S4XLM7wz0/tYotZePUIRmHdPLv7d9dlrINTg0JaYre8AyAsnaroeDm3PPd1t8FChXnLJQXqHDCIBbpGl8LVFk2sFN2X+k+FYiH/eiF+XXyCbG6x8R2Qh5bGAB5D0NMFw6b7Z/1aiIQYEHgf4SJvttS39gznOqVFSY7LKhAxNoZN67KuZbtmhp4LxqIH/5BXuUBWXxCghUDxFUKjF15OdK2lJpMacitVKMFY2V3eIKAKKbJgFdoYVvSmvIYsDGwnpi3x6WWSThYh7lJsTwQ220TfaUnz8WwuM/aPS+eiPGmdMPMVjHv7tjgCUT/8Cjwc0A7kef42O6bJtvnvSzCIlw/S7+7PDPkM4cam7frr1svpQBASIhJ0h5OL1CuMSlNk2SLVidQ75SavEvUFpGrmVFP3ncrVESM31pLVA7tjWjQdZ4mdAm8TjHS9sWobM75RsIY/qFKCg8Aj4U1l2ZC6k72tHdkzTCKEYTnyk+FnZYhUjTTBb8+ggwbMSnFBWiQjY8Ku/xuIx2IzKMhpx9VImnCYmMww60WNbRlISh5SXTfhkmvShHnaE4A6xbO/2ouHtFyAJkkMSDWVPyHCXwdc/VYGpPovTA3aPu0zNiQ9Cji03t+PTcpd7GNwZVs3oFO2wyIU89LNWzM/b+Sl6u8J/ibhJEF3Ki6I7k3jQ5O4CRze2AzSQDgUhLct4SYgXYpIkrDgOG79lK5OHzhuNTFKuzvYPi1JWWul2RUX81rYBgu8kC3aFJeVAcNPxPKzKdlW2NuqtJduc6qS/20PXTjILGHN0f4c71rIAB/JDnAk26p3TmspmGlZyqkQq4G6beObEIImZZdj1mpYcQjStYBnMlFCKdiU60Mgv9kzoRfN5uV4zNBNHLKjrum7373ffYkP8+X3KlL6rKDi0v1y0c95Is2Wds1Dk5/ay1plBJdRWLrDMNSj2P43e9tbUNdvCd5XQyHW7J7qJzB6vfzpcKW0I5foGpY3B5pJ8qkuFYc1wRjEnVF+yheL3xc5DkTlkCOm3Hk1b/BIcvl3Du2mw88vFhwWDRCWdezta3AJSP7elcXs/C6vWD30x+jM7+lZQDsZ6ee6nFJBmzfdB3zHDw6P1B1X3i+M7Vb3kwsFlKmcFOpKstJKiEwf/oqGhRc1Dij90KuHRkDVeUX/JQayGE6lUEP7FGowpPLFc9+BpCa5fdUlz47i4koBCxzukzzJCQ+X115pQFcLTO00252u7uYFQvK/BNxZDRD2d8tzQP+1WKANeLf1nxlRUyaHinu8a/HaGxZBopcSNPq/h1p3NNVa8n5s0tujFL5gKc2V+XufR9cVk8gNBhJd7FoaZJsaTdL0QcJa0J6TIpn1zR+WUjSssXHDywomIEMcF5TAE7w89Ww+McA1vch46bMSGal0tZs9c1NekEtkkN136wwCYBbprZcO7Q4eqARYCglz5SbMc8veA68ycUdMSyGQudru9ZH8PlQ0EWn6kM+y3r6N6efU0L9w2+laRVYz71KKnAK4qYHy6yuBeY/QUWJRqUEG64jSWw4aykxuANQfQ7s9o9Fb7XdeC1EQSFsynv12qBqey2ocr0x+f0JeqEIS9Yjc+mwDv7EHVLiWlLslovx2nAE8E6BK3fK0T7cMX2tl0ueaEOQcms9TVH4J7sjIn2tj+t+vBdknPPT0xfxUvKHBEjn8dTKIXC8ZklDYvBrNacgiL411yluxPSf9od5BzEA56xaUdMvFalIw5um+XiDG0vj7wo2ZhoqjJbAzu49Y9miwrtwmVJQ+gt3H9SKEKilqAiw/m07E5Caj+rOfawsN2Leu+UgidkNygu316+jkwEmergjRkefgg6yS8VlXMyG3828vAdIusebt25t9bf7cRCDlt3tXqfTnLeryWXZ3OBjSmHh0PR/FszVYdUlFXNjnKIabu6afK50jNTWdt+Iw9wcxu3PCuSVum+ZRtfEDS6DFuS++zeDiARTZZOU6J4V3sdr+5rZBGExRq/OMuCq/aEX9tN+chGXGtosQyw3FICH9/f/XAIFUIygzspflwvadGP57SUXxYi+kOh7SBieDKcOCygrJVjyL5EQnH3agdaaSmZoHQrtHdhRlDVaehzEXUjg1C96KSeWnhMXT+r+ePplfKgL6VPATC31qT2GhKYltMaWis9yLTcMnqYYnTIJ8SaYWsO4J1ziV0+fYXI4IE+2RRUff1PZFIul6Bt49FevM3GRZkgOsmbvX0+N+7rvGsJBJa7QFjExjgaG4huSLTakoTnE+kXYGfqK188NamUTIi/aEeEuDECuDkMkh9ZbW8obm0j8qdw+1KQfmJSuoHG0JmKyc88thyc7VoZgiDB19Fxham/lcgjSCubK03HSxvYGZZ1x/CQLHe3/QZXXyQk+RNUuqK8R/nEj4+vDN9AkJj897aRy5AJCLjJKTIukioOIBSPZr862nb/joESov4nL1RbwHZ/mQFL5c799+xnQO0aZIzC8sk2g85UoeTdsZcROoqmsAKNuGSuPzAIwNComTWWJis1xj1v/Pe/ahlHH9cRMYnqYYYmoIsm7NOCPZL/8LgaHs/XnqVTeRWlnJY3YV/h6aiwfm8on8bfEDpje72jk7uiep6eptBDVQ9UNAeA776vAOjiosUM5BEB8hjhPjJKQlWPYn/A72PXlAgji7q7+wQWZFCdAi1R5MzNGhSOGB71xcx9deVUrJhmhCkNU+qlEc8AXI29k2niRXtVh+t95XfTKF1IVeVEOPQ2Qf2P3DuFXdEjyx6qUoyBCM/gdKUpefxMm87sl76uXgPiu3Ti7Q7OYkFup0Oi5/WnetE6p+fKwecG+TgROnb546qGiOqce+SLWHbtGSLiEPSPp/WGNRet3Hz4QjYkuRF15IlesLkf+C+6htPP2cMENkw/hYTZQzbAJFQbdqaMd+I82GQSD6WiTx6+0GAO0PurQDA+1cl1vvVrhBoV/0lffjS8YqPWWj6fJtdCFWkvC38GowTUBGIH1y9RGZYQT88H+2KJzpLiDxQMF9+15YbnhaQH5K8rOM2K0W9fm0+Ex6DmOkAwmg/X1NvnAC2etaPP+1EIaypZ8bsyakVCHwj4I48xnkUtdl9UrbJ75ZcqSVoZUvZ+IPSZb+iMt3qqtf2rZJGHCP1qUnyJrT8sDGVN1tOt83PgHo0zEb7rG/L2vskSPzQpYXDlVr4HZcO0QswS8YhnjPNcngziwx3UJibl2O+xq2bFAVV0kF+Jx0Fd/Fgku1EX5tgEb5t6SYyAYecRiB1neDfoJvODMsI+9XZf8r/lG9S6HB3BjEyIN5ZrgzPqr4NyzZSUV+S7QR11US3KZXCD9g7jTqQ/9U1+26rwi8Zd6b65+p0JPE/2dILKIWoyv7Mo5wHBk17AW8eUr6GYQfmfiVwJFIF9C1VigYWeAl2TP55vEzkP2QD0xlgY/u5CIBR495FZubeq6+xYtWQCUrbhyXwSxNndiTBuAJYf8B7t/O3pMbR4fjnBJc5JOvi155RqGgVtCrzTPDRFHEzXJTWkVeyFBb1xgrkulGsNag+i+Gmhpqej5uX3iY7MCw3pdh0oKoCt8ufiWA5qpR0j5ZewyPvLGXXy+5U8xcozLb342rA4neAHKocOBHu3oCzT/CbkopTh7AzOnsznwuXNjCYoUXLdymSudGLLeBJMGn7kiQGmmugTLp7oXGQKR/a9EKMH0lTibQROXG5M+aE/u53I8HnfFeoFkdnogf0stDR2bc7k92mUtfkiP1RUEgpnPp4AXOejDNRJAlhj0BlV9TPhyCh1ZBr1OslwPRUib3uwKEHjaumJ9xn1waSCKMIRchGmtOnp1GXzvCQ0yO5REn81GpDscqsrO/Yjsk3u0VcGhNWPZmqOazvRqpZoWkNZpg/46zARB0kGSTje1wSWHuIrC5PA8bjoW6jstTQQeMQ0lLMzTCU7GfSuNEBCbrX4y30xpH/wIkMP4gV++Dps9m8KWqzMb5SrB579uAVVyq3CVQ5dNOOEcqS60+4nH68G2t89aUDIBqlBESVz5e7E107s/lYSgs7A7WD39zR4ArSFR5kbwPHQwxMcYfyf4AAOeH07bgcQdr+E6FmJbaITR1tjWW4mKld9Eqlkl1rAqCjARofy5aFuazSWKITmhJMIepwPP9MWEq3rezrLfUn8g6KlQbkXNOWS2CpqjY0Y/r1mBZvfh0BBsM0QSSBNiSKTxDZXApTZrcIZPw5q8+FBRcHhpo8Tvo2CAAi+xXhSB6gZDwhrUiQc0JUiAetoER+CNEEV+dlRvZxri8lVClM9nH7bTUhDsCnomzwuX8Pu+5ZdiZNvh+pH/PN9FCc3RRBn8/sEe1204SwG1dsIthTSvwGiHDfRBJp73Ls9Unziqa9G2R1UiQtDOR4sWffgdpgtQuSljbSo95rS5DBCjg2NHiStZJk1YUjwDWYUdn0MzOWtY9g8yMM70zoOji0W5a2uuscGIqRq72O8PgaaRCfuwdj5f4hkgMkLZa/yiu9m79Muw9XwaRGXvtQD4A6hLgGiKrEs0pJsX6FylO/fszbikEocx9R8RQvqd5GoVk2TF2AMzY60/usAP5tcdNlvLj8x/fymoafWQr6Do4yre6HW/Xyvrq87l88F+fW1WiKAzr9u6VsokrUud3uaWRhZ0/RZ7KmPFFiVecTV+Tq3nNBtzV1p+ja72iFjx66BRFF1niuqzfIJziSEt11oxRajyUdkI/VlZ1GEX3TAckI5ZKpQGt2p+/FcTEhjFAHnmga2gV97NjLfpW8W3KPL4EOnjeMXGCqRdRK0H7fp6cODAndTXGGImwCGPu6VxI35oTXwoRBYLuZU5xmgNokd3Z7B8s716309pl2Vb53pRMYKnJD3o82pCh57vsDq9dWEyM9EqSVyvxJk+E66hAztxjm8Ianaw7Wksf1dTP1M0lV6wwB77aYJpmDPqb6fxJx8zwFp8zM6uOwufAIrJdiiYDMucPcjBFE3MQE2sH7YgOahbTJCjQDcvLixb92ZX7+LWUNyVS67lRm1+Mg9qtDR3SHauaMjLwL4zD2ikRHOQQBLDnTLMhnMUP/1vHrmZ3AKfx+gg3GgvDWYy7wuEY6ghTsH2XNY30XjZvyDHIM3BQO1S/GYtwtaDQ2Iqf/SbfxXITb6/Y9xPZkLJfUlZ1iO34ygcKC3Is1NNqmrUd8u08bo+0QhXaJ2zh0DH5nExjce22tWhJ3LqvIFzt6i8oMEt4hfKioHXGaQsmne6NV1+reD2ogD+zarFCHS2t/IcGDoUhyXLO6iiRDTIAgf4Fw3P5YQ72SRg3zRK8MTI42PBSFfi4MWRRBERDmNFtoOSlxwKOdiAQJTuVocvLjONUDMHtScqo0eCaXxdVNYc7fOSrAJwX3OLXHOE8JUsZT3W9J2sKNgpd1rL6e4aSdZHNsksuAJ1Rqj+dG4IDvvvJIJeyZRf5lMhcQps/d0ZjFMrGF39oQCPeHMk604RaQ7RXl9PiJANeaRtUO+JYu+5vGJDa6m2PP/6+frCjVbNvIwG3ceHMRpsM1mi4I4itW7jNFpiTLlM+DxcH/znhDZTmfHHN0FQwuD163j5DxH5QqDXNYT34ofqsiNzmys0ZwAVPpNAM8wXJ0+oO6q1WQCEcV4roLmUj+A1cWXGVFhRgijBGeNzFyYBQn/CobeIIGcrvJhFg/Z9zuofLXSMvxF7qhT1KtNIt4bNrGuuuWHaPVMRPI4JmbtNkES6atkuGM7VMWbPVB3yqIvH9b4oudmE71jw3A/MCASxWxOUEJNRXYO+MiLcgLS9EQjYkZfRL15vXx74kN0nMZCRJ2OQzlHD5qYI9LEzqDuVoikekgGp2nI8CZ4pTxAYwjXbQzXflkoB0w+C+xElH9Bu3wuD163kuBo4+Spcet1JEUxqRbcgTtzwDhtkc4be6HbqOmZqFA/mr1uPIFTRd0ZbYXqdqdCo6pduMdt/PyZDVaWKV+Jv50u7SHxaLXkB2uYSB+8nw+igkZBUjI/pPuVfxmJN+q/0NZGu+3OXP9Jw9nWZPGYJIHVGL3oCV1tV/IPuv92mVO9tu2TlSQaqU93qacHmkeeXDDFh46xfczV3kdfZ57WqOMPHQ3kTzz2hQiq5ObjHkOpxlLvAK3HdVaLwYGK6O+7J0M6aGd2P+Ve43ho1CyBTvFwA2zTCQKcCaSxlxyaDebDLMaOcQHd2F+b2mZBqVesslrQPM5mkt5O5V/4ht5ouIIJADSfgwUYS6GdnBqAJHxrsBnDNfAcKYj6eBqfXcLb725wzjeQ7SrqKBWoLXm7R4H7bSwGOvsaU9RUpRSe+B6JgQ5homSNnw6Li2VxmeAQ3INJyusseAyerxgjO1/zi9IfrTM1DlLcBb4Vnvm5FW7MHbmCzRUDJ7AhTMS81sZypAv/Crvnr9LMXdg48EYOGtSMu2d/23v2/2FrH5YvKxAn+M5zK3l80cun4dJhIkHUL9cPty8L+HMRWYkkwJEq4QQXVGjUafi9qlovkYB1hHLZYQ8X0KM/Tly7lam71CRc6oxaQy3TsPbqlcsZcXZT0xDk0NSPYHmX+IAIEsbjf9xVBDZG0WK+aq0fkatTYQ+vzvfNheJQnomhUp4aNqpuSBBySD1RK6YXqH6ZhX5W7ZB0GY1G1Dwbck3LIbW3kv5xqlP/pRvIvrxyvtvxN8A/jEVfBjzucjbiM1WejmezsugKt7han2C74Z1ifLNY6pZRJ8uZscseyh7a+DPZ24G+T7DhHWsfDh8bU6bFtKBYLC1C04FVoujvy7V44eleX3WWN0OoRwVHr2ms8ff9XAO+q9kaHYpFruhDyXukutyakKGi25oS0C354GdWHmVARjA+X/fwD4yTRUQ/U0faZdR9JpY5l1wkoFwNbqOK6GVO7RJ7b0zIQsYODNwqisc7l6RdQixdAkbefnMai7Jnx0YhE/wHo0/zP36OBYL1MV9iEjlaBmD8tjR40Z7SnO/huw/lFVWJuD3bBjJrWzUGZTjqj5zifC70Dg00BwHsZZ5G6m29NZtFXva940sHHNzOvBlIRW55GRc8XOMuoH4jLVq+bME4n9diA1OZCpZ8x7aYt6tEU/U142e8BPJgS4wGNjgtp7VDpr0tn7sxOiumFoE8zNikvVkPVEOgolUErHnBt9ERm9XknyrAGLAjbRbst5aiHjcm/mb9RQ5QXhvarzriTd3UuAnSbdUzkRUmB/RsVPDs8VcSMBkR1fVah6IRP484zj8gqbr/upOT9gYgrkHnPXxWWMMZ7hHGikdYX+GZfkcMRJioATmiqprKieQoDZpr5y9KtRh7XKU60xxHlwsVg/oQLj8OJssX1x3A+jyskklwwL128ikPnHRz62jcbcOSk/lcktOih9Y/JTYLEhZzOhG7Aq4Liu3Pit2JDrxNTbccGKuRV+wEV3wLIYnOXiZbazZgEmGjH6BxvJtwhCj09SVGXb9M4KiTPBpAN+6TGQPjvC/lgpuje1wSzrv6Sd2MbOZEyokLAnlCZspP23Z2i+WN+6qCNG5RJmYWKLdGCIMgOPWQlgZbw8w54i9GstcbCl2g3OPxOLj2WeRVdD6nKFv+k2Zg7YsCo6Mrwdedc0XZSytfjELoHm9TmhQme1AU5IfTEuyrbdewkSmk0zQqHSifeRLPTcOkuKsJhY8x+7+P/uLIicQBIdvTTTkj5tmAAp39abEhLM4XHTeKmN+PPOqp3YnEPiw0oR5wwhoLvi3UU/7NfQ88/sRB9m4hJr63yKrNCURVQ4HWNKCAX/i7m4gi6f03KMruyJ06B4FI2Q12fGf5nyk2VVZ6cD9kmUcPSApfPxX4zas9lJQtsliEphfW443ohN9RbVoDgOLaTCy2qTlWl89J7EX9oHFtOGFKwACDxNS4FhHRSJ9l1ldZx7IoAGARBwTNVu8OxFb3qGNOgypsE5Q/cyiIK4UH7+8cApnM6MDQr0rf8H+tiMIiWqSiZKmpYs3FW1togy+jl0PohwAumjMrz+yK+dwsEhO5NT0dtMsKwFrLXcyJi7iopjd6nY3x6VIp63MsRfnA3VYjFTRaFfkDYWQPvu+oANg2cyti6BWTgFRB1du6/PJJV78RDxnUKiJhyVuFUUP4YJ9NAJOZYf1845Ues/K3BNksalpWgerUVYGQ7mrXMLWb4/xjdSs581rkyIE5hQVcc3ulE7PLLpdZAvtojDpyclHhkHrgZb7nAamAAYfeFKM/ar+hyXeZhW4F3llrXg0rwqBgbNKWtAupCvTNFDusKuMTmIRKYwTn0oPpCURTB8W8t3YBusYu6qE6zqumdE7mRqlYfQlmuVp/P4SH7OLm3i6bZgJICN7snzt4gKmOWbiv5+2jakrUVFLR4nAJyvJBd7VWy7knHnpUn/2F5D33GAkIDr0TcLaPZTg7nSXwLgPsoIG0Otu0sTnQ5LamKc1ciZn79TLXCCOvqyT5NO5LkAvh6Ko+y4wt0berC/FRrMSd1OA1RaQUbN4qE3wiXRSpjAQSg0wBfam+1kCeYyRxjGtA29bcZQiI/kSVjwfhoyaiidQZ046syRxzPiCQSPOHUvscDZ+FxfraiDpjEOuXV5X+KWa41/s2FUzX1b+BoSoRI63GNWBlwd893iOEsmv9KJaltD5+Lr/N5AhmzDGEOhSWDItlX+IPUzXCX++I3UCuAyk/iao6CMe7ewe1cX4tASkvDzP06lD9z8YbkkO8IhY7WZaiwUFpv97NRE8mzvFrlBusOz3brPMG9f4zuDWIq+FHTck2xLd/QOnIVgRS3WOZniBGY8t/4UIM5ZUURYvacXIu2Vrm63V51WeOJL6I26qw9Trlxep5N7TeKQL99fEOz2LsVBtecsd+/5/h2QfLwHQZVxWYXj+isfJxWIQbbJ7Tbi+I8/manC5IBOba8o4B42yZlP27W7rBmR/5YWJF1CFLXIBHL3PGdvQWKY/xULMo3ZH/NQlh12qEkWYq8jzTtRed+/4yQ+6cDltgQzcFffJSqHAZ3LLb0rfjcVt+igS4V2OInF1tlqblPGJs7Uj0z+TlbyTYzkaQOP758l21eoq9l37oSZcDGXFy7f/zvXVKU5aPm1hjYMBrU9W5ISF8jwG22k337EwLodKzDHx2dLT3rtehv3GwfdxZSUokF58pLsfqDvAGpMt7fkg5vhjlcnrdoRtGXyPjsW/QwOUXdYG8Yqn9WYsuLMtCvXsPVWbOdWIetp7dcOz4SfrbE0cOx9bDmv1ywR9/Pt9r1R3t45bcsHFYl+OmEz5xRzA5q1fco6ADFlXIxKWtfR+YS4nzguhsN85K0tfaXn3gBKD6vyEDyngSKSHpRhLdYK7yvPmho/ntxL+WgPg8uGp2TPDyzPiF88I82GpqFMWBcCqKnQUrtwfbzPXEdLwoa5/+eDJk8bFddKHDkH0p8c7DebgWSAt6yBo6a7WnwdEGmXGp131LAcZePKprYeFblgNuXHor1m54U2mwJckNmjncaKyeSCQHXJCQnFKVX2jgo26nWJgntzxyNAfY7NN4TuDAScb0YLzyt1EUnljLRPpui7LvCB9q3f/YDuEdbyVYke70m616mT2t2Yxr1/NGJ+PncMWAxIlbox8QPcky/DLKTVD2ImOQjhwUtsiPJ9nSbJ3c775UXuHStTEcOn+FbO/jIrCRaIRgLSdnHjuJeNWm14cAWzTWubFgLs44wiB43LJ23s0QH95gvEH79c7Doc+KN13oCmlNvJn77tE7Vj43HxPDEtNwvhoFNW0nRtQeafkziopqmN+rQFD/j+/4jcXYUxHSPQ0z6QO0zIN6KwErjFmDz3DZSFkRRAI6u6AVFHe78+HWIZg1y/AmG/yho7LA7BKRlpeLbc8znyghtx9gGKno5c7Aa43e/4W2mSZzsXUX7JU/P1m6JYdKTwcHw3IRVdEUjzeJIefH3y1KqKPwqpk2gJ8qrecJfrSH1wVzJaMOtbI9wKRDXORQF+MlokAt7zha0cKshMUzEHQ8uE5ONWigL6KwNe+J9wlOkDw1dZcfunrZbPIlZYb0qNnOptRFLcDU9ZGXXfixQBHJ4cKd6W944kOLyoShZY22PxiT+pR92nFJ0fIHuLppDw+ozFWswMz2RbYsQUSyiZjvZH/DD8acPoSWY2tbMebYdGvOABpGM6DHtdXEFp+tdSMVDe8nuDpR3Fzd6MIS/UG6G653pT5OIdkeyvFhg2XH72hwYc1zxuS4PntrJHG4NZClk8DjmVEtTAwtIkMIXprU/x/lLB2RXouLA4tE7RfBvhUs8Wuzyqd2VdIMBE58yvyYeQADHodFSzRsCSAGHoTnk10uZTqDG1eYwz99DgIijRjajXooEGG582tSe3AWOiMwMRPBsxz4Q5/g8yygdlSB0WqxhVGE0zBkxt80e1jmAVq7LWOxO1v0DBmAILcRv5YTeBO2+/pkr298nkddgcXhBNx+f6wcAUJEKGZIUf7H/0l7T+tnrYHtVfoQPnPf8ctgg3h80NjexPY3wZLwuNsuD0VnCTiwCj6pvBJxRsEMMvAgPPH/fr2rm4uIheMRL2sxgU3NOVRfqnvdvSl0virR57DGsTPNqV2HMRKMV0Ymuk39gHQ+2F/qtjNK3TtaFoev8CurBYroAgPLdctgqFNVPNJNoGIk00HpclhKsxMGDMLShuIKRDxzXIoOqbB9Jm8vY6qoSIwA8Z+MS9NmPNolgXs58arGIMrEBox3HfXZSrYDnYdAYWgLyNk//sTQ015P+I9g2LzJlO3/BYrYyWzAEgCu25x72DScH3LVi7TYXEz8sX1XhqjsqHW0X3A174oRi3Df19yggvTNpdUq4S3wRhOsT0/wq8EX5lqUMclsGLSQrPo4hkbKxZBUA7TdtGt4v/4W8/XPu58MGLoDonIhRclHEcIiZP595/HWeV2YlriPzQIXJkCUDVKx+PtlMloHOq0oy5eVqxxyxa4rZIWMPSIRveqkSTWBKfoFENcm5FRR86BW3ldluX/Y/6gPjlR4CSaIHfWQKuxFdSZ0HNExsVQwH4yX/1FuBhDcCQofn3wXBaFhXKYWE1hpypq8pNRxou5RQcRGDsLbaYmTYJClHVFzl7+9Oqoq89cDHolE+XdPNQXmbC98UCMCbnzmPDymA7WPEY4Tz7IvztDgHgpIpJhN5z4EN4Mbo/xKTHEVbF53kMhu8KD9bAgCk3pxTl6GtDKB0ELJbEkjnuzhpPlTlJjiu+RM3aeye+mgcIQumwZB6tMQJ4hQz/L55A3mAvyS1/dn/IpOFtCYHWA/ZUiXXapetQwR7itY8zToJnMsLRgOro2QgHBtNk/6ZirkuDpHuJcgOtj0y989BW8lrQwU2oMjf9KULtQT/4QQ+4Yy+43k2ydkFwIsW6ThsGdHIyfaMmq5dQpxoiXM2kyYXoWuN3EYgr4BNEBJPoa3oQrSSG/1UufmFygD/iqMVUujQu6iypuhY5VBZApcB9VrKunMRlcz2XR9obaU4fksstiFdF15WJeWz2A3h4rkm4FWACcIzJsTtgnv+J9bvdpGwOq35xDaMD0+C/VIycpSVFE2QV1MUfQYUR4gtYYWJIN2mpuLNPsOGbcJFt0gCg7l8seDJNXrg7DkrdbFR7+g3hLb6znSZTGM2CRTQbeiyxIZ/CS5aQ5AFWTybKoF5PJMNubiHgyllkj73iwFqRWqhcim86m8buVWMwFWPij2gEY9TA6MQo6G1P39JRRJi8BPNvgjb9UHvY0eJ6zPaFWn97Os03oJrdY4RbvqvKaPMLVUbY6Av3OBkkRnglsf3ZM4AjMl8UjAimUME66Ygp0ZsjPLBJUxMMnC4InfjAsjE8/kYSFK8oTUgcB+v0ELkKTVM7s1GelD1IQu4zuUUbB2R2yZAM71dfqLGffbelYU8L5DhdVhRK+/4ueifR4pgUY3/NSmFlj7rlvCrEB/fvZUVs2wFV7iZb43ajmPRPRyIou7e5JYIv3KXSmtsNxOrTL/Kr3xH00GQzL9bvIwrWl6WZIFaEr0cyU8CJXjoasSxeo8LuWJW48m6tZJIXhX8zrKxmBRYv7O9KQqTyjAi3T1PCTOTi5hXMYQ2NKlnPlUnhtKNl1SaarTRyhFOaQluY8sAktI6mxBOvLYNxx62FIfNdnJLCcVE99vEUssAHiVhJQs3Fjvg8aI26v0Ce4cdYFJodErLocRUpCrRZNKEhxdBWWVS2K7X/aw/omT3zLod57y2geFdMPQ/nphjbfgei3VZTkwrXHpzvzAQ2z6S29dDcapXmEiFc3pGWzP3fwoxfa+kLoW/QKldvrNQ2y82bD6gfEikf56szY5A9lnQSKFc3g8UMHvsppKGVVF4xEZCMiv+HSXcBoNnWr4tbUo5P5q6ITjaq56Y9HNHs8GaQaAy+d9HFMNu5Gyj99ODenL9lPjDRk/hXAS9mVm64yASR/wZoYA4WA0CG9iKWq6DVeqwBEORlY1kUc4N2QUiDv8uKXqX3G3Kxxt5YywpljhUaf5wLsb8xlkKn06a/UYYpMKHZgXofxybK/ELOGAoir9Ym+UDKqco/n9mJLM8BxPGpnbqjhhbrFgxKqBIEozfKV8+DnGr9m8BVx2KnE124ziLsdQHYVhV/LIzaYIhTDoRTzwmcZwORikLg1PpApSvo13r2YW25uqKnquSyXB/hsISWh7PlKoDgyAsiZq9vkCvKIvaQxtFSaPhbDS0Wu9c3QIf0KLSKGDFVXo6VD31nEE95ysWv6R5xh0mciE4fIiQokO6cIFBwM/ztUChz3aCcAmhqyuZlzlOCx/33OcVQ4g7TTf7BAT8ThOK7B8lqL9URXxD9SFqKo5zDaWKTjF3lJjPRD3QsiO5zqOgKV9+O/POT7JDxfzGpXV3Wos+PhnQSQHDjeoMZlyyiTrUYYxq1g/twXL0lfqa8R6mYhvVd26kGo2NQ1LKEkSY7LH6nCuKBwCh+FxHInkwAzrDoRMtiTiPLPVx8N+3Kho+wniMkq779l7hlsS9GA4jyT023d/f+Rlu0z1piktYYsfG6THjCeTZjMPWkdbz5YC8J9DvhFi3UH/5CI5WYedEyqoM/iDDPhgs/SRPRAn0dB7ehsW3CpQMULbofk+a4NxWgHhFNO/fOkmTjFtVdX8BR42782EkxvTt2chd2sWRNOihW6N5YhR0Sl3bNC7Hus7Ar1t279KpX5AXjkcH8/a3OMVqxYD+9zoyd1r/HXHX6u8uydNbb0W/IN+/MPk/sLaqTPsm4qqz/WpcLiaG1egdLLnoZ8iWFNVl/DYL6PZrciZ0hC5zAsfeT90llsuRMFGsZnf1wfOnSSp1kJvHYLoKQBS5hWFlj6AfG8Iy4Mif5waasjnRbRRgWqSu41ZZBXTqkd7NQuVFWpQet31Izj6qqv+J/XD8AZsv8cnnj8W37a8u76GeJiGlOcuF5+6EYST8ItXsrhGaVQ2aKxsMlpCEBs9qcDSsVOqpglxFxQ0aJAKVvXWmU6MmHEjXDmSHR86ktrLmwMXeZ1hfX9YCFKF2xc5BoBHKQ9FZc3J1Q9i8xiJYl95RTfkDzhGnYtN3cyoQ1NiSHj2n17kWH7+6jTYxn6z0YOZEXFn8Vb9HKpJ4pirEhpskBa63J73R77YY4XXlAhirArmhXjU5iKLNOnjyimoaIM3woHv0uX8cT1voxGTT8IAs2FSo5x+c5FVlZ3/mf/1+kUVpPH058Hc1+2kXTqZFLsoNgX+WZXydhkosNukM/dHfsEXlOOMUKswUgmLqySdKNsH7Anoo0tO2zWoDVOkWn4meaSASGDsQxgJsve+dVhPrh/slUUmrx8f8klFSuOT25GVxQkoYTPNLLqtXd+uzmFsrRKxH+cg8Y4+6rj7quPuq4+6rj7quPuq4+6rj7quPuq4+jTTIQrfbsooq8Xo6SdvDsQvinv5snY4yYItKddy1cNHxU3wU914G4ngy1YzceSdNtOoKm796sLqSk56w1wVLyPU2GoP6nthwqOQqzIkbfXdcGJmXfkr4mD+3kf6QYH7dXWzKi6TVKf9nbYp0tvwGOdZnmvGkMLYYI84V/LGZAAOep8e5iFe0QUrNeAALdQD8Gct4AnkK5ftUF70FVtF2Xq4Xjq08M11P0EYvpxjUECEwtdUt14GULNWzHnYSbyZkdyGJgwnUB3IiOWawLpf/8JdBi20JjoYXYna60IxGfQoL7/PrdLqVGVK+PIoyVEyfzEKQyHSczWNbBhMHmFQr2ukcOSQNha7MVFLOd7MtT70z36W1tvUqgvGBt6C3XOZU9CazPU9yakqs3jDxp875CXt7SD8gcVzYe8LL4qPFR45oY8pWpGi0r/2p/fs4zBkhWnGnhel5/Rd1JDd4Zq7jVGf/X5s8b5u1BJEWlOAgsjo/KOZZDvt3bwnEfCKETrwv7bsnLNefZRqYmg3ZGfVAFSXb/R332YUw2l3aXD6tG/nrm5mFW6iPg96n2OphAQXqt2UqBdyQ6ma6KsAZKzYle9MpWd16AJos99Ob1cUwejFwLx9kpx1rtuzhWD0zYHq++VOXonsaF1TJsQ48XPZCjNq3IWQA7+ZkKtswKbT6lpSin+RmA2Lz8bsTowpobkhIh4dnUwEaoYBB3/nBSQ9PnOELSpiV9Na67w/gzFFZKCftRFo6pmpmv1XQyklB7LENVjmpLPUuVG5F9LZo+W59/91aSEkxXBwEM2xFg+fq1M82zVCLlya6Z7UGgcNLKm9pod0r8nFWfvdeQhWpf+Dhtfzp9K3AfSqPgiYjgSjq4FhDtR0nw8LP8mIJ8OX/3gtbX+XP5wcvlMHzMc4FaiNd2zXJ28B7WcnY/KG9BXUgf6kmoHhFSrQeXuUNDbdRL+xe1GBS1qnUNTMaB6sInXZS7tZK25ie7rp5CN3b1fToS700UXGbWYegDlloq2xiz5lxaDx3nDxmZUhAmP58C2PdkQ71WHxkFBvBz2J3VbjZjGlpq4V7vQiNtiK7pbn64id7MfsHjhlwheeh8GNHvSbUX1X8I+P4GZ1P7xR9r+c+P2WRClwjF4L4hzf/D77cyfBlIdN0Juf4gv+m/LMOYckDPzAPEwVPWf832cZ+XkB9J0eFDrO95E/tLrHB3hvX5U73/AM4aNqA4Z03XD/XHULsWZfem4gAf8CMlJ55P/dRxS4vq4cPZOCL7WA7BN+FGol1zX2nAPW/WBL60PkyTrAupsW0VS21OtRwDi+cuBUFnLMulb1D48cjXCId4BbbRbf4dBubC/dRHYzhJNdeRMXFf57Xou5Nj4s0qK8gL3/b9uBxTQZNbOQ/PdyTyC2q5wxjJBXPkywiVX4tLsWS87UGNaoF/wyC3UqfeKEuJo7TKJFw3rzOnOHjN8DS3KQb7e6K8dzxiz1Jf/GTq0aYVsVXSPkUb4kEEUahud3CyVDe5hVjontYy8sO+o6Qbjzw11RaBfMIjv/sXjdc/1pK8EqpW9kU1Twr11UXAxG8E1pLLnjJTVWAo/H8HEi5GesqKAozxgUqTIKI/4F7kCbpQLOCez7IPZ+w28dzoD3sOiyoKI3uM4WD/Sq8YL26fxZECgwo7d+703b1By7Hz8d8J5ggSTCdpez4F9yd0x3THdMd0x3THdMd0x3THdOtUJ9EqVUbcqUWUA6n6d2O065PQRiboLG4Og2mG1ZFzRIMtC5xDhvLEHu2SIPLwcHF4VmFYsLenLa+K8D3vnG/wc40ZkliNfnXieW68m2mGednszSUIGzS+7xwaDCwWaESpm6RnJJJwuWqfVSO0lFvqRr5Sn/lUhkwTAxNw2jWpLAE85VmvhZofSwbgKB8e2dZ3BPwPUhHFxYdpsbSAHP4QcoAKU42QoJ81ObZIE0oEaDdMJaqMeYzh9N+7Afwj/KsiXBaHLjHRHSxPiyBYOAwlPQqd9V7Fd4B/SsbCVZF4C2ABOCXWgEVs19IWtev0vp2ZuU8ed7X3MO5X43TgwhSBz6X2jWoD4ksPWcQM+J8KEyJaAYVEdoDRukEDBM1yJ00o3KuHGw/U44RkYEnHLpm84xMcfgmGXsec8Fqc4KOorOqRtGxDViKiOHxrZNtupkSTCP+bQsnKi7REbbIwIr4h88QbYbp4mFfCGb7hdYORjbyJZF3ZxoRPm/JvwIsLQGWZAnXE29hBrZu6n0cK1NhYVtT4SQYJgL6XrC4pJ7cbsqhgOAZk+3xgnbvhtCLkycCnJ3QyOZc8NXyLJttTm3esO19bh+RHQcTH6J2+FdNoFHtOqNYmTH5qj1EwAfAj+/a7Rqt3mgPdA05kcf4r4N43uJUpfg5s7GtA2w7Jb8oxpqdCXGdzZMlsc6alhGuwbqV4vFGRH62p+AH9Uos8kE0jBY+W9UHEuKbj/+4Gs6dLG/h0TYzmEKGVdU4yu5+sQ3/a4QAC/i3dV5ghH4EUmtSP19WJzRLo2BTc2MpgKSD/tKoAuAI8Dv6aPFDJtaC5m5Sy/gaipwxsEFDqkrXNiF1wguGc1fP7YtHnlwol8RmXL61bnT1ERA4dQI6WrspD3LuDrguwDECNR4K9mIVIZvQXzuTAhfF49kN1Dtu0lLrex7v+cWjFJ7J1g40UKLyvdIghu9+Wy72T9Jy9KcmkJVM2imlnc5QwhL1lJdluiRL9m0c7QqsdoEQMBtnLpJX4TU56rOmSeBbP+nFJRZMiAoJQKKO9Vz6HOMQvltoHEbk6Aka/xgxYHNq/Aa4Bg2rQK7tU3dVVqH1ADxNIhexd6OUQDwjoeTx52oaGhdYgqlCoaU8wovTZ+hHVVWvLv6LgJ/MC+01YbzVGyRxRpwgiAfFMBqlxfJskHZ1bjcgANYmKXKNH9ofSGcgrtsp4jyMA8XQvLtOzIquYCd0SLEtbC8lpPLbgK3nVNVGiTXcs36qQQisH27SfPSmWrrRgndUP5S8oGcOrywyfIKhyAaKA/qq+HsCJuC8Yt0c4xI4Ebl6wWZkESdQr7//rzIm6gRfiJZaNUDGBiVwJFvdkTyOcdp31NewsB/qmL9LG88qTFdzolbuvo7009ANiwLj3Dp9jLzzvgdow+TevWNO3sffH1ZuaqkGtLbJJPKHJNgsoJbRcoSujDNvhthxhDSkrfJ38wVRFoFKXDD+no3LTuxnzgrvfEQNwteNX4To+QzqEEwc13BD50fnwTe2depXFtKmq8zdEBHqdKHib6jzKb4Kvuh8ofeteRvNM/VaZNtTgA/KIDw5Bbq/0r5ApLx+9xd/rKuj5qvzkPQ9iIJ12H8oGS7aJlzNSuVh+81SXSvkIA98JJ8BSPWqCXR18NXLxFM5S3OS0v/iC7Q1UgdzqrRabD5ZAhxCGapu6T/DCESA10+KOGm/AWMFCACeO70UUydwzRyGzjtBtnjvCIDZL1giVAFDtHjETWcVTYgNd8kPJMwFsPHX3EWeh9E05X2NZTh0C+kXgbJo3Z15lpanSZWVBSrfVJdTGpZBkUx6sUW6W8lgjyG9/0qM6K/htPFW2QZHqJFZg+4zAOyVm7bou8GKJZXYbLDAkDd0IL2q+9LB9mvhUk+8OtBcim9bqsBX8B74kO8X6eICHWsb549W4H5WIZ/roEFlfWP+CJ/aAntsdovkT6A6tCLwQJydAHiRgkX5RzzM14ZPA2pcSwp8rfT5yxqEZEo54/qo7Uzq/7SLd4poRLFLLofw+DH4fuB9uduTRnGnRzAZaa3/mokIJ62X7tlpVSGTkbZve8VdM/vf9mPSiWiMNvwilcGdXOoS0+3RAwmsRvMN0EnGlltUqNM8bBPaTWhrJR8JvJz8y1jzN0cBrh+HmI4T49G0G07xsIdka96onKIbuoH/S2r68Z3dyjfEV4meWBIMN7UrmKu6Mig36CUtZDJDbNod70UZ7ko8VTkHnfJt0sZIQgMFhqwIIbbG/mgk0V2MfsNSUgt5CUC+SIOc8d2BYm+M2qwzksRXwfgqTj6wnJaIBCNEMEZuyjm+jSZVHV+EDOzHpf3Pt/nRqxFcGPksi1sLOilFYvkJ9yg9TNWSulCtmJXvClBHK38wEVm7WW5aHM81FybAk8e0q8gJe2K/2p20UkVNXhFy8qQo+mZzCMAy1qjFy7XfTE3eG+dL0dsBu89HR1KlVn1skhtQrUPWMsVRjcG1w00y9HIm+9MrUT+sQQDOnOXt3VW8/xfeUHyimdWqVuv1ET5psit85CXYr4N7D0bBgAuI9RwaCAQR/LpmpuG/cRYKDrbQ8sROWliIdKPxkPWgDwuAwUx3ZhXxj6MezDWBbVlGQPvvaUa8q1d6rsVKMhFnHYejeJr10hF+IWss6S51gKlV4olYjwMNxkH2waafmGZp8ojKgRpCis77SE6mkh4dMgHAy8ZEFYY6A7b31rmXIMgEPNmKtbOPb8FC+IKBiTqD/7vW1GiINFYLQzEO6Dc6T06kKKIlhnEoCw3Rh7Y3RVV6oUnmO2vDt0EZgEM3YCo43IiGSbnfVGc+Bb24x9BkXvacFwtmyA/f1dzwhmxnrMW0RdX0vXhrRfXhbRU7cDvlgKXTwkPLSk2TzewG5SHwpFL1z4q77Ajb1FtH5a8OUzYwFJYa01IVT2x1I6F+N342VMpojR2FjmHqJb/9cMmWrTGkPNsTKT0uh1fvmqPm1mGjH8ngnDKz7/whNIZoxaX/pOjS7sHJUgFzY+xqGh8eJ0eMzmPh4hVb5ooPzjPGuXW/hS8EgPr5A7BD97Zkr7NoGrJkn31RYqhp77oGLfUPQqAgCGeysz+hRgrNxcNIdCIHk98D3tspvSZhrW3sHUgymbTjoQw2fmmJZQApmvsZ8wbg28bAqLTAH4xw5+hTZtuUFCXX2876BQeYFjgD55/CIvS7AU8UlbeNfBaKxr+QLVbyC/V92rOOlfjhBd8q/o0XW/xyILvMO2advyGT5sZ/l/GuvW+ktgUgoChEmZeBJ+fj3P9Cln0nzBbZ+Fg5qCtY3Lh0ny3wxpRHK3SJpbsfEKdLuWQfsrbmA39xoQAgb8kd9Jo0txTomAztmnQh5pbAwDUjAalYhfg8g4zQRAn5t5nvMpqPFMaMjDgUNHyNmovCuQinap0h+06npejyyVwA73Tr7Shjq2r6rWWDloOnmcVarpKOGRYhGDAqArCjhRUjEqET0r/n2RHKXb6cVgoviCy+6XwGmIyFV/pavdogfYCJVOE4BaJzMttrNuKs2rA35JWcs0zcP+3qFH5ihySUEadgWa4AsqPm5kjVBltBr+TB5eNWQf+FiuvRhAF228toXKWL9ReqdWv5fT4bS9/+r8xilygCoq5fSJUhWDBsHVrtzj+7Y/+rOYXtUXCF6EIVR5nvXXwhV+I03QhLzv/yWIQkou5BQTB3u9TsI0LYwUwd6S2VkortwlvXsu6aLrQxF0+LY/rPGto8DkF+iO47vUKxt7H5NHFOE4w9EoTsIgt6tTzJsTK9LAr+f3JiU99EPl6V6BV7lMPdAUSrkYHzNH2CHogHVemA8S1oXEuhO/5X2/KLTgR7b9oETi+SMu/D1ggMQjawAF2/KfLRnyGlRGOOYZT/rupKuBNoFK/OkUKrmgjsNl3bH1hk373LfYQgqYmvKZb9EJGJueGozmPi0NnloPdWCJS/wFSKxpJiY0gz5M32lgYUaq5vBmtrMo8IvCUnJhWNka7ArIYFsAAs0Qnnf7Huvb4pqcfAkPHDlpDzuKm4pEIV+a73gZwFNgin+dscjcowiwo3coNFD9JM5ENT1Tlvbo2Gky61KeZTucjJ3of41tt+8I3goc8VioSwKQAR34CioY7vLV1uv6mBTlVECD0koEuQwx7KtcZ3ftfYX+1YkxYqNT/BuiqFt8S/o4+Rl7sYCWpZeDWiP8X+wDf+cNGHGVue03uOo3ssEg4LsbPgDqk6s3q7ypf/3x7hwhRJQlHHOdNXw2+6Pgf2ac7WKXIZKYPwuJkU9R+GV1k5cmYvF/W1WbTk+u64Ni3GfUFamdgZoeC+W0f17W+guSiMfuo0Ce7i16/BTHPPZZytebgHsIP2N+iI8kArtfoJxZDVilyMF3yvwU84dK9Rh8SchGeZ2IEqMq9vvkq9TT9XBGp2OWesW6YAeYdpz1DM0BZ3DlpnF07MFSbUlTv0xLH9EhaQKb2tDUt0FINEzInU6LyVxDSNITzqut9lCXnryXQy6pWnriQWNfilSkaAx1+SKysAR+adc1s2P5+Ne/v3GuqrEaa2QL29KiOLoppfV/ofR+56cDEin4Fl9LAW31kxEDNY0Xae32KLrn8SKZlCD1hR2b8yDjQfBhihgsC9YSdWFvq2/JPZq1MfQVcnXlhyeP8uFdPTkt2J4IsuPAahuqjfC5A3dK2FneFiKcF5JLvGyEl8xiDGL7EvlkjADly6cj0NLU+SNqRJ13T0w3WkirH8mrKOVivF/SSMo/+iJCniAluDldeUNLrtWDd+adDrObAA/DcBUOXuyH/aRWXFz78hfQlxNHzzO8PYPD8v0EF39lIxur8WtfcRmBfwpEljYfQZVxAuItSrJKh6y9HTzzBcPSTmJMEcYQbhHSHySBgITQ6dhet7lXtPnhPjPFYGvqy8oKCCUcVRAlAHz1Dl32m3GIZYgFA29w1aEfIAvFVTXxgydKAaNOsbyjlFqiqqkLw94p21l7kaCB4ofEF21B/BsbXK+L4Zr2PPJPoUfb+w1w34LhEwDpafeUritv/kTs+5guTxYptfkgz2Iv9ecNllAB+/BxDtBKCA+2tVGtd0gik9WdmsLn+JqyaPyqCZUF3rsXdhJJzk2zkoamvZdWYy2ZHZc67tFRxyMYCgeWIjRHOfSpHUkLxmeP2Bio4wkoQK7b/qre7iGSPYgp16vahZ+Q3jfrqbCJ5kAGVisfDeMm7MBSqC0x1R6MvJ8R6bsQnFdwOeYxBjF8qVvrgpLMutrZQZy0Of5/PS4P4hwx3YFqV2jjiCCY/duz8vdWiUDZGbOzzL6Fy/gqfxBW0rwXtdzsbtnfjbskEjK+Fx4gbg3aZgBs7L1c+jsRmvzqH7We7RltxRlG4KfqrOe3yWoh+iN12+1jQn4COC0KkfrTB6aOXkBHz/Zxn91JKdjnsQyHofTf4DZ60dNtM3/YT+waN4HobTM/uFQzCahhFSgLoCbDfuaEXQj/Rhv8zxsb8BoOC+IyJ2SqDjlDiqe9/zLchijXWdzEF/R7VXfTqTHQx94H02cxmu/igpqLWXJP0pJ8rOkwMc5HWnbFPHFiQc+jru0eexdK5XbU8fo9uaLr0DmgIBUISpmaKxKrtzUqE9WcXIhUEm4qVLXykbyiP3wWRC4AbMZdmoN3XUaR63KDrBQ4mBBWfto2cgsKmed/BkQI0G5RLf3v/WpDTgDfyxd2BL4551v0m9c7UaN4lefq96s56mwwz7HFgV254bugS/IzRzb9ZAow1Vetqm3sxjZ1XQfLflxQ2NocbyoeJpCspAZX+i0VaCCB0yJXweXYiplb/BiBIkgktghYc2L37lteYR17St06K4YpaYI0Enq1jV/4uRhuVpxG6Gg9O94DcWZQgJmi3NXldp8bgxGWaC4oXQTzGxFT2O9+TRqF9ZNttKphKCRg4PzpUKnWDz6kYzbbjKjIG1VmDGkttMGshs4hkqKYe2RVEEVcdp5g1pjGpY0VuZSqr6sgUuG6I0VXkgvitzF7fD86NHoZlStQI90mtqs6CXVvFzGIx/XMLeRh5GzIbz3p9DaPwLggKymB0x8xhqXE5vPe4JANHLo6kpLHS68zj4PnoPzmmAKCSlPZIkuaqJ0DE+aeh831XtmNri7tAZgBD8kgY0K99vbJvlsAnvEEfYh+HjzXe8wj4a65VBD2qJ3ZG6XniDI2mGaPGwlO8pIrbEtLiCWRbmHUq0232ab8UGtqUVdMRLr95wJ4zD8ZfEJoMvjKJJxj4o/FYa7mhUBFAD9UcCTS2Jxi+T3XeBO0QBhM6EQXBCGlEkplF0NjDmEqsXE4g1hFEEyBfzTJTjXPOtRD+X+01+jLwsT9yW+WGiM5D0CIpCud2U5jiX/5OfC219hhsNBmYVk7uONzrXYRAOLD/GwFFpzecvQSwRQBw1XC7viKS9M0dz07Pv/0Ddm7gfUP5Xjg0kk16z4ZrVx8wSyRh7e3ww5phdeyhMk83clvFqYVTIlw5NRF/IYHdfpUiOChkp/cefr7TSAWK/nFydkIFCuFfDEFJq0ry1Y/YtylrwxvrQSB031mtIDQeIS1e01qZZDI341d+3mOlnghdDytFrwcaDeVXEUEC4XvOJel33pClP2B1aXJKL0ZJFOSdn0j28LSTa1IEOheDTDGZqtTTlpZejx2kyVZczQLX9nt1vfYF5HQaZJMmrEMYTPvwZIqYl05sdsvjIx4sypZlSnUPyXBTSajKOFJMg4gMYkDZ7FqngN8wAbe1DEfuJRqrSOtzjceVHW998GIXHwZz3FRSzpW4o0Nwp/bMyfjmVCQij/z5SGHdppXzDpQ0P4m1YWKB1ZYNC9TKrhAwHwuagHeSd7Z2zhFpn71CIaKktbPhf40FZ+vpdiGEetjjweJJ1kHcfJhBix9qTgl5FnNyaB1hNk1TkxOpV7XQj7t33X1EuI2M7bfxwUFJTCHGTbkr9QGTyWhz0ZgGddXuLCiGshGkQrF487lqWEMtWjwq2iTubu9JE8jT18sFeDYq2HIswXdKTx/ussBtptFuFyCjMBtknIH7uLEvYF89X3CAWbMHeLwB3kA/yB/CUKUtmViDrnYETL0Er5zweo4JX8rM4YIAuXqIyTQxNk5Bv0Ep1t18+U8npwDs+WGcEI+x3kWJjC6KZYUoQzSgCPtJmkGmqDcMTyKc9DHSHO4a1N8Xo4X5nq7rgKv9D/YXk79cX+RTKFSlJqgGZtFgLWvKiCoIxAl7C9ptU7ImGimay3ScIxtrDKchQtb+6AWC24r5yWRPtCdiKKA5lsoFfSkKGAHiXlRh02dkyrFKnsLBgxlYNiUmSDhF3IPTXDidSPLpeyDq8ZFOrM1UIoe+z2tIYC6h7j3obKnCKGu/XB1FJAeT6l8bqL8PKppcSqsla921BfJqVFOL0QzsYu++OSJYPB6MPEVNfHxGuWO39frn2ApdIs1yIrGFTEUDGK546L/elRwbaVkGVaNEMzbXuSwXQoT4bPU7X151hZZeGsqwxelXc1MZUGQfFlSE4h28YxA1EqaUEORXJsYzMaR5LgRa/UKhguA8WrGYvrXCjIqHHnx9unyXKuG2wnmv/eBZr4uNF/+ywlAQ+JHcFS978yBzo/XFuUHtTOW55dgq/iYwDapT3zblEzNZGZDwW7l0lsM4zuYnczoX2m0opTTPBSpeUNv7dABH0claEE4DjMZyjtRa85fwmgfbVFr4fwsHnzjl87vI0hN+XT8DPc1UG5bqFP0Hv6FwI57UF6umMR9Lgh67o6RvpGhgGPoU8J+EVZFIzq5hLAMJMISghX3y1XJyZ+QfMsORilVKZauroR5+0sCl680Z/XOcSmnrGW805bgew7FgMtFWFyU+We4aS3CU5pqgY7ZFcHoCvymybUB8S/y0/Wc7OZTkCihe+QM4KVBq8Ggric/4WV9+A6vdzqU+yhbZp1wuaW6L50u4ZKz+SAcGbMwa9XHV8Vn98D7Uo/wJ5U4ogwDE6qkzJ74fYqggMJg/tGI3nJ0tmXpX7TusGPRPbzQiW+G0oXOTzAQ6qgMjyqi/GTP9LUy01cY0yK/oRK2tAzlLqUqYR4K+cQ0XZN30fJeCz1JBwfZB+JbLiVjjTjyzv2+/tY51UgGzon5R5fBV7Gtc7bAJ79YZFkHbg7HlHz9XXZDCAYG1a5GyQ5AzFc0ZbXowihTlhFmze1FgVC9k2bYSZKQMH79uBVF1qSql1n9ksvLkfYQ/gq/JpFgAfEQq+VzQDVu/qA3lXYAGtglQjMP0s4XfMGzO2ABllenW2uvdrTOGhBUZ6zq3M/Z1AJ8NNmHMAFaNe7Cil3i50V0UxvcwVjQp18yfeXVyNRypdJRKSfia1/kay5w5AKCiJJjVt20PKe8/nNl/6kkkgDCxdOeH9s61NgXkUntlMQlQSCvBIayEjseH/U2RJBSaq23sVId+rOATZr7gVPhFGWqwtiXvu2d+Wq5zKQhiNDcwBusCqv7kjW+HfIi6L5aQmQFKEvS0DV+Z/j+5nb2cuFjJtUz0Bxr/hlH08SI6KCNtz67WHkDzPs5xD/d2edvzgfDs+FyxsLua3sYU8foSH0gP5+z+bRHR9BZEjNSlkbi1qNalW/Yvx4y8YRj3YXFSlfFGexcsKSzqbn0fvrcuaVvZBNnNx6e1f6FHHedDC6jqBGGyv0stlIp/rQDi7HbKmvklgvH0qNYLqxy70+hNwLeeo0UU8awiR/XD7xclX+FH3IWdjD94LZamLkhF6KtER1yubJH8SJ4TXj7jpdIqVQTlF0RODq7FXzeQETzRX24L41CojJuQiM+qOCH7iRSdfTcO32wbm+yQrMdb+CIAgUoylzOqSea1ittHVdyjYXB6KUZkNju1NDw0qngfFezbMx14q6/LZjQDyIX7oxony1d67XvmZqQz6uuRf+5febdAggh8qqi9jQ9APIgT7n/hRACxzy53YlqCue0/+I6T7qTiBTHQ8Q0v3UzwciACIwJeoPdK+E55PfAGgdAHjADC0LSmU4ELR8ixZRT2A3hmayvOL6W5i0/iJxIHNkjabGO453rZmFDYLYTw7jH+Mu42oC9lQ78ITzjY7v680liwmAinoFEs6Px1r4Qyg7f3zY/BUwMLXxgyPJzJs8eYtNrbRqVCHMvKpp4Bcz0sJxS+ekKvYiAdoAJjVs9f3rShxvBAaCnmGafRnreA4ZztVKYhK9L9MVbjcZkBoLImxoCZ84uwh55xNe7jcaSVPecg7pcDyB75gvVCVk7nR0lF1hQMyUwLY7I7wE68d0IoCiONWy5Bfiq1Hw78AtOk8MbzeBIuas89lmKQ7bHimfgwqrCiFYTPgJxGlWuLSJCT7j1Kx++I9fJtp5EmLrlnty5+ZB0wUL6Y001KgWj1u0FNoRMk0GicTf4oUrZoif0EFx7BvzIzKxQa3LVRYfS7RuXh6dmyt+cw74RkrBLFTtlmTqg0FImJpb3J3q7sQ2+z/0hexJF3YEdfCMJXCLv3gCpj5WZ7EB8UZugTNcpqR4QOe5MHJ3UDYme3wRGDa04WZ+I5YDUXu+a4N6lbs/ou/JmcNUathMI6bH6a7Ws6gotoSivi+lsjxhJ2Cvz0fDcrS9Eh5V+WU1sbPpI//bOXRnhL4rsheNYtbAl4Hya8+kJfCqHfnpcJP+wlZ6mRFo1TZpgIaYGNxViWzlGEHsKD3WV2W0cNjQkbXFC2+ykeK4XDzl5+35os5+xCk6tvTOXLNAXNrA1VJEFpZWl/RLHlZbt0kth1gb0wCOnMc2XxmAMpPkh7vDlxk8MAES1fcBvjQypXKIoRz0H52wTSsPC5RLJ7JDqqf7FbBqUdu5LCBuDZ3X3tEprOmAjIpVNxLA0VPIt9mX9vBHqhvA2sujhIFR66WaLR5TKS0UyX4I4rujTvBofXRv7slKWm+S63xSWk/gS+VH0HGYYAUP3o/8mxHKR4ZMmI28eT3Kd9bJ0YviBA9DdzaHv05eUNHYDxVV4GvcUflEyT+8n34re+7UYVFoDQOy2XyJ46hBwInJCBCN3vBOHLcNYIGCP9FKTDJqKi30nGjUhMDAz2tRLRWMy6zhWB6OSlXOxFSDxDaQgp9TgFEr0sBU7OMFIjJDv8vfAIyXvmQhSN4Xy/ItXWu64AOFzWgPRJiHEKDMheW6eiqZKmpvCrnDVelo/grU0hTdMTcw1lYJKTojqrVAuXQUWL/sxNdVOwi9kDWUvjJKMtYrPBb0ve6qV12kncw9e3atA1Z93enLknbZQt3+cTn2EzdD1To/0kHYHFu7llLnkjS++zLzIo0+ttN+VGXefEaB5NBD4/nysm7JfxSuuZX1JwBje7Huvaq0GU5ahisA1nfGLTUHzQKAGppK71SjfePXdFpWtg5KD6BG+QeOb1fiCZDeOeCcT4EUKA2qgr2lwjK+ED/jmsAMUxwlH1Cmqjg5wkCDZtz9G3++8EjWKqOPJLIU/vIP0GvupB02w5Rrgp72SwdeWLTd/BurY2KJ1f4tFnDEcmSe1v2uMJt8wPfzO99Ord8dY9PjrpE984gH2aaSKrq3P/1MKEcRdumyPOziJVSbeCzCdLBFxe0Y9KAJGwVB91NlueRBKvf9Eza7H7Sq18HXs+78lm8bPPzssfvw2Q+CwZZyZI46QlQdr+GqsiYEjLYVuXpwqY7gyVFtBSkOM7wsfT1MSeUaYBLza1m6iVwn4ZtE03sdcY8QbOGKFHp8BdkBGy2blft2GpOROQntBxMxXaQewB6UnWi8tSlak8V58RkdxD8KMB8S4R5ZlfD+KJgiX9qXcw1BCMNC61/XYmMqgvtICedATzqqNiKgiwwluFfOo2Qqhokl/C9+E9Z1B3cNlb7qdQ11y2ZVLxfuVGKPIoBSObM1yvFHeEGZmso3EAjaaz2fYHBenv5KPK7SWEf9HK87MfzGS5dIodVFXrcTtRkDLeJi+3/oKoR3lVfQAYLgD99wEqy8XAH0d5wfdyJ2ECrV5ZtoOpnso0LPs58KRxY+41eJsNBiNBbgUcryCl2k/rxyS5XicFPc5ngrciREE1VZs0EjGCVZ0Xz2l9cmuyZhfHHdgNFjuDsfGa82NmkTQK1gpA+1sNJ77SFsdCRrOoz6pCsw5xPnF67TiVqP14ugwxXUjJ+Oe/mrPlErebxc06fervMT5KIAQC19vVYh6fqoRpMgXPw2EtjxUSECytkvTFRkD8lMzq3Q5C8XUYuP1QU+0FpMqmfj9htQXts3VMaQ4kFKh72tavJony0SGLB2OmgNqzF3ySFgwOU0re6u7S8pQEfdduCQWRT1KOkCSQptJfU4jp3lJPniHGt+4CAKG9ZfzmDF8s5Dz1//Om2vlqUHZbFgFEET8YoQ6JxWITJU+c0vLGjW6a5q7J2LfOh8XDBI++1abSK33epougrcblKXIXXoxmwHH0XwJg9lV9mlrbxEd34s+cb41GVK4gc0a6X+6MlhELPLpZfbigUOhEKJJv3VCC0GFO3z7xP+ZP5fMHUo8yQzleE2K+kDdBUgqoEARtqpMeLp+0u214cmW+/mmW/Y+libfQmRucUbEa6lC/gRnjRSzqWyp9X3Xs5uYPZfHMDCLZqxrJvlSEBvRU1l3nKWpdR2xFbxKoHW5SPz4Ip17AbSMMGw2VRuRTGjldwYBhEEhQz7LDOtVpttcZgyOjS3pYZ2pDfdf+oVX0MhyZGYx7wJB4nIMmyxgQm0RJ0Le/D5jV27uT7lS3W3MRuIHkXpzPT47h8tjB6xfsoU//47M9jKAD4gEGlQdKnXAcnRpRzqXV9Rrkqngrm6d9hJgYvWh8ROQCxbdvQ3bEYXydXVHn2OJvTcBLG/rhF7tO1rKnYuWn5g6gG8Q09cZ/b+TGDPvjt6zXMcsGnpzd06eKWv5PO+ddoPWMkfBhl9DYd93FV2jaOMi0XxZ+Sra7uzzpMdLzjZdmMlhyFQg++BQJflqisrUP/hiZpm5/2d5Acpun5shNpzM0vaGSugzBTDBps9e/eYxXJ+XeqV+HGKrxVw3F2sBzD6umMQU58FNzVFuH4E8V41KMjfLuCj3MLKk+itVF1kZXIR10OPNeXdI/2QnP1m2ulEnlwblxYZwu9Kgmk0s+5w+qENryg3WSFSmXgtIIeM67qv99rDalWqIKG6RInTjwzNzrmNtv5+wiikWdW1kxylJAlrMuBG/oaAIR+DMwAuTMuWmeumDuC/iybyEikO7gQAGc8p6kez0O2rY3eZTXyGmzUDwDzLJEk7C/lSbVs7LoBwPZOvG2X5rbDJ2AOJT6v0AIo0/7QC5N2rTxoB+fhUYddY/N5s0n67oylUO9ogVxfAQvCiBtOu/hUpP76g4+grvhLxd+oExJ4HMd22uVNP17SBB6raY9wFi6Zm3+wKi/AM38LWVGr2WtOOBQWniXaL5oGx2kcJpHSwXAPLKEbqWD0oMBO9rwSDDxrRv0hfG7Bck/7YG/OInt1OMxjI7XvsoV1foe2DvDYzvamWpCGC2RTdrT747lXAUdttxGzP3cfzA/bxSSn+oDmtZvalM6gUFYXvxB/T35KyMueOpioApFG0f6RUyXaOg4/H/X/vwpAHkNZ18i5cjj00/nShzIXh/gtno3j6vVi78fHO8Jdj9a8su1NrQw1s+g2lP2t2Gx1qlwfHL/xA3rn8Iy/5JOHHL+2fUvK2MxYpv9dYjVqOI7xj5dHwROn4h1HFFILaq9azlXciHNhD/dfwCh8oihYpyWjrxHOOjQXiqr3mOMGmeqgtUCEIzVWjiZAKzPrvSQZt6yHa2cIpWifEpbvEr0QlukuSbdT2gws109HiOJmni8KTnS11fsx/OIkZH0azOq0Be4jmH+pUCXSXZo0uOs1SkiRf/4l3DkArZy728XkI8Eu9ouyFIh1nEKcp1sTJEmaDKW0ZwYADP/BtsoQID1TNb2FngbV76lDpyYlYYbEgE7TFcte0dKhZKSIpPc5BKgAxu95jA4d4C3WB96oGK0GPHUKgzx0GxJop4Fo46lq6IbboyPHrVfmOCeAcHecfh/bjasLpGPLChjiA/3C/LYKW2OZLlbvgys5X7Kv/rlh9TczWqQ3a3GCwor1gymDx4cxQ+EBEA/V/gg2/eJIBnFL/pZcPBc4t+rBnPpX9wb2A35/Oodk59kL7xjFLjcPmc+3C2Zc1WlIGwkF+xH2MaxK/sz5YbIKgT+MKYfzC773U5fDYRXeFK52A7t1Tgx2QJ1DQDWXbNp+BAoZRQDtaT11AKyZi21zfLBw2mvM8gtk9N+tEqshTaQV2yy2mwhPAJSwYKcgOn12EH9c7ztrCxsjhBY6iYIZwya6Ma9zR/4qm8ytZXUIsecsxxziuZwiNgEy4CjRdbS5ANURPYEN5//B7q4iTuyLYvhOWCz6BQpy3SFjlr7GogHHBwlKogT3UPEMFygDl93FAtkOZzscZolJ0fODy+fPsJR7jxMJofY9gTK23GCo85xYljiCKlAB0qq2PBSTvdCUSHKqX10GeX6GN8ldduBVxba37sCSVIdFRj4n2/k1WKBKtEJXh8IOMcCP26Weedox0pVSacI8Q0nVweSutYy0vRir6Pup85awt758tgEwj+M6Ci4yj5fsmI3NFQeEsiPxjQunG03ZCiNQJ6ZzTtDsEtPA81Q5gvJOcGsixketmSnWCoACSoVaRgNQbHA2UbnkYo8V5ITDKd3pIJX9jtOddhT/1nBr2ISoOKiOgbbO8sGaOtpA6PniSDqKYB6SMAXYDrutBa5dWtD2eFfm6roFMNk+zeYFQEe7IxjTTa6I7MESNUrHFlTAP35hRV6a/4ONtchFWRg2Or0+fXXbSuiW14Ym0Nqajt/f/IT7c4khlHTM+34xEQ6YaSXDfU2IsBl8kS8Xv+LYkCrHPnNwtt5wEC0iZ2lsxH3ZLdYnAdsvj3S999cp/70FTQCEAlfBCtqwFYkUaxWPuDZyDko+X3CpDa//LUyGG7eWp7iROHlu4uqFaM50RmazTlf9hR1IO5zVmacwnFWZ2iTaST0kSBtYPBQkzmwolronM9lDj/eT8VvzYmcBm57ke6WCf+DjxNxf9paIwTPujHb1/YfS0OLJpDpaQDjulmssk60qssiLNr8G+V9LCY8fg8v8Ud+9KMXVRm2WZVNIP12RE99jT78NF40A4hTEubQvDQOIuseQiMXfjup6vO4PA09BED1SWcJHTacJPuZUoRuQ0uIa+ZgKXjpoYTCpGiD6NuoAEFYPKKStUUSJmmNqWtpwk3XK14JgYgzH9QVzGuA/yUO5GBmF9tV5rPYBJBZ3uNhV9pk8wXsY9GW55AzM6gcY9aTcnOF9REQZOv7+Ypkh+H/yQ7llN2l+2ubmby17iOgxHrcNVFr5hcKQ5e/zVNeLkW+haoLaOJjEDTXUBzjP0N14bgm7uItScsM2lvXBJd+t0gKdqCe4E+3gp/s77Sw9akOEv2Xc6hSY1FmXqS3DX31iNRHK71T9aaKJQz33gcJiXCEvkPDncn0zWDpByQerFbqfDRWicByoZaiELPgvCioOP+8Bqjlli+TWYBuYn1oBzTp+513TtC1LVaksuDPa3avvZTHyrDU4U1BFqBF5P+ex8NmDe+VEAnjNOIypnnMQnJzHrEMT8CqHPctL2rND90emRnpDkH+gkEm3VBrU7s0bGm7n8oZQJhDf38LSiZZYhE7wGm0OVQrGpaM1Zp8DzAEVh082ezYM2895sOAl8qjPL64b4/UH37HWS/1tqCEqUAFPbE6oMD61XU6c7xpq15muTemflyaYrdsW8sYuh9Q3w1krH88N9wepkRDzGVKQvBRxIp/lxP4vyPvdyu7OBgNC33zNX6TFPogqzOu75AwX5VceEY/hSAP4afyh0cJnnNvNfJLi/p+1+b78YhdWvTWu/zEOL+1kzLPaYVne773f+G/lqaOPp3p9QiSbsrMMcyh5oNBZ7vP/MzHT+tKUfHOmwKBmGC+s5O8Ce1LZv4Mf7U/kEsTsNyp6NSZ/Wrl67mcJ5nGRfIXFz6QhMUB5hQtSZh9/+YZuCGJRNdUa/deSEePjUiQRa0S0AbvUmI+EcBAyW0SPk1GKMFzoseXDph4DY70BX3pnnUp/V2k2Y5z9jEa6WtmdLSKV85uJXMDZ82TveClH0wfxNRFZs3tTjtoESjDWQRKCGMf/Jo0MI1MhqIIXG7ZRNzxjiOafRRmfMwWA1l//qKlhRs/GXbPEd7WnrLf3Ao7mUh2dUSR/fr0ct7sPbt+dHv/b5nFbe+2Hej0QpoUSsbAEtP5OTreDPHILrzdOoWXnlrXFO6BCT+jF4E9dAu/j8LGW+SOXjgJaY8W5jJLsFYDFj653PgGGZN3W8FzXlCdp8OpTYaDQDdGWIC/FZIDvtqy7ncAp1bKpcHu0wflrSmjTtqfzZvMJYauEBucmVfZlhBvDmso5jGfkwtIKtlTwVsJo9paorBRZSM4jkgMTDmx9sLPB1ejiYgfUsxJhnyWq8qjYNoS0Y1IbbS30oLX1eLsHJQY3eQ+GHEmjvUOhAzY7HKIXzvPtDnyuyE492T12MMLY94JtSFaY2EXQpxYtmteZQYUPQCNFH599OO7D4Q2JALdn6fLvhOOb524vSCBx4MVmtLqh16X+NnwAQxSuxyQiC4rq4lQ2Nc535tqyOTFKgEB1r12GvTo/S95WazoPjSjqW1A000w8NvdVX8PNahCSOBtAsOJ8mDeUsbuRJasjiDPkdGD5I20TKiMIVUc4EWDLDXVWHU96DitsD9maf7jQebZ2Cwu5oYQohEgVNZlcLBbwHeNJ/Q4oX55q4ffuky809ATmLnLmzWnTuFtQKxW4zO3wP0mQmjFtxvM9SJmGpvVnX4nmumURTOlJEcfv8jE37nIp9Qnx4xCGAnDXgttJhDSWp0E42wxLrvVZ+DZGzl7GVhAb3dFxHfPmQjLoOK3/MuoJb+xOU8dK70TlxRkvrdmybHb6UcLv0x/8fFBm/B8P+CVQCs+Iur/FU4L7OnUeopRUjs26ZvVAfJoB2Otn/X/x6QvItQsIiUYQnlezH0o6DEHtWiHAG9qLiNPNDFdEKf6R9fbeMolLFuEgcQVI6KGSQyKKmPgLdQ2PEhU+Pj8vBS2vy1fS1OCzNuiYn58D7+2nyM+BlQK8s67OvM1czOawgYY5cCyIvsMcMA6AdWyAbtZR1TqCUpIqKizOXirrXczv+3AWsRtYKw4KjEgbizuGy1jVByIPz3pVzuBtvjDvRv9yq+zGnUCP7quQJomfYOq1AXOmRdZMe5EOav3TBcDK7wApl9IQ10xeXlZpPbuI4XPivkTKh2Ot8B96440oH5HpCZU5FrUznOzjHbIXcn3qaJCAjdoZRvnKztXH3mtxXn9wQuHyOX8PlyU4Z2+am3W9EnCLjywOKrf/3dUkmGcIvKTq+mD5knxU4l50t14ecz49kwbsdFcIRu6PwLWq+f96SuW9lKm0XpGmtWo+ui9EncvqfjAqlQO4po2KNzIlij72DPYvioS7FZnHyBXaE9Ln8UeYfPiq7zl5DfVoXZp6vh2JrP6bPjKe9VDwpI8Ri9xkmQDVbSQ+CpmJrhlp9NEYESi+Nq9PDJTYNpDgP7WBi28U6AbZH4Ppc3xq40K/FPHF1DNnYg5VnMMFC/906hsJDOIk62IDqIH396tOLPPEWgeWSXEA2B1plnlFofIzLv/NG1/NZHPAsM+G6HtUwgKALR31iNPkOt5FwyoQQhobV5eQ1tPh2A5i/HavKUcFIqXemIWOg1Z+d29PdVi2xx7jPaRj7/jmbvrDg9Rs4bpPHlYYuNdh06r/8gVj4KKMrWhoD/ZP7PaDn+pR1PCYbWlJnnlv1NB8s6Ka2XjCWNOlg+ezBCxjPFaQEMEVx6IcOZ7cp8lsu6c/ZUmrxYqyRG0t945di8eVxAUmmXG4YjaL5H/h/cl/u0q+fYZo7FOhzX2u/ZLFEM72hdXb9ym5i0VomFChhzbIReNr4ZurEXEsJFnfJgP+4vYfn3Ah9oYKChFo02Ed2uUaOFRXSPsl6Mx11qAsokeD2QDXmkssDg5gbuhy76SSbfW5Q4H/CKfs1R9AFgYrZ5adXNXFlozgSo7ucC+J+FpMuzzMryJ58SmATtKSiBDaCzS2rb52lblTLkk3q1YL27qqHQLUCD3g1D/yTHh6+kNugu4g/reXMdLMzjmwtTN7vVba4ixssI2MOeNA5J3mJTd/POffYGLs4dAAGOx7UdW+ymdgV9RPWq592ybpZo1/mBSemgPIlv5QivEoheUloc1tC9xFqgZZfKI0t6hXjGkrW0xXpSSbgw0eo2y2cnEHXydVfskVxJm6PsaZ+Dctu2TMG6+phKNzutBCoIC2fIz2bNtUwKFNFYsmdQs47+nr5My+k+lHdzRQRxdkvwCv5DoXxeRh8xVgwiNG5mnFxbBnwzYlb4T3iK4Q03jMrnm80jDA3LH7GjB1dtX7bh8+OBje3xarJdgVpj1W6uBJwXrC0oPRICEuCW9rpUsJaJRKF8JM7ks10Uw172NcsiGIB0HNQT+XZln+aUGH4LycKiAQvvQpd34K9+kNCqDVIpZahLbqY1+enEX7BujSju+CMj0B91GMERpDk9TTnW6K1afj6f+WRIPWhwWYrobP9xQ5icAXJhhAp0lnZnFAul8uzaNQgWsdgNq7MVdvkLN7ND9jrqkXpsscnQ50nvbV4t3yhs5tbeuKe47oSJ5NLHhKPp+MokUX7B6eGWZCz5V0soU97/0IWWgY4SmANAqgNgz2fIwAp+F/+hwshpMzQpOvCyQU2RCjOFfLYFkTNx/uWV3uGEU9TVxoHTyBRyu1jY6qbwJWd9mLcbjxWBdvyZhYgFaF+eNWdEjt2YnPeWw+SIwM8NicNHl9w5VgLnaiwu3f8lhf7phB6GJYulda+037BDTOuSdVZkEHsMCMRFLISMxSHQDI2W/z82AmwKutPGpmzwEe7xowoVFi6/PpEh3quSR+KGH4a7i9uOevzY02orlipWuyP82qWUFnbdGFysVaq0RVTR7JLbvwlVp+8irEXbZVMjkASP5J6JWn8d24ykHOfYWcoEFxG6ioPfJK+EE27z+4a+fqSku2S6n43AM7yQYrhZ8m76osYLTfh/+IWPeCP7zh9YVH1Ed4Qtvy84w1ZyQDPxaQzrq+N9PL/GByRbn3T2tR93MbT3qXiPpUOXNwtP5lvjK86HXbxWsJ8kfAx8oUz1SYdZB5fjtJ9o6dXyiohFfZ3OmT/q6/4MC1MzG5vPI4ZCsp9u3UxAtlR3kQp/Ga8IUotLNnaifvPvRB9W+ygjIxKsZ0VJ/xO3YlEgsIU3EFPcP9e3GEwQJeXkEHYYS/CZaQrqcqDbBtsOQuuP+0YVo5HOlpzXnMgJF6KpYMhrsq79U+q+Q/sRiFwsMoNwfDM5WXk6aPAFQ3AecAtNzP+RlKZjIKFtNgWilxg4zArSseEOO6WEh7f/13LdYrxGN5OisVPD/nNnCnHVaQr20j7R/oy3NIXntYZOQdm+kT4AUC75yZRUleyeuTaHmWHtHCv3h4U0kofMdOqQulIIXtTND3KCJW6trRTNeXNRYsqdN8An1MpqTiHv1NJscgyjOotdZKMWVIsd2S8PD7/q5kQzVhNgSQuy9p+sewRfEc1JEEoL2hWw0DuFsvZJOM/rB2esAEIVtdws4/jeg2xoY3MXZziNV63sYvV220YHXaVXIcAMj/r2rjV/rQBRauMnfWjw2XSYB5s2wKKdfeuPqivGEatt4YVjIomv9XE+LtLFOEXDyIOX3AKS9xCsg7VlNtOX2/ZE1tnGK8MvhFmvllBZ5+6QI3h9SoT9dA3q9t+6PTy7WPaPejraRhtce2cqosu1gsjzfWLQtRnvfbC7SHHWHNRt/bLLt/xQctSjPti0PoX0lL+qmrp7h5ppAz0HeAlWhAxS8SwuVl+1Co+rbljKCqZgJkbXg5NAM8xKb4fei/c3KxsHPi2o9FXn6Wod5SvbplGXzLtMBHYQJ6rP0J/VCMjZ7CO/idTtnyWEmIHwaRWx4DWrawHwvoZ5hHrgGfKWJnAmFDQYLPDyAl39lJAs3F8v95+G9HLNCgGgWoJ7QoVueFxjrMn9gDBhqUgj4hvTQaLdUOhlbpCaXsUCdBalyImg5p+wv7wSSt3OxgHekiMTzf06regyPVDuav9cwyzow01smFtrXjHWZ79VMmHBTyRv08LqxxYHIcw5WFmD3qfFksDZWDOFnzmZmNY0NWmSoGKqUlyAzTmLnF/l19LnEH1teFz4/c1tHS/NoU+obwmTXU3PRqraqYK0Zex8XyoZDie2c+8ul9OuqBYOT3reNGxtmc3rNraYWIebP9pU8P+zq0MAlHOqZQ/f3Nb/SghsJP27mXZiUShJo566vvKAfUFDVM+5bFmVaqzuF4Vk37i+s4HXbOd+IOpuUG3pJGDgJ90snw0Y4I+gnIXGARP6MVbAaJg3MkXoQCTp+2AHZT0OOVpQLZDCH93azQIxCyKhmy1UOqZUBViufUeCElEvkcww7wACgusrl1f6n0L6ZDpVGreDeb+XFVeekJ6dM5VVtajSJAEFPvKs5w3YcEjcfqeMO9QDDkJyu0pzsJGO5J4QAyxr0ToO+2xlrqdDY1YlmQ2NWJZkNjViWZDY1YlmQ2NWJZkNjViWZDY1YlmQ2NWJZkNjViWYn8yBKlDWov7VLEdRKfPpDJNVKYH0i+wOLn1wMsrTOHQ35aOp8hxagHyU/2VkVH0Adn+Td/kvyC0Sf7NzVApBWI4vWOui2CgyTvW3a54i+Md0aQroWDvWs6zOzjXaZtBlo/8i4jfDTXpDCB/w10BHI/yz8v3JTAtQ4a9xWsd3zHzR36cSDq46h+62KjgU7k51ASVDwpwtJitc9SrT8yUwkyfax9ysfPVEXYvyg9iC25R+qDpk/j+U4OzC8GFSERKis5xthGbapdSMjkpfZrpxFad7+3Xc/XoQqDXldnzZ3x9Z9iQ30eQJEQOPCxPBkAiDozI7UDKnssAd/X61Yu8DU5X/07Re7bypj/H/jWi/0FG5p9Q7LEi/iW+aWUYkL2JXOoaq/2s4rb75z+WJ82PHFvFld1z5s7WMmdzCnVe4+anXttkIv7DhGvYsEtYf/pEHjcL4EkK9bxsP50bWx8xXZJ0u6WWaO9tcrEsSXugcekz5ypTTPU/0qPbrX9NuQEf/MWEyOzxiNW7n/vsI9YJBmNNv6P5/qTPE9uZ2Q+HFAXqK0OaZxVjtgJgeeyIyOKlMHx6PAVxUf0weg3Ed0BHVL37Z2lFYkIViXdqY58wN/ujcJFUwLATRYtfr0I9Cc1C0Lo1vPk7OqObNpgaTMierXLu4DsyfsLyTXy7OcpvoHumHTw8u5aOfXvOZrTbNjNzuaKqsh39kfR21D4uVJe+CzS06iailHLtxjoV2k1PaJAhOBYcDnZYewnu2tCy6baaJAHuwMSJiWeAMdjEU+vTP4wjzNVB95nfyhWNYmWmq+mU2nHYXZyLqKMaSp4I3HP+k4vKHpzlqG1xqeJtHK+1x1gfp8zW/gCMpFBXIRsqY/JDBh/5vvcVdR9nruIcfRpbEiqUYD2h/jzu1AEKwl5/gHAyVtvBd8J1Hhs+zSA3fk87w/yraxU1ADQvppLMAttBYzcobJwdxv+VC2GJcf7oN34+u+2GtGXOzGGbFBr+iK5J108ZUulVTXpV5AfZvXBqaADZLBUuAOEr6zs1w2zYJU/I3FmQT/6i/S5T30f65+hZ6/lXgQVcEBRqd8rQjSWp6ngR14U/tNFswJrshevFfW5/3DwFxiggas9dZfJPsTv71ZhP812NKHkYX6Kjel6A/2+dyGvGsU+zZ2YkP8xlecz7Bo91kDJzIxUjMLYfS3HhP+ZsMiYLUW/322XmRVqMUeLLaj8jZORxL8vrcOHy59W8KIg0yjBy2XLRX5P7Ie9Sr1f9KqLUVmGRk0A96GL3u/7o/cTyJ4RWdC5c8AfrYfI/ByJLO72eCkRSz9XrG7JoP7NC59/m8MRy1NE9HGzRu/uQe9ZcAPaWin+rxO69+tLhVP+r29AOaqqxBrEWOSW/s8ThfppfG3yE7H2aJkJqwEUO7bjwTEU7EKiiiPNmLcJBNjxvh8lpdzoLjh8Y5Cd+Z1mipRbpWt5hYhPxPysqlNkUAqtUGP2r/4v1gVaYM0ccReFOJSq2Kth4G89JK+iNgcqkKA+Vylh9mWz427hkeiNLO+lOojxk7WWmj2snQCy/jgT2ash3tDMSKoVcPHzeL9JTMr0EJWrJA4tUZ/xbE2bAqBbhRC/1FNoJ9Y106mVe7AgA/8Lq1UPLfj/aVkp58myCmew3jXZ0/wCv+uMR17aWQU/zTBfxIr28ZGce4zVDXTfMchNhS1bQv5sGwOkgc++2NMbu3byHH2142xDifIpA1zC9osxHCzP9LxHtlhC/kt/2KWaUL6Om7b7wuJn8Z9qTmxckxJO3hakIINs/g/f9e+7NjsShonDmfNj5xtZtxGTH/MPC9dbnfDTUVz5OwR+LocTfuUxeNyskpiCA4IC7n34oHm+L1LHiy9q3/PDbM8YjeAaqEHkNYdUe2uLrzzTGXh4mJRQwTlHhjZPGPOUn3Iv4zb8Uhlsvo9jv7Vr7RJynYOdeQMIb/uPFsXCF6Ok6JH3zRbws/tRMuD0o7dvKVC6Y1l0q4KteGCY5CMfOd8/Y+XCtoOsviw/NfKk32044zI7bqeMRztIaLMEuwwc4k0OZPPhElIKwh6c0r629xs5AMo8t3LS/1TI1ZB49bAGZB8lXHiDoXT/wee7fw6QfYxteumvhJFwGg8ywqOv2dM5sQomKs0Z0wsfNU2mDVZ9CNFQR8gQrpPVLV36M0xpPTfHYZX8tr9aF3yWEA0UABwxiPH7i7dIpU5/gx9DKdzStdBYzWdf1OjYkeUxTGvHw4BZXgRBaUMke/KGs71MybjthgHijd9tfFGWTt8ROksYSMvRg4DvReeNXVok0WZn0E/GUxH0SJ37rxM9muhCZh7T1gQ0LH0siDqWEutWR73DntkgtmBoVswHhptpqsQzzku/RTUtP/9DPDbQze8D3IGkr9SvGWshaovEln4gFw64WNZgHMBwM65A/3Fld4foxni2JMQpg7QXiOlAxVq3wxkuLXkrCAqp80GmvFTRQprkMyrtt8uLRQ6VdLdv2JGhuhTGPwbOcqDu+3p8/wXKcAQApf7LsZCxQe6vxQWooReLQXAjX8vUqJY1hGUHxE0/as3kBJIEsmvwXGQimspEvJ3fSpo/zgQN9oeOSU9Xbr3mTo4mz7dLOSY6JusfxMUElXoXQex/3LjwRbaEDa4oiyv6Hkb+SnLQbIV9+Zf0ifHn9uTUXeyY2/9MPovudoaFt8nKTkAxfye7m1LisDHpYc7/rLozhaW//W0NByi7zf8M+gQIfO6Nz9jsXWSsPAvVO1nLmlcB+/dMPRgqRGduMkoNyu5M5m5dFm4OsKHphBIxNqHkwpQoC2wqIh+gGo6232M0B4CSO0kH81M1QkGo0hfC8MKianxDW1Gj2V0nmVfu06epN76n8bL3bzbD7A/jFHiHBb1yoVwysPz87OsH7HiLFhcZUBUXbQHahuPGRt9oJlC/6R31iKf9XQ0909R1P+AeH1teXHaB9mUfzoctKm0NTwMNlwrptIBOePlii13RiArvlSLA3n6+6JdK9wkWaA7FTuVDQwUjh18Sgrtj8jOUc/UQxhN+BHGbxsTZJZizTrYKXgm0Gf78mvzzOJQ3DTPwBx1JUK++rhKejXmWfcKIoXuPPB9SZLLe4yg6K1APNbFuiqsXKEh76SiOPJe6L5d8EmsUVA0TNJe7oIT/uXxeXHJE5oj5KP8YJz9PvMutfiZiziQMo2oCuv+UWioyMmrfSMLE6XYwKgZoEz6IvHThFNQ/BzoN0htjDQ3I0PBIxWGtxhzrbV+6PI/zTL2BBFZHT1bmiwwVX+hovWD30JMvqAva9QsHHCtPTYQzjS8zTrUz73YhV22FX9BSAdX7yVaflBiEVem7cvixZW80S0XMz0eoGKteS0ATHq/mnQcdPrK0LT1cHe97MRZM2Q01Ybz5egBs5gaPqbtto5yX98OMLoCSfcezNc0VRJ7csuZm8aaIiQZ834JN81NkbHZZ8hhVE37aeOlOD8twd8RAJMK0mdMc+RhbKVvPUWTlqWQ+QZxVKyWDO8aVy1BWvmtUWuVm/aEVsFWYD6uABt7qbVrRez0QoHsik6e7DIf7jZ/TVdXySd2sHBVLRaeIPOi4IA5FJ/NvJuWSFJ2ut9av0lG9eTi7Bb2MTQPDaEz6WMlzzygIOFtTBgxGueKZi+jCcG7yELpMA0s8MbDn0+5NA9jB73VJ3ftQj/1UyXehtcFQanPaXpyAfRkr1CMRsy6ly7Y/IzYvNu/pC2ELgPflPhlLUcB4+WxtP4w4diIC1scIW7HudklJB/LMP9bfgQTAYSXTnKfTrYeHxkByiByEdDai1QDo9TA2HPh/uy+icnDlLjHsisRD6Hq6tw4zpWpuEYpZ6vB54bY1XEbgeTyn7Ax41IDtwAgTjC+Npz/j8a/Fh0JmceKe7vR/PKU1HVnTT5NZxUeVgq9zpWcS4Jg7sJ3pqSlml+BPL1sPeKEqCfzBycx/4U7/0wYxQV8zw/n5ZoSiJt8mKpaQq/vK8JSZq4aQvMXwTcTD/xa4BdERuZ1cQDVEDpwSM4ZT7iJZK2O4X9YFiJOlFYSjQ3MIVkOpFMC1j20IuIPnJsM9Kq5Fz3ZevDVMicKs8/n1Q8Qy7NI4ieLePLYE8Uu5o0d4j/uplQ+wMh0qo4s8BVNwopyKxcgLjkBgsZVbRmuSBgEqm2HCFInwOafoFqCrkP6Hku3NpFYpPYcFRQpKepn2fId+eTDwfZ9gITO3ILS+ywxqWpBPscKTgOZ6jK4js/Z2Dmrelpr+w9UCUi2PwK+8Uxh856cBvY+MHUhZqdRMNZkaFSNfYrd4UBbfKMirfmo43ifPWAzUWvz6g8lfiRV47gV9qak8wXzmXb5lu8PAn5UTCN7KZqa/RV2scAlFRwcc0jdwIvxzyJqg3f7sZIgMW5LTU7DIDKVoi0n7ShvAru8YFFLTUxR+fxLg66cJ5/kMKLviMF52BVxG5hSsh6qno5d4HKJhuEwgT/ZygJUdcTDAY1TUf0dOSYV9W/698wTzV7l1ZUzELADnK2ma/0bagOSYB+wn9IGTLbyYTeSno2V4qzlH+3tPxJnXUzb6tG4cMUktj5MmS+1m/1ArUh29OWeh9xXZfBIfb2Li+yX+6ZDuOCFdm97Jf7pkO44IV2b3sl/umQ7jghXZveyX+6ZDuOCFdm966h/qL3slyirpkO44IVkHfqOyWppcn6KumQ7jeiAA)

cool. co dal? jdu pustit freda

---

# claude response

Vidím to na screenshotu – funguje to (`Cell 5 of 14`, revenue data se pěkně zobrazují). Fundamentals a insider data máš ověřená.

## Než pustíš FRED – rychlá kontrola

1. Máš v `config/secrets.env` (ne `.example`) řádek `FRED_API_KEY=tvůj_klíč`?
2. Přepsal jsi `src/ingestion/fred.py` tím souborem, co jsem poslal? (stejná past jako u SEC EDGAR – zkontroluj `Get-Content src\ingestion\fred.py | Measure-Object -Line`, mělo by být ~70 řádků)

Pokud obojí sedí:
```powershell
python -m src.ingestion.fred
```

## Co čekat za výstup

Mělo by naskákat něco jako:
```
DGS10: staženo XXXX pozorování.
CPIAUCSL: staženo XXX pozorování.
UNRATE: staženo XXX pozorování.
```
A v `data/raw/fred/` tři parquet soubory. Makro data budou mnohem řidší než OHLCV (denní/měsíční hodnoty místo hodinových), to je normální – FRED řady jako CPI vychází jen jednou měsíčně.

## Co pak

1. **Git commit checkpoint** – máš teď 3 funkční zdroje dat (OHLCV, SEC, FRED), je to dobrý bod se zastavit a commitnout (`git add .`, `git commit -m "add sec edgar and fred fetchers"`).
2. Podle plánu je pak na řadě **Senate/House Stock Watcher** (kongresmani) – je to jednoduché (jen CSV/JSON, žádný klíč), takže rychlý čtvrtý zdroj.
3. Ale upřímně – po FREDu bych zvážil **pauzu ve sbírání dalších zdrojů** a přesun k prvnímu skutečnému testu hypotézy (tu "výzkumnou smyčku", co jsme kreslili dřív) na tom, co už máš. Máš teď reálně dost na první experiment (např. "koreluje insider buying s budoucím výnosem u AAPL/MSFT?"), a je to přesně ten moment, kdy by ses jako perfekcionista mohl nechat vlákat do "ještě jeden zdroj dat" donekonečna místo skutečného testování.

Spusť FRED a dej vědět výsledek – pak se rozhodneme, jestli jedeš Senate Stock Watcher, nebo skočíme rovnou na první hypotézu.

---

# you asked

message time: 2026-08-16 14:34:56

(.venv) PS C:\HERMES_FENIX> python -m src.ingestion.fred
2026-08-16 14:29:35,663 [INFO] __main__: DGS10: staženo 16858 pozorovani.
2026-08-16 14:29:37,422 [INFO] __main__: CPIAUCSL: staženo 955 pozorovani.
2026-08-16 14:29:39,456 [INFO] __main__: UNRATE: staženo 943 pozorovani.
(.venv) PS C:\HERMES_FENIX>  (souhlasim, pojdme na nejake vypocty) (.venv) PS C:\HERMES_FENIX> git add ., git commit -m "add sec edgar and fred fetchers"
fatal: not a git repository (or any of the parent directories): .git
(.venv) PS C:\HERMES_FENIX> na git jsem jeste nic nedaval. asi mam udelat novy repo na uctu ze? mam student ucet s vyhodami jako copilot apod.

---

# claude response

## Git setup

Nejdřív komentář k `git add ., git commit...` – to bylo napsané jako dva příkazy oddělené čárkou, PowerShell to bere jako jeden neplatný příkaz. Musí to být dva oddělené řádky. A ano, potřebuješ `git init` jako úplně první krok, než cokoliv jiného – zatím jsi měl jen soubory na disku, žádné Git sledování.

Student účet je super, GitHub Student Pack ti navíc dá **neomezené private repo zdarma** (i normálně jsou dneska private repa na GitHubu zdarma, ale pack přidá i Copilot, Codespaces apod.). Doporučuju **private** repo – nejde o utajení kódu, ale o to, že v projektu časem budou i detaily o tvém tradingu, který nemusíš mít veřejně navěšený.

## První výpočet – s jedním upozorněním

Chtěl bych rovnou otestovat "insider buying předpovídá výnos", ale je tu zádrhel: **Form 4 data, co teď máš, obsahují jen "insider něco podal" (datum + typ formuláře), ne jestli šlo o nákup nebo prodej** – to je schované v XML uvnitř filingu, což jsme zatím neparsovali. Testovat hypotézu s neúplnou informací by ti dalo nesmyslný/zavádějící výsledek.

Takže začneme jednodušší, ale metodologicky správnou zahřívačkou jen na OHLCV datech, co bezpečně máš celá: **testujeme momentum vs. mean-reversion** – predikuje minulý hodinový výnos ten příští? Je to klasický první test v kvantu a hlavně ti to postaví **kostru výzkumného procesu** (feature → statistický test → interpretace), kterou pak jen znovu použijeme, až doděláme detailní insider parsing.

**Než spustíš:** budeš potřebovat scipy: `pip install scipy`

Ulož jako `src/research/test_momentum_hypothesis.py` a spouštěj buňky popořadě.

**Jak číst výsledek:**
- **Pearson/Spearman korelace** – číslo mezi -1 a 1. Blízko 0 (typicky do ±0.05) je u finančních dat úplně normální, trh je efektivní a jednoduché vzorce jsou vzácné.
- **p-hodnota** – jestli je pod 0.05, výsledek pravděpodobně není náhoda (ale s tisíci pozorováními i velmi malá korelace vyjde "statisticky významná", proto se dívej hlavně na **velikost** korelace, ne jen na p-hodnotu).
- **Kvintilová tabulka** – nejpraktičtější pohled: kdyby feature měl reálnou predikční sílu, viděl bys u ní jasný **trend** (Q1 nejnižší průměrný výnos → Q5 nejvyšší = momentum, nebo naopak = mean-reversion). Pokud jsou čísla napříč kvintily podobná/bez trendu, feature nemá alfu.

Ať vyjde cokoliv, je to v pořádku výsledek – tohle je přesně ten "test hypotézy" krok z diagramu, co jsme kreslili. Pošli mi čísla, co ti vyjdou, rozebereme je spolu a pak se pustíme do parsování Form 4 detailů (kdo kolik nakoupil), ať můžeš otestovat i tu insider hypotézu pořádně.

---

# you asked

message time: 2026-08-16 14:39:06

(.venv) PS C:\HERMES_FENIX> git add ., git commit -m "add sec edgar and fred fetchers"
fatal: not a git repository (or any of the parent directories): .git
(.venv) PS C:\HERMES_FENIX> git init
Initialized empty Git repository in C:/HERMES_FENIX/.git/
(.venv) PS C:\HERMES_FENIX> git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore
        IDEAS_BACKLOG.md
        README.md
        config/
        data/
        je mi 17. chci vybudovat aos tradin.txt
        pyproject.toml
        scripts/
        src/
        tests/

nothing added to commit but untracked files present (use "git add" to track)
(.venv) PS C:\HERMES_FENIX> git add
Nothing specified, nothing added.
hint: Maybe you wanted to say 'git add .'?
hint: Disable this message with "git config set advice.addEmptyPathspec false"
(.venv) PS C:\HERMES_FENIX> git add .
warning: in the working copy of '.gitignore', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'IDEAS_BACKLOG.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'config/settings.yaml', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'pyproject.toml', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/backup.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'scripts/health_check.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/backtest/__init__.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/execution/__init__.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/base.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/fred.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/news_sentiment.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/ohlcv.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/sec_edgar.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/weather.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/ingestion/wildfires.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/research/__init__.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/research/explore_data.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/risk/__init__.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/strategy/__init__.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/utils/config.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/utils/logging_config.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_ohlcv.py', LF will be replaced by CRLF the next time Git touches it
(.venv) PS C:\HERMES_FENIX> git commit -m
error: switch `m' requires a value
(.venv) PS C:\HERMES_FENIX> git commit -m "initial commit: ohlcv + sec edgar + fred fetchers"
[master (root-commit) 2d177f4] initial commit: ohlcv + sec edgar + fred fetchers
 31 files changed, 796 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 IDEAS_BACKLOG.md
 create mode 100644 README.md
 create mode 100644 config/settings.yaml
 create mode 100644 data/cache/.gitkeep
 create mode 100644 data/processed/.gitkeep
 create mode 100644 data/raw/.gitkeep
 create mode 100644 je mi 17. chci vybudovat aos tradin.txt
 create mode 100644 pyproject.toml
 create mode 100644 scripts/backup.py
 create mode 100644 scripts/health_check.py
 create mode 100644 src/__init__.py
 create mode 100644 src/backtest/__init__.py
 create mode 100644 src/execution/__init__.py
 create mode 100644 src/ingestion/__init__.py
 create mode 100644 src/ingestion/base.py
 create mode 100644 src/ingestion/fred.py
 create mode 100644 src/ingestion/news_sentiment.py
 create mode 100644 src/ingestion/ohlcv.py
 create mode 100644 src/ingestion/sec_edgar.py
 create mode 100644 src/ingestion/weather.py
 create mode 100644 src/ingestion/wildfires.py
 create mode 100644 src/research/__init__.py
 create mode 100644 src/research/explore_data.py
 create mode 100644 src/risk/__init__.py
 create mode 100644 src/strategy/__init__.py
 create mode 100644 src/utils/__init__.py
 create mode 100644 src/utils/config.py
 create mode 100644 src/utils/logging_config.py
 create mode 100644 tests/__init__.py
 create mode 100644 tests/test_ohlcv.py
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Commit proběhl, ale všiml jsem si jedné věci, kterou stojí za to hned vyřešit, než to pushneš na GitHub.

## Odstraň omylem zachycený soubor

Vidím v seznamu `create mode 100644 je mi 17. chci vybudovat aos tradin.txt` – vypadá to jako poznámka/kopie tvé první zprávy, co se ti nějak povalovala přímo ve složce projektu. Do repozitáře evidentně nepatří (osobní info, netýká se kódu). Protože jsi to **ještě nepushnul na GitHub**, můžeš to čistě odstranit z historie, ne jen smazat v dalším commitu:

```powershell
git rm --cached "je mi 17. chci vybudovat aos tradin.txt"
git commit --amend -m "initial commit: ohlcv + sec edgar + fred fetchers"
```

`--cached` smaže soubor jen z Gitu, ne z disku (klidně ho tam nech nebo smaž ručně, to už je jedno). `--amend` přepíše poslední commit, jako by tam ten soubor nikdy nebyl – funguje to jen proto, že to není zveřejněné nikde jinde.

Ty CRLF/LF warningy klidně ignoruj, to je jen Windows vs. Unix konce řádků, nic to nerozbíjí.

## Pak pokračuj na GitHub

Zbytek kroků z dřívějška (vytvoření repa na GitHub, `git remote add origin ...`, `git branch -M main`, `git push -u origin main`).

Po pushnutí zpátky na `test_momentum_hypothesis.py` – to je teď hlavní věc, na kterou se soustředíme.

---

# you asked

message time: 2026-08-16 14:47:28

![image](data:image/webp;base64,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)

smazal jsem to, byla to jen poznamka na prompt pro tebe... ted zakladam repo:

---

# claude response

Nastavení vypadá přesně správně – **README off, žádný .gitignore, žádná licence** je přesně to, co chceš (README a .gitignore už máš lokálně, druhá kopie z GitHubu by akorát dělala konflikt při pushi). Tu "Jumpstart s Copilotem" sekci klidně přeskoč, nepotřebuješ ji.

Než klikneš na **Create repository** (scroll nahoru), zkontroluj:
- Repository name vyplněné (např. `hermes-fenix`)
- Zaškrtnuté **Private**

Po vytvoření ti GitHub ukáže stránku s příkazy – hledej sekci **"…or push an existing repository from the command line"** (ne tu první s `git init`, tu už máš hotovou). Bude vypadat takhle (s tvým skutečným URL):

```powershell
git remote add origin https://github.com/tvoje-jmeno/hermes-fenix.git
git branch -M main
git push -u origin main
```

**Jedna věc před pushem** – ověř, že ten `.txt` soubor skutečně zmizel i z Gitu, ne jen z disku:

```powershell
git status
```

Pokud tam pořád visí jako untracked/staged, ještě před push udělej:
```powershell
git rm --cached "je mi 17. chci vybudovat aos tradin.txt"
git commit --amend --no-edit
```

Pak spusť ty tři příkazy výše a dej vědět, jak to dopadlo – a pak zpátky na `test_momentum_hypothesis.py`.

---

# you asked

message time: 2026-08-16 14:51:20

create mode 100644 tests/test_ohlcv.py
(.venv) PS C:\HERMES_FENIX> git remote add origin https://github.com/Dubulinus/Hermes.git
(.venv) PS C:\HERMES_FENIX> git branch -M main
(.venv) PS C:\HERMES_FENIX> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
(.venv) PS C:\HERMES_FENIX> git remote add origin https://github.com/Dubulinus/Hermes.git                                         
error: remote origin already exists.
(.venv) PS C:\HERMES_FENIX> git branch -M main
(.venv) PS C:\HERMES_FENIX> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
(.venv) PS C:\HERMES_FENIX>

---

# claude response

"Repository not found" většinou znamená jednu ze dvou věcí – buď repo na GitHubu ve skutečnosti ještě nevzniklo (zůstal jsi na konfigurační stránce a nikdy jsi neklikl finální **"Create repository"** tlačítko), nebo je problém s přihlášením při pushi.

## Krok 1: ověř, že repo existuje

Otevři v prohlížeči přímo:
```
https://github.com/Dubulinus/Hermes
```

**Pokud dostaneš 404** – repo neexistuje, vrať se na github.com/new, projdi to znovu a tentokrát nezapomeň úplně nahoře/dole kliknout zelené **"Create repository"** tlačítko (podle screenshotu jsi byl ještě v nastavení, ne po odeslání).

**Pokud repo vidíš** (a je prázdné) – pak je problém autentizace při pushi. Zkus:
```powershell
git push -u origin main
```
znovu – mělo by se otevřít okno prohlížeče s přihlášením přes GitHub (Git Credential Manager). Pokud se nic neotevřelo napoprvé, může to být tím, že credential manager necachoval přihlášení správně.

Napiš, co uvidíš po otevření té URL v prohlížeči, a půjdeme dál podle toho.

---

# you asked

message time: 2026-08-16 14:52:37

je to private mozna je to tim? nvm

---

# claude response

Ano, přesně to je typický důvod – **soukromé repo vrací "not found" místo "permission denied"** i legitimnímu vlastníkovi, pokud Git při pushi nemá platné přihlášení (GitHub to dělá záměrně, aby nepotvrzoval existenci soukromých repozitářů cizím lidem).

## Řešení

```powershell
git push -u origin main
```

Spusť to znovu a sleduj, jestli se **neotevře okno prohlížeče/přihlašovací okno** (Git Credential Manager na Windows by to měl udělat automaticky). Pokud se objeví, přihlas se svým GitHub účtem a mělo by to pak projít.

**Pokud se nic neotevře** (Windows credential manager někdy "zapomene", že se má zeptat), vyčisti uložené (možná špatné/staré) přihlašovací údaje:

```powershell
git credential-manager reject https://github.com
```

a zkus push znovu – tentokrát by se přihlašovací okno mělo objevit jistě.

**Alternativa, kdyby credential manager dělal potíže** – GitHub teď striktně vyžaduje **Personal Access Token** místo hesla u HTTPS pushů:
1. github.com → klikni na svůj avatar → Settings → úplně dole **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**
2. Zaškrtni scope `repo`, vygeneruj, **zkopíruj token** (zobrazí se jen jednou)
3. Při dalším `git push` když se zeptá na heslo, **vlož token místo hesla**

Zkus nejdřív tu jednodušší variantu (prostě spustit push znovu a přihlásit se přes vyskakovací okno) a napiš, co se stane.

---

# you asked

message time: 2026-08-16 14:53:25

(.venv) PS C:\HERMES_FENIX> git remote add origin https://github.com/Dubulinus/Hermes.git
(.venv) PS C:\HERMES_FENIX> git branch -M main
(.venv) PS C:\HERMES_FENIX> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
(.venv) PS C:\HERMES_FENIX> git remote add origin https://github.com/Dubulinus/Hermes.git                                         
error: remote origin already exists.
(.venv) PS C:\HERMES_FENIX> git branch -M main
(.venv) PS C:\HERMES_FENIX> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
(.venv) PS C:\HERMES_FENIX> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
(.venv) PS C:\HERMES_FENIX> git credential-manager reject https://github.com
Required command was not provided.
Unrecognized command or argument 'reject'.
Unrecognized command or argument 'https://github.com'.
Description:
Usage:
  git-credential-manager [command] [options]
Options:
  --no-ui         Do not use graphical user interface prompts
  --version       Show version information
  -?, -h, --help  Show help and usage information
Commands:
  get          [Git] Return a stored credential
  store        [Git] Store a credential
  erase        [Git] Erase a stored credential
  configure    Configure Git Credential Manager as the Git credential 
               helper
  unconfigure  Unconfigure Git Credential Manager as the Git credential 
               helper
  diagnose     Run diagnostics and gather logs to diagnose problems with 
               Git Credential Manager
  azure-repos  Commands for interacting with the Azure Repos host provider
  github       Commands for interacting with the GitHub host provider
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Než se pustíme dál do credential manageru, **nejdřív tohle prosím ověř** – je fakt možné, že repo z předminula ve skutečnosti nikdy nevzniklo (na screenshotu jsi byl na konfigurační stránce, ale nepotvrdil jsi mi, že jsi klikl finální "Create repository"):

Otevři v prohlížeči přesně:
```
https://github.com/Dubulinus/Hermes
```

**Co uvidíš?**
- 404 / "This is not the web page you are looking for" → repo neexistuje, musíš ho založit (github.com/new, vyplnit název `Hermes`, Private, a tentokrát opravdu doklikat až na zelené tlačítko dole)
- Vidíš prázdné repo se stránkou "Quick setup" → repo existuje, jde skutečně o přihlášení, pokračuj níž

## Pokud repo existuje – oprava přihlášení

Použij podpříkaz, co ti CLI samo nabídlo v nápovědě:

```powershell
git credential-manager github logout
```

Pak zkus push znovu:
```powershell
git push -u origin main
```

Tentokrát by se mělo otevřít okno prohlížeče s přihlášením ke GitHubu (device flow nebo OAuth). Přihlas se svým účtem Dubulinus a autorizuj.

Napiš mi nejdřív, co ukázala ta URL v prohlížeči – ušetří nám to případně kolo kolem credentialů, pokud je problém jinde.

---

# you asked

message time: 2026-08-16 14:54:37

(.venv) PS C:\HERMES_FENIX> git credential-manager github logout
Required argument missing for command: 'logout'.
Description:
  Remove a GitHub account.
Usage:
  git-credential-manager github logout <account> [options]
Arguments:
  <account>  Account to remove
Options:
  --url <url>     URL of the GitHub instance to target, otherwise use 
                  GitHub.com
  --no-ui         Do not use graphical user interface prompts
  -?, -h, --help  Show help and usage information
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Pojďme na to jinak – místo lovení přesných CLI příkazů (evidentně to chce argument, co teď nemáme) použij GUI, je to spolehlivější:

## Krok 1 – ověř, jestli repo vůbec existuje (tohle je prioritní)

Otevři v prohlížeči: `https://github.com/Dubulinus/Hermes`

Napiš mi, jestli vidíš **404 stránku** (repo neexistuje – musíš ho založit) nebo **prázdné repo s "Quick setup" instrukcemi** (repo existuje, jde o přihlášení).

## Krok 2 – pokud repo existuje, vyčisti uložené přihlášení přes Windows

1. Klikni na **Start** a napiš **"Credential Manager"** (nebo "Správce přihlašovacích údajů"), otevři ho
2. Klikni na **"Windows Credentials"** / "Obecná pověření" (Generic Credentials)
3. Najdi položku obsahující `git:https://github.com` nebo podobně
4. Klikni na ni → **Remove/Odebrat**

Pak zpátky do terminálu:
```powershell
git push -u origin main
```

Tohle by mělo vynutit nové přihlašovací okno v prohlížeči, kde se znovu přihlásíš.

Ale prosím nejdřív ověř Krok 1 – pokud repo neexistuje, celý krok 2 je zbytečný a jen bychom se motali v kruhu.

---

# you asked

message time: 2026-08-16 14:58:48

![image](data:image/webp;base64,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)

2026-08-15 19:34:46.675 [info] [main] Log level: Info
2026-08-15 19:34:46.675 [info] [main] Validating found git in: "C:\Program Files\Git\cmd\git.exe"
2026-08-15 19:34:49.646 [info] [main] Using git "2.53.0.windows.1" from "C:\Program Files\Git\cmd\git.exe"
2026-08-15 19:34:49.646 [info] [Model][doInitialScan] Initial repository scan started
2026-08-15 19:34:49.680 [info] [Model][doInitialScan] Initial repository scan completed - repositories (0), closed repositories (0), parent repositories (0), unsafe repositories (0)
2026-08-15 19:36:40.899 [info] [main] Log level: Info
2026-08-15 19:36:40.900 [info] [main] Validating found git in: "C:\Program Files\Git\cmd\git.exe"
2026-08-15 19:36:40.900 [info] [main] Using git "2.53.0.windows.1" from "C:\Program Files\Git\cmd\git.exe"
2026-08-15 19:36:40.905 [info] [Model][doInitialScan] Initial repository scan started
2026-08-15 19:36:44.997 [info] > git rev-parse --show-toplevel [4735ms]
2026-08-15 19:36:44.997 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:51.940 [info] > git rev-parse --show-toplevel [1612ms]
2026-08-15 19:36:51.941 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:52.884 [info] > git rev-parse --show-toplevel [903ms]
2026-08-15 19:36:52.884 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:53.492 [info] > git rev-parse --show-toplevel [566ms]
2026-08-15 19:36:53.492 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:54.143 [info] > git rev-parse --show-toplevel [613ms]
2026-08-15 19:36:54.144 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:54.654 [info] > git rev-parse --show-toplevel [471ms]
2026-08-15 19:36:54.654 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:55.240 [info] > git rev-parse --show-toplevel [540ms]
2026-08-15 19:36:55.240 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:36:55.249 [info] [Model][doInitialScan] Initial repository scan completed - repositories (0), closed repositories (0), parent repositories (0), unsafe repositories (0)
2026-08-15 19:37:24.197 [info] > git rev-parse --show-toplevel [1460ms]
2026-08-15 19:37:24.197 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 19:42:34.781 [info] > git rev-parse --show-toplevel [182ms]
2026-08-15 19:42:34.781 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:13:32.563 [info] > git rev-parse --show-toplevel [1891ms]
2026-08-15 23:13:32.564 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:13:55.170 [info] > git rev-parse --show-toplevel [1184ms]
2026-08-15 23:13:55.170 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:16:56.549 [info] > git rev-parse --show-toplevel [1537ms]
2026-08-15 23:16:56.550 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:18:31.808 [info] > git rev-parse --show-toplevel [467ms]
2026-08-15 23:18:31.808 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:19:02.480 [info] > git rev-parse --show-toplevel [243ms]
2026-08-15 23:19:02.480 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:19:02.995 [info] > git rev-parse --show-toplevel [487ms]
2026-08-15 23:19:02.995 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:20:40.898 [info] > git rev-parse --show-toplevel [224ms]
2026-08-15 23:20:40.898 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:20:41.312 [info] > git rev-parse --show-toplevel [390ms]
2026-08-15 23:20:41.312 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:27:48.481 [info] > git rev-parse --show-toplevel [1540ms]
2026-08-15 23:27:48.482 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:28:00.064 [info] > git rev-parse --show-toplevel [1077ms]
2026-08-15 23:28:00.064 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:28:19.319 [info] > git rev-parse --show-toplevel [1508ms]
2026-08-15 23:28:19.319 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:28:20.216 [info] > git rev-parse --show-toplevel [848ms]
2026-08-15 23:28:20.216 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:31:54.589 [info] > git rev-parse --show-toplevel [1512ms]
2026-08-15 23:31:54.590 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-15 23:31:55.350 [info] > git rev-parse --show-toplevel [704ms]
2026-08-15 23:31:55.350 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:50:05.519 [info] > git rev-parse --show-toplevel [1448ms]
2026-08-16 13:50:05.519 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:54:58.339 [info] > git rev-parse --show-toplevel [834ms]
2026-08-16 13:54:58.339 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:54:58.917 [info] > git rev-parse --show-toplevel [547ms]
2026-08-16 13:54:58.917 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:55:46.273 [info] > git rev-parse --show-toplevel [247ms]
2026-08-16 13:55:46.273 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:55:46.476 [info] > git rev-parse --show-toplevel [181ms]
2026-08-16 13:55:46.476 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:57:20.413 [info] > git rev-parse --show-toplevel [380ms]
2026-08-16 13:57:20.413 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 13:57:20.676 [info] > git rev-parse --show-toplevel [238ms]
2026-08-16 13:57:20.676 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:01:51.108 [info] > git rev-parse --show-toplevel [342ms]
2026-08-16 14:01:51.108 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:01:51.437 [info] > git rev-parse --show-toplevel [295ms]
2026-08-16 14:01:51.437 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:11:56.045 [info] > git rev-parse --show-toplevel [680ms]
2026-08-16 14:11:56.045 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:12:58.444 [info] > git rev-parse --show-toplevel [3251ms]
2026-08-16 14:12:58.444 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:17:29.831 [info] > git rev-parse --show-toplevel [554ms]
2026-08-16 14:17:29.831 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:19:24.663 [info] > git rev-parse --show-toplevel [596ms]
2026-08-16 14:19:24.663 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:19:41.429 [info] > git rev-parse --show-toplevel [236ms]
2026-08-16 14:19:41.429 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:19:42.504 [info] > git rev-parse --show-toplevel [1048ms]
2026-08-16 14:19:42.504 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:20:00.579 [info] > git rev-parse --show-toplevel [3204ms]
2026-08-16 14:20:00.581 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:20:02.740 [info] > git rev-parse --show-toplevel [1763ms]
2026-08-16 14:20:02.740 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:21:20.973 [info] > git rev-parse --show-toplevel [463ms]
2026-08-16 14:21:20.974 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:21:22.500 [info] > git rev-parse --show-toplevel [638ms]
2026-08-16 14:21:22.500 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:23:14.815 [info] > git rev-parse --show-toplevel [655ms]
2026-08-16 14:23:14.815 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:23:15.435 [info] > git rev-parse --show-toplevel [553ms]
2026-08-16 14:23:15.435 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:23:27.497 [info] > git rev-parse --show-toplevel [657ms]
2026-08-16 14:23:27.497 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:23:27.945 [info] > git rev-parse --show-toplevel [412ms]
2026-08-16 14:23:27.945 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:23:54.690 [info] > git rev-parse --show-toplevel [595ms]
2026-08-16 14:23:54.690 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:24:01.867 [info] > git rev-parse --show-toplevel [348ms]
2026-08-16 14:24:01.867 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:26:30.844 [info] > git rev-parse --show-toplevel [4130ms]
2026-08-16 14:26:30.844 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:26:34.210 [info] > git rev-parse --show-toplevel [3291ms]
2026-08-16 14:26:34.210 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:26:53.442 [info] > git rev-parse --show-toplevel [259ms]
2026-08-16 14:26:53.442 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:26:53.666 [info] > git rev-parse --show-toplevel [197ms]
2026-08-16 14:26:53.666 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:26:53.907 [info] > git rev-parse --show-toplevel [195ms]
2026-08-16 14:26:53.908 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:04.806 [info] > git rev-parse --show-toplevel [250ms]
2026-08-16 14:27:04.806 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:05.056 [info] > git rev-parse --show-toplevel [224ms]
2026-08-16 14:27:05.056 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:05.259 [info] > git rev-parse --show-toplevel [180ms]
2026-08-16 14:27:05.259 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:05.498 [info] > git rev-parse --show-toplevel [218ms]
2026-08-16 14:27:05.498 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:05.707 [info] > git rev-parse --show-toplevel [187ms]
2026-08-16 14:27:05.707 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:06.199 [info] > git rev-parse --show-toplevel [472ms]
2026-08-16 14:27:06.199 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:06.409 [info] > git rev-parse --show-toplevel [189ms]
2026-08-16 14:27:06.409 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:06.599 [info] > git rev-parse --show-toplevel [172ms]
2026-08-16 14:27:06.599 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:06.849 [info] > git rev-parse --show-toplevel [226ms]
2026-08-16 14:27:06.849 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:07.084 [info] > git rev-parse --show-toplevel [214ms]
2026-08-16 14:27:07.084 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:07.316 [info] > git rev-parse --show-toplevel [210ms]
2026-08-16 14:27:07.316 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:12.746 [info] > git rev-parse --show-toplevel [295ms]
2026-08-16 14:27:12.746 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:23.207 [info] > git rev-parse --show-toplevel [333ms]
2026-08-16 14:27:23.207 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:32.028 [info] > git rev-parse --show-toplevel [439ms]
2026-08-16 14:27:32.028 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:27:32.292 [info] > git rev-parse --show-toplevel [224ms]
2026-08-16 14:27:32.293 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:06.686 [info] > git rev-parse --show-toplevel [414ms]
2026-08-16 14:28:06.686 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:07.755 [info] > git rev-parse --show-toplevel [196ms]
2026-08-16 14:28:07.755 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:13.721 [info] > git rev-parse --show-toplevel [277ms]
2026-08-16 14:28:13.721 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:16.724 [info] > git rev-parse --show-toplevel [239ms]
2026-08-16 14:28:16.724 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:17.321 [info] > git rev-parse --show-toplevel [265ms]
2026-08-16 14:28:17.321 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:18.434 [info] > git rev-parse --show-toplevel [310ms]
2026-08-16 14:28:18.434 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:19.194 [info] > git rev-parse --show-toplevel [438ms]
2026-08-16 14:28:19.194 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:29.383 [info] > git rev-parse --show-toplevel [622ms]
2026-08-16 14:28:29.383 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:30.148 [info] > git rev-parse --show-toplevel [247ms]
2026-08-16 14:28:30.148 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:28:37.481 [info] > git rev-parse --show-toplevel [638ms]
2026-08-16 14:28:37.481 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:15.316 [info] > git rev-parse --show-toplevel [302ms]
2026-08-16 14:29:15.316 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:19.438 [info] > git rev-parse --show-toplevel [222ms]
2026-08-16 14:29:19.438 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:28.639 [info] > git rev-parse --show-toplevel [638ms]
2026-08-16 14:29:28.639 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:29.282 [info] > git rev-parse --show-toplevel [607ms]
2026-08-16 14:29:29.282 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:29.859 [info] > git rev-parse --show-toplevel [435ms]
2026-08-16 14:29:29.859 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:32.615 [info] > git rev-parse --show-toplevel [326ms]
2026-08-16 14:29:32.615 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:29:34.294 [info] > git rev-parse --show-toplevel [257ms]
2026-08-16 14:29:34.294 [info] fatal: not a git repository (or any of the parent directories): .git
2026-08-16 14:36:51.501 [info] > git rev-parse --show-toplevel [589ms]
2026-08-16 14:36:51.896 [info] > git rev-parse --git-dir --git-common-dir --show-superproject-working-tree [364ms]
2026-08-16 14:36:51.992 [info] [Model][openRepository] Opened repository (path): c:\HERMES_FENIX
2026-08-16 14:36:51.992 [info] [Model][openRepository] Opened repository (real path): c:\HERMES_FENIX
2026-08-16 14:36:51.992 [info] [Model][openRepository] Opened repository (kind): repository
2026-08-16 14:36:52.247 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:36:52.728 [info] > git config --get commit.template [658ms]
2026-08-16 14:36:52.730 [info] > git config --get --local core.virtualfilesystem [698ms]
2026-08-16 14:36:52.731 [warning] [Git][config] git config failed: Failed to execute git
2026-08-16 14:36:53.529 [info] > git fetch [1540ms]
2026-08-16 14:36:53.568 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [1321ms]
2026-08-16 14:36:53.569 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:36:53.728 [info] > git check-ignore -v -z --stdin [1264ms]
2026-08-16 14:36:53.732 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:36:54.114 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:36:54.183 [info] > git check-ignore -v -z --stdin [1458ms]
2026-08-16 14:36:54.581 [info] > git config --get commit.template [1025ms]
2026-08-16 14:36:54.755 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [1037ms]
2026-08-16 14:36:54.755 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:36:54.758 [error] [GitHistoryProvider][resolveHEADMergeBase] Failed to resolve merge base for master: Error: No such branch: master.
2026-08-16 14:36:54.763 [info] > git config --get commit.template [945ms]
2026-08-16 14:36:54.765 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [982ms]
2026-08-16 14:36:54.765 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:36:54.991 [info] > git show --textconv :src/research/explore_data.py [1058ms]
2026-08-16 14:36:55.085 [info] > git ls-files --stage -- src/research/explore_data.py [1010ms]
2026-08-16 14:36:55.228 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [1115ms]
2026-08-16 14:36:55.229 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:36:55.776 [info] > git hash-object -t tree /dev/null [561ms]
2026-08-16 14:36:55.776 [warning] [GitFileSystemProvider][readFile] File not found - git:/c%3A/HERMES_FENIX/src/research/explore_data.py.git?%7B%22path%22%3A%22c%3A%5C%5CHERMES_FENIX%5C%5Csrc%5C%5Cresearch%5C%5Cexplore_data.py%22%2C%22ref%22%3A%22%22%7D
2026-08-16 14:36:55.778 [info] > git hash-object -t tree /dev/null [644ms]
2026-08-16 14:36:55.778 [warning] [GitFileSystemProvider][stat] File not found - git:/c%3A/HERMES_FENIX/src/research/explore_data.py.git?%7B%22path%22%3A%22c%3A%5C%5CHERMES_FENIX%5C%5Csrc%5C%5Cresearch%5C%5Cexplore_data.py%22%2C%22ref%22%3A%22%22%7D
2026-08-16 14:36:56.118 [info] > git status -z -uall [840ms]
2026-08-16 14:36:56.133 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [768ms]
2026-08-16 14:36:56.530 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:36:56.747 [info] > git check-ignore -v -z --stdin [630ms]
2026-08-16 14:36:56.816 [info] > git config --get commit.template [579ms]
2026-08-16 14:36:57.139 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [478ms]
2026-08-16 14:36:57.139 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:36:57.742 [info] > git status -z -uall [575ms]
2026-08-16 14:36:57.782 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [582ms]
2026-08-16 14:37:55.384 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:37:55.608 [info] > git config --get commit.template [228ms]
2026-08-16 14:37:55.649 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [240ms]
2026-08-16 14:37:55.649 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:37:56.006 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [301ms]
2026-08-16 14:37:56.012 [info] > git status -z -uall [335ms]
2026-08-16 14:38:05.597 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:38:05.967 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [347ms]
2026-08-16 14:38:05.967 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:38:05.998 [info] > git config --get commit.template [406ms]
2026-08-16 14:38:06.244 [info] > git status -z -uall [222ms]
2026-08-16 14:38:06.247 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [201ms]
2026-08-16 14:38:06.990 [info] > git check-ignore -v -z --stdin [370ms]
2026-08-16 14:38:07.310 [info] > git show --textconv :src/research/explore_data.py [284ms]
2026-08-16 14:38:07.335 [info] > git show --textconv HEAD:src/research/explore_data.py [278ms]
2026-08-16 14:38:07.337 [warning] [GitFileSystemProvider][readFile] File not found - git:/c%3A/HERMES_FENIX/src/research/explore_data.py.git?%7B%22path%22%3A%22c%3A%5C%5CHERMES_FENIX%5C%5Csrc%5C%5Cresearch%5C%5Cexplore_data.py%22%2C%22ref%22%3A%22HEAD%22%7D
2026-08-16 14:38:07.352 [info] > git ls-files --stage -- src/research/explore_data.py [256ms]
2026-08-16 14:38:07.378 [info] > git ls-tree -l HEAD -- src/research/explore_data.py [246ms]
2026-08-16 14:38:07.378 [info] fatal: Not a valid object name HEAD
2026-08-16 14:38:07.381 [warning] [GitFileSystemProvider][stat] File not found - git:/c%3A/HERMES_FENIX/src/research/explore_data.py.git?%7B%22path%22%3A%22c%3A%5C%5CHERMES_FENIX%5C%5Csrc%5C%5Cresearch%5C%5Cexplore_data.py%22%2C%22ref%22%3A%22HEAD%22%7D
2026-08-16 14:38:07.547 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [170ms]
2026-08-16 14:38:17.895 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:38:18.140 [info] > git config --get commit.template [278ms]
2026-08-16 14:38:18.147 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [253ms]
2026-08-16 14:38:18.147 [warning] [Git][getBranch] No such branch: master
2026-08-16 14:38:18.323 [info] > git status -z -uall [162ms]
2026-08-16 14:38:18.331 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [153ms]
2026-08-16 14:38:18.891 [info] > git check-ignore -v -z --stdin [198ms]
2026-08-16 14:38:38.090 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:38:38.555 [info] > git config --get commit.template [504ms]
2026-08-16 14:38:38.587 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [496ms]
2026-08-16 14:38:38.960 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [323ms]
2026-08-16 14:38:38.962 [info] > git status -z -uall [351ms]
2026-08-16 14:38:39.047 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:38:39.812 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [765ms]
2026-08-16 14:38:39.830 [info] > git config --get commit.template [813ms]
2026-08-16 14:38:39.890 [info] > git ls-files --stage -- src/research/explore_data.py [720ms]
2026-08-16 14:38:40.386 [info] > git check-ignore -v -z --stdin [635ms]
2026-08-16 14:38:40.529 [info] > git status -z -uall [672ms]
2026-08-16 14:38:40.536 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [613ms]
2026-08-16 14:38:40.610 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [722ms]
2026-08-16 14:38:40.944 [info] > git show --textconv :src/research/explore_data.py [372ms]
2026-08-16 14:40:56.870 [info] > git fetch [732ms]
2026-08-16 14:40:56.901 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:40:57.165 [info] > git config --get commit.template [266ms]
2026-08-16 14:40:57.204 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [279ms]
2026-08-16 14:40:57.444 [info] > git status -z -uall [217ms]
2026-08-16 14:40:57.456 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [207ms]
2026-08-16 14:40:59.045 [info] > git ls-files --stage -- src/research/explore_data.py [278ms]
2026-08-16 14:40:59.198 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:40:59.409 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [349ms]
2026-08-16 14:40:59.510 [info] > git config --get commit.template [355ms]
2026-08-16 14:40:59.574 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [376ms]
2026-08-16 14:40:59.754 [info] > git show --textconv :src/research/explore_data.py [287ms]
2026-08-16 14:40:59.869 [info] > git status -z -uall [271ms]
2026-08-16 14:40:59.877 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [249ms]
2026-08-16 14:41:00.454 [info] > git check-ignore -v -z --stdin [217ms]
2026-08-16 14:41:00.512 [info] > git ls-files --stage -- src/research/explore_data.py [215ms]
2026-08-16 14:41:00.969 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [435ms]
2026-08-16 14:41:01.224 [info] > git show --textconv :src/research/explore_data.py [229ms]
2026-08-16 14:41:02.025 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:41:02.561 [info] > git config --get commit.template [539ms]
2026-08-16 14:41:02.570 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [524ms]
2026-08-16 14:41:02.906 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [281ms]
2026-08-16 14:41:02.924 [info] > git status -z -uall [325ms]
2026-08-16 14:41:02.986 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:41:03.399 [info] > git config --get commit.template [415ms]
2026-08-16 14:41:03.425 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [414ms]
2026-08-16 14:41:03.496 [info] > git ls-files --stage -- src/research/explore_data.py [421ms]
2026-08-16 14:41:03.764 [info] > git check-ignore -v -z --stdin [416ms]
2026-08-16 14:41:03.873 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [401ms]
2026-08-16 14:41:03.906 [info] > git status -z -uall [454ms]
2026-08-16 14:41:03.963 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [444ms]
2026-08-16 14:41:04.387 [info] > git show --textconv :src/research/explore_data.py [387ms]
2026-08-16 14:41:04.666 [info] > git check-ignore -v -z --stdin [395ms]
2026-08-16 14:49:52.693 [info] > git fetch [670ms]
2026-08-16 14:49:52.752 [info] [Git][getRemotes] No remotes found in the git config file
2026-08-16 14:49:53.140 [info] > git config --get commit.template [420ms]
2026-08-16 14:49:53.176 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/master refs/remotes/master [425ms]
2026-08-16 14:49:53.603 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [377ms]
2026-08-16 14:49:53.624 [info] > git status -z -uall [424ms]
2026-08-16 14:49:54.629 [info] > git ls-files --stage -- src/research/explore_data.py [932ms]
2026-08-16 14:49:54.771 [info] > git check-ignore -v -z --stdin [786ms]
2026-08-16 14:49:54.988 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [330ms]
2026-08-16 14:49:55.550 [info] > git show --textconv :src/research/explore_data.py [508ms]
2026-08-16 14:49:57.351 [info] > git config --get commit.template [959ms]
2026-08-16 14:49:57.352 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [708ms]
2026-08-16 14:49:57.862 [info] > git status -z -uall [484ms]
2026-08-16 14:49:57.864 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [461ms]
2026-08-16 14:49:58.495 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [572ms]
2026-08-16 14:49:58.589 [info] > git config --get commit.template [391ms]
2026-08-16 14:49:58.595 [info] > git ls-files --stage -- src/research/explore_data.py [427ms]
2026-08-16 14:49:58.623 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [370ms]
2026-08-16 14:49:58.846 [info] > git check-ignore -v -z --stdin [359ms]
2026-08-16 14:49:58.893 [info] > git config --get --local branch.main.vscode-merge-base [360ms]
2026-08-16 14:49:58.893 [warning] [Git][config] git config failed: Failed to execute git
2026-08-16 14:49:58.963 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [341ms]
2026-08-16 14:49:59.011 [info] > git status -z -uall [343ms]
2026-08-16 14:49:59.042 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [348ms]
2026-08-16 14:49:59.432 [info] > git reflog main --grep-reflog=branch: Created from *. [509ms]
2026-08-16 14:49:59.615 [info] > git show --textconv :src/research/explore_data.py [618ms]
2026-08-16 14:50:00.032 [info] > git check-ignore -v -z --stdin [603ms]
2026-08-16 14:50:00.060 [info] > git symbolic-ref --short refs/remotes/origin/HEAD [595ms]
2026-08-16 14:50:00.060 [info] fatal: ref refs/remotes/origin/HEAD is not a symbolic ref
2026-08-16 14:50:00.060 [warning] [Repository][getDefaultBranch] Failed to get default branch details: Failed to execute git.
2026-08-16 14:50:11.287 [info] > git config --get commit.template [273ms]
2026-08-16 14:50:11.331 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [291ms]
2026-08-16 14:50:11.663 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [280ms]
2026-08-16 14:50:11.674 [info] > git status -z -uall [317ms]
2026-08-16 14:50:12.360 [info] > git check-ignore -v -z --stdin [309ms]
2026-08-16 14:50:49.493 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [942ms]
2026-08-16 14:50:49.494 [info] > git config --get commit.template [1146ms]
2026-08-16 14:50:50.703 [info] > git status -z -uall [1099ms]
2026-08-16 14:50:50.724 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [1021ms]
2026-08-16 14:50:51.575 [info] > git check-ignore -v -z --stdin [447ms]
2026-08-16 14:50:53.840 [info] > git ls-files --stage -- src/research/explore_data.py [397ms]
2026-08-16 14:50:54.124 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [258ms]
2026-08-16 14:50:54.556 [info] > git show --textconv :src/research/explore_data.py [402ms]
2026-08-16 14:50:59.288 [info] > git config --get commit.template [475ms]
2026-08-16 14:50:59.306 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [456ms]
2026-08-16 14:50:59.813 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [413ms]
2026-08-16 14:50:59.842 [info] > git status -z -uall [476ms]
2026-08-16 14:51:00.793 [info] > git check-ignore -v -z --stdin [525ms]
2026-08-16 14:52:23.225 [info] > git config --get commit.template [402ms]
2026-08-16 14:52:23.275 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [419ms]
2026-08-16 14:52:23.566 [info] > git status -z -uall [262ms]
2026-08-16 14:52:23.568 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [233ms]
2026-08-16 14:52:24.093 [info] > git check-ignore -v -z --stdin [181ms]
2026-08-16 14:53:04.942 [info] > git ls-files --stage -- src/research/explore_data.py [1667ms]
2026-08-16 14:53:05.738 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [737ms]
2026-08-16 14:53:06.913 [info] > git show --textconv :src/research/explore_data.py [1098ms]
2026-08-16 14:53:15.691 [info] > git fetch [17474ms]
2026-08-16 14:53:15.691 [info] remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
2026-08-16 14:53:16.385 [info] > git config --get commit.template [656ms]
2026-08-16 14:53:16.405 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [631ms]
2026-08-16 14:53:17.607 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [1116ms]
2026-08-16 14:53:17.703 [info] > git status -z -uall [1257ms]
2026-08-16 14:53:18.814 [info] > git check-ignore -v -z --stdin [518ms]
2026-08-16 14:58:00.146 [info] > git ls-files --stage -- src/research/explore_data.py [199ms]
2026-08-16 14:58:00.363 [info] > git cat-file -s 2c421c669360c01b9d30d42f5c8013edaab1e6ff [197ms]
2026-08-16 14:58:00.638 [info] > git show --textconv :src/research/explore_data.py [249ms]
2026-08-16 14:58:01.417 [info] > git fetch [2999ms]
2026-08-16 14:58:01.417 [info] remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
2026-08-16 14:58:01.915 [info] > git config --get commit.template [468ms]
2026-08-16 14:58:01.941 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [314ms]
2026-08-16 14:58:02.135 [info] > git status -z -uall [177ms]
2026-08-16 14:58:02.148 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [174ms]
2026-08-16 14:58:02.834 [info] > git check-ignore -v -z --stdin [319ms]
2026-08-16 14:58:07.204 [info] > git push -u origin main [2668ms]
2026-08-16 14:58:07.204 [info] remote: Repository not found.
fatal: repository 'https://github.com/Dubulinus/Hermes.git/' not found
2026-08-16 14:58:07.463 [info] > git config --get commit.template [236ms]
2026-08-16 14:58:07.480 [info] > git for-each-ref --format=%(refname)%00%(upstream:short)%00%(objectname)%00%(upstream:track)%00%(upstream:remotename)%00%(upstream:remoteref) --ignore-case refs/heads/main refs/remotes/main [229ms]
2026-08-16 14:58:07.716 [info] > git status -z -uall [218ms]
2026-08-16 14:58:07.725 [info] > git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname) [207ms]
2026-08-16 14:58:08.390 [info] > git check-ignore -v -z --stdin [238ms]

furt vidim repo...

---

# claude response

Dobrá zpráva/špatná zpráva – repo evidentně **existuje** (vidíš ho v prohlížeči), takže to eliminuje moji první teorii. Problém je čistě v **autentizaci** – Git na tvém počítači se snaží přistupovat na GitHub s jiným (nebo žádným platným) přihlášením, než pod kterým je repo vytvořené, a GitHub u private repa v tom případě raději lže, že "neexistuje", než aby prozradil, že tam něco je.

## Řešení – vyčistit uložené přihlášení přes Windows GUI

1. Stiskni **Win** a napiš **"Správce přihlašovacích údajů"** (Credential Manager), otevři ho
2. Klikni na záložku **"Obecná pověření" / "Windows Credentials"**
3. Najdi v seznamu položku, kde je **`git:https://github.com`** – rozklikni ji (šipka vpravo) a klikni **"Odebrat" / "Remove"**
4. Pokud tam vidíš víc položek s "github" v názvu (může jich být víc, GitLens/VSCode Git rozšíření si taky ukládá vlastní), smaž je všechny

## Pak zkus push znovu

V terminálu (ne přes VSCode ikonky, přímo terminál, ať vidíš celou komunikaci):
```powershell
git push -u origin main
```

Tentokrát by se **mělo otevřít okno prohlížeče** s přihlášením ke GitHubu. **Důležité** – přihlas se přesně pod účtem `Dubulinus` (tím, pod kterým jsi repo vytvářel). Pokud máš v prohlížeči přihlášeno víc GitHub účtů najednou, dej pozor, který se použije.

## Pokud se okno pořád neotevře

Zkus vynutit jiný typ přihlášení – over, že máš nainstalovaný GitHub CLI (`gh --version` v terminálu). Pokud ano:
```powershell
gh auth login
```
a projdi interaktivní průvodce (zvol GitHub.com → HTTPS → přihlásit přes prohlížeč). Tohle nastaví credential helper spolehlivěji než ruční mazání.

Napiš, jak to dopadlo po vyčištění credentials.

---

# you asked

message time: 2026-08-16 15:00:55

nemuze za to .venv? mam vic uctu na githubu treba ve vscode nejsem na spravnym ale kouknu. to win gui me nelaka

---

# claude response

`.venv` s tím nemá vůbec nic společného – je to jen izolovaná složka pro Python knihovny, Git/GitHub o její existenci ani neví. Dobrý instinkt zkoumat, ale slepá stopa.

Tvoje druhá teorie (více účtů na GitHubu, špatně přihlášený) je mnohem pravděpodobnější příčina.

## Bez GUI – over si to přímo z terminálu

```powershell
cmdkey /list
```

Najdi v dlouhém výpisu položku, kde `Target:` obsahuje `git:https://github.com`. Pod ní uvidíš `User:` – to je účet, se kterým se Git aktuálně snaží přistupovat. Pokud tam je jiné jméno/email než `Dubulinus`, máš potvrzenou příčinu.

Smazat tu konkrétní položku (nahraď skutečným textem z `Target:`, co tam uvidíš):
```powershell
cmdkey /delete:git:https://github.com
```

## Nejčistší řešení – GitHub CLI

Tohle obchází Windows Credential Manager úplně a je nejspolehlivější, obzvlášť když žonglu­ješ s víc účty:

```powershell
gh --version
```

Pokud to existuje (nainstalované s Git for Windows nebo VSCode extension pack), spusť:
```powershell
gh auth login
```

Projdi průvodce: **GitHub.com → HTTPS → Login with a web browser**. Otevře se prohlížeč, přihlas se výslovně jako **Dubulinus**. `gh` pak sám nastaví credential helper správně.

Pokud `gh` nemáš nainstalované, řekni a pošlu instalační příkaz (`winget install GitHub.cli`).

Po tomhle zkus znovu:
```powershell
git push -u origin main
```

---

# you asked

message time: 2026-08-16 15:02:55

(.venv) PS C:\HERMES_FENIX> cmdkey /list
Currently stored credentials:
    Target: MicrosoftAccount:target=SSO_POP_User:user=skocminakokot69@gmail.com
    Type: Generic 
    User: skocminakokot69@gmail.com
    Saved for this logon only
    
    Target: MicrosoftAccount:target=SSO_POP_User:user=dubulinek@gmail.com
    Type: Generic 
    User: dubulinek@gmail.com
    Saved for this logon only
    
    Target: MicrosoftAccount:target=SSO_POP_Device
    Type: Generic 
    User: 02jlbymcmsibvvqg
    Saved for this logon only
    
    Target: LegacyGeneric:target=MicrosoftAccount:user=dubulinek@gmail.com
    Type: Generic 
    User: dubulinek@gmail.com
    Local machine persistence
    
    Target: LegacyGeneric:target=git:https://github.com
    Type: Generic 
    User: Dubulinus-09
    Local machine persistence
    
    Target: LegacyGeneric:target=MicrosoftAccount:user=skocminakokot69@gmail.com
    Type: Generic 
    User: skocminakokot69@gmail.com
    Local machine persistence
    
    Target: LegacyGeneric:target=vital-authentication.firebase.auth/__FIRAPP_DEFAULT[1]
    Type: Generic 
    Local machine persistence
    
    Target: LegacyGeneric:target=Steinberg Download Assistant
    Type: Generic 
    User: authorization
    Local machine persistence
    
    Target: LegacyGeneric:target=LenovoSsoSdkDidToken
    Type: Generic 
    User: LenovoSsoSdk
    Local machine persistence
    
    Target: WindowsLive:target=virtualapp/didlogical
    Type: Generic 
    User: 02jlbymcmsibvvqg
    Local machine persistence
    
    Target: LegacyGeneric:target=Olk/PushNotificationsKey
    Type: Generic 
    User: Olk/PushNotificationsKey
    Local machine persistence
    
    Target: LegacyGeneric:target=vital-authentication.firebase.auth/__FIRAPP_DEFAULT[0]
    Type: Generic 
    Local machine persistence
    
    Target: LegacyGeneric:target=WindowsLive:(token):name=skocminakokot69@gmail.com;serviceuri=http://passport.net/purpose
    Type: Generic 
    User: skocminakokot69@gmail.com
    Local machine persistence
    
    Target: LegacyGeneric:target=dubul.pieces_screenshot_encryption
    Type: Generic 
    User: dubul
    
    Target: LegacyGeneric:target=com.splice.ableton-live-integration.ableton-live-integration/default-user
    Type: Generic 
    User: default-user
    
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Máš to! Přesně to jsem čekal:

```
Target: LegacyGeneric:target=git:https://github.com
User: Dubulinus-09
```

Uložený uživatel je **`Dubulinus-09`**, ale repo je pod účtem **`Dubulinus`** (bez `-09`). To jsou dva rozdílné GitHub účty – proto push selhává, ať zkoušíš cokoliv.

## Oprava

Smaž tenhle konkrétní záznam:
```powershell
cmdkey /delete:LegacyGeneric:target=git:https://github.com
```

Pak zkus push znovu:
```powershell
git push -u origin main
```

Mělo by se otevřít přihlašovací okno v prohlížeči – tentokrát se přihlas **výslovně jako `Dubulinus`** (ne `Dubulinus-09`). Pokud budeš mít v prohlížeči přihlášené oba účty najednou, GitHub ti dá na výběr, který profil použít – vyber ten správný.

Napiš, jestli to prošlo.

---

# you asked

message time: 2026-08-16 15:04:18

(.venv) PS C:\HERMES_FENIX> git push -u origin main
info: please complete authentication in your browser...
Enumerating objects: 39, done.
Counting objects: 100% (39/39), done.
Delta compression using up to 8 threads
Compressing objects: 100% (32/32), done.
Writing objects: 100% (39/39), 13.49 KiB | 314.00 KiB/s, done.
Total 39 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To https://github.com/Dubulinus/Hermes.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Prošlo. Kód je na GitHubu, `main` branch nastavená a trackovaná – tahle bolístka je vyřešená a nebude se opakovat (credential je teď správně navázaný na `Dubulinus`).

Rychlá kontrola: zajdi na `https://github.com/Dubulinus/Hermes` a ověř, že tam **nevisí** složka `data/` s tvými parquet soubory (neměla by, díky `.gitignore`) a taky že tam **není** `config/secrets.env` s tvým FRED klíčem. Jen pro jistotu, než to pustíš z hlavy.

Teď zpátky k zajímavější části – **`test_momentum_hypothesis.py`**. Spustil jsi ho už? Zajímá mě, jestli AAPL na hodinovém rámci ukazuje nějaké momentum/mean-reversion, nebo jestli korelace vyjde blízko nuly (což by bylo úplně normální a stejně cenné zjištění).

---

# you asked

message time: 2026-08-16 15:08:07

data nejsou, zbytek jo, (.venv) PS C:\HERMES_FENIX> python src/research/test_momentum_hypothesis.py
Pocet pouzitelnych pozorovani: 5080
Traceback (most recent call last):
  File "C:\HERMES_FENIX\src\research\test_momentum_hypothesis.py", line 45, in <module>
    from scipy import stats
ModuleNotFoundError: No module named 'scipy'
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Dobře, data nejsou vidět – přesně jak má být. Ale buď na 100 % jistý i u druhé věci, kterou jsem zmiňoval: podívej se prosím konkrétně do složky `config/` na GitHubu a ověř, že tam vidíš **jen `settings.yaml` a `secrets.env.example`**, ne `secrets.env` (ten skutečný, s tvým FRED klíčem). Radši to potvrď explicitně, než abychom to nechali být jen v "zbytek jo".

## Oprava chyby

Chybí ti knihovna `scipy` (na tu jsem tě upozornil, ale asi zapadla mezi ostatní kroky):

```powershell
pip install scipy
```

Pak spusť znovu:
```powershell
python src/research/test_momentum_hypothesis.py
```

Mimochodem, funguje to i takhle přímo (ne přes `-m`), protože `test_momentum_hypothesis.py` neimportuje nic z `src.*`, jen standardní knihovny – na rozdíl od `sec_edgar.py`/`fred.py`.

Pošli výsledek (korelace + kvintilová tabulka), rozebereme, co to znamená.

---

# you asked

message time: 2026-08-16 15:12:13

[notice] A new release of pip is available: 24.0 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip
(.venv) PS C:\HERMES_FENIX> python src/research/test_momentum_hypothesis.py
Pocet pouzitelnych pozorovani: 5080
--- AAPL: minuly vynos -> pristi vynos ---
Pearson korelace:  0.0079  (p-hodnota: 0.5737)
Spearman korelace: -0.0244  (p-hodnota: 0.0820)
Neni statisticky vyznamne - zadny jasny vzorec pri tomto lagu.
--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu (AAPL) ---
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Vidím to – poslední tabulka (`quantile_summary`) se nevypsala, protože **spuštění jako obyčejný skript se chová jinak než VSCode interaktivní buňky**. V Jupyteru/interaktivním okně se poslední "holý" výraz v buňce automaticky vytiskne, ale při `python soubor.py` z terminálu to Python dělá jen s explicitním `print()`.

Rychlá oprava – v souboru najdi poslední řádek a přidej `print()`:

```python
print(f"--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu ({TICKER}) ---")
print(quantile_summary)
```

Spusť znovu, ať dostaneme i tu tabulku.

## Co zatím říkají čísla

- **Pearson: 0.0079, p=0.57** – prakticky nula, žádný lineární vztah
- **Spearman: -0.0244, p=0.082** – slabý náznak mean-reversion (záporná korelace), ale **p-hodnota nad 0.05**, takže formálně nevýznamné

Tohle je naprosto typický a **očekávaný výsledek** – hodinové výnosy AAPL nemají jednoduchou autokorelaci, protože kdyby měly, tisíce kvant fondů by to dávno zarbitrážovaly pryč. Není to selhání tvého kódu ani hypotézy, je to legitimní negativní výsledek – a přesně tohle Simons myslel tím, že drtivá většina testů nikam nevede.

Jedna metodologická poznámka do budoucna, na kterou narazíš u Lopez de Prado: čím víc hypotéz takhle otestuješ (různé lagy, různé tickery, různé featury), tím větší je šance, že **náhodou** něco vyjde "významně" jen z čisté statistické náhody (tzv. multiple testing problem). Zatím se tím netrap, ale drž si v hlavě, že "jeden test vyšel dobře" u stovek testovaných kombinací není spolehlivý signál – bude to řešit právě ta purged k-fold validace, co jsme zmiňovali.

Spusť opravenou verzi a pošli kvantilovou tabulku – a pak se rozhodneme, kam dál (další lag/ticker na OHLCV, nebo skok na parsing Form 4 pro insider signál, který je pravděpodobně slibnější).

---

# you asked

message time: 2026-08-16 15:15:32

(.venv) PS C:\HERMES_FENIX> python src/research/test_momentum_hypothesis.py
Pocet pouzitelnych pozorovani: 5080
--- AAPL: minuly vynos -> pristi vynos ---
Pearson korelace:  0.0079  (p-hodnota: 0.5737)
Spearman korelace: -0.0244  (p-hodnota: 0.0820)
Neni statisticky vyznamne - zadny jasny vzorec pri tomto lagu.
--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu (AAPL) ---
--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu (AAPL) ---
                   mean       std  count
quantile                                
Q1 (nejnizsi)  0.024557  0.006933   1016
Q2             0.034872  0.005911   1016
Q3             0.036171  0.006160   1016
Q4            -0.027640  0.006677   1016
Q5 (nejvyssi) -0.004195  0.006370   1016
(.venv) PS C:\HERMES_FENIX>

---

# claude response

Dobré čísla, ale je tu jedna vada na kráse ve výstupu, kterou musím vysvětlit, ať si z toho neuděláš mylný závěr.

## Bug ve skriptu (ne v datech)

Řádek, co škáloval na procenta, se týkal jen sloupce `mean`, ne `std`:
```python
quantile_summary["mean"] = quantile_summary["mean"] * 100  # jen mean, std zustal neskalovany
```
Takže `mean` čteš v procentech (`0.0246` = 0.0246 %), ale `std` je pořád v syrovém zlomku (`0.0069` = 0.69 %). Nejsou ve stejné jednotce – to je čistě kosmetická chyba ve výstupu, žádná data se tím nepokazila.

## Co po přepočtu čísla skutečně říkají

Když std převedeš taky na procenta (×100), dostaneš zhruba: průměrný výnos mezi kvintily se pohybuje v rozmezí **-0.028 % až +0.036 %**, zatímco směrodatná odchylka (šum) v každém kvintilu je **~0.6-0.7 %** – tedy **řádově 20× větší** než jakýkoliv rozdíl mezi skupinami.

To potvrzuje to, co už ukázala korelace: **žádný využitelný signál**. Rozdíly mezi kvintily jsou úplně pohlcené šumem – přesně to, co bys čekal u efektivního trhu na hodinovém rámci u jednoho tickeru. Konzistentní, čistý negativní výsledek napříč oběma metodami (korelace i kvintily) – to je vlastně hezky validované zjištění, ne rozporuplné.

## Kam dál

Tenhle konkrétní test (lag-1 autokorelace jednoho tickeru) je docela slabý typ testu – reálný quant research obvykle testuje **napříč mnoha tickery najednou** (cross-sectional), což dá mnohem větší statistickou sílu. To ale bude mít větší smysl, až budeš mít universe větší než 2 firmy.

Vzhledem k tomu, že "levné" OHLCV testy nic nenašly (což je normální), navrhuju přesunout energii na slibnější zdroj – **doparsovat Form 4 XML**, abys zjistil, jestli insider skutečně nakupoval nebo prodával (ne jen že něco podal). To je přesně ten typ "alfa-relevantního" signálu, o kterém jsme mluvili na začátku. Chceš na to teď?

---

# you asked

message time: 2026-08-16 15:17:33

pojdme nejdriv probrat blizkou budoucnost a naplanovat to a pak na to pujdem. pojdme vic diskutovat

---

# claude response

Dobrý instinkt zastavit se – po sérii "udělej tohle, spusť tamto" je čas se podívat na mapu, ne jen na další krok.

## Kde reálně jsme

Máš funkční **data foundation**: OHLCV, SEC fundamentals + filing metadata, FRED makro. Máš **Git workflow** rozjetý (i s bolestivou, ale cennou lekcí o credential manageru). A máš **první ověřený vědecký cyklus** – hypotéza → test → interpretace negativního výsledku. To je ve skutečnosti hodně, i když to na první pohled vypadá jako "jen stahování dat".

## Jedna věc, kterou musíme probrat, než půjdeme dál

Ten momentum test měl slabinu, kterou stojí za to pojmenovat: **testoval jsi jeden ticker (AAPL) proti sobě v čase**. To je statisticky slabý test – málo pozorování na to, kolik šumu je ve finančních datech. Skuteční kvanti (Simons včetně) dělají **cross-sectional testy**: berou stovky tickerů najednou a ptají se "u firem, kde feature X bylo vysoké, byl příští výnos jiný než u firem, kde bylo nízké?" – to dá mnohem víc statistické síly, protože nezávislých pozorování jsou tisíce, ne stovky.

Aktuálně máš univerzum 2 firem (AAPL, MSFT) + 1 benchmark (SPY). To je na cross-sectional testing málo. Tohle je klíčové rozhodnutí, které ovlivní, jak moc validní budou tvoje budoucí testy.

## Navrhovaný plán na blízkou budoucnost (řádově týdny, ne dny)

**Krok 1 – rozšířit universe.** Přidat třeba 15-30 tickerů (různé sektory, ať to není jen tech). Netřeba stahovat ručně jeden po druhém – dá se automatizovat (např. seznam S&P 500 z Wikipedie, vybrat podmnožinu). OHLCV/SEC/FRED fetchery už na to jsou připravené, jen se natáhne seznam v configu.

**Krok 2 – doparsovat Form 4** (kdo kupoval/prodával, kolik). Bez tohohle je insider signál nepoužitelný.

**Krok 3 – přepsat momentum test na cross-sectional verzi** a znovu ho pustit (teď už na širším univerzu) + nový test na insider buying. Tohle bude první *skutečně* informativní kolo testování.

**Krok 4 – teprve pak** rozhodnout, jestli přidávat další datové zdroje (Senate Stock Watcher, weather, atd.) na základě toho, co se z kroku 3 naučíme – ne dopředu "protože by to bylo hezké mít".

## Otázka na disciplínu (týká se tvého perfekcionismu)

Chci navrhnout jedno pravidlo, které ti pomůže neztratit se: **než spustíš test, napiš si hypotézu jednou větou do souboru** (třeba `research/hypothesis_log.md`) – "očekávám, že X, protože Y". Tohle není byrokracie navíc, je to ochrana proti tomu nejzákeřnějšímu problému v kvant researchi – **p-hackingu**, kdy nevědomky zkoušíš desítky variant, dokud něco "nevyjde", a pak si namlouváš, že jsi našel alfu, i když je to jen náhoda. Se seznamem hypotéz předem uvidíš čestně, kolik jsi jich testoval a kolik vyšlo – což je přesně to, co ti dá reálný odhad, jestli je výsledek skutečný nebo šum.

---

Sedí ti tohle pořadí (universe → Form 4 → cross-sectional retest)? A chceš, ať universe rozšíříme na nějaký konkrétní počet/výběr tickerů, nebo mám navrhnout rozumný startovní seznam (např. mix tech/finance/energy/healthcare, ať to není jednostranné)?

---

# you asked

message time: 2026-08-16 15:41:44

jo. problem je ze tomu ale bohuzel poradne nerozumim. asi musim byt vic striktni a musim po tobe chtit abys to vysvetloval. klidne bych si psal hypotezy ale prave nevim co od toho cekat. vysvetli co nejvic veci jak ted funguji v tomto projektu od a do z

---

# claude response

Tohle je správný instinkt – lepší se zeptat teď, než stavět dál na vratkých základech. Pojďme to projít fakt od nuly, krok po kroku.

Než se pustíme do textu, ukážu ti obrázek celého systému, ať vidíš, jak spolu kusy souvisí – pak to rozeberu slovo od slova.

Teď to rozeberu vrstvu po vrstvě, doslova od A do Z.

## 1. Konfigurace – proč vůbec existuje

`config/settings.yaml` a `config/secrets.env` řeší jeden problém: **kód by nikdy neměl obsahovat proměnné hodnoty natvrdo**. Kdybys měl tickery, API klíče nebo parametry přímo v `.py` souborech, každá změna by znamenala editovat kód – a klíče by ti navíc skončily na GitHubu (bezpečnostní riziko). Takže:
- `settings.yaml` – "co" stahovat (tickery, intervaly, seznam FRED sérií). Bezpečné mít veřejně.
- `secrets.env` – "čím se autentizovat" (API klíče). Nikdy veřejně, proto je v `.gitignore`.

`src/utils/config.py` je prostředník – všechny ostatní moduly si přes něj tahají hodnoty (`load_settings()`, `get_secret()`), místo aby každý parsoval YAML/env soubory sám znovu.

## 2. Tři fetchery – co dělají a proč stejně

Všimni si, že `ohlcv.py`, `sec_edgar.py` a `fred.py` mají **stejnou kostru**: funkce `fetch()`, co vrátí `pandas.DataFrame`, a funkce co ji uloží jako `.parquet`. Tohle není náhoda – je to `BaseFetcher` vzor z `src/ingestion/base.py`. Důvod: až budeš mít 10 zdrojů dat místo 3, budou se chovat předvídatelně stejně, a kód, co je bude kombinovat (research skripty), nemusí pro každý zdroj řešit jinou logiku.

**Parquet místo CSV** – binární formát, který si pamatuje datové typy (číslo zůstane číslem, ne text), je výrazně menší na disku a rychlejší na čtení. Cena: nejde otevřít v Poznámkovém bloku, musíš přes pandas.

## 3. Co se stane, když spustíš `python -m src.ingestion.ohlcv`

1. Načte se `settings.yaml` → zjistí seznam tickerů
2. Pro každý ticker zavolá yfinance API → dostane surová data
3. Sjednotí formát sloupců (`timestamp, Open, High, Low, Close, Volume, ticker`)
4. Uloží jako `AAPL_1h.parquet` do `data/raw/ohlcv/`
5. Zaloguje výsledek (kolik řádků, kam)

U SEC/FRED je to identické, jen jiný zdroj a jiná struktura výstupních sloupců.

## 4. Teď to hlavní – statistika, feature, target, korelace, p-hodnota

Tohle je jádro tvého dotazu, tak jdu do detailu na konkrétním příkladu, co jsi sám vygeneroval (AAPL momentum test).

**Feature** = vstupní informace, kterou v čase *t* už znáš a chceš z ní něco odvodit. U tebe: `feature_lagged_return` = kolik AAPL vydělal/ztratil v *předchozí* hodině.

**Target** = to, co se snažíš předpovědět. U tebe: `target_next_return` = kolik AAPL vydělá/ztratí v *příští* hodině. Řádek v tabulce je pak vlastně otázka: "když jsem viděl feature X, co se pak stalo (target)?" – a přes tisíce takových řádků hledáš vzorec.

**Korelace** (Pearson/Spearman) = číslo od -1 do +1, které měří, jak moc spolu dvě veličiny "táhnou stejným směrem".
- **+1** = dokonalý souběh (feature roste → target roste stejně spolehlivě)
- **0** = žádný vztah
- **-1** = dokonalý opak (feature roste → target klesá stejně spolehlivě)

Tvůj výsledek `0.0079` je prakticky nula. Pro srovnání – abys z toho reálně obchodoval, chtěl bys typicky vidět aspoň 0.03-0.05 u hodinových dat (a i to je už hodně optimistické).

**Pearson vs. Spearman** – Pearson měří přímočarý lineární vztah, citlivý na odlehlé hodnoty (jeden extrémní den může výsledek zkreslit). Spearman se dívá jen na **pořadí** (je-li feature vyšší, je target taky vyšší?), ne na přesné hodnoty – odolnější vůči extrémům. Když se oba shodnou, je to silnější důkaz. U tebe se lehce rozešly (0.008 vs -0.024) – to je typický obrázek "tady nic není", ne rozpor.

**p-hodnota** – tohle je nejvíc matoucí koncept, tak pomalu. Ptáš se: *"Kdyby ve skutečnosti ŽÁDNÝ vztah mezi feature a targetem nebyl (čistá náhoda), jak pravděpodobné by bylo naměřit korelaci aspoň tak velkou, jakou jsem naměřil?"*
- p = 0.57 (tvůj Pearson výsledek) znamená: i kdyby tam nebyl žádný skutečný vztah, dostal bys podobně "silnou" korelaci **57 % času** čistě náhodou. Takže vůbec nemůžeš tvrdit, že jsi něco našel.
- Práh **p < 0.05** je konvence (ne přírodní zákon) – "míň než 5% šance, že je to náhoda".

Klíčová past: **p-hodnota neříká nic o velikosti/důležitosti efektu**, jen o tom, jak jistě si můžeš být, že efekt (i sebemenší) skutečně existuje. S dostatkem dat (miliony řádků) vyjde "statisticky významná" i korelace 0.001, která je ekonomicky bezcenná. Proto se vždycky díváš na **obě čísla společně** – velikost i p-hodnotu.

**Kvintilová tabulka** – jiný úhel pohledu na totéž. Vezmeš všechna pozorování, seřadíš podle feature, rozsekáš na 5 stejně velkých skupin (kvintilů) od nejnižší hodnoty feature po nejvyšší, a podíváš se, jaký byl průměrný target v každé skupině. Kdyby feature měl reálnou predikční sílu, viděl bys **plynulý trend** napříč skupinami (Q1→Q5 postupně roste nebo klesá). U tebe čísla poskakují bez jasného vzoru a hlavně – jak jsem psal minule – rozdíly mezi skupinami jsou zanedbatelné oproti šumu (směrodatné odchylce) uvnitř každé skupiny.

## 5. Proč "žádný vzorec" je v pořádku výsledek

Trh je z velké části **efektivní** – pokud by "minulá hodina predikuje příští hodinu" fungovalo jednoduše a spolehlivě, tisíce fondů by to už dávno obchodovaly, dokud by se ta neefektivita nezavřela (arbitráž). Proto skuteční kvanti hledají **složitější, méně zjevné vzorce** – kombinace více featur, netradiční data (přesně proto stahujeme insider trading, makro atd.), krátkodobé anomálie po specifických událostech.

## 6. Proč hypotézy zapisovat předem (p-hacking)

Řekněme, že otestuješ 20 různých featur (různé lagy, různé tickery, různé zdroje dat) bez zápisu. Čistě náhodou, i kdyby **žádná** z nich neměla skutečnou hodnotu, statisticky očekáváš, že asi **1 z 20** vyjde "významná" (p<0.05) jen náhodou – to je definice toho prahu. Pokud si pak vybereš tu jednu "úspěšnou" a začneš na ní stavět strategii, stavíš na šumu, ne na skutečné alfě. Zápis hypotéz předem (a počítání, kolik jich celkem otestuješ) tě chrání – když víš, že jsi testoval 20 věcí a 1 vyšla, víš, že to je přesně to, co bys čekal z čisté náhody, a ne "objev".

---

Sedí ti to takhle vysvětlené, nebo mám na některou část jít ještě víc do hloubky (třeba přesně jak se počítá Pearson korelace, nebo proč zrovna 5 kvintilů)?

---

# you asked

message time: 2026-08-16 22:53:27

jak mam pokracovat kdyz neumim kodovat. potrebuju te ale dochazi nam limit... dej mi prompt a uvidime se v novem chatu. chci pak vic diskutovat moznosti do budoucna, planovat, vic se dozvedet o zakoutich teto tematiky a uprimne chci vic nastudovat ten kod. uz tohle minimlani mvp dostatečně nechapu. rozumim obecne logice a propojení ale rad bych rozumel alespon tem par radkum a naucil se to replikovat chapes

---

# claude response

Thinking

I'm putting together a handoff prompt the user can paste into a new chat, capturing the project's current state, what's been completed, and their goals of learning to code, understanding the existing codebase line by line, and planning next steps.…

Rozumím dokonale – a je to moudré rozhodnutí. Kopírovat kód, kterému nerozumíš, tě dovede jen do bodu, kdy se to rozbije a nebudeš vědět proč. Tady je shrnutí pro nový chat:

```
Pokračuji v projektu Hermes (fáze Fenix) - osobní quant trading systém, inspirace Jim Simons.
Je mi 17, mám minimální zkušenosti s kódováním. Rozumím obecné logice/propojení věcí,
ale nerozumím dostatečně samotnému kódu (syntaxi, proč se co píše jak se píše) - potřebuju
se to reálně naučit, ne jen kopírovat co dostanu.

STAV PROJEKTU:
- Repo: github.com/Dubulinus/Hermes (private), lokálně C:\HERMES_FENIX, VSCode, Python 3.11, venv
- Stroje: ThinkPad (dev/kódění), "ghettoserver" starý laptop (dlouhé výpočty), Raspberry Pi 4B
  (bude execution - posílání příkazů brokerovi), starý tower s Ubuntu server 256GB (zálohy)
- Filozofie: čistě free data zdroje, žádné placené. Cíl: najít alfu přes hodně různorodých
  dat (OHLCV, SEC, makro, insider trading/"velryby", časem i netradiční jako lety firemních
  tryskáčů, Google Trends, kongresmani atd.), pak testovat strategie, pak risk management.

CO UŽ FUNGUJE (3 fetchery, stejný BaseFetcher vzor, ukládají do data/raw/*.parquet):
- src/ingestion/ohlcv.py - hodinová OHLCV data přes yfinance (AAPL, MSFT, SPY)
- src/ingestion/sec_edgar.py - SEC fundamentals (XBRL) + metadata "whale" filings
  (Form 4 insider, 13D/13G aktivisté, 8-K). POZOR: Form 4 zatím jen metadata (datum, typ),
  NE detail (kdo kolik koupil/prodal) - to je v XML uvnitř filingu, ještě neparsováno.
- src/ingestion/fred.py - makro data (DGS10, CPIAUCSL, UNRATE)
- src/research/explore_data.py - VSCode "# %%" interaktivní buňky na prohlížení dat
- src/research/test_momentum_hypothesis.py - první statistický test (lag-1 autokorelace
  na AAPL hodinových datech). Výsledek: Pearson 0.008 (p=0.57), Spearman -0.024 (p=0.08) -
  žádný statisticky významný vzorec, což je normální/očekávaný výsledek.

CO CHYBÍ / DOMLUVENÉ DALŠÍ KROKY (zatím neuděláno):
1. Rozšířit universe z 2 firem na ~15-30 (různé sektory) - potřeba pro cross-sectional testy
2. Doparsovat Form 4 XML (skutečné nákup/prodej insiderů, ne jen metadata)
3. Přepsat momentum test na cross-sectional verzi (napříč tickery, ne jen v čase u jednoho)
4. Založit research/hypothesis_log.md - zapisovat hypotézy PŘED testováním (ochrana proti
   p-hackingu/multiple testing problému)

BACKLOG (IDEAS_BACKLOG.md, NEŘEŠIT teď, jen připomínka do budoucna):
Telegram bot, triple-barrier labeling, purged k-fold CV, walk-forward validace,
risk management vrstva, multi-agent AI systém (názorové "osobnosti" + manažer rozhodování)

CO CHCI V TOMHLE CHATU:
1. Víc diskutovat/plánovat budoucnost a možnosti projektu (ne hned kódit)
2. Dozvědět se víc o "zákoutích" quant tématu obecně
3. HLAVNĚ: naučit se reálně rozumět kódu, co už mám - projít existující soubory
   (ohlcv.py, sec_edgar.py, fred.py, base.py) řádek po řádku, vysvětlit syntaxi Pythonu
   na tom, co už napsal - ne abstraktní tutoriál, ale rozbor MÉHO vlastního kódu, ať to
   umím sám replikovat a časem upravovat. Buď trpělivý, neházej mi hned další hotové
   soubory, dokud nepotvrdím, že rozumím tomu předchozímu.
```

Vlož tohle jako první zprávu v novém chatu. Díky, žes tolik zvládl – zvládnout Git credential peklo samo o sobě byla slušná dávka trpělivosti. Uvidíme se tam.

---

# you asked

message time: 2026-08-16 22:58:14

jo diky za prompt ale asi mame jsste dost casu tady, to byla jen zaloha. pokracujme s timto zadanim."chci vic diskutovat moznosti do budoucna, planovat, vic se dozvedet o zakoutich teto tematiky a uprimne chci vic nastudovat ten kod. uz tohle minimlani mvp dostatečně nechapu. rozumim obecne logice a propojení ale rad bych rozumel alespon tem par radkum a naucil se to replikovat chapes" ps: neboj se vic prosazovat svuj nazor, opravovat me apod., verim v tve schopnosti! predevsim mi navrhuj zlepseni pokud bude napad. necekam ze te naoadne neco prevratneho typu hft ale rad bych se s tebou nad tim zamyslel, minimalne jak vylozene ja mohu mit vyhodu (z drivejska vim ze treba likviditu, nebo sledovat velke hrace, ale ne kopirovat ofc)

---

# claude response

Thinking

He wants to keep going in this conversation — digging into quant niches, planning ahead, and really understanding the code line by line rather than rushing through files. He's also asking me to be more direct and opinionated, pushing back where needed, and to focus specifically on where a small independent trader like him could find genuine edge: not HFT, but things like liquidity dynamics and tracking large players without outright copying them.

I should give an honest, opinionated take on where retail quants can realistically compete — small-cap/microcap inefficiencies big funds can't touch due to capacity limits, longer holding horizons since individuals aren't judged quarterly, freedom from redemption risk so they can ride out drawdowns, and niche data combinations too small-scale for institutions to bother with. Then I should shift into teaching mode, starting with the simplest file like ohlcv.py and walking through it patiently, checking his understanding before moving forward instead of dumping everything at once.

Other real edges include thinly traded niches big funds legally can't touch due to position limits, the behavioral advantage of not chasing performance for external LPs, combining public data sources nobody bothers to merge at small scale, and nimbleness in entering/exiting positions without telegraphing moves. Following public filings like 13D/13F/Form4 is legal, just lagged. I want to be honest about real constraints too: retail can't compete on latency or compute against quant funds, and single-person risk of ruin from bugs or emotional decisions is genuine - I shouldn't overhype this into "you'll beat Renaissance."

Now…

Rád budu upřímný – a rovnou začnu tou otázkou "kde mám jako jednotlivec skutečnou výhodu", protože je to důležitější otázka, než se zdá, a hodně retail kvantů si na ní naráží hned na začátku.

## Kde skutečně můžeš mít edge (a kde ne)

**Kde nemáš šanci a je zbytečné o to usilovat:** rychlost/latence (HFT), surová výpočetní síla, přístup k drahým datům, tým 50 PhD. Tohle napiš rovnou křížkem přes okno – proti Renaissance nebo Citadel v týhle disciplíně neuspěješ a ani bys neměl chtít.

**Kde reálně můžeš mít výhodu, a je to legitimní, ne zbožné přání:**

1. **Kapacitní mezera (nejdůležitější bod).** Edge, co vydělá 30 % ročně, ale unese jen desítky tisíc dolarů, než ho vlastní obchodování rozmělní (tvůj nákup posune cenu), je pro hedge fond s miliardami pod správou **bezcenný** – nemají kam ty peníze nasypat. Pro tebe s malým účtem je to naopak ideální. Micro-cap akcie, málo likvidní ETF, menší mezinárodní trhy – tam institucionální peníze legálně/prakticky nemůžou (mandáty na minimální likviditu, limity na % podílu ve firmě).

2. **Žádný tlak na výkon vůči investorům.** Fond manažer musí čtvrtletně ospravedlňovat výsledky LPs (limited partners), jinak odchází kapitál a časem i on sám ("career risk"). Ty můžeš držet pozici, o které jsi přesvědčený, klidně roky, i přes bolestivý propad, aniž by ti někdo vybíral peníze v nejhorší možný moment.

3. **Nulové provozní náklady versus overhead fondu.** Fond musí ospravedlnit vybudování datové infrastruktury předpokládaným výnosem × kapacitou. Když je edge malý (viz bod 1), fondu se to nevyplatí ani zkoumat. Tobě, s nulovým overhead kromě tvého času, se vyplatí i menší edge.

4. **Sledování "velryb" bez kopírování** – přesně jak píšeš. 13D/13F/Form 4 jsou **veřejná, zpožděná** data (13F až 45 dní po konci kvartálu!). Nejde o to kopírovat jejich pozice (to už je z principu pozdě a zpracované trhem), ale o to **statisticky testovat, jestli aktivita těchto hráčů v souhrnu něco predikuje** – to je legální, veřejné a legitimní výzkumný směr, ne insider trading.

Jedna věc, kterou musím zdůraznit i když nechceš slyšet HFT srovnání: **hlavní riziko retail kvanta není "nemám edge", je to bugy, overfitting a emoční rozhodnutí v panice**. Realisticky tvoje první rok/dva pravděpodobně stráví hledáním, proč ti backtest lže (look-ahead bias, survivorship bias, přeplácané poplatky v modelu), víc než hledáním skutečné alfy. To není pesimismus, to je jak to fakt vypadá i u zkušenějších lidí.

---

## Teď k učení kódu

Než začnu chrlit vysvětlení, potřebuju vědět, odkud startuju – abych netrávil čas vysvětlováním věcí, co už znáš, ani nepředpokládal znalosti, co nemáš.

---

# you asked

message time: 2026-08-16 22:59:48

Q: Kdyz vidis v Pythonu 'def nazev_funkce(parametr):', vis presne co to znamena a k cemu to slouzi?
A: Matne, potreboval bych pripomenout

Q: Setkal ses uz s pojmy jako for smycka, if/else podminka, try/except?
A: S nekterymi ano

Q: Jak chces postupovat pri projizdeni kodu?
A: Nejmensi soubor cely od zacatku (ohlcv.py)

---

# claude response

Thinking

Since the user has a shaky grasp of functions but some familiarity with loops and conditionals, I'll teach through ohlcv.py from the top, starting with imports and config, then walking carefully through the first function definition to build up their understanding of syntax step by step.…

Dobrá volba – 108 řádků je zvládnutelné a je to soubor, který už vidíš fungovat, takže spojíš teorii s něčím reálným. Půjdeme po **malých kouscích**, ne celý najednou – zastavím se a počkám na tvoje potvrzení, než půjdu dál.

## Blok 1: Docstring a importy (řádky 1-22)

```python
"""
src/ingestion/ohlcv.py

Downloads OHLCV data via yfinance and stores it as Parquet files.
...
"""
```

Tohle na začátku, v trojitých uvozovkách `"""`, je **docstring** – "dokumentační string". Python ho ignoruje jako kód (nic to nedělá), je to jen text pro lidi, co si soubor otevřou, aby hned věděli, k čemu je. Konvence: první soubor v projektu má nahoře popis sebe sama.

```python
from __future__ import annotations
```

Tohle je trochu technická vychytávka – umožňuje ti psát typové nápovědy (za chvíli vysvětlím, co to je) modernějším způsobem, i na starších verzích Pythonu. Nemusíš přesně chápat proč, stačí vědět, že to bývá první řádek u novějšího Python kódu.

```python
import logging
from pathlib import Path

import pandas as pd
import yfinance as yf
```

**`import`** = "chci použít kód, co napsal někdo jiný (nebo je součástí Pythonu), místo abych ho psal znovu". Rozdíl mezi dvěma styly:
- `import logging` → později píšeš `logging.neco()` (celý název)
- `import pandas as pd` → dáváš tomu **přezdívku** `pd`, protože `pandas.neco()` psát pořád dokola by byla otrava. `pd` a `pd.DataFrame` jsou naprosto univerzální konvence v Pythonu, uvidíš to v každém cizím kódu.
- `from pathlib import Path` → z knihovny `pathlib` chceš **jen jednu konkrétní věc** (`Path`), ne celou knihovnu.

**Co to jsou ty čtyři knihovny:**
- `logging` – zabudovaná v Pythonu, na hezké vypisování zpráv do konzole (to jsou ty řádky co vidíš při běhu jako `[INFO] Stahuji AAPL...`)
- `pathlib.Path` – práce s cestami k souborům/složkám nezávisle na Windows/Mac/Linux (proto to funguje stejně na tvém ThinkPadu i na Raspberry Pi)
- `pandas` – knihovna na tabulková data (to jsou ty `DataFrame` tabulky, co jsi viděl v `explore_data.py`)
- `yfinance` – knihovna, co za tebe komunikuje s Yahoo Finance serverem

---

Zastavím se tady. Než půjdu na "Config" sekci (řádky 24-44), dává ti smysl rozdíl mezi `import logging` a `import pandas as pd`? A je jasné, k čemu je docstring nahoře?

---

# you asked

message time: 2026-08-16 23:04:04

actually jo! kamo ty ses skvelej tohle je super způsob uceni se!! pokračuj!!!

---

# claude response

Skvělé, jedeme dál!

## Blok 2: Konfigurace (řádky 24-36)

```python
# --- Config -----------------------------------------------------------
```

Tohle je jen **komentář** – cokoliv za `#` Python úplně ignoruje, slouží to jen jako vizuální oddělovač pro člověka, co soubor čte (rozděluje ho na "sekce"). Žádná magie, čistě kosmetika.

```python
TICKERS = [
    "AAPL",
    "MSFT",
    "SPY",
    # doplň si vlastní seznam
]
```

Tohle je **proměnná** `TICKERS`, které přiřazuješ **list** (seznam) – v Pythonu se seznam píše v hranatých závorkách `[ ]`, položky oddělené čárkou. Tady je to seznam **textových řetězců** (stringů) – všimni si uvozovek kolem `"AAPL"`. Bez uvozovek by Python hledal proměnnou jménem AAPL, což by spadlo na chybu, protože žádná taková neexistuje.

VŠIMNI SI konvence: `TICKERS` je psáno **velkými písmeny**. To není povinnost Pythonu, je to jen **konvence mezi programátory** – "tohle je konstanta, hodnota, co se v průběhu běhu programu nemění, nastavuje se jednou nahoře a pak se jen čte". Kdybys viděl v cizím kódu `tickers` malým, znamenalo by to "tohle je normální proměnná, co se může měnit". Je to čistě dohoda, Python to sám nekontroluje.

```python
INTERVAL = "1h"      # "1m","5m","15m","1h","1d", ... (viz yfinance docs)
PERIOD = "730d"       # max pro 1h interval; pro "1d" muzes dat "max"
```

Dvě další konstanty, tentokrát ne seznam, ale jednotlivý **string** (text). Komentáře za `#` na stejném řádku ti připomínají, jaké další hodnoty by šly použít.

```python
OUTPUT_DIR = Path("data/raw/ohlcv")
```

Tady se poprvé použije ta `Path`, co jsme importovali. `Path("data/raw/ohlcv")` **vytvoří objekt**, který reprezentuje cestu ke složce – ne obyčejný text, ale speciální typ, který umí věci jako "existuje tahle složka?", "vytvoř mi ji, pokud neexistuje", spojovat cesty pomocí `/` (uvidíš to v dalších blocích). Proto se to nepíše jen jako `OUTPUT_DIR = "data/raw/ohlcv"` (obyčejný text) – `Path` objekt má navíc užitečné schopnosti.

---

**Kontrolní otázka, abych věděl, jestli mám zpomalit nebo zrychlit:** Rozumíš rozdílu mezi `TICKERS = [...]` (seznam) a `INTERVAL = "1h"` (jednotlivý string)? A dává smysl, proč `OUTPUT_DIR` používá `Path(...)` místo obyčejného textu v uvozovkách?

---

# you asked

message time: 2026-08-16 23:06:00

asi potrebuju lehce dovysvetlit uplne základy, kdyz jsi tak dobry ucitel :) zvladnes nejak hezky popsat zaklady pythonu? úplně od maličkosti jako proměnné, seznamy a tak?

---

# claude response

Thinking

They want a proper ground-up primer on Python basics, starting from absolute zero - variables, data types, lists. I should build this tied back to their own code where relevant to keep it engaging, covering the essentials without overwhelming them.

I'll also briefly touch on dictionaries since they'll encounter them in sec_edgar/fred, plus basic operations and indentation rules. I'll keep everything conc…

Jasně, zpomalíme a projdeme si to pořádně – tohle je nejdůležitější základ, na kterém všechno ostatní stojí. Zkoušej si to rovnou psát do Python shellu (napiš `python` do terminálu), ať to vidíš živě, ne jen čteš.

## Proměnná – "pojmenovaná krabička"

Nejlepší mentální obrázek: proměnná je **krabička s cedulkou**, do které si uložíš hodnotu, abys ji mohl použít později, aniž bys ji musel psát pořád znovu.

```python
vek = 17
```

Tady jsi vytvořil krabičku se jménem `vek` a dal do ní hodnotu `17`. Znak `=` v Pythonu **neznamená "rovná se" jako v matematice** – znamená **"přiřaď do"**. Čti to zprava doleva: "vezmi hodnotu 17 a ulož ji do krabičky jménem vek".

```python
>>> vek = 17
>>> print(vek)
17
>>> vek = 18
>>> print(vek)
18
```

Vidíš – hodnotu v krabičce můžeš kdykoliv **přepsat**. `print()` je zabudovaná funkce, co ti hodnotu z krabičky vypíše na obrazovku.

## Základní datové typy

Ne každá hodnota je stejná – Python rozlišuje, o jaký **typ** dat jde:

```python
jmeno = "Tomas"          # str (string) - text, VŽDY v uvozovkách
pocet_akcii = 42          # int (integer) - celé číslo
cena = 178.55             # float - desetinné číslo
je_aktivni = True         # bool - jen True nebo False, nic mezitím
```

Zkus si:
```python
>>> type(vek)
<class 'int'>
>>> type("AAPL")
<class 'str'>
```

`type()` ti řekne, jaký typ hodnota má. **Proč na tom záleží?** Protože s různými typy se dělají jiné operace. `"5" + "3"` (dva stringy) dá `"53"` (spojení textu), zatímco `5 + 3` (dvě čísla) dá `8` (sčítání). Tohle je klasický zdroj chyb u začátečníků – Python se nezeptá "myslel jsi to jako text nebo číslo", prostě udělá to, co typ říká.

## Seznam (list) – krabička na víc věcí v pořadí

```python
tickery = ["AAPL", "MSFT", "SPY"]
```

Seznam v hranatých závorkách `[ ]`, položky oddělené čárkou – přesně jako `TICKERS` v tvém `ohlcv.py`. Klíčová vlastnost: **položky mají pořadí a k jednotlivé položce se dostaneš přes její pozici (index)**.

```python
>>> tickery = ["AAPL", "MSFT", "SPY"]
>>> tickery[0]
'AAPL'
>>> tickery[1]
'MSFT'
>>> len(tickery)
3
```

**Kriticky důležitá past pro každého začátečníka: Python počítá od nuly, ne od jedné.** `tickery[0]` je první prvek, `tickery[1]` druhý, `tickery[2]` třetí (poslední). `len()` ti řekne, kolik prvků seznam má.

```python
>>> tickery.append("GOOGL")
>>> tickery
['AAPL', 'MSFT', 'SPY', 'GOOGL']
```

`.append()` přidá novou položku na konec. Tohle je **metoda** – funkce, co "patří" k danému objektu (seznamu). Všimni si tečkové notace `tickery.append(...)` – uvidíš ji všude (`df.describe()`, `logger.info()` – to samé jako `pd.DataFrame` s tečkou, jen na jiných objektech).

## Slovník (dict) – páry klíč → hodnota

Tohle uvidíš v `fred.py` a `sec_edgar.py`, tak radši hned zmíním. Místo pořadí (jako u seznamu) má slovník **pojmenované přihrádky**:

```python
nastaveni = {
    "interval": "1h",
    "period": "730d",
}
```

```python
>>> nastaveni["interval"]
'1h'
>>> nastaveni["period"]
'730d'
```

Místo čísla (indexu) přistupuješ přes **klíč** (text v uvozovkách). Přesně tohle dělá `settings.get("ohlcv", {}).get("tickers", ...)` v kódu, co jsme psali – jde do slovníku (co vznikl načtením `settings.yaml`) a hledá hodnotu pod klíčem `"ohlcv"`.

## Odsazení (indentation) – Python "bloky"

Tohle je pro Python **naprosto zásadní** a jinačí než většina jazyků. Zatím jsme to neřešili, ale je to nutné vědět, než půjdeme na funkce/podmínky/smyčky (což je přesně další blok v `ohlcv.py`):

```python
if vek >= 18:
    print("Jsi dospělý")
    print("Tohle se taky vypíše, protože je to odsazené stejně")
print("Tohle se vypíše VŽDY, protože není odsazené")
```

**Odsazení (mezery na začátku řádku) v Pythonu určuje, co "patří dovnitř" bloku kódu.** V jiných jazycích (C, JavaScript) se bloky ohraničují složenými závorkami `{ }`. Python místo toho striktně vyžaduje konzistentní odsazení – standardně **4 mezery** (VSCode to dělá automaticky, když stiskneš Tab). Pokud odsazení popleteš, dostaneš `IndentationError`.

---

Tohle je fakt jádro všeho – zbytek (funkce, smyčky, podmínky) na tomhle jen staví. Zkus si prosím do Python shellu napsat pár vlastních proměnných, list a slovník, ať to máš v prstech. Jakmile ti to sedí, vrátíme se zpátky do `ohlcv.py` bloku 2 (kde jsme skončili) a půjdeme na funkce – `def download_ticker(...)` – kde přesně tohle všechno uvidíš v akci.

---

# you asked

message time: 2026-08-16 23:14:00

chapu treba ze TICKERS je list, jen nevim jak vypsani nazvu instrumentů funguje v návaznosti s dalsim kodem, rozumis? a chapu ze capslock=nebude se to menit ale proč to tak je? kdo to tak rekl nebo co nam dava tu jistotu? za chvíli jdu spat tak nemam komp ale dodelame ten prvni soubor co jsme rozdělali

---

# claude response

Thinking

The user wants two things clarified: how the TICKERS list actually flows into the rest of the code, and whether the all-caps naming is an enforced rule or just a convention. I should explain that capitalization is purely a human/community convention for signaling constants—Python itself doesn't enforce or check it, so there's no real "certainty" it won't change, just a shared expectation among programmers.

For the…

Skvělé otázky, obě jdou přesně do hloubky, kterou potřebuješ.

## Odkud kam ten seznam "cestuje"

Podívej se na úplně poslední řádky souboru:

```python
if __name__ == "__main__":
    download_ohlcv(TICKERS, INTERVAL, PERIOD, OUTPUT_DIR)
```

Tohle je moment, kdy se `TICKERS` (ten seznam nahoře) **předá jako vstup** do funkce `download_ohlcv`. Teď se pojď podívat, jak ta funkce vypadá:

```python
def download_ohlcv(tickers: list[str], interval: str = INTERVAL, ...):
    for ticker in tickers:
        ...
```

Všimni si něčeho důležitého: nahoře je proměnná `TICKERS` (velkými), ale uvnitř funkce se najednou jmenuje `tickers` (malými) a je to **jiné jméno pro tu samou hodnotu**, dokud ji tam nosíš. Když zavoláš `download_ohlcv(TICKERS, ...)`, Python řekne: "ok, hodnotu, co je v `TICKERS`, teď uvnitř téhle funkce pojmenuju `tickers` (podle toho, jak si funkce svůj parametr nazvala)". Je to jako bys krabičku s nálepkou "TICKERS" na chvíli přelepil nálepkou "tickers" – obsah (ten samý list tří jmen) zůstává identický.

Pak přichází `for ticker in tickers:` – **cyklus**, který vezme seznam a **postupně, jeden po druhém, vytáhne každou položku** a na chvíli ji uloží do proměnné `ticker` (jednotné číslo, bez "s" – další konvence, "jedna věc ze seznamu víc věcí"). První průchod: `ticker = "AAPL"`, druhý průchod: `ticker = "MSFT"`, třetí: `ticker = "SPY"`. Uvnitř cyklu se pak s tím jedním tickerem (`"AAPL"`) volá `download_ticker(ticker, ...)` – další funkce, co stáhne data jen pro tenhle jeden.

Takže cesta je: **statický seznam nahoře → předán jako vstup do funkce → cyklus ho rozseká na jednotlivé kusy → každý kus zpracován samostatně**. Tohle je fakt jeden z nejběžnějších vzorců v programování vůbec, uvidíš ho furt.

## Proč velká písmena u konstant – a upřímná odpověď na "kdo to řekl"

Tady musím být přesný, protože tvá otázka míří na něco důležitého: **Python sám o sobě velká písmena vůbec nekontroluje ani nevynucuje.** Neexistuje žádné pravidlo jazyka, které by ti zabránilo napsat později v kódu `TICKERS.append("NVDA")` nebo dokonce `TICKERS = ["něco jiného"]` – Python by to bez mrknutí oka provedl. **Ta "jistota", že se to nezmění, není technická – je to jen slib mezi programátory.**

Je to konvence z dokumentu jménem **PEP 8** (oficiální stylový průvodce pro psaní Pythonu, komunitně uznávaný standard, ne vynucené pravidlo). Smysl: když čteš cizí kód a vidíš `NECO_VELKYMI`, okamžitě víš "tohle je nastavovací hodnota, nastavená jednou nahoře, neočekávej že se mění za běhu" – šetří ti to čas při čtení, protože nemusíš pátrat, jestli se to někde tajně přepisuje. Je to totéž jako když lidi dodržují pravidlo "auta jezdí vpravo" – nikdo tě fyzicky nezastaví, když pojedeš vlevo, ale je to sdílená dohoda, díky které systém funguje předvídatelně.

---

Dobrý bod na zastavení pro dnešek – zítra/příště navážeme přesně tam, kde jsme přestali: funkce `def download_ticker(...)`, kde uvidíš přesně tenhle typ (parametry, typové nápovědy jako `ticker: str`) v akci naživo. Vyspi se dobře!

---

# you asked

message time: 2026-08-16 23:24:57

jeste nez pujdu, co mi muze pomoct na teto ceste? mam si koupit knihu na quant trading? Python? koupit tve pro? vic používat github copilota? premyslej komplexne

---

# claude response

Dobrá otázka na závěr večera – a přesně tady chci být upřímný, ne prodejní, i tam kde se to týká Anthropicu.

## Co bych dal jednoznačně na první místo: **structured free kurz na Python základy**

**CS50P (Harvard, zdarma, cs50.harvard.edu/python)** – nejlepší volba, co znám. Je to strukturovaný, na projektech založený kurz, jde od nuly, má cvičení s automatickým testováním (víš hned, jestli to funguje). Zabere pár týdnů v pohodovém tempu. Důvod, proč tohle doporučuju před knihou: **aktivní psaní kódu s okamžitou zpětnou vazbou** se učí rychleji než pasivní čtení. Kniha typu "Automate the Boring Stuff" (taky zdarma online, automatetheboringstuff.com) je dobrý doplněk/referenční příručka, ale jako jediný zdroj bych ji nedoporučoval – chybí jí ten "udělej a hned se dozvíš, jestli to funguje" prvek.

## Kniha na quant konkrétně – ale ne hned

**Zatím ne.** Lopez de Prado ("Advances in Financial Machine Learning"), co jsme zmiňovali, je psaný pro lidi, co už umí programovat a znají statistiku na docela pokročilé úrovni – v tuhle chvíli by ti to spíš ublížilo (frustrace z nesrozumitelnosti) než pomohlo. Až budeš rozumět Pythonu solidně (řekněme za pár měsíců), doporučím konkrétní další krok. Prozatím je tvůj vlastní projekt + tenhle typ rozebírání kódu lepší "učebnice" než cokoliv v knihkupectví, protože je to *tvoje* věc, na které ti záleží – motivace u učení se kódování dělá obrovský rozdíl.

## GitHub Copilot – tady budu upřímně proti, aspoň teď

Máš ho zdarma přes student pack, ale **při tomhle stupni znalostí bych ho vypnul nebo minimálně ignoroval**. Copilot ti našeptává celé řádky/bloky kódu dřív, než sám přemýšlíš, jak by měly vypadat – u někoho, kdo se teprve učí, co `for` smyčka nebo `def` znamená, to vytváří falešný pocit "rozumím tomu", zatímco ve skutečnosti jen přijímáš návrhy. Až budeš základy ovládat (umět bez pomoci napsat vlastní funkci, smyčku, podmínku), Copilot se stane skvělým akcelerátorem na nudné/opakující se části kódu. Teď by tě spíš zpomalil v tom, co skutečně potřebuješ – porozumění.

## Claude Pro – upřímná odpověď, ne prodejní

Nebudu tě přesvědčovat, že to nutně potřebuješ. Pravda je: Pro dává vyšší limity zpráv a přístup k výkonnějším modelům, což se hodí, pokud narážíš na limity uprostřed dlouhého vyučování (jako dneska, kdy jsme přemýšleli o přechodu do nového chatu). Jestli tenhle typ intenzivní, dlouhé konverzace budeš dělat pravidelně, mohlo by se to vyplatit čistě prakticky. Ale není to nutnost pro to, co děláš – free tier ti umožní pokračovat, jen s omezeními na délku/frekvenci. Je to tvoje rozhodnutí podle rozpočtu, ne něco, co bych ti tlačil.

## Matematika/statistika – tohle podceňuješ na vlastní nebezpečí

Viděl jsi dnes p-hodnoty a korelace a bylo to nové. Quant bez slušných statistických základů narazí na strop dřív než bez programovacích dovedností. **Khan Academy (zdarma) – sekce statistika a pravděpodobnost** je skvělý, nenáročný start, jde to dělat souběžně s Pythonem, ne po něm.

## Co bych naopak nedělal

**Nevrhej se do quant Discord/Reddit komunit (r/algotrading apod.) jako primární zdroj učení.** Je tam hodně šumu, přehnaného sebevědomí a lidí co prodávají "signály" nebo kurzy pochybné kvality. Občas se tam najde dobrá diskuze, ale jako začátečník těžko rozeznáš zrno od plev. Radši se tam podívej později, až budeš mít vlastní úsudek na to, co je seriózní a co ne.

---

**Moje upřímné pořadí priorit:** CS50P (Python základy) > Khan Academy statistika (souběžně, klidně pomaleji) > pokračování na tomhle projektu se mnou > *až pak* Copilot a specializovaná quant literatura. Claude Pro je čistě otázka pohodlí/rozpočtu, ne nutnost.

Dobrou noc – příště naváž na `download_ticker()` funkci přesně tam, kde jsme skončili.

---

# you asked

message time: 2026-08-17 13:54:58

bojim se ze nejsem schopnej u toho zustat... bych se musel dat cil na dva dny nebo tak... pokracujme. dodelame vysvetlovani souboru a budeme makat dal

---

# claude response

Chápu tu obavu – a je to fér realistický strach, ne slabost. Jedna praktická rada, pak jedeme dál: **nedávej si cíl "2 dny v kuse programovat"**, to je recept na vyhoření po 2 dnech. Radši **15-20 minut denně, i o víkendu, i když se nechce** – konzistence v malých dávkách vyhrává nad nárazovým maratonem, obzvlášť u učení. Klidně si nastav telefon na připomínku. Teď zpátky do kódu.

## Blok 3: Funkce `download_ticker` (řádky 47-73) – nejdůležitější část souboru

```python
def download_ticker(ticker: str, interval: str, period: str) -> pd.DataFrame | None:
```

Rozeberme **úplně každý kousek** tohohle jednoho řádku, protože je tam toho hodně najednou:

- **`def`** = "definuji funkci" (klíčové slovo, po kterém vždycky následuje jméno funkce)
- **`download_ticker`** = jméno, které si funkce dává – odteď kdekoliv v kódu napíšeš `download_ticker(...)`, Python skočí sem a provede, co je uvnitř
- **`(ticker: str, interval: str, period: str)`** = **parametry** – vstupy, které funkce potřebuje, aby mohla pracovat. Když funkci zavoláš, musíš jí dát tyhle tři věci (v tomhle pořadí, pokud je nepojmenuješ jinak)
- **`: str`** za každým parametrem = **typová nápověda** (type hint) – říká "očekávám, že tohle bude text". Důležité: **Python tohle ve skutečnosti nekontroluje za běhu** – je to jen nápověda pro tebe (a pro VSCode, co ti pak podtrhne chybu červeně, když se spleteš) – jako komentář, co ale editor umí aktivně využít
- **`-> pd.DataFrame | None`** = co funkce **vrátí** na konci. Buď tabulku dat (`pd.DataFrame`), nebo `None` (v Pythonu speciální hodnota znamenající "nic", "prázdno") – to `|` znamená "buď/nebo"

Takže celý řádek v lidské řeči: *"Vytvářím funkci jménem download_ticker. Potřebuje tři texty (ticker, interval, period). Vrátí buď tabulku dat, nebo nic."*

```python
    """Stahne OHLCV data pro jeden ticker. Vrati None pri chybe/prazdnych datech."""
```

Docstring **uvnitř funkce** – stejný princip jako na začátku souboru, jen tady popisuje konkrétně tuhle funkci. Pokud v editoru najedeš myší na `download_ticker` kdekoliv jinde v kódu, VSCode ti tenhle text ukáže jako nápovědu.

```python
    try:
        df = yf.download(ticker, interval=interval, period=period, auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"{ticker}: fetch failed - {e}")
        return None
```

**`try`/`except`** – tohle je "zkus tohle, a pokud to selže, neshoď celý program, ale udělej tohle místo toho". Věci se dějí mimo tvou kontrolu – internet vypadne, Yahoo server neodpovídá, ticker neexistuje. Bez `try/except` by jakákoliv taková chyba **shodila celý skript** (viz `Traceback` chyby, co jsi viděl minule). S `try/except` řekneš "pokud se něco pokazí uvnitř `try` bloku, skoč do `except` a udělej tohle" – tady: zaloguj chybu a **vrať `None`** (funkce skončí, řekne "nepovedlo se").

`as e` – zachytí konkrétní chybovou zprávu do proměnné `e`, abys ji mohl vypsat (vidíš ji v tom `f"{ticker}: fetch failed - {e}"`).

**f-string** – všimni si `f"..."` s `{ticker}` uvnitř. To `f` před uvozovkami znamená "do tohohle textu vlož hodnoty proměnných tam, kde jsou v `{}`". Takže pokud `ticker = "AAPL"`, výsledek bude doslova text `"AAPL: fetch failed - ..."`. Bez toho `f` by se `{ticker}` vypsalo doslovně jako text `{ticker}`, ne jako hodnota.

```python
    if df is None or df.empty:
        logger.warning(f"{ticker}: no data returned (spatny ticker? delisted?)")
        return None
```

**`if`** = podmínka – "pokud je tohle pravda, udělej tohle". Tady: pokud `df` je `None` (stahování selhalo úplně) **NEBO** (`or`) je `df` prázdné (`df.empty` – žádné řádky, i když stahování formálně "prošlo", třeba u špatného tickeru), zaloguj varování a skonči s `None`.

```python
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
```

`isinstance(neco, typ)` – "je tahle věc daného typu?". Tohle řeší praktickou zvláštnost – yfinance občas vrátí sloupce v komplikovanější struktuře (`MultiIndex`), tenhle kód to zjednoduší, pokud k tomu dojde. Nemusíš do detailu chápat MultiIndex teď, důležité je pochopit **vzorec**: "zkontroluj podmínku, a pokud platí, uprav data".

```python
    df.index.name = "timestamp"
    df = df.reset_index()
    df["ticker"] = ticker
    return df
```

Poslední tři řádky: pojmenuje časovou osu dat jako `"timestamp"`, "vytáhne" ji z indexu do normálního sloupce (`reset_index()`), přidá nový sloupec `"ticker"` s hodnotou aktuálního tickeru (aby ses v datech pak vyznal, když budeš mít víc tickerů dohromady), a **vrátí** hotovou tabulku ven z funkce (`return df`) – tohle je ta hodnota, kterou dostaneš, když někde jinde napíšeš `vysledek = download_ticker(...)`.

---

## Blok 4: Funkce `save_parquet` (řádky 76-80) – krátká, rychle

```python
def save_parquet(df: pd.DataFrame, ticker: str, interval: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ticker}_{interval}.parquet"
    df.to_parquet(path, index=False)
    return path
```

- `out_dir.mkdir(parents=True, exist_ok=True)` – vytvoří složku, pokud neexistuje (`mkdir` = "make directory"). `parents=True` znamená "vytvoř i všechny nadřazené složky, co chybí", `exist_ok=True` znamená "neházej chybu, pokud už složka existuje"
- `out_dir / f"{ticker}_{interval}.parquet"` – tohle je ta "užitečná schopnost" `Path` objektu, co jsem sliboval dřív: `/` mezi dvěma cestami je spojí správně (`data/raw/ohlcv` + `AAPL_1h.parquet` → `data/raw/ohlcv/AAPL_1h.parquet`), a to i napříč Windows/Mac/Linux, i když každý systém interně používá jiný oddělovač (`\` vs `/`)
- `df.to_parquet(path, index=False)` – metoda přímo na tabulce, uloží ji na disk ve formátu parquet
- `return path` – vrátí cestu, kam se soubor uložil

---

Tím máš `download_ticker` a `save_parquet` vysvětlené kompletně, a `download_ohlcv` (poslední velkou funkci) jsme z většiny probrali už minule přes tu `for` smyčku. **Celý soubor je teď probraný.** Jak se cítíš – chceš, ať `download_ohlcv` projdeme ještě jednou celou pohromadě pro jistotu, nebo máš pocit, že to sedí a můžeme jít na praktické cvičení (např. zkusit sám drobně upravit tenhle soubor, ať si to osaháš rukama)?

---

# you asked

message time: 2026-08-17 17:04:08

vic vysvetli to "potrebuje tri texty". nevim jak to funguje ve vztahu - je to neco co mi ta funkce bude davat, neco co bude chtit, neco jineho? rozdil mezi """ a #. jak funguje celkove kod? jak premysli pocitac kdyz o cte? specificky mne prekvapilo ze kdyz dam do else "none" tak to spadne. ja cekal ze to bude spis nejak navazovat na nejakou funkci ale to jsem si asi spletl s "true/false). vic rozeber "if df is None or df.empty" nechapu hlavne tu df.empty cast. chapu jak funguje ale vic obecne z programatorkseho pohledu.

---

# claude response

Skvělé otázky, tohle jsou přesně ty věci, co dělají rozdíl mezi "umím to okopírovat" a "rozumím tomu". Jdu do hloubky na každou.

## Funkce jako "stroj" – vstup, zpracování, výstup

Nejlepší mentální model: funkce je jako **kuchyňský mixér**. Má:
- **Vstup** (parametry) – co do něj naházíš (ingredience)
- **Zpracování** (tělo funkce, kód uvnitř) – co s tím udělá
- **Výstup** (return) – co ti z něj vyleze

```python
def download_ticker(ticker: str, interval: str, period: str) -> pd.DataFrame | None:
```

"Potřebuje tři texty" znamená: **než tuhle funkci vůbec můžeš spustit, musíš jí dát tři věci**. Je to jako recept, co říká "potřebuješ 2 vejce, mouku, mléko" – bez nich recept nejde udělat. Když v kódu píšeš:

```python
vysledek = download_ticker("AAPL", "1h", "730d")
```

Tak `"AAPL"` se přiřadí parametru `ticker`, `"1h"` parametru `interval`, `"730d"` parametru `period` (podle **pořadí**, ve kterém jsou napsané). Uvnitř funkce se pak s `ticker` pracuje, jako kdyby to byla normální proměnná s hodnotou `"AAPL"`. Funkce **nedostane** informaci "od koho to dostala" – nezajímá ji, jestli `"AAPL"` přišlo od `TICKERS[0]` nebo jsi to napsal ručně, prostě dostane hodnotu a pracuje s ní.

Na konci `-> pd.DataFrame | None` říká, co funkce **vrátí zpátky** tomu, kdo ji zavolal – to je ten `vysledek` v mém příkladu výše. Je to **jednosměrná ulička**: vstupy jdou dovnitř, funkce se provede, jeden výstup jde ven.

## `"""..."""` vs `#` – proč existují oba

Tohle je dobrý postřeh, že ses zeptal, protože rozdíl je reálný, ne kosmetický:

- **`#` komentář** – Python ho při čtení kódu úplně zahodí, jako by tam nebyl. Nikde v běžícím programu se k němu nedostaneš.
- **`"""docstring"""`** – Python ho **taky nevykoná** jako kód, ale **uloží si ho** jako součást té funkce/souboru. Můžeš se na něj zeptat i za běhu programu:

```python
>>> print(download_ticker.__doc__)
Stahne OHLCV data pro jeden ticker. Vrati None pri chybe/prazdnych datech.
```

Proto VSCode umí zobrazit nápovědu, když najedeš myší na název funkce – čte přímo tenhle docstring. `#` komentář by takhle vytáhnout nešlo. Praktické pravidlo: **docstring = "co tahle funkce/soubor dělá celkově"** (jedna/dvě věty nahoře), **`#` = drobná poznámka k jednomu konkrétnímu řádku**.

## Jak počítač "čte" kód – tohle je klíčové

Představ si to jako **čtení instrukcí v kuchařce shora dolů, řádek po řádku**, ALE s jednou zvláštností: **`def` blok se při čtení "přeskočí" a jen si zapamatuje, kde je** – tělo funkce se **nevykoná v momentě, kdy ho Python čte poprvé**, ale až ve chvíli, kdy ji **někdo zavolá**.

Takže v tvém souboru:
1. Python přečte `def download_ticker(...): ...` → **nezpustí ho**, jen si řekne "aha, existuje funkce jménem download_ticker, tady je recept, kdyby ji někdo potřeboval"
2. Stejně tak přeskočí `def save_parquet` a `def download_ohlcv`
3. Dojde na `if __name__ == "__main__": download_ohlcv(TICKERS, ...)` – **tady** se poprvé něco skutečně spustí
4. Python "skočí" dovnitř `download_ohlcv`, běží tam řádek po řádku
5. Narazí na `download_ticker(ticker, interval, period)` uvnitř `for` smyčky → **skočí** do `download_ticker`, provede celé jeho tělo, a až narazí na `return df` (nebo `return None`), **skočí zpátky** přesně tam, odkud přišel, s tou vrácenou hodnotou v ruce
6. Pokračuje v `download_ohlcv` tam, kde přestal

Je to jako bys v kuchařce měl "viz recept na těsto na straně 12" – přeskočíš tam, uděláš těsto, vrátíš se zpátky na stránku, kde jsi byl, a pokračuješ s hotovým těstem v ruce.

## Tvoje nedorozumění s `return None` – tohle je důležité vyjasnit

Rozumím, kde vznikl zmatek. **`return None` sama o sobě NIKDY nezpůsobí pád programu.** `None` prostě znamená "tady je odpověď: nic". Funkce v pořádku doběhne, jen řekne "nemám pro tebe výsledek".

Kde `None` **může** způsobit pád, je **jinde, později**, když někdo **zapomene zkontrolovat**, že dostal `None`, a zkusí s ním pracovat, jako by to byla tabulka:

```python
vysledek = download_ticker("SPATNY_TICKER", "1h", "730d")  # vrátí None
print(vysledek.empty)  # PÁD! None nemá žádné .empty, protože není tabulka
```

Tohle by spadlo s chybou `AttributeError: 'NoneType' object has no attribute 'empty'`. A **přesně proti tomuhle pádu tě chrání ten `if` check**, na který se ptáš:

```python
if df is None or df.empty:
```

Tenhle řádek existuje **záměrně jako pojistka** – "než se pokusím dál pracovat s `df` jako s tabulkou, nejdřív ověř, že to skutečně tabulka je (není `None`) A že v ní něco je (není prázdná)". Takže tvůj instinkt "čekal jsem, že to bude nějak navazovat" je ve skutečnosti správný pocit, jen obráceně – `None` samo nikam nenavazuje, ale kód **musí explicitně ošetřit případ**, že dostal `None`, jinak by to spadlo o pár řádků/funkcí později.

## `df.empty` – atribut, ne metoda (a jak `if` vyhodnocuje pravdu)

Tady je rozdíl, který stojí za vysvětlení: `df.empty` **nemá závorky**, na rozdíl od `tickery.append("NVDA")`, co mělo. Proč?

- **Metoda** (`.append(...)`, s závorkami) = **akce, sloveso** – "udělej něco" (přidej položku, ulož soubor)
- **Atribut** (`.empty`, bez závorek) = **vlastnost, přídavné jméno** – "popiš mi fakt o sobě", žádná akce se neděje, jen se ptáš na hodnotu, co tabulka o sobě "ví"

`pandas` interně, kdykoliv vytvoří `DataFrame`, si spočítá a uloží spoustu takových vlastností (kolik má řádků, jestli je prázdný, jaké má sloupce...). `df.empty` je jedna z nich – vrátí `True`, pokud tabulka nemá žádné řádky, jinak `False`.

Teď k **celému výrazu** `df is None or df.empty`:

Python ho vyhodnocuje jako **jednu velkou otázku s odpovědí ano/ne**, sestavenou ze dvou menších otázek spojených slovem `or`:
- `df is None` → je `df` doslova ta speciální hodnota "nic"? (`True`/`False`)
- `df.empty` → má tabulka nula řádků? (`True`/`False`)
- `or` → "**stačí, aby ASPOŇ JEDNA** z nich byla `True`, a celý výraz je `True`"

`if` pak nedělá nic jiného, než že se zeptá: *"je to, co je za mnou, `True`, nebo `False`?"* Pokud `True`, provede se odsazený blok pod ním. Je jedno, jak komplikovaný ten výraz je (`is None`, `.empty`, `or`, `and`...) – na konci se to vždycky sesype do jediné hodnoty `True` nebo `False`, a to je jediné, co `if` zajímá.

**Praktický detail navíc**: `is None` se používá místo `== None` ze zvyklosti/přesnosti (`is` kontroluje "je to přesně tenhle samý objekt", `==` by teoreticky mohlo být obelstěno divnými vlastními typy) – zatím to jen vezmi jako "takhle se to na `None` prostě dělá", detail nemusíš řešit teď.

---

Sedí ti todle? Klidně se zeptej na cokoliv, co pořád vrtá hlavou, než půjdeme dál.

---

# you asked

message time: 2026-08-18 16:02:29

budeme na tom delat i s gemini. vcera me ucil programovat prakticky. daval mi problemy lidskymi analogiemi typu "posles asistenta do yfinance pro apple" a ja se u toho naucil neco o programování to bylo BOZI, to budem delat taky. v cem bys ted pokračoval? udelej nastin, shrnutí ukolu a překážek co nas cekaji, pojmj to detailne a komplexne od začátku, mvp az po nejdivočejší sny

---

# claude response

Thinking

The user wants a detailed, comprehensive roadmap from MVP to their wildest dreams, covering tasks and obstacles along the way, plus a note about using Gemini for practical programming teaching with analogies. Given the scope, I need to balance thoroughness with the lower effort setting while still delivering the comprehensive synthesis they're asking for.

I'm thinking this deserves a markdown artifact since it's a reference document they'll want to revisit, structured through phases from current foundation work through MVP completion to the multi-agent AI system vision, with a shorter guiding summary in chat alongside it.

Phase 1 covers expanding the ticker universe, parsing Form 4 XML for actual trade details, and building a hypothesis testing framework, with obstacles like overfitting, survivorship bias, and look-ahead bias. Phase 2 moves into research and alpha discovery with feature engineering, backtesting, and proper cross-validation, while flagging survivorship bias in free data sources and transaction cost modeling as key risks. Phase 3 turns validated signals into actual strategy rules with position sizing, risk management, realistic cost-adjusted backtesting, and paper trading via a broker API.

Phase 4 runs in parallel, covering infrastructure like the Raspberry Pi execution layer, scheduled compute jobs, Telegram notifications, backups, and health checks, with reliability and secrets security as ongoing concerns. Phase 5 is live trading with small real capital, where I want to honestly flag the practical obstacle that most jurisdictions require being 18 to open a brokerage account independently, so a 17-year-old would likely need a custodial account with a parent. Phase 6 is the ambitious long-term vision of a multi-agent, self-adapting AI trading system.…

Gemini s analogiemi zní skvěle jako doplněk – různí učitelé různým stylem se navzájem posilují, žádný problém. Pojďme na tu mapu.

## Fáze 0 – Základy (z velké části hotovo)

**Co máš:** OHLCV, SEC EDGAR metadata, FRED, funkční Git workflow, první (negativní) statistický test, a teď rozjeté učení Pythonu od nuly.

**Co zbývá dodělat, než je tahle fáze fakt uzavřená:** pokračovat v Python základech (funkce už umíš, dál budou smyčky do hloubky, podmínky, práce se soubory) souběžně s kódem, ne odděleně – přesně jak to teď děláme.

---

## Fáze 1 – Dokončení MVP (řádově týdny, tempem 15-20 min/den)

- **Rozšířit universe** z 2 firem na ~15-30 (různé sektory)
- **Doparsovat Form 4 XML** – skutečné nákup/prodej insiderů, ne jen metadata
- **Cross-sectional verze momentum testu** + první test na insider datech
- **Založit hypothesis_log.md** a od teď do něj psát každou hypotézu předem

**Překážky, které tu reálně narazíš:**
- **Survivorship bias** – tohle jsem zatím nezmínil a je to důležité. Yahoo Finance/yfinance ti dá data jen o firmách, co **dnes existují**. Firmy, co zkrachovaly nebo byly vykoupeny, v datech chybí – takže tvůj backtest bude systematicky moc optimistický (vidíš jen "přeživší"). Řešení existují (jiné datasety s delistovanými firmami), ale je to past, na kterou skoro každý začátečník padne.
- **Look-ahead bias** – používání informace, kterou bys v reálném čase v tu chvíli ještě neměl (např. finální revidovaná fundamentální data místo první zveřejněné verze). Budeme na to muset dávat pozor u SEC dat.
- Python prostředí bugy (jak jsme zažili s importy) – tohle bude pokračovat, je to normální součást učení, ne selhání.

---

## Fáze 2 – Výzkum a hledání alfy (měsíce)

- Feature engineering pipeline (systematické vytváření a testování featur, ne ad-hoc skripty)
- **Backtest engine v1** – zatím jednoduchý, vektorizovaný
- **Triple-barrier labeling**, **purged k-fold CV**, **walk-forward validace** (Lopez de Prado aparát, zmiňovaný na začátku)
- Selektivně přidat další datové zdroje **jen na základě toho, co výzkum ukáže jako slibné**, ne dopředu

**Překážky:** tohle je fáze, kde **most** lidí ztroskotá na **overfittingu** – najdou "strategii", co na historických datech vypadá skvěle, protože nevědomky přizpůsobili parametry přesně těm datům. Purged CV a walk-forward jsou obrana proti tomuhle, ale i s nimi to chce disciplínu a pokoru.

---

## Fáze 3 – Strategie a risk management (měsíce)

- Z ověřených signálů → konkrétní pravidla vstup/výstup
- Position sizing, stop-loss, portfoliová úroveň rizika
- Backtest s realistickými náklady (poplatky, slippage, spread)
- **Paper trading** – broker s free API pro simulovaný live provoz (Alpaca má solidní free paper trading)

**Překážky:** paper trading výsledky se často liší od backtestu (realita má víc tření, než modely počítají) – to je normální a je to důvod, proč se paper trading dělá, ne přeskakuje.

---

## Fáze 4 – Infrastruktura a automatizace (běží paralelně s fází 3-4)

- Raspberry Pi jako execution vrstva
- Ghettoserver na plánované/dlouhé výpočty
- Telegram bot, health checks, automatické zálohy na tower server
- Circuit breakers (výpadek proudu, burza neodpovídá – jak jsi zmiňoval na začátku)

**Překážky:** spolehlivost přes 3 fyzicky oddělené stroje je netriviální – síťové výpadky, synchronizace, bezpečnost API klíčů napříč stroji.

---

## Fáze 5 – Živý provoz s reálným (malým) kapitálem

Tady musím být na rovinu ohledně něčeho praktického, co ještě nikdo nezmínil: **je ti 17.** Ve většině jurisdikcí (Česko včetně) potřebuješ na otevření vlastního maklérského účtu **18 let**. Realisticky budeš buď potřebovat počkat, nebo řešit nějakou formu účtu s rodičem/opatrovníkem (custodial account), pokud něco takového broker, co zvolíš, vůbec nabízí. Tohle nijak nebrzdí *výzkum a vývoj* (paper trading jde dělat bez ohledu na věk), ale je dobré to mít v hlavě jako reálnou překážku pro fázi "obchoduju se skutečnými penězi", ne až narazíš na to za rok.

---

## Fáze 6 – "Nejdivočejší sny" (multi-agent AI systém)

Osobnosti pro/proti nákup, manažer rozhoduje, systém se sám adaptuje. Tohle je koncepčně zajímavé, ale **upřímně varuji**: každá přidaná vrstva komplexity (a AI agenti navrch jsou hodně vrstev) **znásobuje riziko overfittingu a ztráty schopnosti pochopit, proč systém dělá to, co dělá**. Než se tam dostaneš, budeš potřebovat fáze 1-5 fakt zvládnuté a ověřené – jinak stavíš složitou nadstavbu na nejistém základu.

---

**Realistický časový odhad** (ne slib, jen orientace): fáze 1 týdny, fáze 2-3 měsíce až přes rok při tempu vedle školy, fáze 5-6 spíš v horizontu let. To není odrazování – je to jen upřímné zarámování, ať víš, že "pomalu" je tady správné tempo, ne selhání.

Kam se chceš teď vrátit – zpátky do Pythonu (další kus `download_ohlcv` funkce), nebo chceš nejdřív založit ten `hypothesis_log.md`, ať máš z dnešní session i něco hmatatelného navíc?

---

# you asked

message time: 2026-08-18 17:54:27

pojdme udelat nejake mega nudne ale mega dulezite veci, zacneme treba tim logem. jeste chci trosku snit nad tim, jake funkce pridame, prosim :) pak pujdem dal, asi to xml parsovvani ne?

---

# claude response

## 1. Hypothesis log – nudné, ale bude tě to chránit před sebeklamem