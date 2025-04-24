import unittest


def run_tests():
    """모든 테스트 실행"""
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
