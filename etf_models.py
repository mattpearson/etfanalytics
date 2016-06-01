from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import sqlite3 
import urllib.request
import html5lib
import re

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

"""

ETF Portfolio Visualizer using D3 - Pie Chart of top 50 holdings in your portfolio is one view. As you update your 
ETF portfolio, it re-calculates your top holdings and adjusts the pie chart. 

Pie chart or bubble chart (bubble - top 50-200 holdings, circular chart composed of bubbles, corresponding in size)
Pie chart - top 50 (?) holdings, everything else is "other"

Also has a complete list of all of your holdings and their portfolio weightings, as well as showing all the constituent ETFs 
each holding is present in. 

You have a list of the top 10 most frequently recurring stocks (frequency of appearance in the portfolio, not weighting)

Portfolio correlation metrics? 

As the user adds ETFs to the analysis, seed a SQL database with each dataframe so that when the user is done and tries to run 
the analysis, the program doesn't need to check dozens of URLs (this could be in the session - like option legs)

Parsing: use try/except, or look for empty list when checking holdings. if conditions false, use other parsing default_parse_method
(second_parse - control this in the get classmethod)

Need function to clean holdings dataframe for cash holdings (ticker is NaN, percent allocation == 0 or less than 0)

- Portfolio metrics: 
	US/International balance (use morningstar quote URLs and scrape for each ETF, then weight)


"""

# default_parse_method = None

class ETFData: 
	def __init__(self, ticker): 
		self.ticker = ticker
		self.holdings = None
		self.num_holdings = None
		self.expense_ratio = None

	@classmethod
	def get(cls, ticker): 
		data = cls(ticker)
		data.first_parse(ticker)
		return data

	def first_parse(self, ticker): 
		# converts percentage string to float
		def convert_percent(pct):
			return float(pct.rstrip('%'))/100

		# Get soup
		base_url='http://etfdailynews.com/tools/what-is-in-your-etf/?FundVariable='
		url = base_url + str(ticker)
		html = urllib.request.urlopen(url).read()
		soup = bs(html, "lxml")

		# Fetch expense ratio
		ratio_pattern = re.compile(r'EXPENSE RATIO')
		percent_pattern = re.compile(r'%$')
		expense_ratio = soup.find('td', text=ratio_pattern).find_next_sibling('td', text=percent_pattern).text
		self.expense_ratio = convert_percent(expense_ratio)

		# Build Holdings Table
		first_holding = soup.find(attrs={'class':'evenOdd'}) 
		holdings_table = "<table>"+str(first_holding.parent.parent)+"</table>"

		# Convert Table to pandas DataFrame
		df = pd.read_html(holdings_table)[0]
		df.columns = ['name', 'ticker', 'allocation']
		df['allocation'] = df.allocation.map(lambda x: convert_percent(x))
		self.holdings = df
		self.num_holdings = len(df)

	def second_parse(self): 
		pass


class Portfolio: 
	def __init__(self): 
		self.etfs = pd.DataFrame({'etf':[], 'allocation':[], 'true_weight':[], 'holdings':[]})
		self.num_etfs = 0
		self.stock_holdings = pd.DataFrame({'name':[], 'ticker':[], 'portfolio_allocation':[]})

	def calculate_weight(self, allocation): 
		# current total user-entered allocation 
		total_allocation = self.etfs['allocation'].sum(axis=0) + allocation

		# Calculate current real allocation
		def true_weight(alloc_input):
			weight_factor = 1/total_allocation
			return weight_factor*alloc_input

		# Update real allocation for each row
		self.etfs['true_weight'] = self.etfs.allocation.map(lambda x: true_weight(x))

		return true_weight(allocation)

	def add(self, ticker, allocation): 
		allocation = float(allocation)/100
		weight = self.calculate_weight(allocation)
		holdings = ETFData.get(ticker).holdings
		self.etfs = self.etfs.append({'etf':ticker, 'allocation':allocation, 'true_weight': weight, 'holdings':holdings}, ignore_index=True).sort_values(by='etf')
		self.num_etfs += 1
		print(self.etfs)

	def get_stock_allocation(self): 
		all_holdings = pd.DataFrame({'name':[], 'ticker':[], 'allocation':[], 'portfolio_weight':[]})
		for each in zip(self.etfs['holdings'], self.etfs['true_weight']):
			port_etf_weight = each[1]
			each[0]['portfolio_weight'] = each[0].allocation.map(lambda x: each[1]*x)
			all_holdings = all_holdings.append(each[0], ignore_index=True)
		return all_holdings





		# self.stock_holdings['stock'] = self.etfs.map(lambda x: list(ETFData.get(x.etf).holdings.ticker.values))
		# self.stock_holdings['portfolio_allocation']



if __name__ == "__main__": 
	a = Portfolio()
	a.add('spy', 8)
	a.add('vti', 4)























