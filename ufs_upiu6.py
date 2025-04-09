from dataclasses import dataclass, field


class CDBProxy(bytearray):
    def __new__(cls, data):
        instance = super().__new__(cls, [0] * 16)
        instance.data = data
        return instance

    def __getitem__(self, index):
        return self.data[16 + index]

    def __setitem__(self, index, value):
        self.data[16 + index] = value


@dataclass
class CommandUPIU:
    data: bytearray = field(default_factory=lambda: bytearray([0] * 32), repr=False)
    Lun: int
    flags: int = 0
    task_tag: int = 0
    
    def __init__(self, Lun, flags=0, task_tag=0):
        self.data = bytearray([0] * 32)
        self.data[0] = 0x01
        self.data[1] = Lun
        self.data[2] = flags
        self.data[3] = task_tag

    @property
    def upiu_type(self):
        return self.data[0]

    @upiu_type.setter
    def upiu_type(self, value):
        self.data[0] = value

    @property
    def Lun(self):
        return self.data[1]

    @Lun.setter
    def Lun(self, value):
        self.data[1] = value

    @property
    def flags(self):
        return self.data[2]

    @flags.setter
    def flags(self, value):
        self.data[2] = value

    @property
    def task_tag(self):
        return self.data[3]

    @task_tag.setter
    def task_tag(self, value):
        self.data[3] = value

    @property
    def cdb(self):
        return CDBProxy(self.data)

    @cdb.setter
    def cdb(self, value):
        if isinstance(value, (bytes, bytearray)):
            if len(value) == 16:
                self.data[16:32] = value
            else:
                raise ValueError("CDB value must be 16 bytes long.")
        else:
            raise TypeError("CDB value must be of type bytes or bytearray.")

    def to_bytearray(self):
        return self.data.copy()

    @classmethod
    def from_bytes(cls, data):
        data = bytearray(data)
        Lun = data[1]
        flags = data[2]
        task_tag = data[3]
        obj = cls(Lun=Lun, flags=flags, task_tag=task_tag)
        obj.data = data
        return obj

    # def __str__(self):
    #     return f"CommandUPIU: {self.to_bytearray().hex()}"


@dataclass
class Write10UPIU(CommandUPIU):
    logical_block_address: int
    transfer_length: int
    dpo: int = 0

    def __init__(self, Lun, logical_block_address, transfer_length, task_tag=0, dpo=0):
        super().__init__(Lun=Lun, task_tag=task_tag)
        opcode = 0x2A
        self.data[8] = opcode
        self.data[9:13] = logical_block_address.to_bytes(4, byteorder='big')
        self.data[14:16] = transfer_length.to_bytes(2, byteorder='big')
        self.data[16+1] = dpo

    @property
    def logical_block_address(self):
        return int.from_bytes(self.data[9:13], byteorder='big')

    @logical_block_address.setter
    def logical_block_address(self, value):
        self.data[9:13] = value.to_bytes(4, byteorder='big')

    @property
    def transfer_length(self):
        return int.from_bytes(self.data[14:16], byteorder='big')

    @transfer_length.setter
    def transfer_length(self, value):
        self.data[14:16] = value.to_bytes(2, byteorder='big')

    @property
    def dpo(self):
        return self.data[16+1]

    @dpo.setter
    def dpo(self, value):
        self.data[16+1] = value

    @classmethod
    def from_bytes(cls, data):
        data = bytearray(data)
        logical_block_address = int.from_bytes(data[9:13], byteorder='big')
        transfer_length = int.from_bytes(data[14:16], byteorder='big')
        Lun = data[1]
        task_tag = data[3]
        dpo = data[16]
        obj = cls(logical_block_address=logical_block_address, transfer_length=transfer_length,
                  Lun=Lun, task_tag=task_tag, dpo=dpo)
        obj.data = data
        return obj


if __name__ == "__main__":
    # 省略 flags 参数
    cmd = CommandUPIU(Lun=3)
    print(cmd)

    write_upiu = Write10UPIU(logical_block_address=0x12345678, transfer_length=0x0010,
                             Lun=1, task_tag=3, dpo=4)
    print("初始 Write10UPIU:", write_upiu)

    print(write_upiu.logical_block_address)
    print(write_upiu.Lun)

    print(list(write_upiu.cdb))
    # 修改 cdb
    write_upiu.cdb[0] = 0xFF
    print("修改 CDB 后的 Write10UPIU:", write_upiu)
    print(list(write_upiu.cdb))

    # 修改 Lun
    write_upiu.Lun = 4
    print("修改 Lun 后的 Write10UPIU:", write_upiu)

    # 修改 dpo
    write_upiu.dpo = 5
    print("修改 DPO 后的 Write10UPIU:", write_upiu)

    write_upiu.flags = 33
    upiu_bytearray = write_upiu.to_bytearray()
    new_upiu = Write10UPIU.from_bytes(upiu_bytearray)
    print("从字节数组恢复的 Write10UPIU:", new_upiu)

    print(list(write_upiu.cdb))
    