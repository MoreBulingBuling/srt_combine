import struct
from dataclasses import dataclass, field


@dataclass
class BaseUPIU:
    data: bytearray = field(default_factory=lambda: bytearray(32))

    def to_bytes(self):
        return bytes(self.data)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != 32:
            raise ValueError("UPIU data must be 32 bytes long.")
        return cls(bytearray(data))

    def to_dict(self):
        data_dict = {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
            if field.name != 'data'
        }
        return data_dict

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name != 'data':
            self._update_data()

    def _update_data(self):
        pass


@dataclass
class CommandUPIU(BaseUPIU):
    opcode: int = 0
    command_type: int = 0
    dme: int = 0
    cid: int = 0
    lun: int = 0
    cdb_length: int = 0
    transfer_direction: int = 0
    dpb: int = 0
    data_transfer_length: int = 0
    cdb: bytes = bytes(16)

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.command_type & 0x03) << 6)
        self.data[1] = (self.data[1] & 0xDF) | ((self.dme & 0x01) << 5)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun
        self.data[6] = (self.data[6] & 0x0F) | ((self.cdb_length & 0x0F) << 4)
        self.data[7] = (self.data[7] & 0x7F) | ((self.transfer_direction & 0x01) << 7)
        self.data[7] = (self.data[7] & 0xBF) | ((self.dpb & 0x01) << 6)
        self.data[8:12] = struct.pack('>I', self.data_transfer_length)
        self.data[16:32] = self.cdb


@dataclass
class ResponseUPIU(BaseUPIU):
    opcode: int = 0
    response_type: int = 0
    cid: int = 0
    lun: int = 0
    data_transfer_length: int = 0
    sense_data: bytes = bytes(16)

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.response_type & 0x03) << 6)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun
        self.data[8:12] = struct.pack('>I', self.data_transfer_length)
        self.data[16:32] = self.sense_data


@dataclass
class TaskManagementRequestUPIU(BaseUPIU):
    opcode: int = 0
    task_management_type: int = 0
    cid: int = 0
    lun: int = 0

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.task_management_type & 0x03) << 6)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun


@dataclass
class TaskManagementResponseUPIU(BaseUPIU):
    opcode: int = 0
    task_management_response_type: int = 0
    cid: int = 0
    lun: int = 0

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.task_management_response_type & 0x03) << 6)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun


@dataclass
class QueryRequestUPIU(BaseUPIU):
    opcode: int = 0
    query_type: int = 0
    cid: int = 0
    lun: int = 0
    query_parameter: bytes = bytes(16)

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.query_type & 0x03) << 6)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun
        self.data[16:32] = self.query_parameter


@dataclass
class QueryResponseUPIU(BaseUPIU):
    opcode: int = 0
    query_response_type: int = 0
    cid: int = 0
    lun: int = 0
    query_response_data: bytes = bytes(16)

    def __post_init__(self):
        self._update_data()

    def _update_data(self):
        self.data[0] = self.opcode
        self.data[1] = (self.data[1] & 0x3F) | ((self.query_response_type & 0x03) << 6)
        self.data[2:4] = struct.pack('>H', self.cid)
        self.data[4] = self.lun
        self.data[16:32] = self.query_response_data


@dataclass
class NopOutUPIU(BaseUPIU):
    pass


@dataclass
class NopInUPIU(BaseUPIU):
    pass


# 使用案例
if __name__ == "__main__":
    # 赋值并打印 CommandUPIU 实例
    cmd_upiu = CommandUPIU(
        opcode=0x12,
        command_type=0x01,
        cid=0x1234,
        lun=0x00,
        cdb_length=0x10,
        transfer_direction=0x01,
        data_transfer_length=0x1000,
        cdb=bytes([0] * 16)
    )
    print("CommandUPIU 实例:")
    print(cmd_upiu)

    # 修改属性值
    cmd_upiu.opcode = 0x13
    print("\n修改 opcode 后 CommandUPIU 的 data:")
    print(cmd_upiu.to_bytes())

    # 将 CommandUPIU 实例转化为字典
    cmd_upiu_dict = cmd_upiu.to_dict()
    print("\nCommandUPIU 转化为字典:")
    print(cmd_upiu_dict)

    