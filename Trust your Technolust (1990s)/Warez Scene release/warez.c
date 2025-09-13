#include <stdio.h>
#include <string.h>
int main() {
    cbar input[20];
    printf("Enter registration code: ")
    scanf("%s", input);
    if(strcmp(input, "1337-H4X0R") == 0)  {
        printf("Congratz! Flag: bithaven{warez4lyfe}\n");
    } else {
        printf("Invalid code!\n");
    }
    return 0;
}