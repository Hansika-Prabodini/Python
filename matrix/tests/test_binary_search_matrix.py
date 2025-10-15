"""
Tests for binary_search_matrix.py module.

Tests both binary_search (1D array search) and mat_bin_search (2D matrix search) functions
with various edge cases and normal scenarios.
"""

import pytest
from matrix.binary_search_matrix import binary_search, mat_bin_search


class TestBinarySearch:
    """Tests for the binary_search function."""

    def test_binary_search_value_found_at_start(self):
        """Test finding value at the beginning of array."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 1)
        assert result == 0

    def test_binary_search_value_found_at_end(self):
        """Test finding value at the end of array."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 15)
        assert result == 4

    def test_binary_search_value_found_in_middle(self):
        """Test finding value in the middle of array."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 7)
        assert result == 2

    def test_binary_search_value_not_found(self):
        """Test searching for value that doesn't exist."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 23)
        assert result == -1

    def test_binary_search_value_less_than_all(self):
        """Test searching for value less than all elements."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 0)
        assert result == -1

    def test_binary_search_value_between_elements(self):
        """Test searching for value that falls between elements."""
        array = [1, 4, 7, 11, 15]
        result = binary_search(array, 0, len(array) - 1, 5)
        assert result == -1

    def test_binary_search_single_element_found(self):
        """Test with single element array where value is found."""
        array = [5]
        result = binary_search(array, 0, 0, 5)
        assert result == 0

    def test_binary_search_single_element_not_found(self):
        """Test with single element array where value is not found."""
        array = [5]
        result = binary_search(array, 0, 0, 3)
        assert result == -1

    def test_binary_search_two_elements(self):
        """Test with two element array."""
        array = [3, 7]
        assert binary_search(array, 0, 1, 3) == 0
        assert binary_search(array, 0, 1, 7) == 1
        assert binary_search(array, 0, 1, 5) == -1

    def test_binary_search_large_array(self):
        """Test with a larger array."""
        array = list(range(1, 101, 2))  # [1, 3, 5, 7, ..., 99]
        assert binary_search(array, 0, len(array) - 1, 1) == 0
        assert binary_search(array, 0, len(array) - 1, 99) == 49
        assert binary_search(array, 0, len(array) - 1, 51) == 25
        assert binary_search(array, 0, len(array) - 1, 100) == -1


class TestMatBinSearch:
    """Tests for the mat_bin_search function."""

    def test_mat_bin_search_value_at_top_left(self):
        """Test finding value at top-left corner."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(1, matrix)
        assert result == [0, 0]

    def test_mat_bin_search_value_at_bottom_right(self):
        """Test finding value at bottom-right corner."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(30, matrix)
        assert result == [4, 4]

    def test_mat_bin_search_value_in_middle(self):
        """Test finding value in the middle of matrix."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(9, matrix)
        assert result == [2, 2]

    def test_mat_bin_search_value_not_found(self):
        """Test searching for value that doesn't exist in matrix."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(34, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_value_less_than_all(self):
        """Test searching for value less than all elements."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(0, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_value_greater_than_all(self):
        """Test searching for value greater than all elements."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        result = mat_bin_search(100, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_empty_matrix(self):
        """Test with empty matrix - tests edge case handling."""
        matrix = []
        result = mat_bin_search(5, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_empty_rows(self):
        """Test with matrix containing empty rows - tests edge case handling."""
        matrix = [[]]
        result = mat_bin_search(5, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_single_element_found(self):
        """Test with single element matrix where value is found."""
        matrix = [[5]]
        result = mat_bin_search(5, matrix)
        assert result == [0, 0]

    def test_mat_bin_search_single_element_not_found(self):
        """Test with single element matrix where value is not found."""
        matrix = [[5]]
        result = mat_bin_search(3, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_single_row(self):
        """Test with single row matrix."""
        matrix = [[1, 3, 5, 7, 9]]
        assert mat_bin_search(1, matrix) == [0, 0]
        assert mat_bin_search(9, matrix) == [0, 4]
        assert mat_bin_search(5, matrix) == [0, 2]
        assert mat_bin_search(6, matrix) == [-1, -1]

    def test_mat_bin_search_single_column(self):
        """Test with single column matrix."""
        matrix = [[1], [3], [5], [7], [9]]
        assert mat_bin_search(1, matrix) == [0, 0]
        assert mat_bin_search(9, matrix) == [4, 0]
        assert mat_bin_search(5, matrix) == [2, 0]
        assert mat_bin_search(6, matrix) == [-1, -1]

    def test_mat_bin_search_different_positions(self):
        """Test finding values in different rows and columns."""
        matrix = [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ]
        # First row, different columns
        assert mat_bin_search(4, matrix) == [0, 1]
        assert mat_bin_search(11, matrix) == [0, 3]
        
        # Middle rows
        assert mat_bin_search(8, matrix) == [1, 2]
        assert mat_bin_search(16, matrix) == [2, 3]
        
        # Last row
        assert mat_bin_search(21, matrix) == [4, 1]
        assert mat_bin_search(26, matrix) == [4, 3]

    def test_mat_bin_search_optimization_early_break(self):
        """Test that search breaks early when first element exceeds target."""
        matrix = [
            [1, 4, 7],
            [10, 13, 16],
            [20, 23, 26],
        ]
        # Target is 5, which is less than first element of second row (10)
        # The function should not search rows starting from 10 onwards
        result = mat_bin_search(5, matrix)
        assert result == [-1, -1]

    def test_mat_bin_search_rectangular_matrix(self):
        """Test with non-square matrix."""
        matrix = [
            [1, 2, 3, 4, 5, 6],
            [7, 8, 9, 10, 11, 12],
        ]
        assert mat_bin_search(1, matrix) == [0, 0]
        assert mat_bin_search(6, matrix) == [0, 5]
        assert mat_bin_search(7, matrix) == [1, 0]
        assert mat_bin_search(12, matrix) == [1, 5]
        assert mat_bin_search(9, matrix) == [1, 2]
        assert mat_bin_search(13, matrix) == [-1, -1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
