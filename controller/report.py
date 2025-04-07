__author__ = 'Manuel Escriche'
import random
from dbase import db_session, Transaction, Account, BookEntry
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
cm = 1/2.54

colors= list(mcolors.TABLEAU_COLORS.keys())
random.shuffle(colors)
ncolors = len(colors)

def create_evo_graph(serie, **kwargs):
    title = kwargs.get('title')
    color = kwargs.get('color', mcolors.TABLEAU_COLORS[colors[-1]])
    figsize = kwargs.get('figsize',  (20*cm, 5*cm))
    
    if all(x==0 for x in serie): return None
    years = [str(ndx) if isinstance(ndx,int) else ndx for ndx in serie.index]
    
    fig, ax = plt.subplots(figsize=figsize, layout='constrained')
    bar = ax.bar(years, serie, color=color)
    labels = [f'{x:,.0f}' for x in serie]
    ax.bar_label(bar, labels=labels)
    ax.set_title(f"{title}")
    #ax.set_xlabel("Year")
    #ax.set_ylabel("Amount(€)")
    ax.set_ylim(0, max(serie)*1.1)
    return fig


def create_mevo_graph(df, **kwargs):
    title = kwargs.get('title').title()
    concepts = df.index.tolist()
    figsize = kwargs.get('figsize',  (20*cm, 5*len(concepts)*cm))
    years = list(map(str,df.columns.tolist()))
    
    fig, ax = plt.subplots(nrows=len(concepts), sharex=True, figsize=figsize, layout='constrained')
    for i, concept in enumerate(concepts):
        color = mcolors.TABLEAU_COLORS[colors[i%ncolors]]
        p = ax[i].bar(years, df.loc[concept], width=0.8, color=color)
        ax[i].bar_label(p, label_type='edge', fmt='%.0f')
        ax[i].set_title(f'{concept}')
        
    fig.suptitle(f'{title}')
    return fig

def create_graph(df, **kwargs):
    title = kwargs.get('title')
    color = kwargs.get('color', 'tab:blue')
    figsize = kwargs.get('figsize',  (8*cm, 8*cm))
        
    year = df.columns[0]
    total = df.loc['Total', year]
    if not total: return None
    last_index = df.index[-1]
    df.drop(last_index, inplace=True)
    df = df.nlargest(4, year)
    categories = df.index.tolist()
    amounts = df[year].to_numpy()
    
    fig, ax = plt.subplots(figsize=figsize, layout='constrained')    
    p = ax.bar(categories, amounts, color=color)
    labels = [f'{x:,.0f}\n({x/total:.0%})' for x in amounts]
    ax.bar_label(p, label_type='edge', labels=labels)
    
    fig.suptitle(f'{year} - {title}')
    ax.set_title(f'Total = {total:,.0f}€', fontsize=10)
    ax.set_ylim(0, total*1.05)
    plt.xticks(rotation=45, ha='right')
    return fig

def create_cmp_graph(df, **kwargs):
    if len(df) <= 2: return None
    title = kwargs.get('title')
    color = kwargs.get('color', 'tab:blue')
    df.drop(df.index[-1], inplace=True) #drop Total

    years = df.columns.tolist()[:-1]
    if len(df) > 5: df = df.iloc[-5:]
    figsize =  kwargs.get('figsize',  ((3+3*len(df))*cm, 8*cm))
    
    fig, ax = plt.subplots(ncols=len(years), sharey=True, figsize=figsize, layout='constrained')
    for i,year in enumerate(years):
        p = ax[i].bar(df.index, df[year], width=0.8, color=color)
        ax[i].bar_label(p, label_type='edge', fmt='%.0f')
        ax[i].set_title(f'{year} - Total={df[year].sum():,.0f}')
        ax[i].tick_params(axis='x', rotation=45 )
    fig.suptitle(f'{title}')
    return fig

def create_table(*data, title=None) -> str:
    table = PrettyTable()
    table.min_table_width = 60
    if title: table.title = title
    for df in data:
        table.field_names = ['Concept'] + df.columns.tolist()
        total_rows = len(df)
        table.add_divider()
        for i,row in enumerate(df.itertuples(index=True),1):
            if i == total_rows:
                table.add_divider()
            table.add_row(row)
        else:
            table.add_divider()
    else:
        table.align = 'r'
        table.align["Concept"] = 'l'
        for col in df.columns:
            head = str(col) if isinstance(col, int) else col
            table.custom_format[head] = lambda f,v: f"{v:,.0f}"   
    return table
       
