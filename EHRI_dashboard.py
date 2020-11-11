#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 23:42:16 2020

@author: Michal Frankl, frankl@mua.cas.cz

Experimental, proof-of-concept dashboard visualising the EHRI repository statistics.

"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from lxml import etree
from lxml.etree import tostring
import json
import xmltodict
#import altair as alt

section = st.sidebar.selectbox('Sections', ('Ghettos', 'EHRI repositories'))

if (section == 'Ghettos'):
    
    st.write("Ghettos")
    
    #res = requests.get('https://portal.ehri-project.eu/vocabularies/ehri_ghettos/export?format=RDF%2FXML')    
 
    @st.cache
    # or via json
    def load_skos(skos_file):
        with open(skos_file) as ghettosxml:
            ghettosdict = xmltodict.parse(ghettosxml.read())
        ghettosxml.close()
        ghettosjson = json.dumps(ghettosdict, indent=4)
        
        ghetto_list = []
        for d in ghettosdict['rdf:RDF']['rdf:Description']:
            gh = []
            try:
                for pl in d['skos:prefLabel']:
                    if pl['@xml:lang'] == 'en':
                        gh.append(pl['#text'])
            except:
                print("no skos label")
            try:
                gh.append(d['geo:lat'])
                gh.append(d['geo:long'])
            except:
                print("no coordinates")
            ghetto_list.append(gh)
        return(ghetto_list)
    
    ghetto_list = load_skos("ghettos.rdf")
    ghettosdf = pd.DataFrame(ghetto_list, columns=['name', 'lat', 'lon']) 
    
    ghettosdf[['lat', 'lon']] = ghettosdf[['lat', 'lon']].apply(pd.to_numeric) 
    ghettosdf = ghettosdf.dropna()
    mapdf = ghettosdf.head(5)
    
    if st.sidebar.checkbox("Show map of ghettos", 1):
        st.map(ghettosdf)
        
    if st.sidebar.checkbox("Show ghettos data", 1):
        st.write(ghettosdf)

if (section == 'EHRI repositories'): 
    
    @st.cache
    def load_repdata():
        repdata = pd.read_csv('https://portal.ehri-project.eu/api/datasets/a3KwGAKDYf?format=csv', names = ['repository_code', 'repository_name', 'lat', 'lon', 'records_top', 'records_low', 'records_total'])
        pd.to_numeric(repdata.lon)
        pd.to_numeric(repdata.lat)
        pd.to_numeric(repdata.records_total)
        return repdata
    
    repdata = load_repdata()
    
    repdata = repdata.dropna()
    
    st.sidebar.title('EHRI repositories with collection descriptions')
    
    c = st.sidebar.slider('Records', repdata['records_total'].min(), repdata['records_total'].max(), (repdata['records_total'].min(), repdata['records_total'].max()))
    c = list(c)
    
    if st.sidebar.checkbox("Show map", 1):
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=np.average(repdata['lat']),
                longitude=np.average(repdata['lon']),
                zoom=2.5,
                pitch=0,
                ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=repdata[(repdata.records_total >= c[0]) & (repdata.records_total <= c[1])],
                    get_position='[lon,lat]',
                    pickable=True,
                    opacity=0.5,
                    stroked=True,
                    filled=True,
                    radius_scale=6,
                    radius_min_pixels=5,
                    radius_max_pixels=80,
                    line_width_min_pixels=1,
                    get_radius="records_total",
                    get_fill_color=[255, 140, 0],
                    get_line_color=[0, 0, 0],
                    ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=repdata[(repdata.records_total >= c[0]) & (repdata.records_total <= c[1])],
                    get_position='[lon,lat]',
                    pickable=True,
                    opacity=0.8,
                    stroked=True,
                    filled=True,
                    radius_scale=6,
                    radius_min_pixels=5,
                    radius_max_pixels=80,
                    line_width_min_pixels=1,
                    get_radius="records_top",
                    get_fill_color=[140, 140, 0],
                    get_line_color=[0, 0, 0],
                    ),
            ],
            tooltip={"text": "{repository_name}\nTop level: {records_top}\nTotal: {records_total}"}
        ))
    
    if st.sidebar.checkbox("Show data", 0):
        st.write(repdata[(repdata.records_total >= c[0]) & (repdata.records_total <= c[1])])
    
st.sidebar.image('EHRI-logo-kleur-beeldscherm-klein.jpg')