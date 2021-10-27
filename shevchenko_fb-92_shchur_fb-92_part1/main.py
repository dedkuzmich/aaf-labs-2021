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
    ident = Word(initChars=alphas, bodyChars=(alphanums + '_'))

    col_indexed = Optional(CaselessLiteral('INDEXED'))
    create_full = Group(ident + col_indexed)
    created = delimitedList(create_full, delim=',')('created')

    create_command = CaselessLiteral('CREATE') + ident('table_name') + '(' + created + ');'
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
    ident = Word(initChars=alphas, bodyChars=(alphanums + '_'))

    value = QuotedString('"', escQuote='""')
    inserted = delimitedList(value, delim=',')('inserted')

    insert_command = CaselessLiteral('INSERT') + Optional(CaselessLiteral('INTO')) + ident('table_name') + '(' + inserted + ');'
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
    ident = Word(initChars=alphas, bodyChars=(alphanums + '_'))

    selected = (Char('*') ^ delimitedList(ident, delim=','))('selected')

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = QuotedString('"', escQuote='""')
    condition = Group((ident ^ value) + operator + (ident ^ value))('condition')

    order_mode = Optional(CaselessLiteral('ASC') ^ CaselessLiteral('DESC'))
    order_full = Group(ident + order_mode)
    ordered = delimitedList(order_full, delim=',')('ordered')

    select_command = CaselessLiteral('SELECT') + selected + CaselessLiteral('FROM') + ident('table_name') + Optional(CaselessLiteral('WHERE') + condition) + Optional(
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
    ident = Word(initChars=alphas, bodyChars=(alphanums + '_'))

    operator = (Word('=') ^ Word('!=') ^ Word('>') ^ Word('<') ^ Word('>=') ^ Word('<='))
    value = QuotedString('"', escQuote='""')
    condition = Group((ident ^ value) + operator + (ident ^ value))('condition')

    delete_command = CaselessLiteral('DELETE') + Optional(CaselessLiteral('FROM')) + ident('table_name') + Optional(CaselessLiteral('WHERE') + condition) + ';'
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
        # str11 = 'CREATE cats1 (id1,     favourite_food1);'
        # str12 = 'CREATE cats (id, name indexed, favourite_food);'
        # str13 = 'CREATE c (i, name indexed, favourite_food);'
        #
        # str21 = 'INSERT cats1 ("0", "burger", "kisa");'
        # str22 = 'INSERT INTO cats1 ("id1", "favourite_food1", "sdfgf", "qyure");'
        # str22 = 'INSERT INTO cats1 ("i  d1", "fa vourite_      food1", "s df gf", "qyu re");'
        #
        # str31 = 'SelEct dgr gg, gw rgwe, wgrgwrwg FroM cat1 wheRE gwrgwe > "ree";'
        # str32 = 'SelEct dgrgg, gwrgwe, wgrgwrwg FroM cat1 wheRE gwrgwe > "ree";'
        # str33 = 'SelEct * FroM cat1 wheRE gwrgwe > "ree";'
        # str34 = 'SELECT dgrgg, gwrgwe, wgrgwrwg FROM cat1 WHERE gwrgwe > "ree" ORDER_BY gladiator ASC, robber DESC, spitfire;'
        # str35 = 'SELECT * FROM cat1 WHERE gwrgwe > "ree" ORDER_BY gladiator ASC, robber DESC, spitfire;'
        # str36 = 'SELECT wewe, wrgwrwwr, ngfngf FROM cat1 WHERE gwrgwe > gwrgwe ORDER_BY gladiator ASC, robber DESC, spitfire;'
        # str37 = 'SELECT * FROM cat1 WHERE gwrgwe > "rtv ee" ORDER_BY gladiator ASC, robber DESC, spitfire;'
        # str38 = 'SELECT * FROM cat1 WHERE "rtv ee" > rrwgr ORDER_BY gladiator ASC, robber DESC, spitfire;'
        #
        # str41 = 'DELETE FROM cats WHERE name = "Mur zik";'
        # str42 = 'DELETE cats;'
        # str41 = 'DELETE FROM cats WHERE "Mur zik" = name;'
        # str41 = 'DELETE FROM cats WHERE name != surname;'

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
