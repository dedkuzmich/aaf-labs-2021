from pyparsing import *


def ClearText(multiline):
    index = multiline.find(';')
    multiline = multiline[slice(0, index + 1)]
    return ' '.join(multiline.replace('\n', '').replace('\r', '').split())


def Input():
    print('Please, enter SQL command (you should use at least one ";" symbol):')
    multiline = ''
    while ';' not in multiline:
        multiline = multiline + input()
    return ClearText(multiline)


def Create(command):
    table_name = (Combine(Char(alphas) + Word(alphanums + '_')))('table_name')
    col_name = Combine(Char(alphas) + Word(alphanums + '_'))

    col_indexed = Optional(CaselessLiteral('INDEXED'))
    crete_full = Group(col_name + col_indexed)
    created = Group(crete_full + ZeroOrMore(Suppress(',') + crete_full))('created')

    create_command = CaselessLiteral('CREATE') + table_name + '(' + created + ');'
    try:
        parsed = create_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        print('Table ' + parsed.table_name + ' was created.')
        print('Created table contains the following columns:')
        for i in parsed.created:
            if (len(i) == 1):
                print(i[0] + ' - non-indexed')
            else:
                print(i[0] + ' - indexed')


def Insert(command):
    table_name = (Combine(Char(alphas) + Word(alphanums + '_')))('table_name')

    value = Suppress('"') + Word(printables, excludeChars='"') + Suppress('"')
    inserted = Group(value + ZeroOrMore(Suppress(',') + value))('inserted')

    insert_command = CaselessLiteral('INSERT') + Optional(CaselessLiteral('INTO')) + table_name + '(' + inserted + ');'
    try:
        parsed = insert_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        print('Following row was inserted into table ' + parsed.table_name + ':')
        for i in parsed.inserted:
            print(i)


def Select(command):
    table_name = (Combine(Char(alphas) + Word(alphanums + '_')))('table_name')
    col_name = Combine(Char(alphas) + Word(alphanums + '_'))

    selected = Group(Char('*') ^ (col_name + ZeroOrMore(Suppress(',') + col_name)))('selected')

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = Suppress('"') + Word(printables, excludeChars='"') + Suppress('"')
    condition = Group(col_name + operator + value)('condition')

    order_mode = Optional(CaselessLiteral('ASC') ^ CaselessLiteral('DESC'))
    order_full = Group(col_name + order_mode)
    ordered = Group(order_full + ZeroOrMore(Suppress(',') + order_full))('ordered')

    select_command = CaselessLiteral('SELECT') + selected + CaselessLiteral('FROM') + table_name + Optional(CaselessLiteral('WHERE') + condition) + Optional(
        CaselessLiteral('ORDER_BY') + ordered) + ';'
    try:
        parsed = select_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        print('Following columns were selected from table ' + parsed.table_name + ':')
        if (parsed.selected[0] == '*'):
            print('All rows were selected.\n')
        else:
            for i in parsed.selected:
                print(i)
            print()
        if (len(parsed.condition) != 0):
            print('Only rows satisfying following condition were selected:')
            print(parsed.condition[0] + ' ' + parsed.condition[1] + ' ' + parsed.condition[2] + '\n')
        if (len(parsed.ordered) != 0):
            print('Selected rows were sorted by following column values (ASC - direct order, DESC - inverse order):')
            for i in parsed.ordered:
                if (len(i) == 1):
                    print(i[0] + ' - ' + 'ASC')
                else:
                    print(i[0] + ' - ' + i[1])


def Delete(command):
    table_name = (Combine(Char(alphas) + Word(alphanums + '_')))('table_name')
    col_name = Combine(Char(alphas) + Word(alphanums + '_'))

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = Suppress('"') + Word(printables, excludeChars='"') + Suppress('"')
    condition = Group(col_name + operator + value)('condition')

    delete_command = CaselessLiteral('DELETE') + Optional(CaselessLiteral('FROM')) + table_name + Optional(CaselessLiteral('WHERE') + condition) + ';'
    try:
        parsed = delete_command.parseString(command)
    except ParseException as pe:
        print('Cannot correctly parse this SQL command!')
        print(pe)
        print('Сolumn: {}'.format(pe.column))
    else:
        if (len(parsed.condition) != 0):
            print('Only rows satisfying following condition were deleted:')
            print(parsed.condition[0] + ' ' + parsed.condition[1] + ' ' + parsed.condition[2] + '\n')
        else:
            print('Table ' + parsed.table_name + ' was deleted.')


def Main():
    while True:
        command = Input()
        # str1 = 'CREATE cats1 (id1,     favourite_food1);'
        # str2 = 'CREATE cats (id, name indexed, favourite_food);'
        # str3 = 'CrEatE\t cats1 (id\r, name \t \n \r inDexEd, \n favourite_food); tehethe\rte'
        #
        # str4 = 'SelEct \n \t dgrgg\r, \t \n \t gwrgwe\n,\t wgrgwrwgw \tFroM\n cat1; trh\nrgsfgsg'
        # str5 = 'SelEct dgrgg, gwrgwe, wgrgwrwg FroM cat1 wheRE gwrgwe > "ree";'
        # str6 = 'SelEct * FroM cat1 wheRE gwrgwe > "ree";'
        # str7 = 'SELECT dgrgg, gwrgwe, wgrgwrwg FROM cat1 WHERE gwrgwe > "ree" ORDER_BY gladiator ASC, robber DESC, spitfire;'
        # str8 = 'SELECT * FROM cat1 WHERE gwrgwe > "ree" ORDER_BY gladiator ASC, robber DESC, spitfire;'
        #
        # str9 = 'DELETE FROM cats WHERE name = "Murzik";'
        # str10 = 'DELETE cats;'
        #
        # str11 = 'INSERT cats1 ("0", "burger", "kisa");'
        # str12 = 'INSERT INTO cats1 ("id1", "favourite_food1", "sdfgf", "qyure");'

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
