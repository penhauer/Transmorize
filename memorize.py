#!/usr/bin/env python3

import argparse
import sys
import sqlite3
import csv


class DAO(object):

    enable_foreign_key_query = """
        pragma foreign_keys = ON;
    """

    get_word_query = """
        select * from words
        where word = ?;
    """

    get_word_meanings_query = """
        select m.creation_date, m.meaning
        from meanings m
            inner join words w on m.word_id = w.id
        where w.word = ?
    """

    word_insertion_query = """
        insert into words (language, word) values ('en', ?);
    """

    insert_meaning_query = """
        insert into meanings (meaning, word_id)
        select ?, w.id
        from words w
        where w.word = ?;
    """

    get_last_query = """
        select w.word, m.meaning, m.creation_date
        from words w
            inner join meanings m on w.id = m.word_id
        order by m.creation_date desc
        limit ?;
    """

    remove_word_query = """
        delete 
        from words
        where word = ?;
    """

    remove_meaning_query = """
        delete 
        from meanings
        where id = ?;
    """

    def __init__(self):
        self.connection = sqlite3.connect('test.db')
        self.cursor = self.connection.cursor()
        self.enable_foreign_key()

    def enable_foreign_key(self):
        self.cursor.execute(DAO.enable_foreign_key_query)

    def get_last(self, n: int):
        self.cursor.execute(DAO.get_last_query, (n, ))
        return self.cursor.fetchall()

    def get_word(self, word: str):
        self.cursor.execute(DAO.get_word_query, (word, ))
        return self.cursor.fetchall()
    
    def get_word_meanings(self, word: str):
        self.cursor.execute(DAO.get_word_meanings_query, (word, ))
        return self.cursor.fetchall()
    
    def insert_word(self, word: str):
        self.cursor.execute(DAO.word_insertion_query, (word, ))
        self.connection.commit()

    def insert_meaning(self, word: str, meaning: str):
        self.cursor.execute(DAO.insert_meaning_query, (meaning, word))
        self.connection.commit()

    def remove_word(self, word: str):
        self.cursor.execute(DAO.remove_word_query, (word, ))
        self.connection.commit()

    def remove_meaning(self, meaning_id: int):
        self.cursor.execute(DAO.remove_meaning_query, (meaning_id, ))
        self.connection.commit()


class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def pretty_print_meanings(word, meanings):
    print()
    print(Color.BOLD, word, Color.END)
    for meaning in meanings:
        print("\t", meaning[1])
    print()



class Memorize(object):

    def __init__(self, dao):

        parser = argparse.ArgumentParser(
            description='Memorize description',
            usage='''memorize <command> [<args>]

command can be one of the following
   add         Record changes to the repository
   remove      Download objects and refs from another repository
   last        sdfasd asdf asdf asdfj
   search      sdfasdfasd asd fsdf s
   imp         import words as csv file
''')
        parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
            
        # use dispatch pattern to invoke method with same name

        self.dao = dao
        getattr(self, args.command)()

    def add(self):
        parser = argparse.ArgumentParser(prog='memorize save', description='')
        parser.add_argument('word', help='word to save')
        parser.add_argument('meaning', help='meaning to save')
        args = parser.parse_args(sys.argv[2:])
        word = self.dao.get_word(args.word)

        if word:
            print(f"There is already word {args.word} saved with following meanings")
            meanings = self.dao.get_word_meanings(args.word)
            pretty_print_meanings(args.word, meanings)
            prompt = input(f"do you still want to save {args.word} ~ {args.meaning} [yes/no]")
            if prompt not in ["yes", "y"]:
                print("save canceled")
                return
        else:
            self.dao.insert_word(args.word)
        print(f"saving {args.word} ~ {args.meaning}")
        self.dao.insert_meaning(args.word, args.meaning)

    def last(self):
        parser = argparse.ArgumentParser(prog='memorize last', description='')
        parser.add_argument('count', type=int, nargs='?', default=10, help='number of words to show')
        args = parser.parse_args(sys.argv[2:])

        last_list = self.dao.get_last(args.count)
        for item in last_list:
            print(item)

    def remove(self):
        parser = argparse.ArgumentParser(prog='memorize remove', description='')
        parser.add_argument('word', help='word to remove')
        args = parser.parse_args(sys.argv[2:])

        meanings = self.dao.get_word_meanings(args.word)
        for i, meaning in enumerate(meanings):
            print(i + 1, "->", meaning)

        index = input("enter index of meaning to remove. use 0 to remove all\n")
        if not index.isnumeric(): 
            print("please enter a number")
            return
        index = int(index)
        if index == 0:
            self.dao.remove_word(args.word)
        else:
            index -= 1
            self.dao.remove_meaning(meanings[index][0])

    def search(self):
        parser = argparse.ArgumentParser(prog='memorize search', description='')
        parser.add_argument('word', help='word to remove')
        args = parser.parse_args(sys.argv[2:])
        meanings = self.dao.get_word_meanings(args.word)

        if meanings:
            pretty_print_meanings(args.word, meanings)
        else:
            print(f"no record of {args.word} found")


    def imp(self):
        parser = argparse.ArgumentParser(prog='memorize import', description='')
        parser.add_argument('file', help='file to import')
        args = parser.parse_args(sys.argv[2:])
        with open(args.file) as file:
            csv_reader = csv.reader(file)
            for line in csv_reader:
                print(line)
                word = self.dao.get_word(line[2])
                if not word:
                    self.dao.insert_word(line[2])
                self.dao.insert_meaning(line[2], line[3])


if __name__ == '__main__':
    Memorize(DAO())

