__author__ = 'Manuel Escriche'
from dbase import db_session, Transaction, Account, BookEntry
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np
cm = 1/2.54

def create_evo_graph(serie, **kwargs):
    title = kwargs.get('title').title()
    color = kwargs.get('color', 'tab:blue')
    figsize = kwargs.get('figsize',  (20*cm, 5*cm))
    
    amounts = serie.to_numpy()
    if all(x==0 for x in amounts): return None
    
    years = [str(ndx) if isinstance(ndx,int) else ndx for ndx in serie.index]
    
    fig, ax = plt.subplots(figsize=figsize, layout='constrained')
    bar = ax.bar(years, amounts, color=color)
    labels = [f'{x:,.0f}' for x in amounts]
    ax.bar_label(bar, labels=labels)
    ax.set_title(f"Concept:{title}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Amount(€)")
    ax.set_ylim(0, max(amounts)*1.1)
    return fig

def create_graph(df, **kwargs):
    title = kwargs.get('title')
    color = kwargs.get('color', 'tab:blue')
    figsize = kwargs.get('figsize',  (8*cm, 8*cm))
        
    year = df.columns[0]
    total = df.loc['Total', year]
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


def create_table(*data) -> str:
    table = PrettyTable()
    table.min_table_width = 60
    
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
       
