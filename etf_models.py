from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import urllib.request
import html5lib
import ast
import re

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class ETFData: 

	def __init__(self, ticker): 
		self.ticker = ticker
		self.holdings = None
		self.num_holdings = None
		self.expense_ratio = None
		self.sector_breakdown = None

	@staticmethod
	def convert_percent(pct): 
		if type(pct)==float:
			return pct/100
		return float(pct.rstrip('%'))/100

	def etf_details(self, ticker): 
		"""
		Fetch sector breakdown and expense ratio from ETFDB
		"""
		url2 = 'http://www.etfdb.com/etf/' + str(ticker)
		html = urllib.request.urlopen(url2).read()
		soup = bs(html, "lxml")

		# Save expense ratio
		percent_pattern = re.compile(r'%$')
		expense_ratio = soup.find('span', text='Expense Ratio:').find_next_sibling('span', text=percent_pattern).text
		self.expense_ratio = self.convert_percent(str(expense_ratio))

		# Fetch sector allocation and convert to list
		sector_breakdown = ast.literal_eval(soup.find('h3', text='Sector Breakdown').find_next_sibling('table', attrs={'class':'base-table'})['data-chart-series'])
		df = pd.DataFrame(sector_breakdown)
		df.columns = ['sector', 'allocation']
		# Remove extra characters from sector names
		df['sector'] = df.sector.map(lambda x: re.sub(' \(.*?\)', '', x))
		self.sector_breakdown = df
		# print(df)

	def holdings_first_parse(self, ticker): 
		"""
		Default API for fetching ETF holdings. Generates a pandas DataFrame with name, 
		ticker, allocation for each holding. Equity ETFs only.
		"""
		url='http://etfdailynews.com/tools/what-is-in-your-etf/?FundVariable=' + str(ticker)
		# decode to unicode, then re-encode to utf-8 to avoid gzip
		html = urllib.request.urlopen(url).read().decode('cp1252').encode('utf-8')
		soup = bs(html, "lxml")

		# Build Holdings Table
		first_holding = soup.find(attrs={'class':'evenOdd'}) 
		holdings_table = "<table>"+str(first_holding.parent.parent)+"</table>"

		# conver to DataFrame
		df = pd.read_html(holdings_table)[0]
		df.columns = ['name', 'ticker', 'allocation']
		df['allocation'] = df.allocation.map(lambda x: self.convert_percent(x))
		self.holdings, self.num_holdings = df, len(df)


	def holdings_second_parse(self, ticker): 
		"""
		Backup source for holdings (zacks.com). Slower (data is parsed from string,
		not read into pandas from table element as in holdings_first_parse) and less reliable data. Output is in same format.
		"""

		def clean_name(str_input): 
			if "<span" in str_input:
				soup = bs(str_input, "lxml")
				return soup.find('span')['onmouseover'].lstrip("tooltip.show('").rstrip(".');")
			return str_input

		def clean_ticker(str_input):
			soup = bs(str_input, "lxml")
			return soup.find('a').text

		def clean_allocation(str_input): 
			if str_input == "NA":
				return 0
			return float(str_input)/100

		url = 'https://www.zacks.com/funds/etf/' + str(ticker) + '/holding'
		html = urllib.request.urlopen(url).read().decode('cp1252')
		str_start, str_end = html.find('data:  [  [ '), html.find(' ]  ]')
		if str_start == -1 or str_end == -1: 
			return False
		list_str = "[["+html[(str_start+12):str_end]+"]]"
		holdings_list = ast.literal_eval(list_str)

		df = pd.DataFrame(holdings_list).drop(2,1).drop(4,1).drop(5,1)
		df.columns = ['name', 'ticker', 'allocation']
		df['allocation'] = df.allocation.map(lambda x: clean_allocation(x))
		df['name'] = df.name.map(lambda x: clean_name(x))
		df['ticker'] = df.ticker.map(lambda x: clean_ticker(x))
		self.holdings, self.num_holdings = df, len(df)

		# print(df['allocation'].sum())

	@classmethod
	def get(cls, ticker, method="first"): 
		ticker = ticker.upper()
		data = cls(ticker)
		data.etf_details(ticker)
		if method=="first":
			result = data.holdings_first_parse(ticker)
			if result==False: 
				return False
		elif method=="second":
			result = data.holdings_second_parse(ticker)
			if result==False: 
				return False
		return data

class Portfolio: 
	def __init__(self): 
		self.port_etfs = pd.DataFrame({
			'etf':[], 
			'allocation':[], 
			'true_weight':[], 
			'holdings':[], 
			'expenses':[], 
			'weighted_expenses':[], 
			'sector_breakdown':[]})
		self.num_etfs = 0
		self.num_holdings = 0
		self.port_holdings = None
		self.port_expenses = None
		self.sector_breakdown = None

	def display_portfolio(self): 
		print(self.port_etfs[['etf', 'allocation', 'true_weight', 'expenses', 'weighted_expenses']])

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
		allocation = float(allocation)/100
		weight = self.calculate_weight(allocation)
		etf = ETFData.get(ticker, "first")
		if not etf: 
			etf = ETFData.get(ticker, "second")
			if not etf: 
				return False

		weighted_expenses = etf.expense_ratio*weight

		# New ETF row
		self.port_etfs = self.port_etfs.append({'etf':ticker, 
			'allocation':allocation, 
			'true_weight': weight, 
			'holdings':etf.holdings, 
			'expenses':etf.expense_ratio, 
			'weighted_expenses':weighted_expenses, 
			'sector_breakdown':etf.sector_breakdown}, ignore_index=True).sort_values(by='etf')
		self.num_etfs += 1
		print("{} added").format(ticker)

	def get_port_expenses(self): 
		self.port_expenses = self.port_etfs['weighted_expenses'].sum()
		return self.port_expenses

	def get_stock_allocation(self):
		"""
		Returns DataFrame with portfolio weight of all individual constituent stocks
		""" 
		all_holdings = pd.DataFrame({'name':[], 'ticker':[], 'allocation':[], 'portfolio_weight':[]})

		for each in zip(self.port_etfs['holdings'], self.port_etfs['true_weight']):
			each[0]['portfolio_weight'] = each[0].allocation * each[1]
			all_holdings = all_holdings.append(each[0], ignore_index=True)

		# Group holdings with NaN or Cash tickers
		all_holdings.ix[all_holdings.ticker.isin(["CASH_USD", "USD", np.nan]), 'ticker'] = 'N/A'
		all_holdings.ix[all_holdings.ticker=="N/A", 'name'] = 'Cash/Other'

		# Group holdings by ticker and add respective weights, match with names
		names = all_holdings.drop_duplicates(subset='ticker')[['name','ticker']]
		grouped_holdings = pd.DataFrame(all_holdings.groupby('ticker')['portfolio_weight'].sum()).reset_index()
		grouped_holdings = pd.merge(grouped_holdings, names, left_on='ticker', right_on='ticker', how='inner').sort_values(by='portfolio_weight', ascending=False)

		self.port_holdings, self.num_holdings = grouped_holdings, len(grouped_holdings)
		return grouped_holdings 

	def get_sector_breakdown(self): 
		"""
		Returns DataFrame with portfolio weight of each sector
		"""
		all_sectors = pd.DataFrame()
		for each in zip(self.port_etfs['sector_breakdown'], self.port_etfs['true_weight']):
			each[0]['portfolio_weight'] = each[0].allocation * each[1]
			all_sectors = all_sectors.append(each[0], ignore_index=True)
		grouped_sectors = pd.DataFrame(all_sectors.groupby('sector')['portfolio_weight'].sum()).sort_values(by='portfolio_weight', ascending=False).reset_index()
		self.sector_breakdown = grouped_sectors
		return grouped_sectors




# if __name__ == "__main__": 

	# a = Portfolio()
	# a.add('VTI', 20)
	# a.add('SPY', 20)
	# a.add('XLK', 10)
	# a.add('IBB', 25)
	# a.add('HDV', 15)
	# a.add('MGK', 5)
	# a.add('IYH', 5)
	# a.get_stock_allocation()
	# a.get_sector_breakdown()














