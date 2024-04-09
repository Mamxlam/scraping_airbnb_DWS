import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

class Preprocessor:

    def __init__(self):
        pass

    def miscols_ident(self, df):
        miscols = df.isnull().sum()>0
        miscols = miscols[miscols == True].index.tolist()
        return miscols

    def impute_predictor(self, dataframe, missing_columns, regressor_type="random_forest"):
        # Excluding strings
        dataframe_no_str = dataframe.select_dtypes(exclude=['object'])
        for col in missing_columns:
            print(f"Performing prediction imputation {col} feature which includes {dataframe_no_str[col].isnull().sum()} missing values.")

            # Identify cols to perform naive imputation (eg when starting and 3 cols have NaNs,
            # to predict one you have to temporarily handle the rest)
            rest_columns = missing_columns.copy()
            rest_columns.remove(str(col))

            intermediate_df = dataframe_no_str.copy()
            # Handle train data in case they have NaN in other cols
            intermediate_df[rest_columns] = intermediate_df[rest_columns].fillna(intermediate_df[rest_columns].mean())
            # Separation
            data_complete = intermediate_df[intermediate_df[col].notnull()]

            data_missing = intermediate_df[intermediate_df[col].isnull()]

            X_complete = data_complete.drop(col, axis=1)
            y_complete = data_complete[col]

            # Model Training
            if regressor_type == 'linear':
                model = LinearRegression()
            elif regressor_type == 'random_forest':
                model = RandomForestRegressor()
            else:
                raise ValueError("Unsupported regressor type")

            model.fit(X_complete, y_complete)

            # Prediction and Imputation
            predictions = model.predict(data_missing.drop(col, axis=1))
            dataframe.loc[dataframe[col].isnull(), col] = predictions

        return dataframe
