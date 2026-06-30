
def factorial_while(n: int) -> int:
	"""Return factorial of n using a while loop."""
	if n < 0:
		raise ValueError("n must be non-negative")
	result = 1
	i = 1
	while i <= n:
		result *= i
		i += 1
	return result


def sum_n_for(n: int) -> int:
	"""Return sum of first n natural numbers using a for loop."""
	if n < 0:
		raise ValueError("n must be non-negative")
	total = 0
	for i in range(1, n + 1):
		total += i
	return total


if __name__ == "__main__":
	try:
		x = int(input("Enter a non-negative integer: "))
	except ValueError:
		print("Please enter a valid integer.")
	else:
		print(f"Factorial of {x} is {factorial_while(x)}")
		print(f"Sum of first {x} natural numbers is {sum_n_for(x)}")

