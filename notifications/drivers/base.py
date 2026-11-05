from abc import ABC, abstractmethod

class BaseNotificationDriver(ABC):

    @abstractmethod
    def send_notification(
        self,
        recipient: str,
        ticket_title: str,
        ticket_id: str,
        new_status: str,
    ) -> bool:
        """Send or simulate a notification."""
        raise NotImplementedError
