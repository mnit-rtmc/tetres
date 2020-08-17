from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, VARCHAR
from sqlalchemy import create_engine

if __name__ == '__main__':
    engine = create_engine('postgresql://postgres@localhost:5432/tetres')
    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    try:
        status = Column("status", VARCHAR(255), nullable=True)
        op.add_column("route_wise_moe_parameters", status)
        print("Successfully added status column!")
    except Exception as e:
        print("Failed adding status column! Error: {}".format(e))
