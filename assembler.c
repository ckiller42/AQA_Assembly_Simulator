/* UPDATE 30/7/2025: 
    1. 16 bits --> 24 bits 
    2. added syntax check
    3. Annotation functionality - bugging at branching addr*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include "check_input.c"

#define HASHSIZE 203
// Section 6.6 of The C Programming Language
// Data Structure: Hash tree substitutes dictionary

struct nlist{
    struct nlist *next;
    char *key;
    int *value;
};
static struct nlist *hashtable[HASHSIZE];

unsigned hash(char *s){
    unsigned hashval;
    for(hashval = 0; *s != '\0'; s++) hashval = *s + 31 * hashval;
    return hashval % HASHSIZE;
}

struct nlist *lookup(char *s){
    struct nlist *res;
    for(res = hashtable[hash(s)]; res != NULL; res = res->next){
        if(strcmp(s, res->key) == 0) return res; // Found the key
    }
    return NULL; // Not Found
}

char *strup(char *s){
    char *p;
    p = (char *) malloc(strlen(s) + 1); // + 1 for '\0';
    if(p != NULL) strcpy(p, s);
    return p;
};

int *intup(int *s){
    int *p;
    p = (int *) malloc(sizeof(s) + 1);
    if(p!=NULL) *p = *s;
    return p;
}

struct nlist *install(char *key, int *val){
    struct nlist *res;
    unsigned hashval;
    if((res = lookup(key)) == NULL){ // current key is available
        res = (struct nlist *) malloc(sizeof(*res));
        if(res == NULL || (res->key = strup(key)) == NULL) return NULL;
        hashval = hash(key);
        res->next = hashtable[hashval];
        hashtable[hashval] = res;
    }else free((void *) res->value);
    if((res->value = intup(val)) == NULL) return NULL;
    return res;
}

void freeHashTable(struct nlist *unit){
    free(unit->key);
    free(unit->value);
    free(unit->next);
}

int getOpcode(char *instruction){
    // changed from 16 bits to 24 bits
    // i.e. added two zeros at the end of hex
    int res = 0;
    if(strcmp(instruction, "LDR") == 0) res = 0;
    else if(strcmp(instruction, "STR") == 0) res = 0x100000;
    else if(strcmp(instruction, "MOV") == 0) res = 0x200000;
    else if(strcmp(instruction, "ADD") == 0) res = 0x300000;
    else if(strcmp(instruction, "SUB") == 0) res = 0x400000;
    else if(strcmp(instruction, "AND") == 0) res = 0x500000;
    else if(strcmp(instruction, "ORR") == 0) res = 0x600000;
    else if(strcmp(instruction, "EOR") == 0) res = 0x700000;
    else if(strcmp(instruction, "MVN") == 0) res = 0x800000;
    else if(strcmp(instruction, "LSL") == 0) res = 0x900000;
    else if(strcmp(instruction, "LSR") == 0) res = 0xa00000;
    else if(strcmp(instruction, "CMP") == 0) res = 0xb00000;
    else if(strcmp(instruction, "B") == 0) res = 0xc00000;
    else if(strcmp(instruction, "HALT") == 0) res = 0xd00000;
    else if(strcmp(instruction, "TRAP") == 0) res = 0xe00000;
    else res = -1;
    return res;
}

int getRegIndex(char *reg){
    int res=0;
    // ONLY INT CAN USE SWITCH......
    if(strcmp(reg, "R0") == 0) res = 0;
    else if(strcmp(reg, "R1") == 0) res = 1;
    else if(strcmp(reg, "R2") == 0) res = 2;
    else if(strcmp(reg, "R3") == 0) res = 3;
    else if(strcmp(reg, "R4") == 0) res = 4;
    else if(strcmp(reg, "R5") == 0) res = 5;
    else if(strcmp(reg, "R6") == 0) res = 6;
    else if(strcmp(reg, "R7") == 0) res = 7;
    else res = -1;
    return res;
}

bool isDirective(char *instruction){
    if(instruction[0] == '.') return true;
    else return false;
}

char getOpcodeType(int opcode){
    char res;
    opcode >>= 20; // CHANGED FROM 12
    switch(opcode){
        case 0 ... 1: // LDR memory
            res = 'M';
            break;
        case 2: // MOV register
            res = 'R';
            break;
        case 3 ... 7: // ADD calculation
            res = 'C';
            break; 
        case 8:
            res = 'R';
            break;
        case 9 ... 10:
            res = 'C';
            break;
        case 11:
            res = 'R';
            break;
        case 12: // B branch
            res = 'B';
            break;
        case 13 ... 14: // TRAP system related
            res = 'T';
            break;
        default:
            printf("Invalid Opcode");
            break;
    }
    return res;
}

void setReg(char toSet, char *index, int *instruction){
    int mask = 0;
    switch (toSet){
    case 'd':
        mask = 17; // CHANGED FROM 9
        break;
    case 'n':
        mask = 14; // CHANGED FROM 6
        break;
    case 't':
        break;
    default:
        printf("Invalid register");
        break;
    }
    int res = getRegIndex(index);
    if(res == -1){puts("Invalid register");printf("%s\n", index);}
    else *instruction |= (res << mask);
}

void setMemAddr(char *addr, int *instruction){
    char *endptr;
    long res;
    if(addr[0] == 'R') puts("Invalid memory format");
    if(addr[0] == '0' && addr[1] == 'x'){
        res = strtol(addr, &endptr, 16);
        if(*endptr != '\0') puts("Invalid hex string");
    }else{
        res = strtol(addr, &endptr, 10);
        if(*endptr != '\0') puts("Invalid dec string");
    }
    if(res <= 0x1ffff) *instruction |= res; // CHANGED FROM 0x1ff
    else puts("Invalid Memory Address");
}

void setImmediate(char *imm, char OpcodeType, int *instruction){
    char *endptr;
    int len = strlen(imm);
    long immediate;
    if(imm[len - 1] == 'b'){
        immediate = strtol(imm, &endptr, 2);
        if(*endptr != '\0') puts("Invalid binary string");
    }else if(imm[len - 1] == 'h'){
        immediate = strtol(imm, &endptr, 16);
        if(*endptr != '\0') puts("Invalid hex string");
    }else if(imm[len - 1] <= '9' && imm[len - 1] >= '0'){
        immediate = strtol(imm, &endptr, 10);
        if(*endptr != '\0') puts("Invalid dec string");
    }else puts("Invalid Operand");
    if(OpcodeType == 'R' && immediate <= 0x1fff){ // CHANGED FROM 0x1f
        *instruction |= 0x2000; // CHANGED FROM 0x20
        *instruction |= immediate;
    }
    else if(OpcodeType == 'C' && immediate <= 0x1fff){ // CHANGED FROM 0x1f
        *instruction |= 0x2000; // CHANGED FROM 0x20
        *instruction |= immediate;
    }
    else puts("Too Large Immediate");
}

void setOperand(char *operand, char OpcodeType, int *instruction){
    char tmp[50], *regt, *imm;
    strcpy(tmp, operand);
    if(tmp[0] == 'R'){
        setReg('t', tmp, instruction);
    }else if(tmp[0] == '#'){
        imm = strtok(tmp, "#");
        setImmediate(imm, OpcodeType, instruction);
    }else printf("Invalid Operand");
}

int getCondition(char *condition){
    int res=0;
    if(strcmp(condition, "EQ") == 0) res = 0;
    else if(strcmp(condition, "NE") == 0) res = 1;
    else if(strcmp(condition, "GT") == 0) res = 2;
    else if(strcmp(condition, "LT") == 0) res = 3;
    else res = -1;
    return res;
}

void setCondition(int condition, int *instruction){
    int mask=17; // CHANGED FROM 9
    *instruction |= (condition << mask);
}

void setBranchAddr(char *label, int *instruction){
    if(label == NULL) puts("Label name collides with condition");
    struct nlist *res = lookup(label);
    // printf("%d\n", *(res->value));
    if(res == NULL) puts("Invalid Label");
    else *instruction |= *(res->value);
}
// Second Pass
int generateMachineCode(char *instruction){
    int res = 0;
    // strtok requires char []
    char tmp[80], *tok, *now, *regd, *regn, *mode, *operand, *addr, *label;
    strcpy(tmp, instruction);
    if(isDirective(instruction)){
        tok = strtok(tmp, " ");
        if(strcmp(tok, ".END") == 0) return generateMachineCode("HALT");
        else if(strcmp(tok, ".ORIG") == 0){
            return 0xf00000; // CHANGED FROM 0xf000
        }
    }
    now = strtok(tmp, " ");
    if(now[strlen(tok) - 1] == ':'){
        return -1;
    }
    res = getOpcode(now);
    switch(getOpcodeType(res)){
        case 'M':
            regd = strtok(NULL, " ");
            setReg('d', regd, &res);
            addr = strtok(NULL, " ");
            setMemAddr(addr, &res);
            break;
        case 'R':
            regd = strtok(NULL, " ");
            setReg('d', regd, &res);
            operand = strtok(NULL, " ");
            setOperand(operand, 'R', &res);
            break;
        case 'C':
            regd = strtok(NULL, " ");
            regn = strtok(NULL, " ");
            setReg('d', regd, &res);
            setReg('n', regn, &res);
            operand = strtok(NULL, " ");
            setOperand(operand, 'C', &res);
            break;
        case 'B':
            // Branching
            label = strtok(NULL, " ");
            int cond = getCondition(label);
            if(cond != -1){
                setCondition(cond, &res);
                label = strtok(NULL, " ");
            }else{
                setCondition(4, &res);
            }
            // printf("%s\n", label);
            setBranchAddr(label, &res);
            break;
        case 'T':
            // Input and output
            break;
        default:
            printf("Invalid Opcode Type");
            break;
    }
    return res;
}
// First Pass
void generateLabel(char *instruction, int *startAddr, int *curAddr){
    struct nlist *now;
    char tmp[100], *tok;
    strcpy(tmp, instruction);
    if(isDirective(instruction)){
        tok = strtok(tmp, " ");
        // .ORIG must be the first instruction or otherwise ignore it
        if(strcmp(tok, ".ORIG") == 0 && *curAddr == 0){
            tok = strtok(NULL, " ");
            setMemAddr(tok, startAddr);
            return;
        }
    }
    tok = strtok(tmp, " ");
    // Records the label into the hash table
    if(tok[strlen(tok) - 1] == ':'){
        tok[strlen(tok) - 1] = '\0';
        // printf("%d\n", *(curAddr));
        now = install(tok, curAddr);
    }
    ++(*curAddr);
}

char *int2bin(int x){
    char *res = malloc(25); // CHANGED FROM 17
    if(!res) return NULL;
    int i;
    for(i=23;~i;i--){ // CHANGED FROM i=15
        res[i]=(x&1)+'0';
        x>>=1;
    }
    res[24]='\0'; // CHANGED FROM i=16
    return res;
}

int main(int argc, char **argv){
    // For the use of subprocess
    char *path = "./records.txt";
    FILE *fp = fopen("./records.txt", "r");
    if(fp == NULL){
        puts("file pointer is null");
        return 1;
    }
    // CHANGE
    // Check syntax
    int err = check_syntax(fp);
    fseek(fp, 0, SEEK_SET);
    if(err){
        printf("There is syntax error at line %d. Assembler stopped.", err);
        return 1;
    }
    // END CHANGE
    int i, cnt=0, startaddr=0, curaddr=0;
    char instruction[MAX_LEN], instruction_list[1001][MAX_LEN];
    while(fgets(instruction, MAX_LEN, fp)){
        instruction[strcspn(instruction, "\n")] = 0;
        strcpy(instruction_list[cnt++], instruction);
        // printf("%s\n", instruction);
    }
    for(i=0;i<cnt;i++){
        generateLabel(instruction_list[i], &startaddr, &curaddr);
        if(startaddr != 0 && i == 0) curaddr = startaddr;
    }
    int machinecode[1001], mc_cnt = 0;
    for(i=0;i<cnt;i++){ // add annotation function
        if(instruction_list[i][0] == ';') continue;
        machinecode[mc_cnt++] = generateMachineCode(instruction_list[i]);
    }
    FILE *frp = fopen("./machine_code.txt", "w");
    // First line be the start address in the memory
    fprintf(frp, int2bin(startaddr));
    fprintf(frp, "\n");
    for(i=0;i<mc_cnt;i++){
        char *tmp = int2bin(machinecode[i]);
        fprintf(frp, tmp);
        fprintf(frp, "\n");
    }
    fclose(fp);
    fclose(frp);
    for(i=0;i<HASHSIZE;i++) freeHashTable(hashtable[i]);
    return 0;
}