#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "ALU.c"
#include "memory.c"
#include "register.c"
// EXTended to 24 bits
// 0000 000 000 0 00 000[00000000]
typedef struct Control{
    bool HALT;
    int IR, PC, MAR, MDR;
    int eq, gt; // -1: undefined, 0: false, 1:true
    Memory *memory;
    ALU *alu;
    Reg *reg;
    void (*doInstruct) (struct Control *unit);
} Control;

typedef struct ISA{
    int opcode, regd, regn, regt, imm, memAddr, mode, condition;
} ISA;

void init(Control *unit, int *instructions, int cnt){
    unit->PC = instructions[0];
    int i;
    for(i=2;i<cnt;i++){
        unit->memory->write(unit->memory, unit->PC+i-2, instructions[i]);
    }
    // for(i=unit->PC;i<cnt+unit->PC;i++){
    //     printf("%d\n",unit->memory->read(unit->memory, i));
    // }
}
// ------------------
// Decode Instruction
int getOpcode(int instruction){
    // 15-12 bits
    int OpcodeMask = 0xf00000; // CHANGED FROM 0xf000
    int opcode = instruction & OpcodeMask;
    opcode >>= 20; // CHANGED FROM 12
    opcode &= 0xf;
    return opcode;
}

int getRegd(int instruction){
    // 11-9 bits
    // same as branch conditions
    int regdMask = 0x0e0000; // CHANGED FROM 0x0e00
    int regd = (instruction & regdMask) >> 17; // CHANGED FROM 9
    return regd;
}

int getCond(int instruction){
    // 0: eq; 1: ne; 2: gt; 3: lt; 4: no condition
    return getRegd(instruction);
}

int getRegn(int instruction){
    // 8-6 bits
    int regnMask = 0x01c000; // CHANGED FROM 0x01c0
    int regn = (instruction & regnMask) >> 14; // CHANGED FROM 6
    return regn;
}

int getMode(int instruction){
    // 5 bit
    // 0: reg; 1: imm
    int modeMask = 0x002000; // CHANGED FROM 0x0020
    int mode = (instruction & modeMask) >> 13; // CHANGED FROM 5
    return mode;
}

int getRegt(int instruction){
    // 2-0 bits
    int regtMask = 0x000007; // CHANGED FROM 0x0007
    int regt = instruction & regtMask;
    return regt;
}

int getMemAddr(int instruction){
    // 8-0 bits
    int memAddrMask = 0x01ffff; // CHANGED FROM 0x01ff
    int memAddr = instruction & memAddrMask;
    return memAddr;
}

int getImm(int instruction){
    // 4-0 bits
    int immMask = 0x001fff; // CHANGED FROM 0x001fff
    int imm = instruction & immMask;
    // if immediate is supposed to be negative
    // if(imm & 0x10){
    //     imm |= 0xffd0;
    // }
    return imm;
}
// Fetch-decode-execute cycle
void fetch(Control *unit){
    // Fetch stage
    unit->MAR = unit->PC;
    unit->MDR = unit->memory->read(unit->memory, unit->MAR);
    unit->PC++;
    unit->IR = unit->MDR;
}

ISA decode(Control *unit){
    int opcode = getOpcode(unit->IR);
    int regd = getRegd(unit->IR);
    int regn = getRegn(unit->IR);
    int mode = getMode(unit->IR);
    int regt = getRegt(unit->IR);
    int immediate = getImm(unit->IR);
    int memAddr = getMemAddr(unit->IR);
    int condition = getCond(unit->IR);
    // printf("Opcode: %d\nRegd: %d\nRegN: %d\nRegT: %d\nMode: %d\nImmediate: %d\nMemAddr: %d\n\n", opcode, regd, regn, regt, mode, immediate, memAddr);
    ISA res = {opcode, regd, regn, regt, immediate, memAddr, mode, condition};
    return res;
}

int execute(ISA set, Control *unit){
    int reg1, reg2, immediate, address, res;
    switch(set.opcode){
        case 0: // LDR 0000 000 000000000
            unit->MAR = set.memAddr;
            unit->MDR = unit->memory->read(unit->memory, unit->MAR);
            unit->reg->write(unit->reg, set.regd, unit->MDR);
            return 0;
            break;
        case 1: // STR 0000 000 000000000
            unit->MDR = unit->reg->read(unit->reg, set.regd);
            unit->MAR = set.memAddr;
            unit->memory->write(unit->memory, unit->MAR, unit->MDR);
            return 0;
            break;
        case 2: // MOV 0000 000 000 1 00 000
            // 0000 000 000 1 00000
            if(set.mode) res = set.imm;
            else res = unit->reg->read(unit->reg, set.regt);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 3: // ADD 0000 000 000 0 00 000
            // 0000 000 000 1 00000
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->add(reg1, reg2);
            if(res>0x7fff) res=0x7fff;
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 4: // SUB same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->sub(reg1, reg2);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 5: // AND same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->and(reg1, reg2);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 6: // ORR same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->orr(reg1, reg2);
            if(res>0x7fff) res=0x7fff;
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 7: // EOR same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->eor(reg1, reg2);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 8: // MVN save as MOV
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->mvn(reg2);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 9: // LSL same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = (unit->alu->lsl(reg1, reg2));
            if(res>0x7fff) res=0x7fff;
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 10: // LSR same as ADD
            reg1 = unit->reg->read(unit->reg, set.regn);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            res = unit->alu->lsr(reg1, reg2);
            unit->reg->write(unit->reg, set.regd, res);
            return 0;
            break;
        case 11: // CMP same as MOV
            reg1 = unit->reg->read(unit->reg, set.regd);
            if(set.mode) reg2 = set.imm;
            else reg2 = unit->reg->read(unit->reg, set.regt);
            unit->eq = unit->alu->isEqual(reg1, reg2);
            unit->gt = unit->alu->isGreat(reg1, reg2);
            return 0;
            break;
        case 12: ; // B 0000 000 000000000
            bool flag=0;
            switch(set.condition){
                case 0:
                    if(unit->eq==1) flag=1;
                    else flag=0;
                    break;
                case 1:
                    if(unit->eq==1) flag=0;
                    else flag=1;
                    break;
                case 2:
                    if(unit->gt==1) flag=1;
                    else flag=0;
                    break;
                case 3:
                    if(unit->gt==0) flag=1;
                    else flag=0;
                    break;
                case 4:
                    flag=1;
                    break;
                default:
                    flag=0;
                    break;
            }
            if(flag){
                unit->PC = set.memAddr;
            }
            return 0;
            break;
        case 13: // HALT same as TRAP
            return 1;
            break;
        case 14: // TRAP 0000 000000000000
            // Input and output
            return 0;
            break;
        // opcode15 reserved: Currently for passing extra .ORIG
        case 15:
            return 0;
            break;
        default:
            puts("Invalid Opcode");
    }
}

void doInstruct(Control *unit){
    // Do the cycle
    fetch(unit);
    ISA set = decode(unit);
    unit->HALT = execute(set, unit);
}

void setMemVal(Control *unit, int addr, int val){
    // Memory value is changed manually
    unit->memory->write(unit->memory, addr, val);
}

Control *createControl(int PC,int size){
    Control *unit = calloc(1, sizeof(Control));
    unit->HALT = 0;
    unit->PC = PC;
    unit->memory = constructMemory(size);
    unit->alu = ConstructALU();
    unit->reg = regConstruct();
    unit->eq = unit->gt = unit->IR = unit->MAR = unit->MDR = -1;
    unit->doInstruct = doInstruct;
    return unit;
}

void freeControl(Control *unit){
    alufree(unit->alu);
    freeMemory(unit->memory);
    regfree(unit->reg);
    free(unit);
}

void testLink(char *instruction){
    printf("%s\n", instruction);
}