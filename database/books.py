from typing import List, Type
from database.db_baseclass import Database
from models.books import DatabaseBookDataModel


def get_all_books_data(db: Database) -> List[DatabaseBookDataModel] | Type[list[None]]:
    db_result = db.execute_db_request(
        query='SELECT * from public.books',
        fetchmode='all'
    )
    if db_result is not None:
        books_list = []
        for book_data_bundle in db_result:
            book_data = DatabaseBookDataModel(
                id=book_data_bundle.id,
                title=book_data_bundle.title,
                author=book_data_bundle.author,
                isbn=book_data_bundle.isbn
            )
            books_list.append(book_data)
        return books_list
    else:
        return List[None]


def get_book_data_by_id(db: Database, book_id: str) -> DatabaseBookDataModel | None:
    db_result = db.execute_db_request(
        query='SELECT * from public.books WHERE id = %s;',
        params=(book_id,),
        fetchmode='one'
    )
    if db_result is not None:
        book_data = DatabaseBookDataModel(
            id=db_result.id,
            title=db_result.title,
            author=db_result.author,
            isbn=db_result.isbn
        )
        return book_data
    else:
        return None


def get_book_data_by_isbn(db: Database, isbn: str) -> DatabaseBookDataModel | None:
    db_result = db.execute_db_request(
        query='SELECT * from public.books WHERE isbn = %s;',
        params=(isbn,),
        fetchmode='one'
    )
    if db_result is not None:
        book_data = DatabaseBookDataModel(
            id=db_result.id,
            title=db_result.title,
            author=db_result.author,
            isbn=db_result.isbn
        )
        return book_data
    else:
        return None


def get_books_count(db: Database) -> int:
    db_result = db.execute_db_request(
        query="SELECT count(*) FROM public.books;",
        fetchmode='one'
    )
    books_count = db_result[0]
    return books_count
