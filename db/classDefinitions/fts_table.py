from sqlalchemy import Column, Integer, String
from .shared_base import Base




class BookFTS(Base):
    __tablename__ = 'book_fts'
    __table_args__ = {'sqlite_with_rowid': False}  # FTS tables already use 'rowid' internally
    rowid = Column(Integer, primary_key=True)
    title = Column(String)
    authors = Column(String)

    def __repr__(self):
        return f"<BookFTS(title={self.title}, authors={self.authors})>"

# # fts_table
# from sqlalchemy import Column, Integer, String
# from .date_columns import TimestampMixin 
# from .shared_base import Base

# class BookFTS(Base, TimestampMixin):
#     __tablename__ = 'book_fts'
#     rowid = Column(Integer, primary_key=True)  # FTS5 uses 'rowid' as a unique identifier
#     title = Column(String)
#     authors = Column(String)

#     def __repr__(self):
#         return f"<BookFTS(title={self.title}, authors={self.authors})>"