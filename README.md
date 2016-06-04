# etfanalytics

##### What it is
This is a tool for analyzing ETF portfolios. 
It is generally very difficult to find detailed holdings data for ETFs in a usable format, especially without paying for data. This tool allows users to fetch holdings for any equity ETF and calculate the weighting of individual stocks in large portfolios of ETFs. 

##### How it works
For each ETF the user adds to a portfolio, data is fetched from one of two websites using BeautifulSoup and loaded into a pandas DataFrame.
Each time the user adds an ETF to the portfolio, that ETF's expense ratio and holdings are saved. The user can then fetch the weighted expense ratio of the portfolio and a complete DataFrame of individual stock holdings, arranged in descending order of weight in the portfolio.

##### Fetching Holdings - Example
`ETFData.get('IBB').holdings` returns the DataFrame
```
                               name ticker  allocation
0                    BIOGEN INC INC   BIIB    0.089004
1                      CELGENE CORP   CELG    0.087885
2                         AMGEN INC   AMGN    0.086218
3               GILEAD SCIENCES INC   GILD    0.083413
4     REGENERON PHARMACEUTICALS INC   REGN    0.077043
5       ALEXION PHARMACEUTICALS INC   ALXN    0.042271
6                      ILLUMINA INC   ILMN    0.041029
7                          MYLAN NV    MYL    0.040936
8        VERTEX PHARMACEUTICALS INC   VRTX    0.035575
9                       INCYTE CORP   INCY    0.024840
10      BIOMARIN PHARMACEUTICAL INC   BMRN    0.023097
11           ENDO INTERNATIONAL PLC   ENDP    0.020308
12                     ALKERMES PLC   ALKS    0.016314
13       SHIRE ADR REPRESENTING PLC   SHPG    0.014365
14         JAZZ PHARMACEUTICALS PLC   JAZZ    0.012873
15     ALNYLAM PHARMACEUTICALS INC.   ALNY    0.010856
16        UNITED THERAPEUTICS CORP.   UTHR    0.010565
17                  MEDIVATION INC.   MDVN    0.010258
18        IONIS PHARMACEUTICALS INC   IONS    0.008954
19                      QIAGEN N.V.   QGEN    0.008924
20            SEATTLE GENETICS INC.   SGEN    0.008635
21      ANACOR PHARMACEUTICALS INC.   ANAC    0.006708
22      NEUROCRINE BIOSCIENCES INC.   NBIX    0.006144
23            JUNO THERAPEUTICS INC   JUNO    0.006047
24                       AKORN INC.   AKRX    0.005421
25      CHINA BIOLOGIC PRODUCTS INC   CBPO    0.005360
26                  BIO TECHNE CORP   TECH    0.005219
27    ULTRAGENYX PHARMACEUTICAL INC   RARE    0.005090
28             MYRIAD GENETICS INC.   MYGN    0.005019
29    INTERCEPT PHARMACEUTICALS INC   ICPT    0.005015
..                              ...    ...         ...
190        ARATANA THERAPEUTICS INC   PETX    0.000178

```

##### Portfolio Metrics - Example
`my_etf_portfolio.get_stock_allocation()` for the portfolio:

``` 
   allocation  etf  expenses  true_weight  weighted_expenses
0        0.15  HDV    0.0012         0.15           0.000180
1        0.25  IBB    0.0048         0.25           0.001200
6        0.05  IYH    0.0043         0.05           0.000215
2        0.05  MGK    0.0009         0.05           0.000045
3        0.20  SPY    0.0009         0.20           0.000180
4        0.20  VTI    0.0005         0.20           0.000100
5        0.10  XLK    0.0014         0.10           0.000140
```

returns the DataFrame
```
     ticker  portfolio_weight                             name
12     AAPL          0.031298                        APPLE INC
1460   GILD          0.027542              GILEAD SCIENCES INC
191    AMGN          0.026914                        AMGEN INC
646    CELG          0.025971                     CELGENE CORP
441    BIIB          0.025202                   BIOGEN INC INC
3775    XOM          0.022184                 EXXON MOBIL CORP
1894    JNJ          0.021195                JOHNSON & JOHNSON
2879   REGN          0.021013    REGENERON PHARMACEUTICALS INC
3648     VZ          0.020267       VERIZON COMMUNICATIONS INC
2290   MSFT          0.018671            Microsoft Corporation
2660    PFE          0.016589                       PFIZER INC
2671     PG          0.013837                 PROCTER & GAMBLE
926     CVX          0.013268                     CHEVRON CORP
2276    MRK          0.012488                   MERCK & CO INC
2718     PM          0.012475  PHILIP MORRIS INTERNATIONAL INC
176    ALXN          0.012329      ALEXION PHARMACEUTICALS INC
1796   INTC          0.012088           INTEL CORPORATION CORP
1956     KO          0.011485                        COCA-COLA
1256     FB          0.011459                   FACEBOOK INC-A
856    CSCO          0.011434                CISCO SYSTEMS INC
1761   ILMN          0.011416                     ILLUMINA INC
2331    MYL          0.011178                         MYLAN NV
1499  GOOGL          0.011059                   ALPHABET INC-A
1498   GOOG          0.010892                   ALPHABET INC-C
3627   VRTX          0.010117       VERTEX PHARMACEUTICALS INC
3302      T          0.009765                        AT&T Inc.
2247     MO          0.008466                 ALTRIA GROUP INC
3569      V          0.007710                 VISA INC-CLASS A
2144    MCD          0.007270                   MCDONALDS CORP
1780   INCY          0.006606                      INCYTE CORP
...     ...               ...                              ...

```





