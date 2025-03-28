__author__='Manuel Escriche'
import re, json
from dbase import find_path, db_session
from dbase import Account as db_Account

class Node:
    def __init__(self, name):
        self.name = name.lower()
        self.children = list()
        self.parent = None
        
    @property
    def path(self):
        if self.parent:
            return self.parent.path.title() + '/' + self.name.title()
        else: return ''

    def add_children(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)
            
    def find(self, condition): # return first occurrence meeting condition
        if condition(self):
            return self
        for child in self.children:
            if result := child.find(condition):
                return result
        return None        
    
    def search(self, condition): #returns all occurrences meeting condition
        results = list()
        if condition(self):
            results.append(self)
        for child in self.children:
            results.extend(child.search(condition))
        return results
            
    def get_level(self):
        level = 0
        p = self.parent
        while (p:= self.parent):
            level += 1
            self = p
        return level
    
    def proxy(self):
        node = self
        while len(node.children) == 1:
            node = next(iter(node.children))
        return node
    
    def print_tree(self):
        spaces = '  ' * self.get_level() * 3
        prefix = spaces + "|___" if self.parent else ''
        print(prefix + str(self))
        if self.children:
            for child in self.children:
                child.print_tree()

    def __str__(self):
        return self.name
    
class Group(Node):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name.title()
        #return f'GRP({self.name.title()})'
    
    @property
    def ext_name(self):
        return self.path
    
class Account(Node):
    def __init__(self, name, code, gname):
        super().__init__(name)
        self.code = code
        self.gname = gname
        
    def __str__(self):
        return self.gname
        #return f'ACC({self.name}:{self.code}:{self.gname})'
        
    @property
    def ext_name(self):
        return self.gname

class AccountsTree:
    def __init__(self, data):
        self.root = Node('/')
        for entry in data:
            self._add_account(*entry )
                
    @classmethod
    def from_db(cls):
        with db_session() as db:
            accounts = db.query(db_Account).all()
            data = [(acc.path,acc.name, acc.code, acc.gname) for acc in accounts]
            return cls(data)

    @classmethod
    def from_file(cls, filename):
        with open(filename) as acc_file:
            _data = json.load(acc_file)
            data = list()
            for rec in _data:
                con, typ, name, code = rec['content'], rec['type'], rec['name'], rec['code']
                path = find_path(rec['code'])                
                gname = f'[{typ[0]}{con[0]}-{code}] {name}'
                data.append((path, name, code, gname))
            else:
                return cls(data)
    
    def find_node(self, name):
        if match := re.fullmatch(r'(/\w+)+', name):
            #name = name.split('/')[-1].lower()
            return self.root.find(lambda node: isinstance(node, Group) and node.path == name)
        elif match := re.fullmatch(r'\[((C|D)(R|N))-(\d+)\]\s(?P<name>[-\/\s\w]+)', name):
            #name = match.group('name').lower()
            return self.root.find(lambda node: isinstance(node, Account) and node.gname == name)
        else:
            return self.root.find(lambda node: node.name == name.lower())
    
    def print(self, name='/'):
        if node := self.find_node(name):
            node.print_tree()
            
    def _add_path(self, path):
        chunks = path.split('/')
        father = self.root
        for chunk in chunks:
            if node := father.find(lambda node: node.name == chunk):
                father = node
            else:
                node = Group(chunk)
                father.add_children(node)
                father = node
        else:
            return father
            
    def _add_account(self, path, name, code, gname):
        father = self._add_path(path)
        accounts = father.search(lambda node: isinstance(node, Account))
        for node in accounts:
            if node.name == name:
                return #existing account
            
        #search for parents
        parents = [acc for acc in accounts if code.startswith(acc.code)]
        if not parents:
            p_name = path.split('/')[-1]
            parent = father.find(lambda node: node.name == p_name)
            
        elif len(parents) == 1:
            parent = next(iter(parents))
        else: # several fathers
            matching = list()
            for parent in parents:
                size = min(len(parent.code), len(code))
                test = [parent.code[i] == code[i] for i in range(size)]
                matching.append(sum(test))
            ndx = matching.index(max(matching))
            parent = parents[ndx]

        node = Account(name, code, gname)
        parent.add_children(node)

    def get_account_codes(self, node):
        accounts = node.search(lambda node: isinstance(node, Account))
        codes = [account.code for account in accounts]
        return codes

    def get_accounts(self):
        accounts = self.root.search(lambda node: isinstance(node, Account))
        return accounts
    
    def get_groups(self):
        groups = self.root.search(lambda node: isinstance(node, Group))
        return groups
    
    def get_nodes(self):
        nodes = self.root.search(lambda node: isinstance(node, Account) or isinstance(node, Group))
        #return nodes
        return [node.ext_name for node in nodes]

