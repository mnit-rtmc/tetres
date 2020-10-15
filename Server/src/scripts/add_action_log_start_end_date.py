from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, Float, UnicodeText, DateTime
from sqlalchemy import create_engine

if __name__ == '__main__':
    engine = create_engine('postgresql://postgres@localhost:5432/tetres')
    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    print("Adding column processed_start_date...")
    try:
        processed_start_date = Column("processed_start_date", DateTime, nullable=True)
        op.add_column("action_log", processed_start_date)
        print("Successfully added processed_start_date column!")
    except Exception as e:
        print("Failed adding processed_start_date column! Error: {}".format(e))
    print("Adding column processed_end_date...")
    try:
        processed_end_date = Column("processed_end_date", DateTime, nullable=True)
        op.add_column("action_log", processed_end_date)
        print("Successfully added processed_end_date column!")
    except Exception as e:
        print("Failed adding processed_end_date column! Error: {}".format(e))
