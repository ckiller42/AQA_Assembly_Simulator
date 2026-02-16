// DEBUG prints are annottated
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_LEN 128
#define DELIMITER " "

bool check_imm(char *operand){
    if(operand[0]=='#'){
        int i;
        for(i=1;i<strlen(operand);i++){
            if(operand[i]<='9'&&operand[i]>='0') continue;
            else return 0;
        }
        return 1;
    }else return 0;
}

bool check_mem(char *operand){
    int val = atoi(operand);
    if(!val&&operand[0]!='0') return 0;
    else if(val>0x200) return 0;  // Maximum memory CHANGEABLE
    else return 1;
}

bool check_reg(char *operand){
    if(operand[0]=='R'){
        if(strlen(operand)!=2) return 0;
        if(operand[1]>='0'&&operand[1]<='7') return 1;
        else return 0;
    }else return 0;
}

int check_syntax(FILE *fp){
    /*
    input:
    fp: FILE pointer
    return:
    0: file passed
    >0: file has syntax error at line ____
    -1: smth went wrong within the checker function
    NB: Check if fp needs to be reset by fseek
    */
    char ins[MAX_LEN];
    int line_num=0;
    while(fgets(ins, MAX_LEN, fp)){
        // DEBUG
        // printf("%s", ins);
        // if(ins[0] == ';') continue;
        line_num++;
        if(line_num == 1){
            char op[MAX_LEN];
            int pos = strcspn(ins, " ");
            memcpy(op, ins, pos);
            if(strcmp(op, ".ORIG")) return line_num;
            memset(op, 0, sizeof(op));
            memcpy(op, ins+6, strlen(ins+6)-1);
            if(!check_mem(op)) return line_num;
            else continue;
        }
        ins[strcspn(ins, "\n")] = '\0';
        // label
        int pos = strcspn(ins, ":");
        int i=0;
        if(ins[pos]==':' && pos+1==strlen(ins)){ // label exists
            for(i=0;i<pos;i++){
                if((ins[i]>='A'&&ins[i]<='Z') || (ins[i]>='a'&&ins[i]<='z') || (ins[i]>='0'&&ins[i]<='9') || ins[i]=='_') continue;
                else return line_num;
            }
            continue;
        }
        char opcode[MAX_LEN];
        pos = strcspn(ins, DELIMITER);
        // HALT
        if(pos == strlen(ins)){
            if(!strcmp(ins, "HALT") || !strcmp(ins, ".END")) return 0;
            else return line_num;
        }
        ins[pos] = 1;
        if(pos>3) return line_num;  // Longest opcode is 3 characters
        memset(opcode, 0, sizeof(opcode));
        memcpy(opcode, ins, pos);  // ins[0:pos]
        int now = pos;
        // DEBUG
        // printf("opcode: %s\n", opcode);
        switch(pos){
            case 1:
                if(strcmp(opcode, "B")) return line_num;
                now = strcspn(ins, DELIMITER); ins[now]=1;
                if(ins[now+1]){ // conditional branching
                    char con[MAX_LEN];
                    if(now-pos>3) return line_num;
                    memset(con, 0, sizeof(con));
                    memcpy(con, ins+pos+1, 2);
                    // DEBUG
                    // printf("condition: %s\n", con);
                    // conditions
                    if(strcmp(con, "EQ") && strcmp(con, "NE") && strcmp(con, "GT") && strcmp(con, "LT")) return line_num;
                    pos = now;
                }
                // label
                for(i=pos+1;i<strlen(ins)-1;i++){
                    if((ins[i]>='A'&&ins[i]<='Z') || (ins[i]>='a'&&ins[i]<='z') || (ins[i]>='0'&&ins[i]<='9') || ins[i]=='_') continue;
                    else return line_num;
                }
                break;
            case 3:
                if(!strcmp(opcode, "LDR") || !strcmp(opcode, "STR")){
                    char reg[MAX_LEN];
                    // Check first register
                    now = strcspn(ins, DELIMITER); ins[now]=1;
                    memset(reg, 0, sizeof(reg));
                    memcpy(reg, ins+pos+1, now-pos-1);
                    // DEBUG
                    // printf("Reg1: %s\n", reg);
                    if(!check_reg(reg)) return line_num;
                    pos = now;
                    // Check memory
                    char memory[MAX_LEN];
                    memset(memory, 0, sizeof(memory));
                    memcpy(memory, ins+pos+1, strlen(ins+pos+1));
                    // DEBUG
                    // printf("Memory: %s\n", memory);
                    bool res = check_mem(memory);
                    if(!res) return line_num;
                    else break;
                }else if(!strcmp(opcode, "ADD") || !strcmp(opcode, "SUB") || !strcmp(opcode, "AND") || !strcmp(opcode, "ORR") || !strcmp(opcode, "EOR") || !strcmp(opcode, "LSL") || !strcmp(opcode, "LSR")){
                    char reg[MAX_LEN];
                    // Check first register
                    now = strcspn(ins, DELIMITER); ins[now]=1;
                    memset(reg, 0, sizeof(reg));
                    memcpy(reg, ins+pos+1, now-pos-1);
                    // DEBUG
                    // printf("Reg1: %s\n", reg);
                    if(!check_reg(reg)) return line_num;
                    pos = now;
                    // Check second register
                    now = strcspn(ins, DELIMITER); ins[now]=1;
                    memset(reg, 0, sizeof(reg));
                    memcpy(reg, ins+pos+1, now-pos-1);
                    // DEBUG
                    // printf("Reg2: %s\n", reg);
                    if(!check_reg(reg)) return line_num;
                    pos = now;
                    // Check operand
                    char operand[MAX_LEN];
                    memset(operand, 0, sizeof(operand));
                    memcpy(operand, ins+pos+1, strlen(ins+pos+1));
                    // DEBUG
                    // printf("Operand: %s\n", operand);
                    bool res = check_imm(operand) || check_reg(operand);
                    if(!res) return line_num;
                    else break;
                }else if(!strcmp(opcode, "MOV") || !strcmp(opcode, "CMP") || !strcmp(opcode, "MVN")){
                    char reg[MAX_LEN];
                    // Check first register
                    now = strcspn(ins, DELIMITER); ins[now]=1;
                    memset(reg, 0, sizeof(reg));
                    memcpy(reg, ins+pos+1, now-pos-1);
                    // DEBUG
                    // printf("Reg1: %s\n", reg);
                    if(!check_reg(reg)) return line_num;
                    pos = now;
                    // Check operand
                    char operand[MAX_LEN];
                    memset(operand, 0, sizeof(operand));
                    memcpy(operand, ins+pos+1, strlen(ins+pos+1));
                    // DEBUG
                    // printf("Operand: %s\n", operand);
                    bool res = check_imm(operand) || check_reg(operand);
                    if(!res) return line_num;
                    else break;
                }else return line_num;
            default:
                return line_num;
        }
    }
    return 0;
}
