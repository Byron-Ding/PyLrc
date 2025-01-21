import datetime

import pytest
from NewestVersion.MyLyric.LyricTimeTab import LyricTimeTab


standard_init_time_tab: str = "[00:00.00]"

class Test_LyricTimeTab:

    """
    Test the normal LyricTimeTab class.

    测试正常的 LyricTimeTab 类。
    """
    def test_LyricTimeTab_propertyDecorated_property_normal(self):
        """
        Test the property decorated property of LyricTimeTab class.

        测试 LyricTimeTab 类的装饰属性。
        """
        standard_time_tab = LyricTimeTab(standard_init_time_tab, ("normal", None))

        print()

        print("LyricTimeTab.original_time_tab:", standard_time_tab.original_time_tab)
        print("LyricTimeTab.current_time_tab:", standard_time_tab.current_time_tab)
        assert standard_time_tab.original_time_tab == standard_time_tab._original_time_tab
        assert standard_time_tab.current_time_tab == standard_time_tab._current_time_tab

        print("LyricTimeTab.mode:", standard_time_tab.mode)
        print("LyricTimeTab.match_result:", standard_time_tab.match_result)
        assert standard_time_tab.mode == standard_time_tab._mode
        assert standard_time_tab.match_result == standard_time_tab._match_result

        print("LyricTimeTab.brackets:", standard_time_tab.brackets)
        print("LyricTimeTab.time_stamp:", standard_time_tab.time_stamp)
        print("LyricTimeTab.minutes_seconds_seperator:", standard_time_tab.minutes_seconds_seperator)
        print("LyricTimeTab.seconds_milliseconds_seperator:", standard_time_tab.seconds_milliseconds_seperator)
        assert standard_time_tab.brackets == standard_time_tab._brackets
        assert standard_time_tab.time_stamp == standard_time_tab._time_stamp
        assert standard_time_tab.minutes_seconds_seperator == standard_time_tab._minutes_seconds_seperator
        assert standard_time_tab.seconds_milliseconds_seperator == standard_time_tab._seconds_milliseconds_seperator



    def test_LyricTimeTab_calculation(self):
        """
        Test the calculation method of LyricTimeTab class.

        测试 LyricTimeTab 类的计算方法。
        """
        standard_time_tab = LyricTimeTab(standard_init_time_tab, ("normal", "None"))

        standard_time_tab += 1
        print()


        print(standard_time_tab.time_stamp)
        assert standard_time_tab.time_stamp == datetime.timedelta(seconds=1)


def test_LyricTimeTab_calculation():
    """
    Test the calculation method of LyricTimeTab class.

    测试 LyricTimeTab 类的计算方法。
    """
    standard_time_tab = LyricTimeTab(standard_init_time_tab, ("normal", "None"))

    standard_time_tab += 1
    print()


    print(standard_time_tab.time_stamp)
    assert standard_time_tab.time_stamp == datetime.timedelta(seconds=1)





if __name__ == '__main__':
    pytest.main(['-W', "warning", '-s', __file__])