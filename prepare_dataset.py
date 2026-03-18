import pandas as pd
import os
from sklearn.model_selection import train_test_split
from outfit_recommender import OutfitRecommender
from dataset import OutfitDataset

def create_sample_dataset():
    """
    Create a sample dataset for testing the recommender system
    In production, replace this with your actual dataset
    """
    data = {
        'weather': ['sunny', 'rainy', 'cold'] * 100,
        'gender': ['male', 'female'] * 150,
        'skin_tone': ['#FFE4C4', '#8D5524', '#C68642'] * 100,  # Sample skin tones
        'body_type': ['slim', 'average', 'athletic', 'plus-size'] * 75,
        'occasion': ['casual', 'formal', 'party'] * 100,
        'hair_type': ['straight', 'wavy', 'curly'] * 100,
        'style': ['classic', 'bohemian', 'streetwear', 'minimalist'] * 75,
        'outfit_id': [f'outfit_{i}' for i in range(300)]  # 300 sample outfits
    }
    
    return pd.DataFrame(data)

def main():
    # Create or load dataset
    dataset = OutfitDataset()
    df = dataset.load_dataset()
    if df is None:
        df = dataset.create_sample_dataset()
    
    # Initialize the recommender
    recommender = OutfitRecommender()
    
    # Create a DataFrame with the input features in the correct order
    input_data = df[recommender.feature_order].copy()
    
    # Get the target variable
    y = df['outfit_id']
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        input_data, y, test_size=0.2, random_state=42
    )
    
    # Train the recommender
    recommender.train(X_train, y_train)
    
    # Save the trained model
    recommender.save_model('outfit_recommender_model.joblib')
    
    # Test the recommender with ordered input
    test_input = {
        'weather': 'sunny',
        'gender': 'female',
        'skin_tone': '#FFE4C4',
        'body_type': 'average',
        'occasion': 'casual',
        'hair_type': 'straight',
        'style': 'classic'
    }
    
    recommendations = recommender.recommend(test_input)
    print("Sample recommendations:", recommendations)

if __name__ == "__main__":
    main()