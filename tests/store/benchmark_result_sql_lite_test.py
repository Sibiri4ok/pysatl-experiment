from pathlib import Path

import numpy as np
import pytest

from stattest.persistence.sql_lite_store import BenchmarkResultSqLiteStore


store_name = "pysatl.sqlite"


class TestBenchmarkResultSqLiteStoreService:
    @pytest.fixture
    def store(self):
        store = BenchmarkResultSqLiteStore(name=store_name)
        store.init()
        return store

    def teardown_method(self, method):
        try:
            Path(store_name).unlink()
            Path(store_name + "-journal").unlink()
        except OSError:
            pass

    def test_get_benchmarks_empty(self, store):
        assert len(store.get_benchmarks(0, 5)) == 0

    def test_get_benchmark_empty(self, store):
        assert len(store.get_benchmark("test", 10)) == 0

    def test_get_benchmark_value(self, store):
        store.insert_benchmark("test", 10, [0.5, 0.7])
        ar = np.array(store.get_benchmark("test", 10))
        expected = np.array([0.5, 0.7])
        assert np.array_equal(ar, expected)

    def test_get_benchmarks_value(self, store):
        store.insert_benchmark("test", 10, [0.5, 0.7])
        ar = store.get_benchmarks(0, 5)
        expected = np.array([0.5, 0.7])
        assert np.array_equal(ar[0].benchmark, expected)
        assert ar[0].test_code == "test"
