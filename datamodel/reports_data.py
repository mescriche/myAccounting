__author__ = 'Manuel Escriche'
from enum import Enum
from typing import Literal
from datamodel.accounts_tree import AccountsTree
from dbase import db_session, Transaction
import pandas as pd

delta_char = "\u0394"

class ReportDataSource: #Report Data Source
    def __init__(self, acc_tree):
        self.acc_tree = acc_tree

    def get_nodes(self):
        return self.acc_tree.get_nodes()
    
    def search_data(self, title, *years, verbose=False):
        if node := self.acc_tree.find_node(title):
            if verbose: node.print_tree()
            root = node.path.split('/')[1]

            if root  in ('Claims', 'Assets'):
                doc = 'Balance'
            elif root in ('Input', 'Output'):
                doc = 'Income'
            else:
                raise Exception('Unknown master group')
            
            node_proxy = node.proxy()
            if verbose:
                print('\nnode:', node,' proxy:', node_proxy)
            for child in node_proxy.children:
                child.codes = self.acc_tree.get_account_codes(child)
                if verbose: print(child.name, child.codes)
            else:
                if verbose: node.print_tree()

            with db_session() as db:
                data = list()
                for year in years:
                    desc = f'{doc.title()} closing seat for year {year}'
                    if verbose: print(f'\n{desc}')
                    trans = db.query(Transaction).filter_by(description=desc).one()
                    for child in node_proxy.children:
                        entries = [entry for entry in trans.entries if entry.account.code in child.codes]
                        amount = sum([entry.amount for entry in entries])
                        data.append([child.name, year, amount])
                    else:
                        if hasattr(node_proxy, 'code'):
                            entries = [entry for entry in trans.entries if entry.account.code == node_proxy.code]
                            amount = sum([entry.amount for entry in entries])
                            data.append([node_proxy.name, year, amount])
                        
                else:
                    if verbose:
                        for item in data: print(item)
                    index = [(concept.title(), year) for concept, year, _ in data]
                    index = pd.MultiIndex.from_tuples(index, names=['Concept','Year'])
                    amounts = [amount for _, _, amount in data]
                    df = pd.DataFrame({'amount': amounts}, index=index)
                    if verbose: print(df)
                    return df
        else:
            self.acc_tree.print(title)
            print(f'not found node for {title}')
            raise Exception(f'not found node for title {title}')        

    def get_data(self, title, *years, **kwargs):
        verbose = kwargs.get('verbose', False)
        multiIndex = kwargs.get('multiIndex', False)
        delta = kwargs.get('delta', False)
        total = kwargs.get('total', True)
        #diff = kwargs.get('diff', False)

        df = self.search_data(title, *years, verbose=verbose)
        if multiIndex: return df
        else:
            df = df.unstack(level='Year')
            df.columns = df.columns.droplevel(0)
            df = df.sort_values(by=list(df.columns[::-1]), ascending=True)
            if delta and len(years) >= 2:
                columns = df.select_dtypes(include='number').columns
                df[delta_char] = df[columns[-1]] - df[columns[0]]
                df['Abs'] = df[delta_char].abs()
                df.sort_values(by='Abs', ascending=True, inplace=True)
                df.drop('Abs', axis=1, inplace=True)
            if total:
                df.loc['Total'] = df.sum(numeric_only=True)
            return df

