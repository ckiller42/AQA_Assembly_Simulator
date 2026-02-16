// For subprocess
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "control.c"

#define MEM_SIZE 512

int main(){
    int PC;
    struct Control *unit = createControl(PC, MEM_SIZE);
    
    freeControl(unit);
    return 0;
}