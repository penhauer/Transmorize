#!./venv/bin/python3

import argparse
import csv
import sys

import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()


class Word(Base):
    __tablename__ = "words"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      server_default=sqlalchemy.text("(datetime('now', 'localtime'))"))
    meanings = sqlalchemy.orm.relationship(
        "Meaning", back_populates="word", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Word(id={self.id}, word={self.word})"


class Meaning(Base):
    __tablename__ = "meanings"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    meaning = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Word.__tablename__ + ".id"), nullable=False)
    word = sqlalchemy.orm.relationship("Word", back_populates="meanings")

    creation_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      server_default=sqlalchemy.text("(datetime('now', 'localtime'))"))

    def __repr__(self):
        return f"Meaning(id={self.id}, meaning={self.meaning})"

database_name = "dict.db"
engine = sqlalchemy.create_engine(f"sqlite:///{database_name}", echo=False, future=True)
session = sqlalchemy.orm.Session(engine)



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
        print("\t", meaning.meaning)
    print()


def get_word(word):
    return session.query(Word).filter(Word.word == word).first()


def get_last(count):
    return session.query(Meaning) \
        .join(Word) \
        .order_by(Meaning.creation_date.desc()) \
        .limit(count).all()


def search_word(word):
    return session.query(Word) \
        .filter(sqlalchemy.and_(Word.word.like(f"%{word}%"))) \
        .all()


def add_word(w):
    word = Word(word=w, meanings=[])
    session.add(word)
    session.commit()
    return word


def add_meaning(word, meaning):
    meaning = Meaning(word=word, meaning=meaning)
    session.add(meaning)
    session.commit()


def remove_word(word):
    session.delete(word)
    session.commit()


def remove_meaning(meaning):
    session.delete(meaning)
    session.commit()


def remove():
    def parse_arguments():
        parser = argparse.ArgumentParser(prog='memorize remove', description='')
        parser.add_argument('word', help='word to remove')
        args = parser.parse_args(sys.argv[2:])
        return args.word

    def print_word_meanings(word):
        for i, meaning in enumerate(word.meanings):
            print(i + 1, "->", meaning)

    def get_index_to_remove():
        index = input("enter index of meaning to remove. use 0 to remove all\n")
        if not index.isnumeric():
            print("please enter a number")
            return
        index = int(index)
        return index

    def remove_meaning_or_word(word, index):
        if index == 0:
            print("removing whole word")
            remove_word(word)
        else:
            index -= 1
            meaning = word.meanings[index]

            if len(word.meanings) == 1:
                remove_word(word)
                print("removed the word")
            else:
                remove_meaning(meaning)
                print(f"removed meaning {meaning}")


    w = parse_arguments()
    word = get_word(w)
    if not word:
        print(f"no record of word {w} found")
        return
    print_word_meanings(word)
    index = get_index_to_remove()
    remove_meaning_or_word(word, index)


class Memorize(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Memorize description',
            usage='''
memorize <command> [<args>]

command can be one of the following
   add         Add a word and meaning
   remove      Remove meanings of a word or the word itself
   last        Show last Added words
   search      Search for similar added words
   imp         import words from a csv file in google translate format
''')
        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)()

    def add(self):
        parser = argparse.ArgumentParser(prog='memorize save', description='')
        parser.add_argument('word', help='word to save')
        parser.add_argument('meaning', help='meaning to save')
        args = parser.parse_args(sys.argv[2:])

        word = session.query(Word).where(Word.word == args.word).one_or_none()

        if word:
            print(f"There is already word {args.word} saved with following meanings")
            meanings = word.meanings
            pretty_print_meanings(args.word, meanings)
            prompt = input(f"do you still want to save {args.word} ~ {args.meaning} [yes/no]")
            if prompt not in ["yes", "y"]:
                print("save canceled")
                return
        else:
            word = add_word(args.word)
        print(f"saving {args.word} ~ {args.meaning}")
        add_meaning(word, args.meaning)

    def last(self):
        parser = argparse.ArgumentParser(prog='memorize last', description='')
        parser.add_argument('count', type=int, nargs='?', default=10, help='number of words to show')
        args = parser.parse_args(sys.argv[2:])
        last_list = get_last(args.count)
        for item in last_list:
            print(item.word.word, "\t\t", item.meaning)

    def remove(self):
        remove()

    def search(self):
        parser = argparse.ArgumentParser(prog='memorize search', description='')
        parser.add_argument('word', help='word to remove')
        args = parser.parse_args(sys.argv[2:])
        words = search_word(args.word)
        for word in words:
            pretty_print_meanings(word.word, word.meanings)

    def imp(self):
        parser = argparse.ArgumentParser(prog='memorize import', description='')
        parser.add_argument('file', help='file to import')
        args = parser.parse_args(sys.argv[2:])
        with open(args.file) as file:
            csv_reader = csv.reader(file)
            for line in csv_reader:
                print(line)
                word = get_word(line[2])
                if not word:
                    add_word(line[2])
                if not line[3] in word.meanings:
                    add_meaning(word, line[3])

    def init(self):
        print("initializing")
        pass


if __name__ == '__main__':
    Memorize()
