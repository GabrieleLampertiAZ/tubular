"""
This module contains transformers that deal with imputation of missing values.
"""

import pandas as pd
import numpy as np

from tubular.base import BaseTransformer


class BaseImputer(BaseTransformer):
    """Base imputer class containing standard transform method that will use pd.Series.fillna with the
    values in the impute_values_ attribute.

    Other imputers in this module should inherit from this class.
    """

    def transform(self, X):
        """Impute missing values with median values calculated from fit method.

        Parameters
        ----------
        X : pd.DataFrame
            Data to impute.

        Returns
        -------
        X : pd.DataFrame
            Transformed input X with nulls imputed with the median value for the specified columns.

        """

        self.check_is_fitted(["impute_values_"])

        X = super().transform(X)

        for c in self.columns:

            X[c] = X[c].fillna(self.impute_values_[c])

        return X


class ArbitraryImputer(BaseImputer):
    """Transformer to impute null values with an arbitrary pre-defined value.

    Parameters
    ----------
    impute_value : int or float or str
        Value to impute nulls with.

    columns : None or str or list, default = None
        Columns to impute, if the default of None is supplied all columns in X are used
        when the transform method is called.

    **kwargs
        Arbitrary keyword arguments passed onto BaseTransformer.init method.

    Attributes
    ----------
    impute_value : int or float or str
        Value to impute nulls with.

    """

    def __init__(self, impute_value, columns, **kwargs):

        if columns is None:

            raise ValueError("columns must be specified in init for ArbitraryImputer")

        super().__init__(columns=columns, **kwargs)

        if (
            not isinstance(impute_value, int)
            and not isinstance(impute_value, float)
            and not isinstance(impute_value, str)
        ):

            raise ValueError(
                "impute_value should be a single value (int, float or str)"
            )

        self.impute_values_ = {}
        self.impute_value = impute_value

    def transform(self, X):
        """Impute missing values with the supplied impute_value.

        If columns is None all columns in X will be imputed.

        Parameters
        ----------
        X : pd.DataFrame
            Data containing columns to impute.

        Returns
        -------
        X : pd.DataFrame
            Transformed input X with nulls imputed with the specified impute_value, for the specified columns.

        """

        self.check_is_fitted(["impute_value"])
        self.columns_check(X)

        for c in self.columns:

            # for categorical dtypes have to set new category for the impute values first
            if "category" in X[c].dtype.name:

                if self.impute_value not in X[c].cat.categories:

                    X[c].cat.add_categories(self.impute_value, inplace=True)

            self.impute_values_[c] = self.impute_value

        X = super().transform(X)

        return X


class MedianImputer(BaseImputer):
    """Transformer to impute missing values with the median of the supplied columns.

    Parameters
    ----------
    columns : None or str or list, default = None
        Columns to impute, if the default of None is supplied all columns in X are used
        when the transform method is called.

    **kwargs
        Arbitrary keyword arguments passed onto BaseTransformer.init method.

    Attributes
    ----------
    impute_values_ : dict
        Created during fit method. Dictionary of float / int (median) values of columns
        in the columns attribute. Keys of impute_values_ give the column names.

    """

    def __init__(self, columns=None, **kwargs):

        super().__init__(columns=columns, **kwargs)

    def fit(self, X, y=None):
        """Calculate median values to impute with from X.

        Parameters
        ----------
        X : pd.DataFrame
            Data to "learn" the median values from.

        y : None or pd.DataFrame or pd.Series, default = None
            Not required.

        """

        super().fit(X, y)

        self.impute_values_ = {}

        for c in self.columns:

            self.impute_values_[c] = X[c].median()

        return self


class MeanImputer(BaseImputer):
    """Transformer to impute missing values with the mean of the supplied columns.

    Parameters
    ----------
    columns : None or str or list, default = None
        Columns to impute, if the default of None is supplied all columns in X are used
        when the transform method is called.

    **kwargs
        Arbitrary keyword arguments passed onto BaseTransformer.init method.

    Attributes
    ----------
    impute_values_ : dict
        Created during fit method. Dictionary of float / int (mean) values of columns
        in the columns attribute. Keys of impute_values_ give the column names.

    """

    def __init__(self, columns=None, **kwargs):

        super().__init__(columns=columns, **kwargs)

    def fit(self, X, y=None):
        """Calculate mean values to impute with from X.

        Parameters
        ----------
        X : pd.DataFrame
            Data to "learn" the mean values from.

        y : None or pd.DataFrame or pd.Series, default = None
            Not required.

        """

        super().fit(X, y)

        self.impute_values_ = {}

        for c in self.columns:

            self.impute_values_[c] = X[c].mean()

        return self


class ModeImputer(BaseImputer):
    """Transformer to impute missing values with the mode of the supplied columns.

    Parameters
    ----------
    columns : None or str or list, default = None
        Columns to impute, if the default of None is supplied all columns in X are used
        when the transform method is called.

    **kwargs
        Arbitrary keyword arguments passed onto BaseTransformer.init method.

    Attributes
    ----------
    impute_values_ : dict
        Created during fit method. Dictionary of float / int (mode) values of columns
        in the columns attribute. Keys of impute_values_ give the column names.

    """

    def __init__(self, columns=None, **kwargs):

        super().__init__(columns=columns, **kwargs)

    def fit(self, X, y=None):
        """Calculate mode values to impute with from X.

        Parameters
        ----------
        X : pd.DataFrame
            Data to "learn" the mode values from.

        y : None or pd.DataFrame or pd.Series, default = None
            Not required.

        """

        super().fit(X, y)

        self.impute_values_ = {}

        for c in self.columns:

            self.impute_values_[c] = X[c].mode()[0]

        return self


class NearestMeanResponseImputer(BaseImputer):
    """Class to impute missing values with; the value for which the average response is closest
    to the average response for the unknown levels.

    If no nulls are present in the column to impute then there is the option to use the median
    instead, in which case the transformer acts the same as the MedianImputer.

    Parameters
    ----------
    response_column : str
        Response column used to determine the value to impute with. The average response for
        each level of every column is calculated. The level which has the closest average response
        to the average response of the unknown levels is selected as the imputation value.
    columns : None or str or list, default = None
        Columns to impute, if the default of None is supplied all columns in X are used
        when the transform method is called.
    use_median_if_no_nulls : bool, default = False
        If there are no nulls in a column on which the model is fitted, should the median of the column be learned instead?
        If use_median_if_no_nulls = False and there are no nulls in the column to impute an error will be raised.
    """

    def __init__(
        self, response_column, use_median_if_no_nulls=False, columns=None, **kwds
    ):

        if not type(response_column) is str:

            raise TypeError("response_column must be a str")

        if not type(use_median_if_no_nulls) is bool:

            raise TypeError("use_median_if_no_nulls must be a bool")

        self.response_column = response_column
        self.use_median_if_no_nulls = use_median_if_no_nulls

        super().__init__(columns=columns, **kwds)

    def fit(self, X, y=None):
        """Calculate mean or median values to impute with.

        Parameters
        ----------
        X : pd.DataFrame
            Data to fit the transformer on.
        y : None or pd.DataFrame or pd.Series, default = None
            Not required.

        """

        super().fit(X, y)

        if not pd.api.types.is_numeric_dtype(X[self.response_column]):

            raise ValueError("dtypes in response_column must be numeric.")

        if X[self.response_column].isnull().sum() > 0:

            raise ValueError(
                f"Response column ({self.response_column}) has null values."
            )

        self.impute_values_ = {}

        for c in self.columns:

            c_nulls = X[c].isnull()

            if c_nulls.sum() == 0:

                if self.use_median_if_no_nulls:

                    self.impute_values_[c] = X[c].median()

                else:

                    raise ValueError(
                        f"Column {c} has no missing values, cannot use this transformer."
                    )

            else:

                mean_response_by_levels = pd.DataFrame(
                    X.loc[~c_nulls].groupby(c)[self.response_column].mean()
                ).reset_index()

                mean_response_nulls = X.loc[c_nulls, self.response_column].mean()

                mean_response_by_levels["abs_diff_response"] = np.abs(
                    mean_response_by_levels[self.response_column] - mean_response_nulls
                )

                # take first value having the minimum difference in terms of average resposne
                self.impute_values_[c] = mean_response_by_levels.loc[
                    mean_response_by_levels["abs_diff_response"]
                    == mean_response_by_levels["abs_diff_response"].min(),
                    c,
                ].values[0]

        return self


class NullIndicator(BaseTransformer):
    """Class to create a binary indicator column for null values.

    Parameters
    ----------
    columns : None or str or list, default = None
        Columns to produce indicator columns for, if the default of None is supplied all columns in X are used
        when the transform method is called.

    """

    def __init__(self, columns=None, **kwds):

        super().__init__(columns=columns, **kwds)

    def transform(self, X):
        """Create new columns indicating the position of null values for each variable in self.columns.

        Parameters
        ----------
        X : pd.DataFrame
            Data to add indicators to.

        """

        X = super().transform(X)

        for c in self.columns:

            X[f"{c}_nulls"] = X[c].isnull().astype(int)

        return X
