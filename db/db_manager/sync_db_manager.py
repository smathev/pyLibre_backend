# sync_db_manager.py
from sqlalchemy import create_engine, text
from .base_db_manager import BaseDBManager
from sqlalchemy.orm import sessionmaker
from ..classDefinitions.shared_base import Base
from ..classDefinitions.configure_relationship import ConfigureRelationships
from loguru import logger

class SyncDBManager(BaseDBManager):
    def __init__(self):
        super().__init__()
        self.engine = create_engine(f'sqlite:///{self.db_file}')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        try:
            Base.metadata.create_all(self.engine)
            logger.info('Database tables created successfully.')
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")

    def set_relationships(self):
        try:
            with self.Session() as session:
                relationship_config = ConfigureRelationships()
                relationship_config.configure_relationships(session)
                logger.info('Relationships set successfully.')
        except Exception as e:
            logger.error(f"Error setting relationships: {e}")

    def create_fts_table(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS book_fts USING fts5(title, authors);
                '''))
                logger.info('FTS table created successfully.')
        except Exception as e:
            logger.error(f"Error creating FTS table: {e}")
