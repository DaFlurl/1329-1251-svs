#!/usr/bin/env python3
"""
Convert Excel JSON data to dashboard format
"""
import json
import os

def convert_to_dashboard_format(input_file, output_file):
    """Convert Excel JSON to dashboard format"""
    
    # Load the Excel JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract data from Excel format
    positive_data = []
    negative_data = []
    combined_data = []
    
    # Process positive data
    if 'Positive' in data and 'sheets' in data['Positive']:
        positive_sheet = data['Positive']['sheets']['Positive']
        if 'data' in positive_sheet:
            for player in positive_sheet['data']:
                if player.get('Name') and player.get('Position'):
                    positive_data.append({
                        'position': int(player.get('Position', 0)),
                        'name': player.get('Name', ''),
                        'score': float(player.get('Score', 0)),
                        'alliance': player.get('Alliance', 'None'),
                        'monarchId': str(player.get('Monarch ID', ''))
                    })
    
    # Process negative data
    if 'Negative' in data and 'sheets' in data['Negative']:
        negative_sheet = data['Negative']['sheets']['Negative']
        if 'data' in negative_sheet:
            for player in negative_sheet['data']:
                if player.get('Name') and player.get('Position'):
                    negative_data.append({
                        'position': int(player.get('Position', 0)),
                        'name': player.get('Name', ''),
                        'score': float(player.get('Score', 0)),
                        'alliance': player.get('Alliance', 'None'),
                        'monarchId': str(player.get('Monarch ID', ''))
                    })
    
    # Process combined data
    if 'Combined' in data and 'sheets' in data['Combined']:
        combined_sheet = data['Combined']['sheets']['Combined']
        if 'data' in combined_sheet:
            for player in combined_sheet['data']:
                if player.get('Name') and player.get('Position'):
                    combined_data.append({
                        'position': int(player.get('Position', 0)),
                        'name': player.get('Name', ''),
                        'score': float(player.get('Total Score', 0)),
                        'positive': float(player.get('Positive', 0)),
                        'negative': float(player.get('Negative', 0)),
                        'alliance': player.get('Alliance', 'None'),
                        'monarchId': str(player.get('Monarch ID', ''))
                    })
    
    # Create dashboard format
    dashboard_data = {
        'positive': positive_data,
        'negative': negative_data,
        'combined': combined_data,
        'metadata': {
            'totalPlayers': len(combined_data),
            'totalAlliances': len(set(player['alliance'] for player in combined_data)),
            'lastUpdate': '2025-11-27T12:00:00Z',
            'dataFile': os.path.basename(input_file)
        }
    }
    
    # Save dashboard format
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {input_file} to {output_file}")
    print(f"Players: {len(positive_data)} positive, {len(negative_data)} negative, {len(combined_data)} combined")
    print(f"Alliances: {dashboard_data['metadata']['totalAlliances']}")

if __name__ == "__main__":
    # Convert Monday data
    convert_to_dashboard_format('monday_data.json', 'data/monday_data.json')
    
    # Convert scoreboard data
    convert_to_dashboard_format('scoreboard-data.json', 'data/scoreboard-data.json')