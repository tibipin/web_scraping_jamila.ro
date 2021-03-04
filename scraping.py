import requests
from bs4 import BeautifulSoup
import pandas


base_url = 'https://jamilacuisine.ro/retete-video/mancaruri/'
df_master = pandas.DataFrame()
df_ingredients = pandas.DataFrame()
r = requests.get(url=base_url)
supa = BeautifulSoup(r.text, 'html.parser')
last_page = int(supa.find_all('span', {'class': 'pages'})[0].text.split()[-1])

# ===> Bucla asta extrage toate Titlurile si Linkurile catre retete

for i in range(1, last_page+1):
    base_url = f'https://jamilacuisine.ro/retete-video/mancaruri/page/{i}'
    r = requests.get(url=base_url)
    supa = BeautifulSoup(r.text, 'html.parser')
    r.close()
    pag = supa.find_all('div', {'id': 'tdi_62_67f'})
    retete_si_linkuri = supa.find_all('div', {'class': 'td-module-meta-info'})
    titluri = [j.find_all('a')[0]['title'] for j in retete_si_linkuri]
    linkuri = [j.find_all('a')[0]['href'] for j in retete_si_linkuri]
    temp_df = pandas.DataFrame({'Titluri': titluri, 'Linkuri': linkuri})
    df_master = df_master.append(temp_df)

df_master.drop_duplicates(inplace=True)

# ===> Bucla asta intra pe fiecare reteta si extrage ingredientele

for i in df_master.iterrows():
    base_url = i[1]['Linkuri']
    r = requests.get(url=base_url)
    supa = BeautifulSoup(r.text, 'html.parser')
    r.close()
    try:
        html_ingredients = (supa.find_all('ul', {'class': 'wprm-recipe-ingredients'})[0]).find_all('input')
        ingredients = [j.attrs['aria-label'] for j in html_ingredients]
        temp_df = pandas.DataFrame({'Linkuri': base_url, 'Ingredients': ingredients})
        df_ingredients = df_ingredients.append(temp_df)
    except:
        continue


df = pandas.merge(df_ingredients, df_master, how='inner', left_on='Linkuri', right_on='Linkuri')
df.to_excel('retete.xlsx', index=False)
