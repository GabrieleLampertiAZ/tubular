import pytest
import pandas as pd
import numpy as np
import tubular.testing.test_data as d
import tubular.testing.helpers as h

import tubular
from tubular.imputers import NearestMeanResponseImputer


class TestInit(object):
    """Tests for NearestMeanResponseImputer.__init__"""

    def test_arguments(self):
        """Test that init has expected arguments."""

        h.test_function_arguments(
            func=NearestMeanResponseImputer.__init__,
            expected_arguments=[
                "self",
                "response_column",
                "use_median_if_no_nulls",
                "columns",
            ],
            expected_default_values=(False, None),
        )

    def test_class_methods(self):
        """Test that NearestMeanResponseImputer has fit and transform methods."""

        x = NearestMeanResponseImputer(
            response_column="c", use_median_if_no_nulls=False, columns=None
        )

        h.test_object_method(obj=x, expected_method="fit", msg="fit")

        h.test_object_method(obj=x, expected_method="transform", msg="transform")

    def test_inheritance(self):
        """Test that NearestMeanResponseImputer inherits from BaseImputer."""

        x = NearestMeanResponseImputer(
            response_column="c", use_median_if_no_nulls=False, columns=None
        )

        h.assert_inheritance(x, tubular.imputers.BaseImputer)

    def test_super_init_called(self, mocker):
        """Test that init calls BaseTransformer.init."""

        expected_call_args = {
            0: {"args": (), "kwargs": {"columns": None, "verbose": True, "copy": True}}
        }

        with h.assert_function_call(
            mocker, tubular.base.BaseTransformer, "__init__", expected_call_args
        ):

            NearestMeanResponseImputer(
                response_column="c",
                use_median_if_no_nulls=False,
                columns=None,
                verbose=True,
                copy=True,
            )

    def test_response_column_not_str_error(self):
        """Test that an exception is raised if response_column is not str"""

        with pytest.raises(TypeError, match="response_column must be a str"):

            NearestMeanResponseImputer(response_column=0)

    def test_use_median_if_no_nulls_not_bool_error(self):
        """Test that an exception is raised if use_median_if_no_nulls is not bool"""

        with pytest.raises(TypeError, match="use_median_if_no_nulls must be a bool"):

            NearestMeanResponseImputer(
                response_column="a", use_median_if_no_nulls="abc"
            )

    def test_values_passed_in_init_set_to_attribute(self):
        """Test that the values passed in init are saved in an attribute of the same name."""

        x = NearestMeanResponseImputer(
            response_column="c", columns="a", use_median_if_no_nulls=True
        )

        h.test_object_attributes(
            obj=x,
            expected_attributes={
                "response_column": "c",
                "use_median_if_no_nulls": True,
            },
            msg="Attributes for NearestMeanResponseImputer set in init",
        )


class TestFit(object):
    """Tests for NearestMeanResponseImputer.fit"""

    def test_arguments(self):
        """Test that fit has expected arguments."""

        h.test_function_arguments(
            func=NearestMeanResponseImputer.fit,
            expected_arguments=["self", "X", "y"],
            expected_default_values=(None,),
        )

    def test_super_fit_called(self, mocker):
        """Test that fit calls BaseTransformer.fit."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        expected_call_args = {
            0: {
                "args": (d.create_NearestMeanResponseImputer_test_df(), None),
                "kwargs": {},
            }
        }

        with h.assert_function_call(
            mocker, tubular.base.BaseTransformer, "fit", expected_call_args
        ):

            x.fit(df)

    def test_non_numeric_response_column_error(self):
        """Test an error is raised if response_column is non-numeric"""

        df = pd.DataFrame(
            {"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1], "c": ["a", "b", "c", "d", "e"]}
        )

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        with pytest.raises(
            ValueError, match="dtypes in response_column must be numeric."
        ):

            x.fit(df)

    def test_null_values_in_response_error(self):
        """Test an error is raised if the response column contains null entries."""

        df = d.create_df_3()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        with pytest.raises(ValueError, match=r"Response column \(c\) has null values."):

            x.fit(df)

    def test_use_median_if_no_nulls_false_and_columns_with_no_nulls_error(self):
        """Test an error is raised if a non-response column contains no nulls and use_median_if_no_nulls is false."""

        df = pd.DataFrame(
            {"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1], "c": [3, 2, 1, 4, 5]}
        )

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        with pytest.raises(
            ValueError,
            match="Column a has no missing values, cannot use this transformer.",
        ):

            x.fit(df)

    def test_fit_returns_self(self):
        """Test fit returns self?"""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x_fitted = x.fit(df)

        assert (
            x_fitted is x
        ), "Returned value from NearestMeanResponseImputer.fit not as expected."

    def test_fit_not_changing_data(self):
        """Test fit does not change X."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x.fit(df)

        h.assert_equal_dispatch(
            expected=d.create_NearestMeanResponseImputer_test_df(),
            actual=df,
            msg="Check X not changing during fit",
        )

    def test_learnt_values(self):
        """Test that the nearest response values learnt during fit are expected."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x.fit(df)

        h.test_object_attributes(
            obj=x,
            expected_attributes={
                "impute_values_": {
                    "a": np.float64(2),
                    "b": np.float64(3),
                }
            },
            msg="impute_values_ attribute",
        )

    def test_learnt_values2(self):
        """Test that the nearest mean response values learnt during fit are expected - when values to be learnt include medians"""

        df = pd.DataFrame(
            {
                "a": [1, 1, 2, 3, 3, 5],
                "b": [np.nan, np.nan, 1, 3, 3, 4],
                "c": [2, 3, 2, 1, 4, 1],
            }
        )

        x = NearestMeanResponseImputer(
            response_column="c", columns=["a", "b"], use_median_if_no_nulls=True
        )

        x.fit(df)

        h.test_object_attributes(
            obj=x,
            expected_attributes={
                "impute_values_": {
                    "a": np.float64(2.5),
                    "b": np.float64(3),
                }
            },
            msg="impute_values_ attribute",
        )


class TestTransform(object):
    """Tests for NearestMeanResponseImputer.transform"""

    def expected_df_1():
        """Expected output for ."""

        df = pd.DataFrame(
            {"a": [1, 1, 2, 3, 3, 2], "b": [3, 3, 1, 3, 3, 4], "c": [2, 3, 2, 1, 4, 1]}
        )

        df[["a", "b"]] = df[["a", "b"]].astype("float64")

        return df

    def expected_df_2():
        """Expected output for ."""

        df = pd.DataFrame(
            {
                "a": [1, 1, 2, 3, 3, 2],
                "b": [np.nan, np.nan, 1, 3, 3, 4],
                "c": [2, 3, 2, 1, 4, 1],
            }
        )

        df["a"] = df["a"].astype("float64")

        return df

    def expected_df_3():
        """Expected output for ."""

        df = pd.DataFrame({"a": [2, 3, 4, 1, 4, 2]})

        df["a"] = df["a"].astype("float64")

        return df

    def test_arguments(self):
        """Test that transform has expected arguments."""

        h.test_function_arguments(
            func=NearestMeanResponseImputer.transform, expected_arguments=["self", "X"]
        )

    def test_check_is_fitted_called(self, mocker):
        """Test that BaseTransformer check_is_fitted called."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x.fit(df)

        expected_call_args = {0: {"args": (["impute_values_"],), "kwargs": {}}}

        with h.assert_function_call(
            mocker, tubular.base.BaseTransformer, "check_is_fitted", expected_call_args
        ):

            x.transform(df)

    def test_super_transform_called(self, mocker):
        """Test that BaseTransformer.transform called."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x.fit(df)

        expected_call_args = {
            0: {"args": (d.create_NearestMeanResponseImputer_test_df(),), "kwargs": {}}
        }

        with h.assert_function_call(
            mocker, tubular.base.BaseTransformer, "transform", expected_call_args
        ):

            x.transform(df)

    @pytest.mark.parametrize(
        "df, expected",
        h.row_by_row_params(
            d.create_NearestMeanResponseImputer_test_df(), expected_df_1()
        )
        + h.index_preserved_params(
            d.create_NearestMeanResponseImputer_test_df(), expected_df_1()
        ),
    )
    def test_nulls_imputed_correctly(self, df, expected):
        """Test missing values are filled with the correct values."""

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        # set the impute values dict directly rather than fitting x on df so test works with helpers
        x.impute_values_ = {"a": 2.0, "b": 3.0}

        df_transformed = x.transform(df)

        h.assert_equal_dispatch(
            expected=expected,
            actual=df_transformed,
            msg="Check nulls filled correctly in transform",
        )

    @pytest.mark.parametrize(
        "df, expected",
        h.row_by_row_params(
            d.create_NearestMeanResponseImputer_test_df(), expected_df_2()
        )
        + h.index_preserved_params(
            d.create_NearestMeanResponseImputer_test_df(), expected_df_2()
        ),
    )
    def test_nulls_imputed_correctly2(self, df, expected):
        """Test missing values are filled with the correct values - and unrelated columns are unchanged."""

        x = NearestMeanResponseImputer(response_column="c", columns="a")

        # set the impute values dict directly rather than fitting x on df so test works with helpers
        x.impute_values_ = {"a": 2.0}

        df_transformed = x.transform(df)

        h.assert_equal_dispatch(
            expected=expected,
            actual=df_transformed,
            msg="Check nulls filled correctly in transform",
        )

    @pytest.mark.parametrize(
        "df, expected",
        h.row_by_row_params(
            pd.DataFrame({"a": [np.nan, 3, 4, 1, 4, np.nan]}), expected_df_3()
        )
        + h.index_preserved_params(
            pd.DataFrame({"a": [np.nan, 3, 4, 1, 4, np.nan]}), expected_df_3()
        ),
    )
    def test_nulls_imputed_correctly4(self, df, expected):
        """Test missing values are filled with the correct values - with median value from separate dataframe."""

        x = NearestMeanResponseImputer(
            response_column="c", columns="a", use_median_if_no_nulls=True
        )

        # set the impute values dict directly rather than fitting x on df so test works with helpers
        x.impute_values_ = {"a": 2.0}

        df_transformed = x.transform(df)

        h.assert_equal_dispatch(
            expected=expected,
            actual=df_transformed,
            msg="Check nulls filled correctly in transform",
        )

    def test_learnt_values_not_modified(self):
        """Test that the impute_values_ from fit are not changed in transform."""

        df = d.create_NearestMeanResponseImputer_test_df()

        x = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x.fit(df)

        x2 = NearestMeanResponseImputer(response_column="c", columns=["a", "b"])

        x2.fit(df)

        x2.transform(df)

        h.assert_equal_dispatch(
            expected=x.impute_values_,
            actual=x2.impute_values_,
            msg="Impute values not changed in transform",
        )
