from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, Float, UnicodeText
from sqlalchemy import create_engine

if __name__ == '__main__':
    engine = create_engine('postgresql://postgres@localhost:5432/tetres')
    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)
    print("Adding column vht...")
    for i in range(2010, 2020):
        try:
            vht = Column("vht", Float, nullable=True)
            op.add_column("tt_{}".format(i), vht)
            print("Successfully added vht column!")
        except Exception as e:
            print("Failed adding vht column! Error: {}".format(e))
        try:
            dvh = Column("dvh", Float, nullable=True)
            op.add_column("tt_{}".format(i), dvh)
            print("Successfully added dvh column!")
        except Exception as e:
            print("Failed adding dvh column! Error: {}".format(e))
        try:
            lvmt = Column("lvmt", Float, nullable=True)
            op.add_column("tt_{}".format(i), lvmt)
            print("Successfully added lvmt column!")
        except Exception as e:
            print("Failed adding lvmt column! Error: {}".format(e))
        try:
            uvmt = Column("uvmt", Float, nullable=True)
            op.add_column("tt_{}".format(i), uvmt)
            print("Successfully added uvmt column!")
        except Exception as e:
            print("Failed adding uvmt column! Error: {}".format(e))
        try:
            cm = Column("cm", Float, nullable=True)
            op.add_column("tt_{}".format(i), cm)
            print("Successfully added cm column!")
        except Exception as e:
            print("Failed adding cm column! Error: {}".format(e))
        try:
            cmh = Column("cmh", Float, nullable=True)
            op.add_column("tt_{}".format(i), cmh)
            print("Successfully added cmh column!")
        except Exception as e:
            print("Failed adding cmh column! Error: {}".format(e))
        try:
            acceleration = Column("acceleration", Float, nullable=True)
            op.add_column("tt_{}".format(i), acceleration)
            print("Successfully added acceleration column!")
        except Exception as e:
            print("Failed adding acceleration column! Error: {}".format(e))
        try:
            meta_data = Column("meta_data", UnicodeText, nullable=True)
            op.add_column("tt_{}".format(i), meta_data)
            print("Successfully added meta_data column!")
        except Exception as e:
            print("Failed adding meta_data column! Error: {}".format(e))
