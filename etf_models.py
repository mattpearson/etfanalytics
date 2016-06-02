from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import urllib.request
import html5lib
import re


import gzip
import io

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

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
		# decode to unicode, then re-encode to utf-8 to avoid bytes string / gzip
		html = urllib.request.urlopen(url).read().decode('cp1252').encode('utf-8')
		# print(type(html))
		# print(html)
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
		self.port_etfs = pd.DataFrame({'etf':[], 'allocation':[], 'true_weight':[], 'holdings':[], 'expenses':[], 'weighted_expenses':[]})
		self.num_etfs = 0
		self.num_stocks = 0
		self.port_stocks = None
		self.port_expenses = None

	def calculate_weight(self, allocation): 
		# current total user-entered allocation 
		total_allocation = self.port_etfs['allocation'].sum(axis=0) + allocation

		# Calculate current real allocation
		def true_weight(alloc_input):
			weight_factor = 1/total_allocation
			return weight_factor*alloc_input

		# Update real allocation and weighted expenses for each row
		self.port_etfs['true_weight'] = self.port_etfs.allocation.map(lambda x: true_weight(x))
		self.port_etfs['weighted_expenses'] = self.port_etfs['expenses']*self.port_etfs['true_weight']

		return true_weight(allocation)

	def add(self, ticker, allocation): 
		ticker = ticker.upper()
		allocation = float(allocation)/100

		# real current portfolio weight of allocation (update all values)
		weight = self.calculate_weight(allocation)

		# get holdings Dataframe
		etf = ETFData.get(ticker)
		holdings = etf.holdings
		weighted_expenses = etf.expense_ratio*weight

		# New ETF row with ticker, allocation, weight, and dataframe of holdings
		self.port_etfs = self.port_etfs.append({'etf':ticker, 'allocation':allocation, 'true_weight': weight, 'holdings':holdings, 'expenses':etf.expense_ratio, 'weighted_expenses':weighted_expenses}, ignore_index=True).sort_values(by='etf')
		self.num_etfs += 1
		print(self.port_etfs)

	def get_port_expenses(self): 
		self.port_expenses = self.port_etfs['weighted_expenses'].sum()
		return self.port_expenses

	def get_stock_allocation(self): 
		all_holdings = pd.DataFrame({'name':[], 'ticker':[], 'allocation':[], 'portfolio_weight':[]})

		for each in zip(self.port_etfs['holdings'], self.port_etfs['true_weight']):
			# each stock's portfolio weight is its allocation within the etf * the etf's real weight in the portfolio
			each[0]['portfolio_weight'] = each[0].allocation * each[1]
			all_holdings = all_holdings.append(each[0], ignore_index=True)

		nulls = all_holdings.loc[all_holdings.ticker.isnull()]
		cash = all_holdings.loc[all_holdings.ticker.isin(['CASH_USD'])]
		others = pd.concat([nulls, cash])
		print(others)
		print((others['portfolio_weight'].sum())*100)

		# get list of unique stock names (if tickers are repeated, their names may be different due to capitalization etc)
		names = all_holdings.drop_duplicates(subset='ticker').drop('allocation', 1).drop('portfolio_weight', 1)

		# generate dataframe with ticker and sum of weights across ETFs using groupby
		grouped_holdings = pd.DataFrame(all_holdings.groupby('ticker')['portfolio_weight'].sum()).reset_index()

		# merge grouped holdings with list of unique stock names (dropped by the groupby operation)
		grouped_holdings = pd.merge(grouped_holdings, names, left_on='ticker', right_on='ticker', how='inner').sort_values(by='portfolio_weight')
		self.port_stocks, self.num_stocks = grouped_holdings, len(grouped_holdings)
		return grouped_holdings 



if __name__ == "__main__": 
	a = Portfolio()
	a.add('spy', 35)
	a.add('iyw', 10)























