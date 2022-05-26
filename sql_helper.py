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
    history = orm.relationship("BalanceSlice", back_populates="profile")

    def __repr__(self):
        return f"Profile(id={self.id!r}, balance={self.balance!r}, companies={', '.join(i.name for i in self.companies)})"


class Company(Base):
    __tablename__ = "companies"

    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"))
    name = sq.Column("name", sq.Text)
    worth = sq.Column("worth", sq.Numeric(14, 2))

    owner = orm.relationship("Profile", uselist=False, back_populates="companies")
    history = orm.relationship("WorthSlice", uselist=False, back_populates="company")

    def __repr__(self):
        return f"Company(id={self.id!r}, name={self.name!r}, worth={self.worth!r})"


class BalanceSlice(Base):
    __tablename__ = "balancehistory"

    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"), nullable=False)
    balance = sq.Column("balance", sq.Numeric(14, 2), nullable=False)
    time = sq.Column("time", sq.DateTime, nullable=False)
    tag = sq.Column("tag", sq.Text)

    profile = orm.relationship("Profile", uselist=False, back_populates="history")

    def __repr__(self):
        return f"BalanceSlice(id={self.id!r}, profile_id={self.profile_id!r}, balance={self.balance!r}, time={self.time!r}, tag={self.tag!r})"


class WorthSlice(Base):
    __tablename__ = "worthhistory"

    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    company_id = sq.Column("company_id", sq.Integer, sq.ForeignKey("companies.id"), nullable=False)
    worth = sq.Column("worth", sq.Numeric(14, 2), nullable=False)
    time = sq.Column("time", sq.DateTime, nullable=False)
    tag = sq.Column("tag", sq.Text)

    company = orm.relationship("Company", uselist=False, back_populates="history")

    def __repr__(self):
        return f"WorthSlice(id={self.id!r}, company_id={self.company_id!r}, worth={self.worth!r}, time={self.time!r}, tag={self.tag!r})"

mapper_registry.metadata.create_all(engine)

if __name__ == "__main__":
    with Session() as session:
        result: sq.engine.Result = session.execute(sq.select(Profile))
        for row in result:
            print(row[0])
