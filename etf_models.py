from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.request
import html5lib
import re



"""

ETF Portfolio Visualizer using D3 - Pie Chart of top 50 holdings in your portfolio is one view. As you update your 
ETF portfolio, it re-calculates your top holdings and adjusts the pie chart. 

Also has a complete list of all of your holdings and their portfolio weightings, as well as showing all the constituent ETFs 
each holding is present in. 

You have a list of the top 10 most frequently recurring stocks (frequency of appearance in the portfolio, not weighting)

Portfolio correlation metrics? 

As the user adds ETFs to the analysis, seed a SQL database with each dataframe so that when the user is done and tries to run 
the analysis, the program doesn't need to check dozens of URLs (this could be in the session - like option legs)

Parsing: use try/except, or look for empty list when checking holdings. if conditions false, use other parsing default_parse_method
(second_parse - control this in the get classmethod)


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
		# Get soup
		base_url='http://etfdailynews.com/tools/what-is-in-your-etf/?FundVariable='
		url = base_url + str(ticker)
		html = urllib.request.urlopen(url).read()
		soup = bs(html, "lxml")

		# Fetch expense ratio
		ratio_pattern = re.compile(r'EXPENSE RATIO')
		percent_pattern = re.compile(r'%$')
		expense_ratio = soup.find('td', text=ratio_pattern).find_next_sibling('td', text=percent_pattern).text
		self.expense_ratio = float(expense_ratio.rstrip('%'))/100

		# Build Holdings Table
		first_holding = soup.find(attrs={'class':'evenOdd'}) 
		holdings_table = "<table>"+str(first_holding.parent.parent)+"</table>"

		# Convert Table to pandas DataFrame
		df = pd.read_html(holdings_table)[0]
		df.columns = ['name', 'ticker', 'allocation']
		self.holdings = df
		self.num_holdings = len(df)

	def second_parse(self): 
		pass







# def get_holdings(ticker): 
# 	# Get soup
# 	base_url='http://etfdailynews.com/tools/what-is-in-your-etf/?FundVariable='
# 	url = base_url + str(ticker)
# 	html = urllib.request.urlopen(url).read()
# 	soup = bs(html, "lxml")

# 	# Fetch expense ratio
# 	ratio_pattern = re.compile(r'EXPENSE RATIO')
# 	percent_pattern = re.compile(r'%$')
# 	expense_ratio = soup.find('td', text=ratio_pattern).find_next_sibling('td', text=percent_pattern).text

# 	# Build Holdings Table
# 	first_holding = soup.find(attrs={'class':'evenOdd'}) 
# 	holdings_table = "<table>"+str(first_holding.parent.parent)+"</table>"

# 	# Convert Table to pandas DataFrame
# 	df = pd.read_html(holdings_table)[0]
# 	df.columns = ['name', 'ticker', 'allocation']

# 	print(expense_ratio)
# 	return df	











