# weite a program to calculate the average of 3 numbers
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))
num3 = float(input("Enter the third number: ")) 
average = (num1 + num2 + num3) / 3
print("The average of the three numbers is: ", average)


# weite a program to check if a number is even or odd
num = int(input("Enter a number: "))
if (num % 2 == 0):
    print(num, "is an even number.")
else:    
    print(num, "is an odd number.")    

# without using if else statement
num = int(input("Enter a number: "))
result = "even" if num % 2 == 0 else "odd"
print(num, "is an", result, "number.")  

# write a program to calculate grade based on marks
marks = float(input("Enter the marks: "))
if (marks >= 90):
    grade = "A+"
elif (marks >= 80):
    grade = "A"
elif (marks >= 60):
    grade = "B"
elif (marks >= 50):
    grade = "C"
else:
    grade = "D"
print("The grade is: ", grade)

# generate factorial of a number
try:
    num = int(input("Enter a non-negative integer: "))
    if num < 0:
        print("Factorial is not defined for negative numbers.")
    else:
        factorial = 1
        for i in range(1, num + 1):
            factorial *= i
        print("The factorial of", num, "is", factorial)
except ValueError:
    print("Invalid input. Please enter an integer.")

# sum of n natural numbers
n = int(input("Enter a number: "))
sum_natural = n * (n + 1) // 2
print("The sum of the first", n, "natural numbers is", sum_natural)     


# write a program to check if a number is prime or not
num = int(input("Enter a number: "))
if num > 1:
    for i in range(2, int(num**0.5) + 1):
        if (num % i) == 0:
            print(num, "is not a prime number.")
            break
    else:
        print(num, "is a prime number.")
else:    print(num, "is not a prime number.")
