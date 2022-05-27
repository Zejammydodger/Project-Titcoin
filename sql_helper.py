import sqlalchemy as sq
import sqlalchemy.orm as orm
from decimal import Decimal
import datetime
import time

with open("secrets/password.txt", mode="r") as file:
    password = file.readline()
engine = sq.create_engine(f"mysql+mysqlconnector://root:{password}@localhost/TitCoin", echo=False, future=True)
del password

mapper_registry = orm.registry()
Base = mapper_registry.generate_base()


# helper functions
def get_session():
    return orm.sessionmaker(bind=engine, autocommit=True).begin()


def format_time(_datetime: datetime.datetime):
    return _datetime.strftime("%Y-%m-%d %H:%M:%S")


def get_time():
    return format_time(datetime.datetime.utcfromtimestamp(time.time()))


# mapping of user profiles
class Profile(Base):
    __tablename__ = "profiles"

    # columns
    id = sq.Column("id", sq.BigInteger, primary_key=True, nullable=False)
    _balance = sq.Column("balance", sq.Numeric(14, 2))

    # relationships
    companies = orm.relationship("Company", back_populates="owner")
    history = orm.relationship("BalanceSlice", back_populates="profile")
    share_entries = orm.relationship("ShareEntry", back_populates="profile")

    def __init__(self, id: int, balance: Decimal):
        super().__init__()
        self.id = id
        self._balance = balance

    # changes the balance of a user (it supports negative numbers btw)
    def change_balance(self, amount: Decimal, time: datetime.datetime = None, tag: str = None):
        # sets the balance
        self._balance += amount

        # adds a log into the history
        session: orm.Session = orm.Session.object_session(self)
        session.add(BalanceSlice(self, self._balance, time, tag))
        session.flush()

    @property
    def worth(self):
        return self.balance + sum([share_entry.worth for share_entry in self.share_entries])

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, b: Decimal):
        assert b >= 0

        # sets the balance
        self._balance = b

        # adds a log into the history
        session: orm.Session = orm.Session.object_session(self)
        session.add(BalanceSlice(self, self._balance, datetime.datetime.utcfromtimestamp(time.time()), "override"))
        session.flush()

    def __repr__(self):
        return f"Profile(id={self.id!r}, balance={self._balance!r}, companies={', '.join(i.name for i in self.companies)})"


# mapping of companies
class Company(Base):
    __tablename__ = "companies"

    # columns
    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    _profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"))
    name = sq.Column("name", sq.Text)
    worth = sq.Column("worth", sq.Numeric(14, 2))

    # relationships
    owner = orm.relationship("Profile", uselist=False, back_populates="companies")
    history = orm.relationship("WorthSlice", uselist=False, back_populates="company")
    share_entries = orm.relationship("ShareEntry", back_populates="company")

    def __init__(self, owner: Profile, name: str, worth: Decimal):
        super().__init__()
        self._profile_id = owner.id
        self.name = name
        self.worth = worth

    @property
    def num_shares(self) -> int:
        return sum([share_entry.num_shares for share_entry in self.share_entries])

    @property
    def share_value(self):
        return self.worth / self.num_shares

    def __repr__(self):
        return f"Company(id={self.id!r}, name={self.name!r}, worth={self.worth!r})"


# mapping of profile balance history entry
class BalanceSlice(Base):
    __tablename__ = "balancehistory"

    # columns
    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    _profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"), nullable=False)
    balance = sq.Column("balance", sq.Numeric(14, 2), nullable=False)
    time = sq.Column("time", sq.DateTime, nullable=False)
    tag = sq.Column("tag", sq.Text)

    # relationships
    profile = orm.relationship("Profile", uselist=False, back_populates="history")

    def __init__(self, profile: Profile, balance: Decimal, time: datetime.datetime = None, tag: str = None):
        super().__init__()
        self._profile_id = profile.id
        self.balance = balance
        self.time = format_time(time) if time else get_time()
        self.tag = tag

    def __repr__(self):
        return f"BalanceSlice(id={self.id!r}, profile_id={self._profile_id!r}, balance={self.balance!r}, time={self.time!r}, tag={self.tag!r})"


# mapping of company worth history entry
class WorthSlice(Base):
    __tablename__ = "worthhistory"

    # columns
    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    _company_id = sq.Column("company_id", sq.Integer, sq.ForeignKey("companies.id"), nullable=False)
    worth = sq.Column("worth", sq.Numeric(14, 2), nullable=False)
    time = sq.Column("time", sq.DateTime, nullable=False)
    tag = sq.Column("tag", sq.Text)

    # relationships
    company = orm.relationship("Company", uselist=False, back_populates="history")

    def __init__(self, company: Company, worth: Decimal, time: datetime.datetime = None, tag: str = None):
        super().__init__()
        self._company_id = company.id
        self.worth = worth
        self.time = format_time(time) if time else get_time()
        self.tag = tag

    def __repr__(self):
        return f"WorthSlice(id={self.id!r}, company_id={self._company_id!r}, worth={self.worth!r}, time={self.time!r}, tag={self.tag!r})"


# mapping of share ownership entry
class ShareEntry(Base):
    __tablename__ = "shares"

    # columns
    id = sq.Column("id", sq.Integer, primary_key=True, nullable=False, autoincrement=True)
    _profile_id = sq.Column("profile_id", sq.BigInteger, sq.ForeignKey("profiles.id"), nullable=False)
    _company_id = sq.Column("company_id", sq.Integer, sq.ForeignKey("companies.id"), nullable=False)
    num_shares = sq.Column("num_shares", sq.BigInteger, nullable=False)

    # relationships
    profile = orm.relationship("Profile", uselist=False, back_populates="share_entries")
    company = orm.relationship("Company", uselist=False, back_populates="share_entries")

    def __init__(self, profile: Profile, company: Company, num_shares: int):
        super().__init__()
        self._profile_id = profile.id
        self._company_id = company.id
        self.num_shares = num_shares

    @property
    def worth(self):
        return self.num_shares * self.company.share_value

    def __repr__(self):
        return f"ShareEntry(id={self.id!r}, profile_id={self._profile_id!r}, company_id={self._company_id!r}, num_shares={self.num_shares!r})"


# builds all the mapped classes
mapper_registry.metadata.create_all(engine)


if __name__ == "__main__":
    with get_session() as session:
        result: sq.engine.Result = session.execute(sq.select(Profile))
        for row in result:
            row: tuple[Profile]
            row[0].change_balance(-50, tag="debug")
            print(row[0])
