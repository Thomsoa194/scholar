import streamlit as st 
import pandas as pd 
from bs4 import BeautifulSoup 
import requests, lxml, os 
import base64
import numpy as np

headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

proxies = {
  'http': os.getenv('HTTP_PROXY')
}
def get_profile_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text

  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'Web URL':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['Web URL'].append('https://scholar.google.co.uk/citations?hl=en&user=' + gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df
def get_profile_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'Web URL':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['Web URL'].append('https://scholar.google.co.uk/citations?hl=en&user=' + gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df
# Retrieves the next link from the Google Scholar Profile page

def get_next_link_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  return next_link

# Retrieves the next link from the Google Scholar Profile page
def get_next_link_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  #next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  next_link = btn_onclick.split('\\')[-3][3:]
  return next_link

############################
# Display app content
# Display app content

st.set_page_config(layout='wide')

st.markdown('''
# Scholar App 
This App retrieves researcher citation data from ***Google Scholar***.
''')

st.sidebar.header('Scholar App Settings')

org_list = {'Pfizer':'2173004527418493312',
            'AbbVie Inc':'12853406975335582193',
            'Johnson & Johnson Co.':'4573284240757692467',
            'Bristol-Myers Squibb Co.':'3674275271446335276',
            'Sanofi':'45911632759936575',
            'Genentech':'3165367052879174657',
            'AstraZeneca':'992515209104559621',
            'Amgen':'6577310867458702644',
            "Abbott Laboratories":"12347773627327339907"}

orgid = st.sidebar.selectbox('Select an Institution', 
                              ('Pfizer', 
                              'AbbVie Inc', 
                              'Johnson & Johnson Co.',
                              'Bristol-Myers Squibb Co.',
                              'Sanofi',
                              'Genentech',
                              'AstraZeneca',
                              'Amgen',
                              "Abbott Laboratories") )
orgid = org_list[orgid]

query_size = st.sidebar.slider('Query size', 10, 500, 10, 10)
query_size = int(query_size/10)

p_index = 10
df_list = []
for i in range(query_size):
  if i == 0:
    df1 = get_profile_1(orgid)
    df_list.append(df1)
    nxt_link_1 = get_next_link_1(orgid)
    #p_index += 10
    print(nxt_link_1, p_index)
  if i == 1:
    df2 = get_profile_2(orgid, nxt_link_1, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_1, p_index)
    df_list.append(df2)
    p_index += 10
    print(nxt_link_2, p_index)
  if i > 1:
    df3 = get_profile_2(orgid, nxt_link_2, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_2, p_index)
    df_list.append(df3)
    p_index += 10
    print(nxt_link_2, p_index)

df = pd.concat(df_list)
df.reset_index(drop=True, inplace=True)

df

# Download the data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="research_data.csv">Download CSV File</a>'
    return href


st.markdown(filedownload(df), unsafe_allow_html=True)