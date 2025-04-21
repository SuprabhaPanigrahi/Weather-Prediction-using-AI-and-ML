import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
import requests
import io
import warnings
warnings.filterwarnings('ignore')

# API Integration for Data Fetching
class WeatherDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
        
    def fetch_historical_data(self, dataset, start_date, end_date, stations=None):
        params = {
            'dataset': dataset,
            'startDate': start_date,
            'endDate': end_date,
            'format': 'csv',
            'units': 'metric',
            'dataTypes': 'PRCP,TMAX,TMIN,TAVG,AWND,WDF2,WDF5,WSF2,WSF5',
            'stations': stations if stations else '',
            'token': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

# Data Preprocessing
class WeatherDataPreprocessor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.imputer = SimpleImputer(strategy='mean')
        
    def preprocess_data(self, df):
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Feature engineering
        df = self.create_features(df)
        
        # Encode categorical variables
        df = self.encode_categorical(df)
        
        # Normalize data
        df = self.normalize_data(df)
        
        return df
    
    def handle_missing_values(self, df):
        # Drop columns with too many missing values
        threshold = len(df) * 0.7
        df = df.dropna(thresh=threshold, axis=1)
        
        # Impute remaining missing values
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = self.imputer.fit_transform(df[numeric_cols])
        
        return df
    
    def create_features(self, df):
        # Convert date to datetime
        if 'Date.Full' in df.columns:
            df['date'] = pd.to_datetime(df['Date.Full'])
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['day_of_month'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Temperature features
        if all(col in df.columns for col in ['Data.Temperature.Max Temp', 'Data.Temperature.Min Temp']):
            df['temp_range'] = df['Data.Temperature.Max Temp'] - df['Data.Temperature.Min Temp']
            df['temp_avg'] = (df['Data.Temperature.Max Temp'] + df['Data.Temperature.Min Temp']) / 2
        
        return df
    
    def encode_categorical(self, df):
        # One-hot encode station and state
        if 'Station.State' in df.columns:
            df = pd.get_dummies(df, columns=['Station.State'], prefix='state')
        if 'Station.City' in df.columns:
            df = pd.get_dummies(df, columns=['Station.City'], prefix='city')
        
        return df
    
    def normalize_data(self, df):
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        return df

# Feature Extraction and Selection
class FeatureEngineer:
    def __init__(self):
        self.selector = None
        self.pca = None
        
    def select_features(self, X, y, k=20):
        self.selector = SelectKBest(score_func=f_regression, k=k)
        X_selected = self.selector.fit_transform(X, y)
        return X_selected
    
    def apply_pca(self, X, n_components=0.95):
        self.pca = PCA(n_components=n_components)
        X_pca = self.pca.fit_transform(X)
        return X_pca
    
    def get_feature_importance(self, X, y):
        if not self.selector:
            self.select_features(X, y)
        return pd.DataFrame({'feature': X.columns, 'importance': self.selector.scores_})\
               .sort_values('importance', ascending=False)

# Precipitation Prediction using simpler models
class PrecipitationPredictor:
    def __init__(self, model_type='random_forest'):
        self.model = self.build_model(model_type)
        
    def build_model(self, model_type):
        if model_type == 'random_forest':
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == 'linear_regression':
            return LinearRegression()
        elif model_type == 'svr':
            return SVR(kernel='rbf')
        else:
            raise ValueError("Unknown model type")
    
    def train_model(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def evaluate_model(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Test MSE: {mse:.4f}")
        print(f"Test MAE: {mae:.4f}")
        print(f"Test R2 Score: {r2:.4f}")
        
        return y_pred
    
    def print_feature_importance(self):
        if hasattr(self.model, 'feature_importances_'):
            print("\nFeature Importances:")
            for feature, importance in zip(X.columns, self.model.feature_importances_):
                print(f"{feature}: {importance:.4f}")

# Main Pipeline
def main():
    # Load data (in this case from CSV, but could use API)
    try:
        df = pd.read_csv('weather.csv')
        print("Data loaded successfully from CSV")
    except:
        print("Could not load data from CSV. Using API instead...")
        api_key = "YOUR_API_KEY"  # Replace with actual API key
        fetcher = WeatherDataFetcher(api_key)
        df = fetcher.fetch_historical_data(
            dataset="daily-summaries",
            start_date="2016-01-01",
            end_date="2016-01-31",
            stations="USW00093814"  # Example station
        )
        if df is None:
            print("Failed to fetch data. Exiting.")
            return
    
    # Initial data inspection
    print("\nData Overview:")
    print(df.head())
    print("\nData Shape:", df.shape)
    print("\nData Info:")
    print(df.info())
    print("\nMissing Values:")
    print(df.isnull().sum().sort_values(ascending=False))
    
    # Preprocessing
    preprocessor = WeatherDataPreprocessor()
    df_processed = preprocessor.preprocess_data(df)
    
    # Prepare features and target
    X = df_processed.drop(['Data.Precipitation', 'Date.Full', 'date'], axis=1, errors='ignore')
    y = df_processed['Data.Precipitation']
    
    # Feature selection
    engineer = FeatureEngineer()
    importance_df = engineer.get_feature_importance(X, y)
    print("\nTop 20 Important Features:")
    print(importance_df.head(20))
    
    X_selected = engineer.select_features(X, y, k=20)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y, test_size=0.2, random_state=42
    )
    
    # Model training and evaluation
    print("\nRandom Forest Model Evaluation:")
    rf_predictor = PrecipitationPredictor('random_forest')
    rf_predictor.train_model(X_train, y_train)
    rf_pred = rf_predictor.evaluate_model(X_test, y_test)
    
    print("\nLinear Regression Model Evaluation:")
    lr_predictor = PrecipitationPredictor('linear_regression')
    lr_predictor.train_model(X_train, y_train)
    lr_pred = lr_predictor.evaluate_model(X_test, y_test)
    
    print("\nSupport Vector Regression Model Evaluation:")
    svr_predictor = PrecipitationPredictor('svr')
    svr_predictor.train_model(X_train, y_train)
    svr_pred = svr_predictor.evaluate_model(X_test, y_test)
    
    # Print first 5 predictions vs actual
    print("\nSample Predictions (First 5 records):")
    results = pd.DataFrame({
        'Actual': y_test[:5],
        'RF Predicted': rf_pred[:5],
        'LR Predicted': lr_pred[:5],
        'SVR Predicted': svr_pred[:5]
    })
    print(results)

if __name__ == "__main__":
    main()