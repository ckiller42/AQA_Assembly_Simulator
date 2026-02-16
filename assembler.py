from components import ALU, memory, register


class Assembler:
    # Use 2's complement for all numbers
    def __init__(self, file):
        self.msg = []
        self.file = file
        self.read_instructions()
        self.__format1 = ['LDR', 'STR', 'MOV', 'MVN']
        self.__format2 = ['ADD', 'SUB', 'AND', 'ORR', 'EOR', 'LSR', 'LSL']
        self.__format3 = ['B']
        self.__format4 = ['CMP']
        self.index = 0
        self._preCmpEq = -1  # -1: Undefined; 0: ne; 1: eq
        self._preCmpGt = -1  # -1: Undefined; 0: lt; 1: gt
        self.mode = 0  # 0: immediate; 1: reg

    def read_instructions(self):
        try:
            with open(self.file, 'r') as f:
                self.msg = (f.readlines())
                for i in range(len(self.msg)):
                    self.msg[i] = self.msg[i].replace('\n', '')
        except:
            raise FileNotFoundError
        if len(self.msg) == 0:
            raise Exception("No Instruction Exists")

    def checkOperandMemory(self, data:str):
        if data[-1] == 'h':
            data = data.removesuffix('h')
        elif data[-1] == 'b':
            data = data.removesuffix('b')
        for c in data:
            if c > '9' or c < '0':
                return False
        return True

    def checkOperandImmediate(self, data:str):
        if data[0] != '#':
            return False
        data = data.removeprefix('#')
        if data[-1] == 'b':
            data = data.removesuffix('b')
        elif data[-1] == 'h':
            data = data.removesuffix('h')
        for c in data:
            if c > '9' or c < '0':
                return False
        return True

    def checkOperandReg(self, data:str):
        if data[0] != 'R':
            return False
        data = data.removeprefix('R')
        if len(data) > 2 or len(data) < 1 or data[0] < '0' or data[0] > '9':
            return False
        elif len(data) == 2 and (data[1] < '0' or data[1] > '9'):
            return False
        return True

    def decodeOperand(self, data:str):
        if data[0] == 'R':
            data.removeprefix('R')
            self.mode = 1
        else:
            self.mode = 0
        if data[0] == '#':
            data.removeprefix('#')
        if data[-1] == 'b':
            data = data.removesuffix('b')
            return int(data, 2)
        elif data[-1] == 'h':
            data = data.removesuffix('h')
            return int(data, 16)
        return int(data)

    def assemble(self):
        # Note: Check Validity of User-Input Operand
        now = self.msg[self.index].split(' ')
        opcode = now[0]
        if opcode in self.__format1:
            reg_to = now[1]
            operand = now[2]
            if opcode == 'LDR':
                if not self.checkOperandMemory(operand):
                    return "Wrong Operand Format"
                register.set_register(int(reg_to), memory.get_memory(self.decodeOperand(operand)))
            elif opcode == 'STR':
                if not self.checkOperandMemory(operand):
                    return "Wrong Operand Format"
                memory.set_memory(self.decodeOperand(operand), register.get_register(int(reg_to)))
            elif opcode == 'MOV':
                if not self.checkOperandImmediate(operand) and not self.checkOperandReg(operand):
                    return "Wrong Operand Format"
                now = self.decodeOperand(operand)
                if self.mode:
                    now = register.get_register(now)
                register.set_register(int(reg_to), now)
            elif opcode == 'MVN':
                if not self.checkOperandImmediate(operand) and not self.checkOperandReg(operand):
                    return "Wrong Operand Format"
                now = self.decodeOperand(operand)
                if self.mode:
                    now = register.get_register(now)
                register.set_register(int(reg_to), (1 << len(bin(now)[2:])) - 1 - now)
        elif opcode in self.__format2:
            res = 0
            reg_to = int(now[1])
            reg_from = int(now[2])
            operand = now[3]
            val = register.get_register(reg_from)
            if not self.checkOperandImmediate(operand) and not self.checkOperandReg(operand):
                return "Wrong Operand Format"
            now = self.decodeOperand(operand)
            if self.mode:
                now = register.get_register(now)
            if opcode == "ADD":
                res = ALU.add(now, val)
            elif opcode == 'SUB':
                res = ALU.sub(val, now)
            elif opcode == 'AND':
                res = ALU.Not(ALU.nand(val, now))
            elif opcode == 'ORR':
                res = ALU.orr(val, now)
            elif opcode == 'EOR':
                res = ALU.xor(val, now)
            elif opcode == 'LSR':
                res = ALU.lsr(val, now)
            elif opcode == 'LSL':
                res = ALU.lsr(val, now)
            register.set_register(reg_to, res)
        elif opcode == 'CMP':
            reg_from = int(now[1])
            operand = now[3]
            val = register.get_register(reg_from)
            if not self.checkOperandImmediate(operand) and not self.checkOperandReg(operand):
                return "Wrong Operand Format"
            now = self.decodeOperand(operand)
            self._preCmpEq = ALU.isEqual(val, now)
            if self._preCmpEq:
                self._preCmpGt = -1
            else:
                self._preCmpGt = ALU.isGreat(val, now)
        elif opcode == 'B':
            pass


def main():
    ass = Assembler('./records.txt')
    ass.assemble()


if __name__ == '__main__':
    main()
