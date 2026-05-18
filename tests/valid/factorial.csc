func factorial(n) {
    result = 1;
    while n > 1 {
        result = result * n;
        n = n - 1;
    }
    return result;
}

x = factorial(5);
print(x);
