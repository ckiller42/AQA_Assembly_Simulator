#include <stdio.h>
#include <stdlib.h>

typedef struct Memory{
    int size;
    int *data;
    int (*read)(struct Memory *pt, int address);
    void (*write)(struct Memory *pt, int address, int val);
    void (*freeMemory)(struct Memory *pt);
} Memory;

int readMem(Memory *pt, int address){
    return pt->data[address];
}

void writeMem(Memory *pt, int address, int val){
    pt->data[address] = val;
}

void freeMemory(Memory *pt){
    // Have to free the inner pointer!! Otherwise UAF might occurs
    free(pt->data);
    free(pt);
}

Memory *constructMemory(int size){
    Memory *unit = calloc(1, sizeof(Memory));
    unit->size = size;
    unit->data = calloc(1, sizeof(int) * size); // 16 bits = 2 bytes
    unit->read = readMem;
    unit->write = writeMem;
    unit->freeMemory = freeMemory;
    return unit;
}