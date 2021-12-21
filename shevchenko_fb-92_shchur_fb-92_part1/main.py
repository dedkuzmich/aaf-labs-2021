from pyparsing import *
from prettytable import PrettyTable
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

    def Insert_Element(self, value, counter = empty()):
        self.values.append(value)
        if counter != empty():
            self.counter = counter

        if self.indexed == True:
            temp = self.tree
            if value not in temp:
                temp[value] = [self.counter]
            elif isinstance(temp[value], list):
                temp[value].append(self.counter)
            else:
                temp[value] = [temp[value], self.counter]
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
        postfix = 0
        for i in range(0, len(header)):
            count = header.count(header[i])
            if count > 1:
                header[i] = header[i] + '*' * postfix
                postfix = postfix + 1

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


def Get_IDs(T, condition, Index_checker):
    operator = condition[1]
    ids = []
    if T.Check_Column(condition[0]) == True and T.Check_Column(condition[2]) == True:
        idx_1 = 0
        idx_2 = 0
        for column_1 in T.columns:
            if column_1.name == condition[0]:
                idx_1 = T.columns.index(column_1)

        for column_2 in T.columns:
            if column_2.name == condition[2]:
                idx_2 = T.columns.index(column_2)

        for idx in range(len(T.columns[0].values)):
            val_1 = T.columns[idx_1].values[idx]
            val_2 = T.columns[idx_2].values[idx]
            if (operator == '=' and val_1 == val_2) or (operator == '!=' and val_1 != val_2) \
                    or (operator == '>' and val_1 > val_2) or (operator == '<' and val_1 < val_2) \
                    or (operator == '>=' and val_1 >= val_2) or (operator == '<=' and val_1 <= val_2):
                id = T.columns[0].values[idx]
                ids.append(id)
    else:
        name = ''
        value = ''
        if T.Check_Column(condition[0]) == True and T.Check_Column(condition[2]) == False:
            name = condition[0]
            value = condition[2]
        elif T.Check_Column(condition[0]) == False and T.Check_Column(condition[2]) == True:
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

        for column in T.columns:
            if column.name == name:
                if column.indexed == True and Index_checker == True:
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
                                id.append(int(T.columns[0].values[idx]))
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


def Create_Empty_Table(name, T):
    empty_cols = []
    for column in T.columns:
        empty_cols.append(Column(column.name, column.indexed))
    Buff_T = Table(name, empty_cols)
    return Buff_T


def Add_Row(Source_T, Destination_T, id):
    for ID in Source_T.columns[0].values:
        if str(ID) == str(id):
            row_idx = Source_T.columns[0].values.index(ID)
            for col_idx in range(len(Destination_T.columns)):
                Destination_T.columns[col_idx].Insert_Element(Source_T.columns[col_idx].values[row_idx], int(id))
            break


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


def Change_Row(Source_T, Destination_T):
    Change_mass = []
    for dest_idx in Destination_T.columns[0].values:
        for source_idx in Source_T.columns[0].values:
            if dest_idx == source_idx:
                Change_mass.append(Destination_T.columns[0].values.index(dest_idx))
    for col in Source_T.columns:
        col_indx = Source_T.columns.index(col)
        for i in range(0, len(Change_mass)):
            Destination_T.columns[col_indx].values[Change_mass[i]] = col.values[i]
    return Destination_T



def Order_Table(T, order, order_depth, index_checker):
    if (order_depth >= len(order)):
        return T

    Buff_T = Create_Empty_Table('Buff_T', T)
    for id in T.columns[0].values:
        Add_Row(T, Buff_T, id)

    ids = []
    for column in T.columns:
        if column.name == order[order_depth][0]:
            if column.indexed == True and index_checker == True:
                for id in SortedDict(column.tree).values():
                    ids = ids + id
            else:
                for sorted_val in SortedList(column.values):
                    for row_idx in range(len(column.values)):
                        if column.values[row_idx] == sorted_val:
                            id = T.columns[0].values[row_idx]
                            if id not in ids:
                                ids.append(id)

            if order[order_depth][1] == 'DESC':
                ids = list(reversed(ids))

            for target_row_idx in range(len(ids)):
                buff_row_idx = Buff_T.columns[0].values.index(str(ids[target_row_idx]))
                for col_idx in range(len(T.columns)):
                    T.columns[col_idx].values[target_row_idx] = Buff_T.columns[col_idx].values[buff_row_idx]

            sorted_values = []
            for i in range(len(column.values)):
                if i == column.values.index(column.values[i]):
                    count = column.values.count(column.values[i])
                    if count >= 2:
                        sorted_values.append(column.values[i])
            for val in sorted_values:
                Fragment_T = Create_Empty_Table('Fragment_T', T)
                IDs = Get_IDs(T, [order[order_depth][0], '=', val], False)
                for id in IDs:
                    Add_Row(T, Fragment_T, str(id))
                Fragment_T = Order_Table(Fragment_T, order, order_depth + 1, False)
                Change_Row(Fragment_T, T)
                del Fragment_T
    return T


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
        # визначаємо в якій частині використати індексацію
        Indx_part = ''
        if parsed.condition != empty():
            for Table in DataBase:
                if Table.name == parsed.table_name:
                    for col in Table.columns:
                        if col.name == parsed.condition[0] and col.indexed == True:
                            Indx_part = Indx_part + 'Where'
                            break
                        elif col.name == parsed.condition[0] and col.indexed == False:
                            Indx_part = Indx_part + 'NoWhere'
                            break
        else:
            Indx_part = Indx_part + 'NoWhere'
        if parsed.ordered != empty():
            for Table in DataBase:
                if Table.name == parsed.table_name:
                    for col in Table.columns:
                        if col.name == parsed.ordered[0][0] and col.indexed == True:
                            Indx_part = Indx_part + 'Order'
                        elif col.name == parsed.ordered[0][0] and col.indexed == False:
                            Indx_part = Indx_part + 'NoOrder'
                            break
        else:
            Indx_part = Indx_part + 'NoOrder'
        if parsed.condition == empty() and parsed.ordered == empty():
            Indx_part = 'NoIndex'

        print(Indx_part)
        for Table in DataBase:
            if Table.name == parsed.table_name:
                printable_cols = []
                if (parsed.selected[0] == '*'):
                    printable_cols = Table.columns
                else:
                    if Table.Check_Columns(parsed.selected) == False:
                        print('At least 1 operand of condition must be a name of the column!')
                        return
                    for column in Table.columns:
                        for name in parsed.selected:
                            if column.name == name:
                                printable_cols.append(column)
                if Indx_part == 'NoIndex':
                    Table.Print_Selected(printable_cols)
                    return
                if parsed.ordered != empty():
                    order = []
                    for i in parsed.ordered:
                        name = i[0]
                        if Table.Check_Column(name) == False:
                            print('There is no column named', name)
                            return
                        if len(i) == 1:
                            mode = 'ASC'
                        else:
                            mode = i[1]
                        order.append([name, mode])
                if parsed.condition != empty():
                    if Table.Check_Column(parsed.condition[0]) == False and Table.Check_Column(parsed.condition[2]) == False:
                        print('At least 1 operand of condition must be a name of the column!')
                        return
                Where_Table = Create_Empty_Table('Where_Table', Table)
                # якщо індексація відбуваєтсья по Where то спочатку відкидаємо непотріні рядки а потім сортуємо
                if Indx_part == 'WhereNoOrder':
                    operator = parsed.condition[1]
                    ids = Get_IDs(Table, [parsed.condition[0], operator, parsed.condition[2]], True)
                    for id in ids:
                        Add_Row(Table, Where_Table, id)
                    if parsed.ordered != empty():
                        Where_Table = Order_Table(Where_Table, order, 0, False)
                # якщо індексація відбуваєтсья по Order то спочатку сортуємо а потім відкидаємо непотрібні
                if Indx_part == 'NoWhereOrder':
                    for id in Table.columns[0].values:
                        Add_Row(Table, Where_Table, id)
                    Where_Table = Order_Table(Where_Table, order, 0, True)
                    if parsed.condition != empty():
                        operator = parsed.condition[1]
                        ids = Get_IDs(Table, [parsed.condition[0], operator, parsed.condition[2]], False)
                        print(ids)
                        for id in ids:
                            Where_Table.Delete_Row(id)
                # якщо індексація відбуваєтсья і по Order і по Where то спочатку відкидаємо непотрібні а потім сортуємо
                if Indx_part == 'WhereOrder':
                    operator = parsed.condition[1]
                    ids = Get_IDs(Table, [parsed.condition[0], operator, parsed.condition[2]], True)
                    for id in ids:
                        Add_Row(Table, Where_Table, id)
                    if parsed.ordered != empty():
                        Where_Table = Order_Table(Where_Table, order, 0, True)
                # якщо індексація не відбуваєтсья по Order та Where то спочатку відкидаємо непотрібні а потім сортуємо
                if Indx_part == 'NoWhereNoOrder':
                    operator = parsed.condition[1]
                    ids = Get_IDs(Table, [parsed.condition[0], operator, parsed.condition[2]], False)
                    for id in ids:
                        Add_Row(Table, Where_Table, id)
                    if parsed.ordered != empty():
                        Where_Table = Order_Table(Where_Table, order, 0, False)
                Where_Table.Print_Selected(printable_cols)
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
                        ids = Get_IDs(Table, parsed.condition, True)
                        for id in ids:
                            Table.Delete_Row(id)
                        Table.Print()
                break


def Main():
    str100 = 'CREATE cats (age, name INDEXED, food, color, owner);'

    str200 = 'INSERT cats ("10", "bobrik", "abracadabra", "blue", "Bill");'
    str201 = 'INSERT cats ("3", "abra", "burger", "green", "Tim");'
    str202 = 'INSERT cats ("5", "kitty", "applepie", "orange", "Sam");'
    str203 = 'INSERT cats ("7", "kiskis", "melon", "black", "Tom");'
    str204 = 'INSERT cats ("10", "bobrik", "abracadabra", "brown", "John");'
    str205 = 'INSERT cats ("20", "zzzz", "fish", "green", "Sam");'
    str206 = 'INSERT cats ("6", "murzilka", "pumpkin", "white", "Ben");'
    str207 = 'INSERT cats ("18", "bobrik", "milk", "green", "Kris");'
    str208 = 'INSERT cats ("13", "bobrik", "abracadabra", "green", "Archy");'
    str209 = 'INSERT cats ("14", "cobra", "meat", "purple", "Martin");'
    str210 = 'INSERT cats ("13", "kiskis", "milk", "red", "Jack");'
    str211 = 'INSERT cats ("25", "cobra", "pizza", "yellow", "Anton");'
    str212 = 'INSERT cats ("5", "abra", "bread", "lighblue", "Joseph");'
    str213 = 'INSERT cats ("7", "kiskis", "melon", "blue", "Alex");'

    str300 = 'SELECT ID, name, food FROM cats WHERE food < "fish" ORDER_BY name DESC;'
    str301 = 'SELECT ID, name, food FROM cats WHERE food < "fish" ORDER_BY food DESC;'
    str302 = 'SELECT name, food FROM cats;'
    str303 = 'SELECT ID, name, food FROM cats WHERE food != "fish" ORDER_BY name ASC;'
    str304 = 'SELECT ID, name, food FROM cats WHERE food = "burger";'
    str305 = 'SELECT ID, name, food FROM cats WHERE name <= "cobra";'
    str306 = 'SELECT name FROM cats WHERE food < "fish" ORDER_BY name ASC, food DESC;'
    str307 = 'SELECT ID, name, food, color, owner FROM cats ORDER_BY name ASC;'
    str308 = 'SELECT ID, name, food, color, owner FROM cats ORDER_BY name ASC, food ASC;'
    str309 = 'SELECT ID, name, name, food, color, owner FROM cats ORDER_BY name, food, color DESC;'
    str310 = 'SELECT ID, name, food, color FROM cats ORDER_BY color DESC, food ASC, name DESC;'
    str311 = 'SELECT * FROM cats ORDER_BY color DESC;'

    str400 = 'DELETE FROM cats WHERE food != "burger";'
    str401 = 'DELETE FROM cats WHERE name > "cobra";'
    str402 = 'DELETE FROM cats WHERE name != food;'
    str403 = 'DELETE FROM cats WHERE "cobra" < name;'
    str404 = 'DELETE FROM cats;'

    # str1 = 'create t (x INDEXED, y);'
    # str2 = 'insert t ("aaa", "zz1");'
    # str3 = 'insert t ("aaa", "zz2");'
    # str4 = 'insert t ("xxx", "zzz3");'
    # str5 = 'insert t ("yyy", "zzz4");'
    # str6 = 'select * from t where x = "aaa";'
    # str7 = 'delete t where y = "zz2";'
    # str8 = 'select * from t where x = "aaa";'
    # str9 = 'select * from t  where x = "aaa" ORDER_BY x,y;'
    # str10 = 'select * from t;'
    # coms = [str1, str2, str3, str4, str5]
    # coms = coms + [str9, str10]

    coms = [str100]
    coms = coms + [str200, str201, str202, str203, str204, str205, str206, str207, str208, str209, str210, str211, str212, str213]
    coms.append(str309)
    for com in coms:
        # command = Input()
        command = Clear_Text(com)

        print('\nEntered SQL command: ' + command + '\n')
        lexem = command.split(' ')[0]
        if lexem == CaselessLiteral('CREATE'):
            Create(command)
        elif lexem == CaselessLiteral('INSERT'):
            Insert(command)
        elif lexem == CaselessLiteral('SELECT'):
            Select(command)
        elif lexem == CaselessLiteral('DELETE'):
            Delete(command)
        elif lexem == CaselessLiteral('EXIT;'):
            print('Thank you for working with our program!')
            return 0
        else:
            print('Entered command is unrecognised!')
        print('\n\n---------------------------------------------------------------\n\n')


Main()
