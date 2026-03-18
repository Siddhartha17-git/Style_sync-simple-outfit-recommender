import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

class OutfitRecommender:
    def __init__(self):
        # Increase neighbors for more diverse recommendations
        self.knn = KNeighborsClassifier(
            n_neighbors=5,  # Reduced from 8 to 5 for more precise matches
            weights='distance',
            metric='manhattan',  # Changed from euclidean to manhattan for better categorical feature handling
            p=1
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Define feature order and weights
        self.feature_order = [
            'weather',
            'gender',
            'skin_tone',
            'body_type',
            'occasion',
            'hair_type',
            'style'
        ]
        
        # Adjust feature weights for better matching
        self.feature_weights = {
            'weather': 3.0,    # Increased importance of weather
            'gender': 4.0,     # Increased importance of gender
            'skin_tone': 1.0,  # Reduced importance
            'body_type': 2.5,  # Increased importance
            'occasion': 4.0,   # Increased importance of occasion
            'hair_type': 0.5,  # Further reduced importance
            'style': 3.0      # Increased importance of style
        }
        
        # Initialize label encoders for categorical features
        for feature in self.feature_order:
            self.label_encoders[feature] = LabelEncoder()
    
    def preprocess_input(self, data):
        """
        Preprocess input data with weighted features in consistent order
        """
        if isinstance(data, pd.DataFrame):
            processed_data = data.copy()
        else:
            processed_data = pd.DataFrame([data])
        
        # Create weighted features DataFrame with consistent order
        weighted_data = pd.DataFrame()
        
        # Define default values for missing data
        default_values = {
            'weather': 'sunny',
            'gender': 'female',
            'skin_tone': '#FFE4C4',
            'body_type': 'average',
            'occasion': 'casual',
            'hair_type': 'straight',
            'style': 'classic'
        }
        
        # Fill missing values with defaults
        for feature in self.feature_order:
            if feature not in processed_data.columns or processed_data[feature].isnull().any():
                processed_data[feature] = processed_data.get(feature, pd.Series()).fillna(default_values[feature])
        
        # Process features in the defined order
        for feature in self.feature_order:
            weight = self.feature_weights[feature]
            if feature == 'skin_tone':
                # Convert hex color to RGB values and normalize with weight
                try:
                    weighted_data[f'{feature}_r'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[0:2], 16)) / 255.0 * weight)
                    weighted_data[f'{feature}_g'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[2:4], 16)) / 255.0 * weight)
                    weighted_data[f'{feature}_b'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[4:6], 16)) / 255.0 * weight)
                except (ValueError, AttributeError) as e:
                    # If there's an error parsing the hex color, use a default color
                    weighted_data[f'{feature}_r'] = float(int('FF', 16)) / 255.0 * weight
                    weighted_data[f'{feature}_g'] = float(int('E4', 16)) / 255.0 * weight
                    weighted_data[f'{feature}_b'] = float(int('C4', 16)) / 255.0 * weight
            else:
                # Encode categorical variables and apply weight
                encoded_feature = self.label_encoders[feature].transform(processed_data[feature].astype(str))
                weighted_data[feature] = encoded_feature.astype(float) * weight
        
        # Ensure all values are finite
        weighted_data = weighted_data.fillna(0.0)
        
        # Define the expected column order
        expected_columns = []
        for feature in self.feature_order:
            if feature == 'skin_tone':
                expected_columns.extend([f'{feature}_r', f'{feature}_g', f'{feature}_b'])
            else:
                expected_columns.append(feature)
        
        # Ensure columns are in the correct order
        weighted_data = weighted_data.reindex(columns=expected_columns)
        
        return weighted_data

    def train(self, X, y):
        """
        Train the KNN model with weighted features
        """
        # Ensure X has all required features in correct order
        for feature in self.feature_order:
            if feature not in X.columns:
                raise ValueError(f"Missing required feature: {feature}")
        
        # Fit label encoders first
        for feature in self.feature_order:
            if feature != 'skin_tone':
                self.label_encoders[feature].fit(X[feature].astype(str))
        
        # Preprocess features
        X_processed = self.preprocess_input(X)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_processed)
        
        # Store the feature names and their order
        self.feature_names_ = X_processed.columns.tolist()
        
        # Train the model
        self.knn.fit(X_scaled, y)
        
        # Mark that the model has been fitted
        self.is_fitted = True
        
        return self
    
    def recommend(self, user_input, n_recommendations=4):
        """
        Generate outfit recommendations with improved confidence scores and diversity
        """
        try:
            df = pd.read_csv('outfit_dataset.csv')
            
            # First, filter by gender - this is a strict requirement
            df = df[df['gender'].str.lower() == user_input['gender'].lower()]
            
            if df.empty:
                print(f"No outfits found for gender: {user_input['gender']}")
                return []

            # Add weather-based filtering
            weather = user_input['weather'].lower()
            weather_compatible = {
                'sunny': ['sunny', 'warm', 'hot'],
                'rainy': ['rainy', 'wet', 'drizzle'],
                'cold': ['cold', 'chilly', 'freezing'],
                'snowy': ['snowy', 'cold', 'freezing'],
                'cloudy': ['cloudy', 'overcast', 'partly_sunny']
            }
            
            # Filter outfits based on weather compatibility
            compatible_weather = weather_compatible.get(weather, [weather])
            df = df[df['weather'].str.lower().isin(compatible_weather)]
            
            if df.empty:
                print(f"No outfits found for weather: {weather}")
                return []

            # Convert user input to DataFrame
            input_df = pd.DataFrame([user_input])
            
            # Get features for training from filtered dataset
            X = df[self.feature_order]
            y = df['outfit_id']
            
            # Create a temporary KNN model for this recommendation
            temp_knn = KNeighborsClassifier(
                n_neighbors=min(4, len(df)),
                weights='distance',
                metric='manhattan',  # Changed to manhattan for better categorical handling
                p=1
            )
            
            # Process features
            X_processed = self.preprocess_input(X)
            input_processed = self.preprocess_input(input_df)
            
            # Scale features
            temp_scaler = StandardScaler()
            X_scaled = temp_scaler.fit_transform(X_processed)
            input_scaled = temp_scaler.transform(input_processed)
            
            # Fit and get recommendations
            temp_knn.fit(X_scaled, y)
            distances, indices = temp_knn.kneighbors(input_scaled, n_neighbors=min(n_recommendations, len(df)))
            
            # Get recommendations
            recommendations = df.iloc[indices[0]]['outfit_id'].values
            
            # Calculate confidence scores with weather emphasis
            confidence_scores = 100 * np.exp(-0.5 * distances[0])
            
            # Create recommendation list with detailed matching
            recommendation_list = []
            for outfit_id, confidence in zip(recommendations, confidence_scores):
                outfit_data = df[df['outfit_id'] == outfit_id].iloc[0]
                match_score = 0
                matching_features = []
                
                # Calculate detailed match score and collect matching features
                for feature in self.feature_order:
                    if feature == 'gender':
                        match_score += self.feature_weights[feature]  # Always matches due to filter
                        matching_features.append(feature)
                    elif feature == 'weather':
                        # Give higher weight to exact weather matches
                        if user_input[feature].lower() == outfit_data[feature].lower():
                            match_score += self.feature_weights[feature] * 1.5
                            matching_features.append(feature)
                        elif outfit_data[feature].lower() in compatible_weather:
                            match_score += self.feature_weights[feature]
                    elif feature == 'skin_tone':
                        user_rgb = self._hex_to_rgb(user_input[feature])
                        outfit_rgb = self._hex_to_rgb(outfit_data[feature])
                        similarity = self._color_similarity(user_rgb, outfit_rgb)
                        match_score += self.feature_weights[feature] * similarity
                        if similarity > 0.8:  # 80% similar colors
                            matching_features.append(feature)
                    else:
                        if user_input[feature].lower() == outfit_data[feature].lower():
                            match_score += self.feature_weights[feature]
                            matching_features.append(feature)
                
                # Normalize match score
                total_weight = sum(self.feature_weights.values())
                match_score = (match_score / total_weight) * 100
                
                recommendation_list.append({
                    'outfit_id': outfit_id,
                    'confidence': float(confidence),
                    'match_score': float(match_score),
                    'matching_features': matching_features,
                    'description': outfit_data['description']
                })
            
            # Sort by match score and confidence
            recommendation_list.sort(key=lambda x: (x['match_score'], x['confidence']), reverse=True)
            
            return recommendation_list[:n_recommendations]
            
        except Exception as e:
            print(f"Error in recommendations: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
            
    def _preprocess_with_encoders(self, data, encoders):
        """Helper method to preprocess data with given encoders"""
        if isinstance(data, pd.DataFrame):
            processed_data = data.copy()
        else:
            processed_data = pd.DataFrame([data])
        
        weighted_data = pd.DataFrame()
        
        for feature in self.feature_order:
            weight = self.feature_weights[feature]
            if feature == 'skin_tone':
                try:
                    weighted_data[f'{feature}_r'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[0:2], 16)) / 255.0 * weight)
                    weighted_data[f'{feature}_g'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[2:4], 16)) / 255.0 * weight)
                    weighted_data[f'{feature}_b'] = processed_data[feature].apply(
                        lambda x: float(int(x.lstrip('#')[4:6], 16)) / 255.0 * weight)
                except (ValueError, AttributeError):
                    weighted_data[f'{feature}_r'] = float(int('FF', 16)) / 255.0 * weight
                    weighted_data[f'{feature}_g'] = float(int('E4', 16)) / 255.0 * weight
                    weighted_data[f'{feature}_b'] = float(int('C4', 16)) / 255.0 * weight
            else:
                encoded_feature = encoders[feature].transform(processed_data[feature].astype(str))
                weighted_data[feature] = encoded_feature.astype(float) * weight
        
        expected_columns = []
        for feature in self.feature_order:
            if feature == 'skin_tone':
                expected_columns.extend([f'{feature}_r', f'{feature}_g', f'{feature}_b'])
            else:
                expected_columns.append(feature)
        
        return weighted_data.reindex(columns=expected_columns)
    
    def _calculate_match_score(self, user_input, outfit_id):
        """
        Calculate a detailed match score based on feature importance
        """
        try:
            df = pd.read_csv('outfit_dataset.csv')
            outfit = df[df['outfit_id'] == outfit_id].iloc[0]
            
            score = 0
            max_score = 0
            
            for feature in self.feature_order:
                weight = self.feature_weights[feature]
                max_score += weight
                
                if feature == 'skin_tone':
                    # For skin tone, calculate color similarity
                    user_rgb = self._hex_to_rgb(user_input[feature])
                    outfit_rgb = self._hex_to_rgb(outfit[feature])
                    similarity = self._color_similarity(user_rgb, outfit_rgb)
                    score += weight * similarity
                else:
                    # For other features, exact match check
                    if user_input[feature] == outfit[feature]:
                        score += weight
            
            # Normalize score to 0-100 range
            return (score / max_score) * 100
        except Exception as e:
            print(f"Error calculating match score: {str(e)}")
            return 0
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _color_similarity(self, rgb1, rgb2):
        """Calculate color similarity between two RGB colors"""
        try:
            # Calculate Euclidean distance between colors
            distance = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
            # Convert distance to similarity score (0-1)
            similarity = 1 - (distance / 441.67)  # Max distance is sqrt(255^2 * 3)
            return max(0, min(1, similarity))
        except Exception as e:
            print(f"Error calculating color similarity: {str(e)}")
            return 0
    
    def save_model(self, filepath):
        """Save the model to a file"""
        model_data = {
            'knn': self.knn,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_order': self.feature_order,
            'feature_weights': self.feature_weights,
            'feature_names_': self.feature_names_ if hasattr(self, 'feature_names_') else None,
            'is_fitted': self.is_fitted if hasattr(self, 'is_fitted') else False
        }
        joblib.dump(model_data, filepath)

    def load_model(self, filepath):
        """Load the model from a file"""
        try:
            model_data = joblib.load(filepath)
            if isinstance(model_data, dict):
                self.knn = model_data['knn']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_order = model_data['feature_order']
                self.feature_weights = model_data['feature_weights']
                if 'feature_names_' in model_data:
                    self.feature_names_ = model_data['feature_names_']
                if 'is_fitted' in model_data:
                    self.is_fitted = model_data['is_fitted']
            else:
                # If the loaded data is not a dictionary, it might be the entire recommender
                self.__dict__.update(model_data.__dict__)
            return self
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise