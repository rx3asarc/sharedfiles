# THE PLAN — 73/27 allocation, Austria, long horizon

**Status:** FINAL (rev. 3). Supersedes rev. 1 and rev. 2.
**Date:** 2026-09-13
**Assumes:** a long horizon (10+ years) and no requirement for the capital within it. If that
assumption fails, this plan is the wrong instrument entirely.

> **Standing instruction for this document:** every numeric field requires a **named primary
> source and a retrieval date**. See §11 for the source register. Figures without one are
> marked as assumptions.

---

## 1 — THE ALLOCATION

```
┌────────────────────────────────────────────┐
│  73%   Global equity index        (base)   │
│  27%   Global X Uranium UCITS     (theme)  │
└────────────────────────────────────────────┘
```

The theme target **decays** — Rule 3, §4.

### Why 27% and not more

A 26-name policy-catalyst basket fell a **median −17.5%** in one quarter, worst name −72.9%.
*(n=26, one quarter, one macro regime — illustration, not evidence. §6.)*

At 27%, a theme halving costs roughly 13% of the portfolio. At 100%, it costs half the capital
on a first investment. **73/27 is the size where a bad outcome is survivable without
capitulating.**

### Why not zero

The mandate — uranium **and** microreactors — was stated explicitly and repeatedly. Reducing it
to zero substitutes a preference for an instruction. 27% honours it at a size that cannot do
terminal damage.

---

## 2 — WHAT THE THEME ACTUALLY PROVIDES

**Cameco is counted once.** A single position cannot serve two mandates.

| Exposure | Weight in fund | Weight in portfolio |
|---|---|---|
| Reactor developers — Oklo ~7.6%, NuScale ~3.9% | ~11.5% | **~3%** |
| Reactor fuel / enrichment — Centrus | ~3.7% | ~1% |
| Uranium producers — Cameco, UEC, Kazatomprom, NexGen, Paladin, Energy Fuels, Denison | ~47% | ~13% |
| Cameco's 49% Westinghouse stake (eVinci) | inside Cameco's ~15.6% | already counted |

```
Uranium mandate       -> satisfied at ~13% of the portfolio
Microreactor mandate  -> satisfied at ~3% of the portfolio
```

**This is a weakness and is recorded as one.** See §10, open item.

---

## 3 — COSTS, CORRECTED

```
Vanguard FTSE All-World (VWCE)   OCF 0.14%    <- rev. 1 said 0.22%; rev. 2 said 0.29%
Global X Uranium (URNU)          TER 0.65%
```

**Two consecutive errors on this field, and the second is instructive.** Rev. 2 corrected the
ISIN using a source page from which three other fields were read correctly — holdings count,
fund size, and index name — but transcribed the expense figure as 0.29%. The same page states
0.14%. **The source was read correctly three times and wrongly once.** Corrected against
Vanguard's own KIID and factsheet, which both state **0.14%**.

*(Vanguard cut the OCF from 0.19% to 0.14%; a 31 May 2026 factsheet still shows 0.19%. Always
date the figure.)*

---

## 4 — RULE CONFLICT RESOLVED

Rev. 1 held three rules that contradicted each other — no top-up below target, no adds beyond
target, and direct contributions to whichever side drifted. They cannot all hold.

> **RULE — the theme target decays on a published schedule and is maintained by
> contributions.**
>
> | Period | Theme target |
> |---|---|
> | Years 0–1 | 27% |
> | By year 5 | 22% |
> | By year 10 | 15% |
> | Thereafter | 15% floor |
>
> **Mechanism:** each new contribution is split in the target proportions. Nothing is bought
> outside that split; nothing is sold except under the exception below.
>
> **Exception — windfall capture only:** if the theme exceeds **target + 10 percentage points**,
> trim back to target.

**Deleted:** "never top up below 15%" and "no adds beyond target." The decaying target performs
both jobs.

**Is the decay intentional? Yes, explicitly.** Because contributions drive **~83%** of the
terminal outcome (§8), and **no forecasting edge in this sector was demonstrated anywhere in
this project** — backlog predicted nothing, dispersion inside the uranium complex was 21.7
points, and the one name that passed the framework and then outperformed may have done so
because of an acquisition rather than the model. A position with no demonstrated edge should
shrink.

**Consequence, stated plainly:** maintaining the target means contributions buy the theme when
it has fallen. That is the mechanical cost of a fixed target, and preferable to chasing whatever
rose.

---

## 5 — THE THIRD OPTION: WHICH MANDATE DID YOU MEAN MORE?

Rev. 1 and rev. 2 framed this as a shortfall — "accept ~3% microreactor, or add a position."
**That was the wrong frame.** The real choice is **which mandate matters more**, because no
single UCITS fund delivers both at weight.

### Option A — keep URNU as the theme

```
Tracks    Solactive Global Uranium & Nuclear Components
Holdings  56 · top-10 ~64%
Profile   uranium-heavy, some reactor
Mandates  uranium ~13% of portfolio · microreactor ~3%
TER       0.65%
```

### Option B — swap to a nuclear-technology fund

```
Fund      VanEck Uranium and Nuclear Technologies UCITS ETF
ISIN      IE000M7V94E1 · WKN A3D47K · ticker NUKL
TER       0.55%                  Holdings 25 · top-10 67.83%
AUM       EUR 2,013m             Launched 3 Feb 2023 · Ireland
```

Its top ten inverts the ratio — reactor, component and technology names dominate:

```
Cameco                    15.58%     (uranium + Westinghouse)
Oklo                       8.20%
Sprott Physical Uranium    6.94%     (physical metal)
NexGen Energy              6.83%
Samsung C&T                5.48%
IHI Corp                   5.32%     <- reactor components
AtkinsRealis Group         5.24%     <- nuclear engineering (CANDU)
Mitsubishi Heavy           4.90%     <- reactor technology
Fuji Electric              4.87%     <- reactor technology
Hitachi                    4.47%     <- reactor technology
```

**This is a materially different fund.** Where URNU is a uranium-producer index with reactor
names attached, NUKL is a nuclear-technology index with uranium holdings attached. It is
**more microreactor/technology**, **less mining** — the inverse emphasis.

**Trade-offs, stated:** fewer holdings (25 vs 56), higher concentration (top-10 67.83% vs ~64%),
smaller fund (€2.0bn vs ~€0.6bn), and it still carries Cameco as its largest position at 15.58%.
Higher reactor exposure is also higher regulatory and execution risk — the exact risk category
this project found most exposed to delays.

### Option C — split the theme

Half URNU, half NUKL. Satisfies both mandates at comparable weight, at the cost of managing two
positions and paying two TERs.

### The decision, reframed

> **Not:** "the microreactor mandate is underweight."
>
> **But:** "uranium and microreactors are different bets. Which did you mean more?"
>
> - If **uranium** is the point and reactors are a hedge → **Option A**.
> - If **reactor technology** is the point → **Option B**.
> - If both matter equally → **Option C**.

Under Option A, ~3% microreactor is a *deliberate* choice, not a shortfall. Under Option B, ~13%
uranium becomes the deliberate choice. **Either is defensible; the plan requires the choice to
be made rather than defaulted into.**

---

## 6 — NO STOP-LOSS: the structural reason

The backtest figures used in rev. 1 are demoted to **illustration only: n=26, one quarter, one
macro regime — not evidence.**

**1. A stop-loss is a price-based exit; the holding has no price-based thesis.** The thesis is a
multi-decade buildout. There is no price at which "the buildout happened" or "the buildout
failed." A percentage stop bears no relationship to the thing invested in.

**2. A stop converts ordinary volatility into permanent loss.** This sector's defining measured
characteristic is dispersion, not direction. A stop is triggered by dispersion. It guarantees
realising the drawdown and forfeits recovery — the only mechanism by which an equity position
pays you.

**3. The risk control is position size, not an exit trigger.** 73/27 with a decaying theme caps
damage at the allocation stage. Adding a stop double-counts the control while adding a failure
mode.

**4. Stops are for leverage and hard mandates. Neither applies.** They exist to prevent a
leveraged position being force-closed, or to satisfy a drawdown limit someone is bound by. This
is unleveraged and no such limit exists.

**5. It is unenforceable in practice.** A fund held at a Steuereinfach broker is not monitored
tick-by-tick. Any stop executes late, at a worse price, in exactly the conditions that
triggered it.

**Therefore: the exit is thesis-based, not price-based.** Volatility is the cost of the sector,
not a signal.

---

## 7 — WHAT NOT TO DO WHEN THE THEME FALLS

**New, and previously unstated.**

> **If the theme falls so far that 100% of contributions cannot restore the target weight over a
> reasonable period — do not sell the base to fund it.**
>
> The base is never sold to top up the theme. Not for rebalancing, not for conviction, not for
> any reason short of genuine need for the capital.

The reasoning is structural: the base is the instrument with **3,758 holdings and 0.14% costs**;
the theme is **~10 real positions** in a sector where no forecasting edge was demonstrated.
Liquidating the diversified asset to buy more of the concentrated one inverts the entire logic
of the allocation — and does so precisely when the concentrated position has just been shown to
behave badly.

**If the theme drifts below target and contributions cannot close the gap, the correct action is
to accept the drift.** The target is a direction, not an obligation. A permanently underweight
theme is a *better* outcome than a base raided to defend it.

---

## 8 — AUSTRIAN TAX, RESTATED

### The mechanic

**An accumulating fund does not avoid tax.** The fund's annual income is taxed as a deemed
distribution (*ausschüttungsgleiche Erträge*, agE) at **27.5% KESt**, whether or not cash is
paid out. Switching to distributing does not help — Austria taxes the income annually either
way. The wrapper is tax-neutral; only the cash-flow timing differs.

### The drag is an upper bound, not a point estimate

**Corrected.** Rev. 2 stated ~0.5%/yr as if fixed. It is a **ceiling**, for two reasons:

```
1  The agE base is income NET OF FUND EXPENSES.
   Gross dividend yield ~1.8%, fund OCF 0.14%
   => agE base ~= 1.66%, not 1.8%

2  Austria credits foreign withholding tax already paid
   at fund level (anrechenbare Quellensteuer) against the
   KESt due. Underlying US holdings are withheld at treaty
   rate inside the fund, and that credit reduces the
   additional KESt payable.
```

```
UPPER BOUND   27.5% x 1.8%   ~= 0.50% / yr
              actual is lower, by (1) and (2)
```

**The true figure is not known without the annual agE per unit** — published each year, 5–7
months after fiscal year end. It is observable, not a surprise. **Treat 0.5% as a ceiling.**

### The projection, net of tax

Assumptions, all stated: **20 years · gross nominal return 7% · dividend yield 1.8% · KESt 27.5%
on agE annually and on gains at exit · inflation 2% · annual contributions equal to 0.36 × the
lump sum · contributions monthly.** Fund costs are inside the 7% gross, not modelled
separately.

| Scenario | Nominal | **Real** |
|---|---|---|
| No tax at all (reference only) | 15.50× | 10.43× |
| Tax on annual agE, no exit CGT | 14.52× | 9.77× |
| **Tax on agE + CGT at exit — expected** | **13.45×** | **9.05×** |

**Lump sum alone, no contributions, net of all tax: 2.29× nominal · 1.54× real.**

### What the tax costs, and what contributions are worth

```
tax drag removes ~13% of terminal value      (15.50x -> 13.45x)
contributions are ~83% of terminal value     (2.29x -> 13.45x)
```

### Sensitivity — the assumptions dominate the allocation

```
gross return 5% -> 8%       10.99x  ->  15.00x     <- dominant factor
dividend yield 1.2% -> 2.2% 13.45x  ->  12.89x     <- minor
```

**The return assumption matters more than the 73/27 split.** Nothing here is precision; the
honest framing is a range.

---

## 9 — THE THEME FUND'S TAX POSITION, DOWNGRADED

The OeKB register shows **0,0000** for agE and all other fields. **Rev. 1 read that as "no tax
drag." That was wrong.**

### Both records are one fiscal year behind

```
URNU      FY ends 30.06.   reported 29.01.2026  ->  covers FY to 30.06.2025
Sprott    FY ends 31.03.   reported 20.10.2025  ->  covers FY to 31.03.2025
current fiscal year: NOT YET REPORTED (due ~Jan 2027)
```

**Correct reading:** *no taxable deemed distribution in the most recently reported fiscal year.*

### Why zero is plausible rather than an artefact

Structurally explicable and checkable: fund expenses (0.65%) against a low weighted dividend
yield — uranium miners broadly pay no dividend, and Cameco's is minimal. **Net investment income
≤ 0, so agE = 0.** A low-income, high-expense sector fund has nothing to distribute. A tech or
dividend fund would show a positive figure.

### Operationally

- Theme-fund drag is ~zero *currently*, **not guaranteed forward**. If underlying dividends grow
  past the expense offset, a positive agE appears.
- It is published annually **before** the tax is levied (5–7 months after fiscal year end,
  confirmed by both records: 7.0 and 6.7 months).
- **The base fund does carry a positive agE.** A cash buffer is required **for the base**, not
  the theme.

---

## 10 — DEPLOYMENT, DIVERSIFICATION, AND THE OPEN ITEM

### Deployment rule

> **Base: deploy immediately as a lump sum. Theme: three equal tranches, one per month.**

**Base immediate:** 3,758 companies. Single-day entry timing is noise over 10+ years, and
holding cash to wait is a certain cost against an uncertain benefit.

**Theme staged:** ~10 real positions, high dispersion, first investment. Three entries remove
single-day regret risk at the cost of roughly 1.5 months of cash drag on 27% — negligible over
20 years. **This is regret management, not return optimisation.** If you prefer one rule: deploy
everything at once; the expected-return difference is immaterial.

### Diversification, qualified

```
URNU top-10              ~64% of assets
Cameco alone             ~15.6%
Remaining ~46 positions  ~36%, individually very small
=> about ten real positions plus a tail
=> effective independent bets ~15-20 (estimate)
```

**The theme is not a diversified 56-name portfolio.** A single name can move it materially.

**The base is genuinely diversified:** 3,758 holdings, top-10 ≈ 22.6% *(secondary source)*.

**That is precisely the argument for 73/27 — the diversification lives in the base.**

### ⚠️ Open item

**Under Option A (§5), the microreactor mandate is satisfied at ~3% of the portfolio.** This is
a stated fact, not a recommendation. The decision between Options A, B and C is open and is the
single judgement this document does not make.

---

## 11 — SOURCE REGISTER

**Every numeric field, with its source and retrieval date. Retrieval date 2026-09-13 unless
stated.**

| Field | Value | Source | Primary? |
|---|---|---|---|
| VWCE ISIN | IE00BK5BQT80 | Vanguard KIID for IE00BK5BQT80 | ✅ |
| VWCE WKN / ticker | A2PKXG / VWCE | justETF profile page | ⚪ |
| VWCE OCF | **0.14%** | Vanguard KIID ("Ongoing charges 0.14%"); Vanguard factsheet 30 Jun 2026 | ✅ |
| VWCE OCF, prior | 0.19% (pre-cut) | Vanguard factsheet 31 May 2026 | ✅ |
| VWCE holdings | 3,758 | justETF profile page | ⚪ |
| VWCE fund size | EUR 50,681m | justETF, retrieved 2026-09-13 | ⚪ |
| VWCE share-class assets | USD 46,664m as at 31 May 2026 | Vanguard factsheet 31 May 2026 | ✅ |
| ⚠️ *discrepancy* | *the two size figures differ by scope, date and FX — not reconciled* | | |
| VWCE top-10 | 22.6% | ETF Kompass (secondary) | ⚪ |
| VWRL (distributing alt.) ISIN | IE00B3RBWM25, A1JX52 | justETF profile page | ⚪ |
| URNU ISIN | IE000NDWFGA5 | **OeKB register**; Global X fund page | ✅ |
| URNU TER | 0.65% | Global X fund page, "as of 04 Sep 2026" | ✅ |
| URNU holdings | 56 | Global X fund page, 04 Sep 2026 | ✅ |
| URNU fund AUM (baseline) | **USD 733,846,613.01**, 04 Sep 2026 | Global X fund page | ✅ |
| URNU fund size (alt.) | EUR 645m | justETF | ⚪ |
| URNU index | Solactive Global Uranium & Nuclear Components TR v2 | Global X fund page | ✅ |
| URNU top-10 | ~64% | computed from published constituent weights | ⚪ |
| URNU Meldefonds status | **J**, Status AKTIV, Melde-ID 646362, Kundennr. 1000121438 | **OeKB Steuerdaten register**, retrieved by holder | ✅ |
| URNU fiscal year end | 30.06.; reported 29.01.2026 | **OeKB register** | ✅ |
| URNU agE, reported year | 0,0000 (all fields) | **OeKB register** | ✅ |
| URNU fiscal representative | Dr. Helmut Moritz | **OeKB register** | ✅ |
| Sprott UCITS ISIN | IE0005YK6564 | **HANetf KIID** ("ISIN: IE0005YK6564") | ✅ |
| Sprott UCITS TER | 85 bps | HANetf fund page | ✅ |
| Sprott UCITS net assets | USD 413,497,410 | HANetf fund page | ✅ |
| Sprott UCITS securities lending | **Yes** | **HANetf fund page** ("Securities Lending: Yes") | ✅ |
| URNU securities lending | **no statement found** | Global X fund page — *absence of a statement is not evidence of absence* | ❌ |
| Sprott Meldefonds status | J, AKTIV, Melde-ID 625255, Kundennr. 1000101467 | **OeKB register** | ✅ |
| Sprott fiscal year end | 31.03.; reported 20.10.2025 | **OeKB register** | ✅ |
| NUKL ISIN / WKN / ticker | IE000M7V94E1 / A3D47K / NUKL | justETF profile page | ⚪ |
| NUKL TER | 0.55% | justETF profile page | ⚪ |
| NUKL holdings / top-10 | 25 / 67.83% | justETF profile page | ⚪ |
| NUKL AUM | EUR 2,013m | justETF profile page | ⚪ |
| NUKL launched | 3 Feb 2023, Ireland | justETF profile page | ⚪ |
| NUKL top-10 constituents | as listed in §5 | justETF holdings table | ⚪ |
| KESt rate | 27.5% | Austrian BMF / EStG §27a | ✅ |
| Return, dividend yield, inflation, contribution multiple | 7%, 1.8%, 2%, 0.36× | **assumptions — not sourced** | ❌ |
| Basket median return | −17.5%, n=26, one quarter | this project's own measurement | ⚪ |
| Uranium spot 11 Sep 2026 | USD 90.15 | Trading Economics | ⚪ |
| Uranium term price, 30 Jun 2026 | USD 97.00 | TradeTech | ✅ |

**Legend:** ✅ primary (issuer, regulator, or filing) · ⚪ secondary/aggregator · ❌ not
established, or an assumption

### Errors found in this field, recorded for discipline

| # | Error | Origin | How found |
|---|---|---|---|
| 1 | ISIN `IE00BK5BQT36` — **does not exist** | uncited source, marked "verified" in this project's notes | direct ISIN resolution check |
| 2 | OCF `0.22%` | assumption, never sourced | Vanguard KIID |
| 3 | OCF `0.29%` — wrong, from a page read correctly for three other fields | transcription error in the rev. 2 correction itself | Vanguard KIID + factsheet |
| 4 | Cameco counted toward two mandates | double-counting in rev. 1 | internal review |
| 5 | "no tax drag" from a `0,0000` record | misread a one-year-lagged filing as current | OeKB fiscal-year check |

**Three of the five were introduced by this project while correcting earlier mistakes.**

---

## 12 — THE INSTRUMENTS

| | Fund | ISIN | WKN | Ticker | TER | Holdings |
|---|---|---|---|---|---|---|
| **Base** | Vanguard FTSE All-World UCITS ETF (USD) Acc | IE00BK5BQT80 | A2PKXG | VWCE | **0.14%** | 3,758 |
| **Theme A** | Global X Uranium UCITS ETF USD Acc | IE000NDWFGA5 | A3DC8S | URNU | **0.65%** | 56 |
| *Theme B* | *VanEck Uranium and Nuclear Technologies UCITS ETF* | *IE000M7V94E1* | *A3D47K* | *NUKL* | *0.55%* | *25* |
| *Base alt.* | *Vanguard FTSE All-World UCITS ETF (USD) Dist* | *IE00B3RBWM25* | *A1JX52* | *VWRL* | *0.14%* | *3,758* |

**Buy the EUR lines** — both are USD-denominated and trade in EUR. Buy on Xetra or Tradegate;
otherwise FX is paid on every trade for no purpose.

### The broker

**Requirement: Steuereinfach** — withholds KESt, reports to the Finanzamt, maintains the loss
pool automatically.

| Broker | Steuereinfach AT |
|---|---|
| Flatex AT | Yes |
| Trade Republic | Yes — **verify on their Austrian page** |
| Dadat | Yes |

⚠️ **Verify Steuereinfach on the broker's own Austrian page in the week the account is opened.**
An uncited source in this project got this backwards once.

**Not suitable:** Interactive Brokers, Degiro, Scalable — none Steuereinfach in Austria for this
purpose; an E1 + E1kv return would be required by hand each year.

---

## 13 — EXIT RULES

**Base:** never sell. Only add. Sole exception: genuine need for the capital.

**Theme — maintenance:** the decaying target and contribution split (§4), with a windfall trim
above target + 10pp.

**Theme — annual check, 15 minutes, once a year:**

```
[ ] Still KESt-Meldefonds "J" on OeKB?
[ ] TER still 0.65% (or 0.55% under Option B)?
[ ] AUM still comfortably above ~EUR 300m?
      baseline: URNU USD 733.8m (04 Sep 2026) / NUKL EUR 2,013m
[ ] Any change in securities lending?  (Sprott UCITS: Yes, per HANetf)
[ ] Top-10 concentration still under ~70%?   (URNU ~64% / NUKL 67.83%)
[ ] Has a positive agE appeared?  (cash-buffer implication)
```

Any failure triggers a review, not a sale.

**Theme — thesis invalidation, sell:**

- Nuclear policy support **structurally reverses** — governments withdrawing the programmes the
  sector depends on. A change of direction, not a bad quarter.
- The fund **changes index methodology** away from nuclear.
- **Top-10 exceeds ~75%** — it ceases to be a sector fund.

**No stop-loss** — §6. **No averaging down** outside the contribution split — §4, §7.

---

## 14 — THIS WEEK

```
1  Open a Steuereinfach broker account (Flatex AT / Trade Republic)
   Verify "Steuereinfach" on their Austrian page

2  Confirm both ISINs in the broker's search
   IE00BK5BQT80   base
   IE000NDWFGA5   theme A   (or IE000M7V94E1 theme B)

3  Read both KIDs. Confirm OCF 0.14% and TER 0.65% for yourself
   Do not take this document's word for it — see §11

4  Buy: base immediately, full amount, EUR line
        theme in 3 equal monthly tranches, EUR line

5  Set one calendar reminder, 12 months out — the §13 check
```

## WHAT NOT TO DO

- Do not buy any of the 26 names individually. That list is a research object, not a portfolio.
- Do not buy URA or URNM — US-domiciled, no PRIIPs KID, not purchasable by an Austrian retail
  investor.
- Do not use a non-Steuereinfach broker to save a small commission.
- Do not add a third position "for balance."
- Do not check prices daily.
- **Do not sell the base to top up the theme** — §7.
- Do not treat §8's projection as a forecast. It is a set of assumptions, and the return
  assumption dominates.
