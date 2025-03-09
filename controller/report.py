__author__ = 'Manuel Escriche'
from datamodel.seeds import seed
from dbase import db_session, Transaction, Account, BookEntry
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np
cm = 1/2.54

def get_income_data(label, year) -> dict:
    _desc = f'Income closing seat for year {year}'
    with db_session() as db:
        try:
            trans = db.query(Transaction).filter_by(description=_desc).one()
        except: raise

        if label == 'input':
            rev = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['rev'].code)])
            return  dict(rev=rev)
        elif label == 'output':
            out = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['out'].code)])
            earn = sum([entry.amount for entry in trans.entries
                        if entry.account.code == seed['earn'].code])
            return  dict(out=out,earn=earn)
        elif label == 'revenue':
            rev_pay = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_pay'].code)])
            rev_div = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_div'].code)])
            rev_int = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_int'].code)])
            rev_dis = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_dis'].code)])
            rev_reg = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_reg'].code)])
            rev_oth = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['rev_oth'].code)])
            return dict(
                rev_pay=rev_pay, rev_div=rev_div, rev_int=rev_int,
                rev_dis=rev_dis, rev_reg=rev_reg, rev_oth=rev_oth
            )
        elif label == 'outgoing':
            tax = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['tax'].code)])
            exp = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['exp'].code)])
            ins = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['ins'].code)])
            return dict(tax=tax, ins=ins, exp=exp)
        elif label == 'expense':
            exp_per = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exp_per'].code)])
            exp_hou = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exp_hou'].code)])
            exp_veh = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exp_veh'].code)])
            exp_ser = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exp_ser'].code)])
            exp_lnd = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exp_lnd'].code)])
            return dict(
                exp_per=exp_per, exp_hou=exp_hou,
                exp_veh=exp_veh, exp_ser=exp_ser, exp_lnd=exp_lnd
            )
        elif label == 'persons':
            expp_feed = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_feed'].code)])
            expp_clot = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_clot'].code)])
            expp_heal = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_heal'].code)])
            expp_info = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_info'].code)])
            expp_conn = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_conn'].code)])
            expp_acco = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_acco'].code)])
            expp_rest = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_rest'].code)])
            expp_trans =sum([entry.amount for entry in trans.entries
                    if entry.account.code.startswith(seed['expp_trans'].code)])
            expp_ent = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_ent'].code)])
            expp_lot = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expp_lot'].code)])
            return dict(
                expp_feed=expp_feed, expp_clot=expp_clot, expp_heal=expp_heal,
                expp_info=expp_info, expp_conn=expp_conn, expp_acco=expp_acco,
                expp_rest=expp_rest, expp_trans=expp_trans,
                expp_ent=expp_ent, expp_lot=expp_lot
            )
        elif label == 'house':
            exph_wws = sum([entry.amount for entry in trans.entries
                         if entry.account.code.startswith(seed['exph_wws'].code)])
            exph_ele = sum([entry.amount for entry in trans.entries
                         if entry.account.code.startswith(seed['exph_ele'].code)])
            exph_fuel = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exph_fuel'].code)])
            exph_con = sum([entry.amount for entry in trans.entries
                         if entry.account.code.startswith(seed['exph_con'].code)])
            exph_main=sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['exph_main'].code)])
            return dict(
                exph_wws=exph_wws, exph_ele=exph_ele,
                exph_fuel=exph_fuel, exph_con=exph_con,
                exph_main=exph_main
            )
        elif label == 'vehicle':
            expv_fuel = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expv_fuel'].code)])
            expv_park = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expv_park'].code)])
            expv_main = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expv_main'].code)])
            expv_toll = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['expv_toll'].code)])
            return dict(
                expv_fuel=expv_fuel, expv_main=expv_main,
                expv_toll=expv_toll
            )
        elif label == 'services':
            exps_not = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_not'].code])
            exps_reg = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_reg'].code])
            exps_law = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_law'].code])
            exps_arch = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_arch'].code])
            exps_comp = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_comp'].code])
            exps_bank = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_bank'].code])
            exps_trans = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_trans'].code])
            exps_form = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_form'].code])
            exps_adv = sum([entry.amount for entry in trans.entries
                            if entry.account.code == seed['exps_adv'].code])
            return dict(
                exps_not=exps_not, exps_reg=exps_reg, exps_law=exps_law,
                exps_arch=exps_arch, exps_comp=exps_comp,
                exps_bank=exps_bank, exps_trans=exps_trans,
                exps_form=exps_form, exps_adv=exps_adv
            )
        elif label == 'tax':
            tax_irpf=sum([entry.amount for entry in trans.entries
                          if entry.account.code == seed['tax_irpf'].code])
            tax_veh=sum([entry.amount for entry in trans.entries
                         if entry.account.code == seed['tax_veh'].code])
            tax_house=sum([entry.amount for entry in trans.entries
                           if entry.account.code == seed['tax_house'].code])
            tax_other=sum([entry.amount for entry in trans.entries
                           if entry.account.code in seed['tax_other'].code])
            return dict(
                tax_irpf=tax_irpf, tax_veh=tax_veh,
                tax_house=tax_house, tax_other=tax_other
            )
        elif label == 'insurance':
            ins_soc = sum([entry.amount for entry in trans.entries
                           if entry.account.code == seed['ins_soc'].code])
            ins_veh = sum([entry.amount for entry in trans.entries
                           if entry.account.code == seed['ins_veh'].code])
            ins_other = sum([entry.amount for entry in trans.entries
                             if entry.account.code == seed['ins_other'].code])
            return dict(
                ins_soc=ins_soc, ins_veh=ins_veh, ins_other=ins_other
            )
        else: return None
   
def get_balance_data(label, year) -> dict:
    _desc = f'Balance closing seat for year {year}'
    with db_session() as db:
        try:
            trans = db.query(Transaction).filter_by(description=_desc).one()
        except: raise

        house = sum([entry.amount for entry in trans.entries
                     if entry.account.code.startswith(seed['house'])])
        land = sum([entry.amount for entry in trans.entries
                    if entry.account.code.startswith(seed['land'])])
        vehicle = sum([entry.amount for entry in trans.entries
                       if entry.account.code.startswith(seed['vehicle'])])
        tools = sum([entry.amount for entry in trans.entries
                     if entry.account.code.startswith(seed['tools'])])
        furn = sum([entry.amount for entry in trans.entries
                    if entry.account.code.startswith(seed['furn'])])
        dev = sum([entry.amount for entry in trans.entries
                   if entry.account.code.startswith(seed['dev'])])
        pplan = sum([entry.amount for entry in trans.entries
                     if entry.account.code.startswith(seed['pplan'])])
        wallet = sum([entry.amount for entry in trans.entries
                      if entry.account.code.startswith(seed['wallet'])])
        bank_acc = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['bank_acc'])])
        inv_fund = sum([entry.amount for entry in trans.entries
                        if entry.account.code.startswith(seed['inv_fund'])])
        shares = sum([entry.amount for entry in trans.entries
                      if entry.account.code.startswith(seed['shares'])])
        fixed = sum([house,land,vehicle,tools,furn,dev])
        current = sum([wallet,bank_acc,inv_fund,shares,pplan])
        wealth = sum([entry.amount for entry in trans.entries
                      if entry.account.code.startswith(seed['wealth'])])
        earn = sum([entry.amount for entry in trans.entries
                    if entry.account.code.startswith(seed['earn'])])
        credit_card=sum([entry.amount for entry in trans.entries
                         if entry.account.code.startswith(seed['credit_card'])])
        debt = credit_card
            
    if label == 'assets':            
        return dict(fixed=fixed, current=current)
    elif label == 'claims':
        return dict(wealth=wealth, earn=earn, debt=debt)
    elif label == 'fixed':
        return dict(house=house, land=land, vehicle=vehicle,
                    tools=tools, furn=furn, dev=dev)
    elif label == 'current':
        return dict(wallet=wallet, bank_acc=bank_acc, inv_fund=inv_fund,
                    shares=shares, pplan=pplan)
    else:
        return None


def get_data(title:str, year:int) ->dict:
    _title = title.lower()
    if _title in ('assets', 'claims', 'fixed', 'current'):
        return get_balance_data(_title, year)
    elif _title in ('input', 'output', 'revenue', 'outgoing',
                    'expense','persons','house', 'vehicle',
                    'services', 'tax', 'insurance'):
        return get_income_data(_title, year)
    else:
        raise ValueError(f'Unknown title: {title}')

def get__data(title:str, years:tuple) ->list:
    _title = title.lower()
    data = dict()
    for year in years:
        if _title in ('assets', 'claims', 'fixed', 'current'):
            data[year] = get_balance_data(_title, year)
        elif _title in ('input', 'output', 'revenue', 'outgoing',
                        'expense','persons','house', 'vehicle',
                        'services','tax', 'insurance'):
            data[year]=get_income_data(_title, year)
        else:
            raise ValueError(f'Unknown title: {title}')
    else:
        return data
    
def create_graph(title:str, year:int, color:str):
    data = get_data(title, year)
    categories = tuple([seed[k].name for k in data.keys()]) 
    
    figsize = (10*cm, 10*cm) if len(categories) <= 5 else (13*cm, 10*cm)
    fig, ax = plt.subplots(figsize=figsize, layout='constrained')
    
    amounts = np.array([v for v in data.values()])
    total = sum(amounts)
    p = ax.bar(categories, amounts, color=color)
    labels = [f'{x:,.0f}\n({x/total:.0%})' for x in amounts]
    ax.bar_label(p, label_type='edge', labels=labels)
    
    fig.suptitle(f'{year} - {title}')
    ax.set_title(f'Total = {total:,.0f}€', fontsize=10)
    ax.set_ylim(0, total*1.05)
    plt.xticks(rotation=45, ha='right')
    return fig

def create_joint_table(titles:tuple, years:tuple) -> str:
    table = PrettyTable()
    table.align = 'r'
    fields = ['Year']
    data = {(year,title):get_data(title.lower(), year)
            for year in years for title in titles}
    total = {(year,title):sum(data[(year,title)].values())
             for year in years for title in titles}
    fields = ['Year']
    for title in titles:
        fields += [seed[key].name for key in data[years[0],title].keys()]
        fields += [f'Total {title}']
    else:
        table.field_names = fields
        
    for year in reversed(years):
        values = [str(year)]
        for title in titles:
            values += [f'{v:,.0f}' for v in data[(year,title)].values()]
            values += [f'{total[(year,title)]:,.0f}']
        else:
            table.add_row(values)
    else:
        table.add_divider()
        dff = ['']
        for title in titles:
            dff += [f'{a-b:,.0f}'\
                    for a,b in zip(data[(years[-1],title)].values(),
                                   data[(years[0],title)].values())]
            dff += [f'{total[(years[-1],title)] - total[(years[0],title)]:,.0f}']
        else:
            table.add_row(dff)   
    return str(table)
        
def create_table(title:str, years:tuple) -> str: 
    table = PrettyTable()
    table.align = 'r'
    data  = { year:get_data(title.lower(),year) for year in years }
    total = { year: sum(data[year].values()) for year in years }
        
    table.field_names=['Year']+\
        [seed[k].name for k in data[years[0]].keys()]+\
        ['Total']
        
    for year in reversed(years):
        table.add_row([str(year)] +
                      [f'{v:,.0f}' for v in data[year].values()] +
                      [f'{total[year]:,.0f}'])    
    else:
        table.add_divider()
        diffs =  [''] +\
            [f'{a-b:,.0f}' for a,b in zip(data[years[-1]].values(),
                                          data[years[0]].values())] +\
            [f'{total[years[-1]] - total[years[0]]:,.0f}']
        table.add_row(diffs)
        return str(table)
