import pynotify

class Notificator:
    class __impl:
	__urgency = pynotify.URGENCY_LOW

        def set_status_icon(self, status_icon):
            self.__status_icon = status_icon

        def show_notification(self, title, msg, timeout=6000, icon=None):
            notification = pynotify.Notification(title, msg, icon)
            notification.set_urgency(self.__urgency)
            notification.set_timeout(timeout)
            if self.__status_icon:
                notification.set_property("status-icon", self.__status_icon)
            notification.show()

    __instance = None

    def __init__(self):
        if Notificator.__instance is None:
            Notificator.__instance = Notificator.__impl()

        self.__dict__['_Notificator__instance'] = Notificator.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
