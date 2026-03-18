import pandas as pd
from outfit_recommender import OutfitRecommender
import joblib

def retrain_model():
    # Load the dataset
    print("Loading dataset...")
    df = pd.read_csv('outfit_dataset.csv')
    
    # Initialize the recommender
    print("Initializing recommender...")
    recommender = OutfitRecommender()
    
    # Prepare features and target
    feature_columns = [
        'weather', 'gender', 'skin_tone', 'body_type',
        'occasion', 'hair_type', 'style'
    ]
    X = df[feature_columns]
    y = df['outfit_id']
    
    # Train the model
    print("Training model...")
    recommender.train(X, y)
    
    # Save the trained model
    print("Saving model...")
    joblib.dump(recommender, 'outfit_recommender_model.joblib')
    print("Model retrained and saved successfully!")

if __name__ == "__main__":
    retrain_model() 