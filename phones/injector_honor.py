import time
from injector import Injector


class InjectorHonor(Injector):
    def __init__(self, devices, app, strategy_list, emulator_path, android_system, root_path, resource_path,
                 testcase_count, event_num, timeout, setting_random_denominator, rest_interval, choice):
        super(InjectorHonor, self).__init__(devices, app, strategy_list, emulator_path, android_system, root_path, resource_path,
                 testcase_count, event_num, timeout, setting_random_denominator, rest_interval, choice)

    def change_setting_before_run(self, event_count, strategy):
        super(InjectorHonor, self).change_setting_before_run(event_count, strategy)

    def inject_setting_during_run(self, event_count, strategy, request_flag):
        super(InjectorHonor, self).inject_setting_during_run(event_count, strategy, request_flag)

    def change_setting_after_run(self, event_count, strategy):
        super(InjectorHonor, self).change_setting_after_run(event_count, strategy)

    def replay_setting(self, event, strategy_list):
        super(InjectorHonor, self).replay_setting(event, strategy_list)

    def clear_and_start_setting(self, device0, device1):
        super(InjectorHonor, self).clear_and_start_setting(device0, device1)

    def network_immediate_1(self):
        super(InjectorHonor, self).network_immediate_1()

    def network_lazy_1(self):
        super(InjectorHonor, self).network_lazy_1()

    def network_lazy_2(self):
        super(InjectorHonor, self).network_lazy_2()

    def location_lazy_1(self):
        super(InjectorHonor, self).location_lazy_1()

    def location_lazy_2(self):
        super(InjectorHonor, self).location_lazy_2()

    def display_immediate_2(self):
        super(InjectorHonor, self).display_immediate_2()

    def display_immediate_1(self):
        super(InjectorHonor, self).display_immediate_1()

    def developer_lazy_1(self):
        raise NotImplementedError

    def sound_lazy_1(self):
        raise NotImplementedError

    def battery_lazy_1(self):
        raise NotImplementedError

    def permission_lazy_1(self):
        print("Start change permission")
        self.devices[0].adb_permission(self.app.package_name, "OFF")
        self.devices[1].adb_permission(self.app.package_name, "ON")
        print("End change permission")

    def language(self):
        raise NotImplementedError

    def time(self):
        raise NotImplementedError

    def init_setting(self):
        for device in self.devices:
            device.adb_setting("open_gps")
            # close airplane
            device.adb_setting("network_lazy_1_1")
            # open wifi
            device.adb_setting("network_lazy_2_2")
            time.sleep(self.rest_interval*1)
            device.use.press("home")

    def dy_init(self):
        for device in self.devices:
            device.use(resourceId="com.ss.android.ugc.aweme:id/duq").click(timeout=3.0)
            time.sleep(self.rest_interval)
            device.use(resourceId="com.ss.android.ugc.aweme:id/et_search_kw").set_text("123")
            device.use(text="搜索").click(timeout=3.0)




