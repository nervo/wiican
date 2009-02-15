import pynotify


class Notificator:
    __urgency = pynotify.URGENCY_LOW
    __status_icon = None

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

