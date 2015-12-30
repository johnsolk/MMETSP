#include <stdio.h>
#include <unistd.h>
int main ()
{
    printf("This is an example; Hello World\n");
    sleep(300); /*Do nothing for 300 seconds so we have time to see the process
		run in qstat*/
    printf("Sleep completed, exiting\n");
}

