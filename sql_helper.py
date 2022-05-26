import sqlalchemy as sq
import sqlalchemy.orm as orm

with open("secrets/password.txt", mode="r") as file:
    password = file.readline()
engine = sq.create_engine(f"mysql+mysqlconnector://root:{password}@localhost/TitCoin", echo=False, future=True)

"""
with engine.connect() as conn:
    result = conn.execute(text("select * from Profiles"))
    print(result.all())
"""

#with Session(engine) as session:
#    result = session.execute(text("select * from Profiles"))
#    print(result.all())

mapper_registry = orm.registry()
Base = mapper_registry.generate_base()
Session = orm.sessionmaker(bind=engine)


class Profile(Base):
    __tablename__ = "profiles"

    id = sq.Column("id", sq.BigInteger, primary_key=True, nullable=False)
    balance = sq.Column("balance", sq.Numeric(14, 2))

    companies = orm.relationship("Company", back_populates="owner")
    history = orm.relationship("BalanceSlice")

    def __repr__(self):
        return f"Profile(id={self.id!r}, balance={self.balance!r}, companies={', '.join(i.name for i in self.companies)})"


class Company(Base):
    __tablename__ = "companies"

    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"))
    name = sq.Column("name", sq.TEXT)
    worth = sq.Column("worth", sq.Numeric(14, 2))

    owner = orm.relationship("Profile", uselist=False, back_populates="companies")

    def __repr__(self):
        return f"Company(id={self.id!r}, name={self.name!r}, worth={self.worth!r}, owner={self.owner.id!r})"


class BalanceSlice(Base):
    __tablename__ = "balancehistory"

    profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"))
    balance = sq.Column("balance", sq.Numeric(14, 2))
    tag = sq.Column("tag", sq.TEXT)
    time = sq.Column("time", sq.DATETIME)

    def __repr__(self):
        return f"BalanceSlice(profile_id={self.profile_id!r}, balance={self.balance!r}, tag={self.tag!r}, time={self.time!r})"


mapper_registry.metadata.create_all(engine)

with Session() as session:
    result: sq.engine.Result = session.execute(sq.select(Profile))
    for row in result:
        print(row[0].companies[1].owner)