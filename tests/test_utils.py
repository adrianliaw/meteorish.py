from ddpserver import utils
from nose.tools import assert_equal, assert_not_equal


def test_gen_id():
    assert_not_equal(utils.gen_id(), utils.gen_id())
    assert_equal(len(utils.gen_id()), 17)
    assert_equal(len(utils.gen_id(10)), 10)
