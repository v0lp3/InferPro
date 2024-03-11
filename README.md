# Infer Pro

## Summary

- Infer Pro is software that generates applicable patches for vulnerabilities reported by the [Infer Static Analyzer](https://github.com/facebook/infer) 
- This project was created for the course `Ingegneria dei Sistemi Distribuiti` at UniCT.
- The patches are generated using the [Gemini Pro API](https://ai.google.dev/)

## Example

> [!NOTE]  
> Different execution can produce different results.

Given the following code as input:

```c
#include <string.h>

int main () {

        char* test = malloc(-1);
        strcpy(test, "yoooooooo");

}
```

Infer will produce the following report:

```
main.c:6: error: Buffer Overrun L1
  Offset: 9 Size: [0, -1].
  4.
  5.         char* test = malloc(-1);
  6.         strcpy(test, "yoooooooo");
             ^
  7.
  8. }

main.c:5: error: Inferbo Alloc Is Big
  Length: 18446744073709551615.
  3. int main () {
  4.
  5.         char* test = malloc(-1);
                          ^
  6.         strcpy(test, "yoooooooo");
  7.

main.c:6: error: Null Dereference
  pointer `test` last assigned on line 5 could be null and is dereferenced by call to `strcpy()` at line 6, column 9.
  4.
  5.         char* test = malloc(-1);
  6.         strcpy(test, "yoooooooo");
             ^
  7.
  8. }


Found 3 issues
                  Issue Type(ISSUED_TYPE_ID): #
          Null Dereference(NULL_DEREFERENCE): 1
  Inferbo Alloc Is Big(INFERBO_ALLOC_IS_BIG): 1
        Buffer Overrun L1(BUFFER_OVERRUN_L1): 1
```

The software will produce the following patch file:

```diff
--- test3/main.c
+++ test3/main.c
@@ -2,7 +2,11 @@
 
 int main () {
 
-        char* test = malloc(-1);
-        strcpy(test, "yoooooooo");
+        char* test = NULL;
+        if(test = malloc(256)) {
+                strcpy(test, "yoooooooo");
+                free(test);
+        }
 
 }
```


## Author

- [Andrea Maugeri](https://github.com/v0lp3)
