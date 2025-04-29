# bluetooth_agent.py

from dbus_next.service import ServiceInterface, method
from dbus_next import Variant


class SimpleAutoAcceptAgent(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.Agent1")

    @method()
    def RequestAuthorization(self, device: "s"):
        print(f"RequestAuthorization for {device}")
        return

    @method()
    def RequestPinCode(self, device: "s"):
        print(f"RequestPinCode for {device}")
        return "0000"

    @method()
    def RequestPasskey(self, device: "s"):
        print(f"RequestPasskey for {device}")
        return Variant("u", 123456)

    @method()
    def RequestConfirmation(self, device: "s", passkey: "u"):
        print(f"RequestConfirmation {device} {passkey}")
        return

    @method()
    def AuthorizeService(self, device: "s", uuid: "s"):
        print(f"AuthorizeService {device} {uuid}")
        return

    @method()
    def Cancel(self):
        print("Agent Cancelled")
