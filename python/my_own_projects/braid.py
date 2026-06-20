arr = list("1234567")

print("".join(arr))

while True:
    # Move last element to the middle
    x = arr.pop()
    mid = len(arr) // 2
    arr.insert(mid, x)
    print("".join(arr))

    # Move first element to the middle
    x = arr.pop(0)
    mid = len(arr) // 2
    arr.insert(mid, x)
    print("".join(arr))
 
"""
1234567
1237456
2371456
2376145
3762145
3765214
7653214
7654321
6547321
6541732
5416732
5412673
4125673
4123567 
"""