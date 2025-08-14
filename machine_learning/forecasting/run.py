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
    
    Args:
        train_dt: List of training dates
        train_usr: List of training user counts
        train_mtch: List of training match/event counts
        test_dt: List containing test date
        test_mtch: List containing test match/event count
        
    Returns:
        Predicted user count as float
        
    >>> n = linear_regression_prediction([2,3,4,5], [5,3,4,6], [3,1,2,4], [2,1], [2,2])
    >>> bool(abs(n - 5.0) < 1e-6)  # Checking precision because of floating point errors
    True
    """
    # Design matrix with intercept term and features
    x = np.array([[1, item, train_mtch[i]] for i, item in enumerate(train_dt)])
    y = np.array(train_usr)
    
    # Calculate regression coefficients using normal equation
    x_transpose = x.transpose()
    beta = np.dot(np.dot(np.linalg.inv(np.dot(x_transpose, x)), x_transpose), y)
    
    # Make prediction (note: there might be a bug with the original formula)
    return abs(beta[0] + test_dt[0] * beta[1] + test_mtch[0] * beta[2])


def sarimax_predictor(train_user: list, train_match: list, test_match: list) -> float:
    """
    Second method: SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors)
    
    Uses time series analysis to learn patterns in historical data and predict future values.
    
    Args:
        train_user: List of historical user counts
        train_match: List of historical event counts (exogenous variable)
        test_match: List containing the event count for prediction
        
    Returns:
        Predicted user count as float
        
    >>> sarimax_predictor([4,2,6,8], [3,1,2,4], [2])
    6.6666671111109626
    """
    # Suppress the User Warning raised by SARIMAX due to insufficient observations
    simplefilter("ignore", UserWarning)
    
    # Define model parameters
    order = (1, 2, 1)             # (p,d,q) - AR order, differencing, MA order
    seasonal_order = (1, 1, 1, 7)  # (P,D,Q,s) - Seasonal components with period 7 (weekly)
    
    # Create and fit the model
    model = SARIMAX(
        train_user, exog=train_match, order=order, seasonal_order=seasonal_order
    )
    model_fit = model.fit(disp=False, maxiter=600, method="nm")
    
    # Predict next value(s)
    result = model_fit.predict(1, len(test_match), exog=[test_match])
    return float(result[0])


def support_vector_regressor(x_train: list, x_test: list, train_user: list) -> float:
    """
    Third method: Support Vector Regressor (SVR)
    
    Similar to SVM but optimized for regression tasks. Uses a kernel function to
    map inputs to a higher-dimensional space and find the optimal regression function.
    
    Args:
        x_train: List of feature vectors (date and event counts) for training
        x_test: List containing the feature vector for prediction
        train_user: List of target user counts for training
        
    Returns:
        Predicted user count as float
        
    >>> support_vector_regressor([[5,2],[1,5],[6,2]], [[3,2]], [2,1,4])
    1.634932078116079
    """
    # Initialize SVR with RBF kernel
    regressor = SVR(kernel="rbf", C=1, gamma=0.1, epsilon=0.1)
    
    # Train the model
    regressor.fit(x_train, train_user)
    
    # Make prediction
    y_pred = regressor.predict(x_test)
    return float(y_pred[0])


def interquartile_range_checker(train_user: list) -> float:
    """
    Optional method: Interquartile Range (IQR) outlier detection
    
    Calculates the lower limit for outlier detection using the IQR method.
    Values below this limit may be considered outliers.
    
    Args:
        train_user: List of user counts
        
    Returns:
        Lower limit threshold as float
        
    >>> interquartile_range_checker([1,2,3,4,5,6,7,8,9,10])
    2.8
    """
    # Create a copy to avoid modifying the input list
    sorted_data = sorted(train_user)
    
    # Calculate quartiles
    q1 = np.percentile(sorted_data, 25)
    q3 = np.percentile(sorted_data, 75)
    
    # Calculate IQR and lower limit
    iqr = q3 - q1
    low_lim = q1 - (iqr * 0.1)
    
    return float(low_lim)


def data_safety_checker(list_vote: list, actual_result: float) -> bool:
    """
    Used to review all the votes (list of predictions) and compare them to the actual result.
    Determines if the actual data is "safe" based on model consensus.
    
    Args:
        list_vote: List of predictions from different models
        actual_result: The actual observed value
        
    Returns:
        Boolean indicating if the data is considered safe
        
    >>> data_safety_checker([2, 3, 4], 5.0)
    False
    """
    safe = 0
    not_safe = 0

    if not isinstance(actual_result, float):
        raise TypeError("Actual result should be float. Value passed is a list")

    for predicted_value in list_vote:
        if predicted_value > actual_result:
            # Bug fix: should increment safe counter, not assign to not_safe + 1
            safe += 1
        elif abs(predicted_value - actual_result) <= 0.1:
            # Close enough to be considered matching
            safe += 1
        else:
            not_safe += 1
            
    # Return True if more predictions consider the data safe than not
    return safe > not_safe


if __name__ == "__main__":
    """
    Main execution flow for data safety checking.
    
    Data columns:
    - total user in a day
    - how much online event held in one day
    - what day is that (sunday-saturday)
    """
    # Load the data
    data_input_df = pd.read_csv("ex_data.csv")

    # Normalize the data to improve model performance
    normalize_df = Normalizer().fit_transform(data_input_df.values)
    
    # Extract feature columns
    total_user = normalize_df[:, 0].tolist()  # User counts
    total_match = normalize_df[:, 1].tolist()  # Event counts
    total_date = normalize_df[:, 2].tolist()   # Day of week
    
    # Split into training and test sets (using last entry as test)
    train_size = len(total_date) - 1
    
    # For SVR (input variables = event count and day of week)
    x = normalize_df[:, [1, 2]].tolist()
    x_train = x[:train_size]
    x_test = x[train_size:]

    # For linear regression & SARIMAX
    train_date = total_date[:train_size]
    train_user = total_user[:train_size]
    train_match = total_match[:train_size]

    test_date = total_date[train_size:]
    test_user = total_user[train_size:]
    test_match = total_match[train_size:]

    # Run multiple prediction models and collect their results
    res_vote = [
        linear_regression_prediction(
            train_date, train_user, train_match, test_date, test_match
        ),
        sarimax_predictor(train_user, train_match, test_match),
        support_vector_regressor(x_train, x_test, train_user),
    ]

    # Check the safety of today's data based on model consensus
    is_safe = data_safety_checker(res_vote, test_user[0])
    not_str = "" if is_safe else "not "
    print(f"Today's data is {not_str}safe.")