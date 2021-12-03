from abc import ABCMeta, abstractmethod
from typing import BinaryIO, Dict, Any

from baseservice.iodevices.common import Message
from baseservice.utils import KwargsException


class OutputDeviceException(KwargsException):
    """
    a base exception class for all output device related exceptions
    """
    pass


class OutputDevice(metaclass=ABCMeta):
    """
    base class for all output devices
    """

    def __init__(self, manager: 'OutputDeviceManager', name: str):
        """

        :param manager: the output device manager that created this device
        :param name: the name of this device
        """
        self._manager = manager
        self._name = name

    @abstractmethod
    def send_stream(self, message: Message):
        """
        sends a message to the device. this should be implemented by child classes

        :param message: the message to send
        """
        pass


class OutputDeviceManager(metaclass=ABCMeta):
    """
    this is a base class for output device managers. it is used to create output devices
    """
    @abstractmethod
    def get_output_device(self, name: str) -> OutputDevice:
        """
        creates an output device. this should be implemented by child classes

        :param name: the name of the output device to create
        :return: the created output device
        """
        pass
