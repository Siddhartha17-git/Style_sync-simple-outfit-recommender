import pandas as pd
import os
import json

class OutfitDataset:
    def __init__(self):
        self.dataset_path = 'outfit_dataset.csv'
        self.images_dir = 'outfit_images'
        self.create_directories()
        
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def create_sample_dataset(self):
        """Create a sample dataset with realistic outfit combinations"""
        outfits = [
            # Summer Casual
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#FFE4C4',
                'body_type': 'slim',
                'occasion': 'casual',
                'hair_type': 'straight',
                'style': 'classic',
                'description': 'Light floral sundress with beige sandals and a straw hat'
            },
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#8D5524',
                'body_type': 'athletic',
                'occasion': 'casual',
                'hair_type': 'curly',
                'style': 'bohemian',
                'description': 'Loose white cotton blouse with high-waisted denim shorts and gladiator sandals'
            },
            # Winter Formal
            {
                'weather': 'cold',
                'gender': 'male',
                'skin_tone': '#C68642',
                'body_type': 'athletic',
                'occasion': 'formal',
                'hair_type': 'short',
                'style': 'classic',
                'description': 'Navy wool suit with light blue shirt, burgundy tie, and oxford shoes'
            },
            {
                'weather': 'cold',
                'gender': 'female',
                'skin_tone': '#FFE4C4',
                'body_type': 'plus-size',
                'occasion': 'formal',
                'hair_type': 'wavy',
                'style': 'classic',
                'description': 'Black A-line midi dress with structured blazer and pearl accessories'
            },
            # Party Outfits
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#8D5524',
                'body_type': 'average',
                'occasion': 'party',
                'hair_type': 'curly',
                'style': 'streetwear',
                'description': 'Metallic crop top with high-waisted leather pants and chunky boots'
            },
            {
                'weather': 'cold',
                'gender': 'male',
                'skin_tone': '#FFE4C4',
                'body_type': 'slim',
                'occasion': 'party',
                'hair_type': 'wavy',
                'style': 'streetwear',
                'description': 'Black turtleneck with leather jacket, ripped jeans, and chelsea boots'
            },
            # Rainy Day
            {
                'weather': 'rainy',
                'gender': 'female',
                'skin_tone': '#C68642',
                'body_type': 'athletic',
                'occasion': 'casual',
                'hair_type': 'straight',
                'style': 'streetwear',
                'description': 'Oversized hoodie with leggings, waterproof boots, and crossbody bag'
            },
            {
                'weather': 'rainy',
                'gender': 'male',
                'skin_tone': '#8D5524',
                'body_type': 'plus-size',
                'occasion': 'casual',
                'hair_type': 'short',
                'style': 'classic',
                'description': 'Navy raincoat with khaki pants, waterproof boots, and umbrella'
            },
            # Summer Formal
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#FFE4C4',
                'body_type': 'slim',
                'occasion': 'formal',
                'hair_type': 'straight',
                'style': 'classic',
                'description': 'Pastel linen blazer with matching pants, silk camisole, and nude heels'
            },
            {
                'weather': 'sunny',
                'gender': 'male',
                'skin_tone': '#C68642',
                'body_type': 'athletic',
                'occasion': 'formal',
                'hair_type': 'short',
                'style': 'classic',
                'description': 'Light grey linen suit with white shirt, no tie, and brown loafers'
            },
            # Streetwear
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#8D5524',
                'body_type': 'athletic',
                'occasion': 'casual',
                'hair_type': 'straight',
                'style': 'streetwear',
                'description': 'Cropped vintage tee with cargo pants, chunky sneakers, and bucket hat'
            },
            {
                'weather': 'cold',
                'gender': 'male',
                'skin_tone': '#FFE4C4',
                'body_type': 'slim',
                'occasion': 'casual',
                'hair_type': 'short',
                'style': 'streetwear',
                'description': 'Oversized graphic hoodie with wide-leg pants and limited edition sneakers'
            },
            # Bohemian
            {
                'weather': 'sunny',
                'gender': 'female',
                'skin_tone': '#C68642',
                'body_type': 'plus-size',
                'occasion': 'casual',
                'hair_type': 'wavy',
                'style': 'bohemian',
                'description': 'Flowing maxi dress with embroidery, layered necklaces, and leather sandals'
            },
            {
                'weather': 'sunny',
                'gender': 'male',
                'skin_tone': '#8D5524',
                'body_type': 'average',
                'occasion': 'casual',
                'hair_type': 'long',
                'style': 'bohemian',
                'description': 'Loose linen shirt with printed pants, leather sandals, and beaded accessories'
            },
            # Winter Casual
            {
                'weather': 'cold',
                'gender': 'female',
                'skin_tone': '#FFE4C4',
                'body_type': 'athletic',
                'occasion': 'casual',
                'hair_type': 'straight',
                'style': 'classic',
                'description': 'Cashmere sweater with high-waisted jeans, ankle boots, and wool coat'
            },
            {
                'weather': 'cold',
                'gender': 'male',
                'skin_tone': '#C68642',
                'body_type': 'plus-size',
                'occasion': 'casual',
                'hair_type': 'short',
                'style': 'classic',
                'description': 'Quarter-zip sweater with chinos, desert boots, and puffer jacket'
            }
        ]
        
        # Create DataFrame
        data = {
            'outfit_id': [],
            'image_path': [],
            'weather': [],
            'gender': [],
            'skin_tone': [],
            'body_type': [],
            'occasion': [],
            'hair_type': [],
            'style': [],
            'description': []
        }
        
        # Add outfits to dataset
        for i, outfit in enumerate(outfits):
            outfit_id = f'outfit_{i+1}'
            data['outfit_id'].append(outfit_id)
            data['image_path'].append(f'{self.images_dir}/{outfit_id}.jpg')
            for key, value in outfit.items():
                data[key].append(value)
        
        return pd.DataFrame(data)
    
    def save_dataset(self, df):
        """Save the dataset to CSV"""
        df.to_csv(self.dataset_path, index=False)
        print(f"Dataset saved to {self.dataset_path}")
    
    def load_dataset(self):
        """Load the dataset from CSV"""
        if os.path.exists(self.dataset_path):
            return pd.read_csv(self.dataset_path)
        return None
    
    def add_outfit(self, outfit_data, image_path=None):
        """Add a new outfit to the dataset"""
        df = self.load_dataset() or self.create_sample_dataset()
        
        # Generate new outfit ID
        new_id = f'outfit_{len(df) + 1}'
        
        # Add new outfit
        new_row = {
            'outfit_id': new_id,
            'image_path': image_path or f'{self.images_dir}/{new_id}.jpg',
            **outfit_data
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_dataset(df)
        return new_id

def main():
    # Create and save sample dataset
    dataset = OutfitDataset()
    df = dataset.create_sample_dataset()
    dataset.save_dataset(df)
    print("Sample dataset created successfully!")

if __name__ == "__main__":
    main() 