import sqlite3
from typing import ClassVar

import numpy as np
from sqlalchemy import Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, scoped_session, sessionmaker
from typing_extensions import override

from stattest.persistence import IRvsStore
from stattest.persistence.sql_lite_store.base import ModelBase, SessionType
from stattest.persistence.sql_lite_store.db_init import get_request_or_thread_id, init_db


class RVS(ModelBase):
    """
    RVS data database model.

    """

    __tablename__ = "rvs_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # type: ignore
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # type: ignore
    size: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # type: ignore
    data: Mapped[str] = mapped_column(String(), nullable=False)  # type: ignore


class RVSStat(ModelBase):
    """
    RVS stat data database model.

    """

    __tablename__ = "rvs_stat"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)  # type: ignore
    size: Mapped[int] = mapped_column(Integer, primary_key=True)  # type: ignore
    count: Mapped[int] = mapped_column(Integer)  # type: ignore


class RvsSqLiteStore(IRvsStore):
    session: ClassVar[SessionType]
    __separator = ";"

    def __init__(self, name="pysatl.sqlite"):
        super().__init__()
        self.name = name

    @override
    def init(self):
        sqlite3.register_adapter(np.int64, lambda val: int(val))
        engine = init_db("sqlite:///" + self.name)
        RvsSqLiteStore.session = scoped_session(
            sessionmaker(bind=engine, autoflush=False),
            scopefunc=get_request_or_thread_id,
        )
        ModelBase.metadata.create_all(engine)

    @override
    def insert_all_rvs(self, generator_code: str, size: int, data: [[float]]):
        if len(data) == 0:
            return

        data_to_insert = [
            {
                "code": generator_code,
                "size": int(size),
                "data": RvsSqLiteStore.__separator.join(map(str, d)),
            }
            for d in data
        ]
        statement = text("INSERT INTO rvs_data (code, size, data) VALUES (:code, :size, :data)")
        RvsSqLiteStore.session.execute(statement, data_to_insert)
        RvsSqLiteStore.session.commit()

    @override
    def insert_rvs(self, code: str, size: int, data: [float]):
        data_str = RvsSqLiteStore.__separator.join(map(str, data))
        RvsSqLiteStore.session.add(RVS(code=code, size=int(size), data=data_str))
        RvsSqLiteStore.session.commit()

    @override
    def get_rvs_count(self, code: str, size: int):
        data = self.get_rvs(code, size)
        return len(data)

    @override
    def get_rvs(self, code: str, size: int) -> [[float]]:
        samples = (
            RvsSqLiteStore.session.query(RVS)
            .filter(
                RVS.code == code,
                RVS.size == size,
            )
            .all()
        )

        if not samples:
            return []

        return [
            [float(x) for x in sample.data.split(RvsSqLiteStore.__separator)] for sample in samples
        ]

    @override
    def get_rvs_stat(self) -> [(str, int, int)]:
        result = (
            RvsSqLiteStore.session.query(RVS.code, RVS.size, func.count(RVS.code))
            .group_by(RVS.code, RVS.size)
            .all()
        )

        if result is None:
            return []

        return result

    @override
    def clear_all_rvs(self):
        RvsSqLiteStore.session.query(RVS).delete()
