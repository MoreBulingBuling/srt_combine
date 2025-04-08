import struct
from dataclasses import dataclass, field


@dataclass
class BaseUPIU:
    data: bytearray = field(default_factory=lambda: bytearray(32))

    def __init__(self):
        # 直接在 __dict__ 中初始化 _updating_data
        self.__dict__['_updating_data'] = False

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
        if name not in self.__dataclass_fields__:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        if not self.__dict__.get('_updating_data', False):
            self.__dict__['_updating_data'] = True
            super().__setattr__(name, value)
            if name != 'data':
                self._update_data()
            self.__dict__['_updating_data'] = False
        else:
            super().__setattr__(name, value)

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


# SCSI WRITE 10 命令
@dataclass
class Write10UPIU(CommandUPIU):
    opcode: int = 0x2A
    command_type: int = 0
    dme: int = 0
    cdb_length: int = 10
    transfer_direction: int = 1  # 写操作，数据从主机到设备
    dpb: int = 0
    logical_block_address: int = 0
    data_transfer_length: int = 0

    def __post_init__(self):
        self._update_cdb()
        super().__post_init__()

    def _update_cdb(self):
        cdb = bytearray(16)
        cdb[0] = self.opcode
        cdb[2:6] = struct.pack('>I', self.logical_block_address)
        cdb[7:9] = struct.pack('>H', self.data_transfer_length // 512)  # 以 512 字节块为单位
        self.cdb = bytes(cdb)

    def _update_data(self):
        self._update_cdb()
        super()._update_data()


# SCSI READ 10 命令
@dataclass
class Read10UPIU(CommandUPIU):
    opcode: int = 0x28
    command_type: int = 0
    dme: int = 0
    cdb_length: int = 10
    transfer_direction: int = 0  # 读操作，数据从设备到主机
    dpb: int = 0
    logical_block_address: int = 0
    data_transfer_length: int = 0

    def __post_init__(self):
        self._update_cdb()
        super().__post_init__()

    def _update_cdb(self):
        cdb = bytearray(16)
        cdb[0] = self.opcode
        cdb[2:6] = struct.pack('>I', self.logical_block_address)
        cdb[7:9] = struct.pack('>H', self.data_transfer_length // 512)  # 以 512 字节块为单位
        self.cdb = bytes(cdb)

    def _update_data(self):
        self._update_cdb()
        super()._update_data()


# SCSI TEST UNIT READY 命令
@dataclass
class TestUnitReadyUPIU(CommandUPIU):
    opcode: int = 0x00
    command_type: int = 0
    dme: int = 0
    cdb_length: int = 6
    transfer_direction: int = 0  # 无数据传输
    dpb: int = 0

    def __post_init__(self):
        self._update_cdb()
        super().__post_init__()

    def _update_cdb(self):
        cdb = bytearray(16)
        cdb[0] = self.opcode
        cdb[1] = self.lun
        self.cdb = bytes(cdb)

    def _update_data(self):
        self._update_cdb()
        super()._update_data()


# 使用案例
if __name__ == "__main__":
    # 创建 WRITE 10 UPIU 实例
    write10_upiu = Write10UPIU(cid=0x1234, lun=0x00, logical_block_address=0x00000100, data_transfer_length=5120)

    print("WRITE 10 UPIU:")
    print(write10_upiu.to_bytes())

    # 修改属性值
    write10_upiu.logical_block_address = 0x00000200
    print("\n修改 logical_block_address 后 WRITE 10 UPIU 的 data:")
    print(write10_upiu.to_bytes())

    # 创建 READ 10 UPIU 实例
    read10_upiu = Read10UPIU(cid=0x5678, lun=0x00, logical_block_address=0x00000200, data_transfer_length=2048)
    print("\nREAD 10 UPIU:")
    print(read10_upiu.to_bytes())

    # 创建 TEST UNIT READY UPIU 实例
    test_unit_ready_upiu = TestUnitReadyUPIU(cid=0x9ABC, lun=0x00)
    print("\nTEST UNIT READY UPIU:")
    print(test_unit_ready_upiu.to_bytes())

    