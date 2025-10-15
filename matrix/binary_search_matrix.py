def binary_search(array: list, lower_bound: int, upper_bound: int, value: int) -> int:
    """
    This function carries out Binary search on a 1d array and
    return -1 if it do not exist
    array: A 1d sorted array
    value : the value meant to be searched
    >>> matrix = [1, 4, 7, 11, 15]
    >>> binary_search(matrix, 0, len(matrix) - 1, 1)
    0
    >>> binary_search(matrix, 0, len(matrix) - 1, 23)
    -1
    """
    # Base case: if bounds cross, value not found in array
    if lower_bound > upper_bound:
        return -1
    
    # Calculate middle index (floor division to get integer)
    r = (lower_bound + upper_bound) // 2
    
    # Check if middle element is the target value
    if array[r] == value:
        return r
    
    # If middle element is less than target, search right half
    if array[r] < value:
        return binary_search(array, r + 1, upper_bound, value)
    # Otherwise, search left half
    else:
        return binary_search(array, lower_bound, r - 1, value)


def mat_bin_search(value: int, matrix: list) -> list:
    """
    This function loops over a 2d matrix and calls binarySearch on
    the selected 1d array and returns [-1, -1] is it do not exist
    value : value meant to be searched
    matrix = a sorted 2d matrix
    >>> matrix = [[1, 4, 7, 11, 15],
    ...           [2, 5, 8, 12, 19],
    ...           [3, 6, 9, 16, 22],
    ...           [10, 13, 14, 17, 24],
    ...           [18, 21, 23, 26, 30]]
    >>> target = 1
    >>> mat_bin_search(target, matrix)
    [0, 0]
    >>> target = 34
    >>> mat_bin_search(target, matrix)
    [-1, -1]
    """
    # Handle edge cases: empty matrix or empty first row
    if not matrix or not matrix[0]:
        return [-1, -1]
    
    # Iterate through each row of the matrix
    for index in range(len(matrix)):
        # Optimization: if first element of current row exceeds target,
        # no need to search further rows (matrix is sorted)
        if matrix[index][0] > value:
            break
        
        # Perform binary search on current row
        r = binary_search(matrix[index], 0, len(matrix[index]) - 1, value)
        
        # If value found, return [row_index, column_index]
        if r != -1:
            return [index, r]
    
    # Value not found in entire matrix
    return [-1, -1]


if __name__ == "__main__":
    import doctest

    doctest.testmod()