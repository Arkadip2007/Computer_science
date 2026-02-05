#include <stdio.h>
#include <stdlib.h>

int main() {
    char choice;
    printf("Are you sure you want to shutdown the system? (y/n): ");
    scanf(" %c", &choice);

    if(choice == 'y' || choice == 'Y') {
        system("shutdown now");// only linux command
    } else {
        printf("Shutdown cancelled.\n");// 
    }

    return 0;
} 