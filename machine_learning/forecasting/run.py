"""
this is code for forecasting
but I modified it and used it for safety checker of data
for ex: you have an online shop and for some reason some data are
missing (the amount of data that u expected are not supposed to be)
        then we can use it
*ps : 1. ofc we can use normal statistic method but in this case
         the data is quite absurd and only a little^^
      2. ofc u can use this and modified it for forecasting purpose
         for the next 3 months sales or something,
         u can just adjust it for ur own purpose
"""

from warnings import simplefilter

import numpy as np
import pandas as pd
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVR
from statsmodels.tsa.statespace.sarimax import SARIMAX


def linear_regression_prediction(
    train_dt: list, train_usr: list, train_mtch: list, test_dt: list, test_mtch: list
) -> float:
    """
    First method: linear regression
    input : training data (date, total_user, total_event) in list of float
    output : list of total user prediction in float
    >>> n = linear_regression_prediction([2,3,4,5], [5,3,4,6], [3,1,2,4], [2,1], [2,2])
    >>> bool(abs(n - 5.0) < 1e-6)  # Checking precision because of floating point errors
    True
    """
    # Use column_stack for more efficient matrix construction
    x = np.column_stack([np.ones(len(train_dt)), train_dt, train_mtch])
    y = np.array(train_usr)
    # Use linalg.solve instead of computing inverse for better performance and stability
    beta = np.linalg.solve(x.T @ x, x.T @ y)
    return abs(beta[0] + test_dt[0] * beta[1] + test_mtch[0] * beta[2])


def sarimax_predictor(train_user: list, train_match: list, test_match: list) -> float:
    """
    second method: Sarimax
    sarimax is a statistic method which using previous input
    and learn its pattern to predict future data
    input : training data (total_user, with exog data = total_event) in list of float
    output : list of total user prediction in float
    >>> sarimax_predictor([4,2,6,8], [3,1,2,4], [2])
    6.6666671111109626
    """
    # Suppress the User Warning raised by SARIMAX due to insufficient observations
    simplefilter("ignore", UserWarning)
    order = (1, 2, 1)
    seasonal_order = (1, 1, 1, 7)
    model = SARIMAX(
        train_user, exog=train_match, order=order, seasonal_order=seasonal_order
    )
    model_fit = model.fit(disp=False, maxiter=600, method="nm")
    result = model_fit.predict(1, len(test_match), exog=[test_match])
    return float(result[0])


def support_vector_regressor(x_train: list, x_test: list, train_user: list) -> float:
    """
    Third method: Support vector regressor
    svr is quite the same with svm(support vector machine)
    it uses the same principles as the SVM for classification,
    with only a few minor differences and the only different is that
    it suits better for regression purpose
    input : training data (date, total_user, total_event) in list of float
    where x = list of set (date and total event)
    output : list of total user prediction in float
    >>> support_vector_regressor([[5,2],[1,5],[6,2]], [[3,2]], [2,1,4])
    1.634932078116079
    """
    regressor = SVR(kernel="rbf", C=1, gamma=0.1, epsilon=0.1)
    regressor.fit(x_train, train_user)
    y_pred = regressor.predict(x_test)
    return float(y_pred[0])


def interquartile_range_checker(train_user: list) -> float:
    """
    Optional method: interquatile range
    input : list of total user in float
    output : low limit of input in float
    this method can be used to check whether some data is outlier or not
    >>> interquartile_range_checker([1,2,3,4,5,6,7,8,9,10])
    2.8
    """
    # Use numpy array for more efficient operations, avoid in-place sort
    user_array = np.array(train_user)
    q1, q3 = np.percentile(user_array, [25, 75])
    iqr = q3 - q1
    return q1 - (iqr * 0.1)


def data_safety_checker(list_vote: list, actual_result: float) -> bool:
    """
    Used to review all the votes (list result prediction)
    and compare it to the actual result.
    input : list of predictions
    output : print whether it's safe or not
    >>> data_safety_checker([2, 3, 4], 5.0)
    False
    """
    if not isinstance(actual_result, float):
        raise TypeError("Actual result should be float. Value passed is a list")

    # Vectorized operations for better performance
    votes_array = np.array(list_vote)
    
    # Count votes efficiently
    greater_than_actual = np.sum(votes_array > actual_result)
    close_to_actual = np.sum(np.abs(votes_array - actual_result) <= 0.1)
    
    safe = greater_than_actual + close_to_actual  # Fix the logic error
    not_safe = len(list_vote) - safe
    
    return safe > not_safe


if __name__ == "__main__":
    """
    data column = total user in a day, how much online event held in one day,
    what day is that(sunday-saturday)
    """
    data_input_df = pd.read_csv("ex_data.csv")

    # start normalization - more efficient data loading and normalization
    data_values = data_input_df.values
    normalize_df = Normalizer().fit_transform(data_values)
    
    # Efficient data splitting using array slicing (no .tolist() conversions)
    # Split data once at the boundary
    split_idx = -1
    
    # Extract columns directly as arrays
    total_user = normalize_df[:, 0]
    total_match = normalize_df[:, 1] 
    total_date = normalize_df[:, 2]
    
    # Training data (all but last row)
    train_user = total_user[:split_idx]
    train_match = total_match[:split_idx]
    train_date = total_date[:split_idx]
    
    # Test data (last row only)
    test_user_val = total_user[split_idx]
    test_match_val = total_match[split_idx]
    test_date_val = total_date[split_idx]
    
    # For SVR - prepare feature matrix efficiently
    x_train = normalize_df[:split_idx, [1, 2]]  # match and date columns
    x_test = normalize_df[split_idx:, [1, 2]]   # last row

    # voting system with forecasting - convert to lists only when required by functions
    res_vote = [
        linear_regression_prediction(
            train_date.tolist(), train_user.tolist(), train_match.tolist(), 
            [test_date_val], [test_match_val]
        ),
        sarimax_predictor(train_user.tolist(), train_match.tolist(), [test_match_val]),
        support_vector_regressor(x_train.tolist(), x_test.tolist(), train_user.tolist()),
    ]

    # check the safety of today's data
    not_str = "" if data_safety_checker(res_vote, float(test_user_val)) else "not "
    print(f"Today's data is {not_str}safe.")
