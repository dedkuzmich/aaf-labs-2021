from pyparsing import *
from prettytable import PrettyTable
import copy
import numpy as np
from sortedcontainers import SortedDict, SortedList

DataBase = []


def Find_Occurrences(list, value):
    indexes = []
    for idx in range(len(list)):
        if list[idx] == value:
            indexes.append(idx)
    return indexes


class Column:
    def __init__(self, name, indexed):
        self.name = name
        self.indexed = indexed
        self.values = []
        self.counter = 0
        if indexed == True:
            self.tree = {}

    def Delete_Element(self, index, id):
        value = self.values[index]
        self.values.pop(index)
        if self.indexed == True:
            temp = self.tree
            if len(temp[value]) == 1:
                del temp[value]
            else:
                temp[value].remove(int(id))
            self.tree = SortedDict(temp)

    def Insert_Element(self, value):
        self.values.append(value)
        if self.indexed == True:
            temp = self.tree
            if value not in temp:
                temp[value] = [self.counter]
            elif isinstance(temp[value], list):
                temp[value].append(self.counter)
            else:
                temp[value] = [temp[value], self.counter]
            self.tree = SortedDict(temp)
        self.counter = self.counter + 1


class Table:
    def __init__(self, name, cols):
        self.name = name
        self.columns = cols

    def Print(self):
        header = []
        for column in self.columns:
            header.append(column.name)
        table = PrettyTable(header)

        for idx in range(len(self.columns[0].values)):
            row = []
            for column in self.columns:
                row.append(column.values[idx])
            table.add_row(row)
        print(table)

    def Print_Selected(self, cols):
        header = []
        for column in self.columns:
            for col in cols:
                if column.name == col.name:
                    header.append(column.name)
        table = PrettyTable(header)

        for idx in range(len(self.columns[0].values)):
            row = []
            for column in self.columns:
                for col in cols:
                    if column.name == col.name:
                        row.append(column.values[idx])
            table.add_row(row)
        print(table)

    def Delete_Row(self, id):
        for ID in self.columns[0].values:
            if int(ID) == int(id):
                idx = self.columns[0].values.index(ID)
                for column in self.columns:
                    column.Delete_Element(idx, id)
                break

    def Check_Column(self, name):
        for column in self.columns:
            if name == column.name:
                return True
        return False

    def Check_Columns(self, names):
        for name in names:
            if self.Check_Column(name) == False:
                print('There is no column ', name, ' in table ', self.name)
                return False
        return True


def Check_Table(name):
    for table in DataBase:
        if table.name == name:
            return True
    print('There is no table named', name, 'in data base!')
    return False


def Get_IDs(Table, condition):
    operator = condition[1]
    ids = []
    if Table.Check_Column(condition[0]) == True and Table.Check_Column(condition[2]) == True:
        idx_1 = 0
        idx_2 = 0
        for column_1 in Table.columns:
            if column_1.name == condition[0]:
                idx_1 = Table.columns.index(column_1)

        for column_2 in Table.columns:
            if column_2.name == condition[2]:
                idx_2 = Table.columns.index(column_2)

        for idx in range(len(Table.columns[0].values)):
            val_1 = Table.columns[idx_1].values[idx]
            val_2 = Table.columns[idx_2].values[idx]
            if (operator == '=' and val_1 == val_2) or (operator == '!=' and val_1 != val_2) \
                    or (operator == '>' and val_1 > val_2) or (operator == '<' and val_1 < val_2) \
                    or (operator == '>=' and val_1 >= val_2) or (operator == '<=' and val_1 <= val_2):
                id = Table.columns[0].values[idx]
                ids.append(id)
    else:
        name = ''
        value = ''
        if Table.Check_Column(condition[0]) == True and Table.Check_Column(condition[2]) == False:
            name = condition[0]
            value = condition[2]
        elif Table.Check_Column(condition[0]) == False and Table.Check_Column(condition[2]) == True:
            name = condition[2]
            value = condition[0]
            if operator == '>':
                operator = '<'
            elif operator == '<':
                operator = '>'
            elif operator == '>=':
                operator = '<='
            elif operator == '<=':
                operator = '>='

        for column in Table.columns:
            if column.name == name:
                if column.indexed == True:
                    for val in column.tree:
                        if (operator == '=' and val == value) or (operator == '!=' and val != value) \
                                or (operator == '>' and val > value) or (operator == '<' and val < value) \
                                or (operator == '>=' and val >= value) or (operator == '<=' and val <= value):
                            id = column.tree[val]
                            ids = ids + id
                else:
                    for val in column.values:
                        if (operator == '=' and val == value) or (operator == '!=' and val != value) \
                                or (operator == '>' and val > value) or (operator == '<' and val < value) \
                                or (operator == '>=' and val >= value) or (operator == '<=' and val <= value):
                            pass

                            indexes = Find_Occurrences(column.values, val)
                            id = []
                            for idx in indexes:
                                id.append(Table.columns[0].values[idx])
                            ids = ids + id
    return np.unique(ids)


def Clear_Text(multiline):
    index = multiline.find(';')
    multiline = multiline[slice(0, index + 1)]
    return ' '.join(multiline.replace('\n', '').replace('\r', '').split())


def Input():
    print('Please, enter SQL command (you should use at least one ";" symbol):')
    multiline = ''
    while ';' not in multiline:
        multiline = multiline + input()
    return Clear_Text(multiline)


def Create(command):
    ident = Word(initChars = alphas, bodyChars = (alphanums + '_'))

    col_indexed = Optional(CaselessLiteral('INDEXED'))
    create_full = Group(ident + col_indexed)
    created = delimitedList(create_full, delim = ',')('created')

    create_command = CaselessLiteral('CREATE') + ident('table_name') + '(' + created + ');'
    try:
        parsed = create_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        print('Created table', parsed.table_name, 'contains the following columns:')
        columns = []
        column = Column('ID', False)
        columns.append(column)
        for i in parsed.created:
            if (len(i) == 1):
                print(i[0] + '  NON-INDEXED')
                column = Column(i[0], False)
            else:
                print(i[0] + '  INDEXED')
                column = Column(i[0], True)
            columns.append(column)

        table = Table(parsed.table_name, columns)
        table.Print()
        DataBase.append(table)


def Insert(command):
    ident = Word(initChars = alphas, bodyChars = (alphanums + '_'))

    value = QuotedString('"', escQuote = '""')
    inserted = delimitedList(value, delim = ',')('inserted')

    insert_command = CaselessLiteral('INSERT') + Optional(CaselessLiteral('INTO')) + ident('table_name') + '(' + inserted + ');'
    try:
        parsed = insert_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        if Check_Table(parsed.table_name) == False:
            return

        for Table in DataBase:
            if Table.name == parsed.table_name:
                if (len(parsed.inserted) == len(Table.columns) - 1):

                    parsed.inserted.insert(0, str(Table.columns[0].counter))
                    for idx in range(len(Table.columns)):
                        Table.columns[idx].Insert_Element(parsed.inserted[idx])

                    Table.Print()
                else:
                    print('You should insert', len(Table.columns) - 1, 'elements!')
                break


def Select(command):
    ident = Word(initChars = alphas, bodyChars = (alphanums + '_'))

    selected = (Char('*') ^ delimitedList(ident, delim = ','))('selected')

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = QuotedString('"', escQuote = '""')
    condition = Group((ident ^ value) + operator + (ident ^ value))('condition')

    order_mode = Optional(CaselessLiteral('ASC') ^ CaselessLiteral('DESC'))
    order_full = Group(ident + order_mode)
    ordered = delimitedList(order_full, delim = ',')('ordered')

    select_command = CaselessLiteral('SELECT') + selected + CaselessLiteral('FROM') + ident('table_name') + Optional(CaselessLiteral('WHERE') + condition) + Optional(
        CaselessLiteral('ORDER_BY') + ordered) + ';'
    try:
        parsed = select_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        if Check_Table(parsed.table_name) == False:
            return

        for Table in DataBase:
            if Table.name == parsed.table_name:
                printable_cols = []
                if (parsed.selected[0] == '*'):
                    printable_cols = Table.columns
                else:
                    if Table.Check_Columns(parsed.selected) == False:
                        return
                    for column in Table.columns:
                        for name in parsed.selected:
                            if column.name == name:
                                printable_cols.append(column)

                Where_Table = copy.deepcopy(Table)
                if parsed.condition != empty():
                    operator = ''
                    if parsed.condition[1] == '=':
                        operator = '!='
                    elif parsed.condition[1] == '!=':
                        operator = '='
                    elif parsed.condition[1] == '>':
                        operator = '<='
                    elif parsed.condition[1] == '<':
                        operator = '>='
                    elif parsed.condition[1] == '>=':
                        operator = '<'
                    elif parsed.condition[1] == '<=':
                        operator = '>'

                    if Where_Table.Check_Column(parsed.condition[0]) == False and Table.Check_Column(parsed.condition[2]) == False:
                        print('At least 1 operand of condition must be a name of the column!')
                        return
                    else:
                        ids = Get_IDs(Where_Table, [parsed.condition[0], operator, parsed.condition[2]])
                        for id in ids:
                            Where_Table.Delete_Row(id)

                Order_table = copy.deepcopy(Where_Table)
                if parsed.ordered != empty():
                    for i in parsed.ordered:
                        name = i[0]
                        if Table.Check_Column(name) == False:
                            print('There is no column named', name)
                            return
                        if len(i) == 1:
                            order = 'ASC'
                        else:
                            order = i[1]

                        Buff_table = copy.deepcopy(Order_table)
                        ids = []
                        for column in Order_table.columns:
                            if column.name == name:
                                if column.indexed == True:
                                    for id in SortedDict(column.tree).values():
                                        ids = ids + id
                                else:
                                    for sorted_val in SortedList(column.values):
                                        for row_idx in range(len(column.values)):
                                            if column.values[row_idx] == sorted_val:
                                                id = Order_table.columns[0].values[row_idx]
                                                if id not in ids:
                                                    ids.append(id)
                                break

                        if order == 'DESC':
                            ids = list(reversed(ids))

                        for target_row_idx in range(len(ids)):
                            buff_row_idx = Buff_table.columns[0].values.index(str(ids[target_row_idx]))
                            for col_idx in range(len(Order_table.columns)):
                                Order_table.columns[col_idx].values[target_row_idx] = Buff_table.columns[col_idx].values[buff_row_idx]

                Order_table.Print_Selected(printable_cols)
            break


def Delete(command):
    ident = Word(initChars = alphas, bodyChars = (alphanums + '_'))

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = QuotedString('"', escQuote = '""')
    condition = Group((ident ^ value) + operator + (ident ^ value))('condition')

    delete_command = CaselessLiteral('DELETE') + Optional(CaselessLiteral('FROM')) + ident('table_name') + Optional(CaselessLiteral('WHERE') + condition) + ';'
    try:
        parsed = delete_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        if Check_Table(parsed.table_name) == False:
            return

        for Table in DataBase:
            if Table.name == parsed.table_name:
                if parsed.condition == empty():
                    print('Table ' + Table.name + ' was deleted.')
                    DataBase.remove(Table)
                else:
                    if Table.Check_Column(parsed.condition[0]) == False and Table.Check_Column(parsed.condition[2]) == False:
                        print('At least 1 operand of condition must be a name of the column!')
                        return
                    else:
                        ids = Get_IDs(Table, parsed.condition)
                        for id in ids:
                            Table.Delete_Row(id)
                        Table.Print()
                break


def Main():
    # str100 = 'CREATE cats (age, name INDEXED, favourite_food);'

    # str200 = 'INSERT cats ("10", "bobrik", "meat");'
    # str201 = 'INSERT cats ("3", "abra", "burger");'
    # str202 = 'INSERT cats ("5", "kitty", "applepie");'
    # str203 = 'INSERT cats ("7", "kiskis", "melon");'
    # str204 = 'INSERT cats ("14", "cobra", "milk");'
    # str205 = 'INSERT cats ("20", "zzzz", "fish");'
    # str206 = 'INSERT cats ("6", "murzilka", "pumpkin");'
    # str207 = 'INSERT cats ("18", "bobrik", "abracadabra");'

    # str200 = 'INSERT cats ("10", "bobrik", "meat");'
    # str201 = 'INSERT cats ("19", "kiskis", "burger");'
    # str202 = 'INSERT cats ("25", "bobrik", "applepie");'
    # str203 = 'INSERT cats ("27", "kiskis", "kiskis");'
    # str204 = 'INSERT cats ("15", "cobra", "burger");'
    # str205 = 'INSERT cats ("20", "bobrik", "fish");'
    # str206 = 'INSERT cats ("12", "murzilka", "cobra");'
    # str207 = 'INSERT cats ("18", "bobrik", "abracadabra");'

    # str300 = 'SELECT ID, name, favourite_food FROM cats WHERE favourite_food < "fish" ORDER_BY name DESC;'
    # str301 = 'SELECT ID, name, favourite_food FROM cats WHERE favourite_food < "fish" ORDER_BY favourite_food DESC;'
    # str302 = 'SELECT name, favourite_food FROM cats;'
    # str303 = 'SELECT ID, name, favourite_food FROM cats WHERE favourite_food != "fish" ORDER_BY name ASC;'
    # str304 = 'SELECT ID, name, favourite_food FROM cats WHERE favourite_food = "burger";'
    # str305 = 'SELECT ID, name, favourite_food FROM cats WHERE name <= "cobra";'
    # str306 = 'SELECT ID, name, favourite_food FROM cats WHERE favourite_food < "fish" ORDER_BY name DESC, favourite_food;'

    # str400 = 'DELETE FROM cats WHERE favourite_food != "burger";'
    # str401 = 'DELETE FROM cats WHERE name > "cobra";'
    # str402 = 'DELETE FROM cats WHERE name != favourite_food;'
    # str403 = 'DELETE FROM cats WHERE "cobra" < name;'
    # str404 = 'DELETE FROM cats;'

    while (True):
        command = Input()
        command = Clear_Text(command)
        print('\nEntered SQL command: ' + command + '\n')
        lexem = command.split(' ')[0]
        if (lexem == CaselessLiteral('CREATE')):
            Create(command)
        elif (lexem == CaselessLiteral('INSERT')):
            Insert(command)
        elif (lexem == CaselessLiteral('SELECT')):
            Select(command)
        elif (lexem == CaselessLiteral('DELETE')):
            Delete(command)
        elif (lexem == CaselessLiteral('EXIT;')):
            print('Thank you for working with our program!')
            return 0
        else:
            print('Entered command is unrecognised!')
        print('\n\n---------------------------------------------------------------\n\n')


Main()
