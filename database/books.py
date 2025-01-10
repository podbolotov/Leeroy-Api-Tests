from database.db_baseclass import Database
from models.books import DatabaseBookDataModel


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
