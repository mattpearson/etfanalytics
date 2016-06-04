# etfanalytics

##### What it is
This is a tool for analyzing ETF portfolios. 
It is generally very difficult to find detailed holdings data for ETFs in a usable format, especially without paying for data. This tool allows users to fetch holdings for any equity ETF and calculate the weighting of individual stocks in large portfolios of ETFs. 

##### How it works
For each ETF the user adds to a portfolio, data is fetched from one of two websites using BeautifulSoup and loaded into a pandas DataFrame.
Each time the user adds an ETF to the portfolio, that ETF's expense ratio and holdings are saved. The user can then fetch the weighted expense ratio of the portfolio and a complete DataFrame of individual stock holdings, arranged in descending order of weight in the portfolio.

##### Example
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
