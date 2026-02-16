#include "components/control.c"
#include <string.h>
#define MAXLEN 32  // 24 bits. Give some extra space in case
#define MAXLOOP 10000
char* itob(int num){
    char *res = calloc(MAXLEN, sizeof(char)); // safety issue?
    for(int i=23;~i;i--){
        res[i]=(num&1)+'0';
        num>>=1;
    }
    return res;
}
int main(){
    char *path = "./machine_code.txt";
    FILE *fp = fopen(path, "r");
    if(fp == NULL){
        puts("file pointer is null");
        return 1;
    }
    int cnt = 0, ins_ptr = 0;
    char ins[MAXLEN], ins_list[1001][MAXLEN];
    while(fgets(ins, MAXLEN, fp)){
        ins[strcspn(ins, "\n")] = 0;
        strcpy(ins_list[cnt++], ins);
    }
    int ins_int[cnt], i;
    for(i=0;i<cnt;i++){
        ins_int[i] = strtol(ins_list[i], NULL, 2);
    }
    Control *control = createControl(ins_int[0], 0x200); ins_ptr++;
    init(control, ins_int, cnt);
    int loop = 0;
    while(control->PC < cnt-2 && !control->HALT){
        // printf("PC:%d\n",control->reg->read(control->reg, 7));
        // printf("PC:%d\n", control->PC);
        doInstruct(control);
        if(loop > MAXLOOP){
            puts("The loop does not end.");
            freeControl(control); // free memory control
            return 1;
        }
        loop++;
    }
    for(int i=0;i<8;i++){
        int reg_val = control->reg->read(control->reg, i);
        // printf("Reg %d: %d\n", i, reg_val);
        printf("Reg %d: %d_10 %s_2\n", i, reg_val, itob(reg_val));
    }
    freeControl(control); // free memory control
    return 0;
}