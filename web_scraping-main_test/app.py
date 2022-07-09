from distutils.fancy_getopt import wrap_text
from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.findAll('div', attrs = {'class' : 'lister-item mode-advanced'})


movie_title = []
rating = []
metascore = []
votes = []
gross = []

#insert the scrapping process here
for store in table:
    name = store.h3.a.text
    movie_title.append(name)
    
    rate = store.find('div', class_ = 'inline-block ratings-imdb-rating').text.replace('\n', '')
    rating.append(rate)
    
    meta = store.find('span', class_ = 'metascore').text.replace(' ','') if store.find('span', class_ = 'metascore') else '0'
    metascore.append(meta)
        
    value = store.find_all('span', attrs = {'name': 'nv'})

    vote = value[0].text
    votes.append(vote)
    
    grosses = value[1].text if len(value) >1 else '0'
    gross.append(grosses)
    
#change into dataframe	
best_50 = pd.DataFrame({'Movie Title': movie_title, 'Rate': rating, 'Metascore': metascore, 'Votes': votes})   

#insert data wrangling here
index = pd.Index(range(1, 51, 1))
imdb_50 = best_50.set_index(index)

imdb_50['Rate'] = imdb_50['Rate'].astype('float') 
imdb_50['Metascore'] = imdb_50['Metascore'].astype('int')
imdb_50['Votes'] = imdb_50['Votes'].str.replace(',','').astype('int')

top7 = imdb_50.nlargest(7,'Votes')[['Movie Title','Votes']].set_index('Movie Title')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{top7["Votes"].sum().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = sns.barplot(x="Votes", y=top7.index, data=top7)
	
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)

def new_func(ax):
    wrap_text(ax,10)


if __name__ == "__main__": 
    app.run(debug=True)

