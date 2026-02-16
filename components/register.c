#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Reg{
    int registers[8];
    int (*read)(struct Reg*, int);
    void (*write)(struct Reg*, int, int);
} Reg;

int readReg(Reg *pt, int index){
    return pt->registers[index];
}

void writeReg(Reg *pt, int index, int val){
    pt->registers[index] = val;
}

Reg *regConstruct(){
    Reg *regs = calloc(1, sizeof(Reg));
    // 16 bits system --> 4 * sizoef(int)
    memset(regs->registers, 0, sizeof(int)*4);
    regs->read = readReg;
    regs->write = writeReg;
    return regs;
}

void regfree(Reg *pt){
    free(pt);
}