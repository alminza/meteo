# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 09:17:47 2020

@author: Malcor
"""

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///BDDlite.db', echo=False)

Session = sessionmaker(bind=engine)
Base = declarative_base()


class InfoMeteoLite(Base):
    __tablename__ = 'info_meteolite'
    Date = Column(String, primary_key=True)
    Time = Column(String)


def main() -> None:
    Base.metadata.create_all(engine)
    session = Session()
    try:
        results = session.query(InfoMeteoLite).order_by(InfoMeteoLite.Date).all()
        print([(row.Date, row.Time) for row in results])
    finally:
        session.close()


if __name__ == "__main__":
    main()


