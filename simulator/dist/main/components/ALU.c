#include <stdlib.h>

typedef struct ALU{
    int (*add)(int, int);
    int (*and)(int, int);
    int (*isEqual)(int, int);
    int (*isGreat)(int, int);
    int (*sub)(int, int);
    int (*orr)(int, int);
    int (*eor)(int, int);
    int (*mvn)(int);
    int (*lsl)(int, int);
    int (*lsr)(int, int);
} ALU;

int add(int x,int y){
    return x + y;
}

int sub(int x,int y){
    return x - y;
}

int isEqual(int x,int y){
    return x == y;
}

int isGreat(int x,int y){
    return (isEqual(x, y)?-1:(x>y?1:0));
}

int and(int x, int y){
    return x & y;
}

int orr(int x, int y){
    return x | y;
}

int eor(int x, int y){
    return x ^ y;
}

int not(int x){
    return ~x;
}

int lshift(int x,int y){
    return x << y;
}

int rshift(int x,int y){
    return x >> y;
}

void alufree(ALU *alu){
    free(alu);
}

ALU *ConstructALU(){
    ALU *alu = calloc(1, sizeof(ALU));
    alu->add = add;
    alu->isEqual = isEqual;
    alu->and = and;
    alu->isGreat = isGreat;
    alu->sub = sub;
    alu->orr = orr;
    alu->eor = eor;
    alu->mvn = not;
    alu->lsl = lshift;
    alu->lsr = rshift;
    return alu;
}