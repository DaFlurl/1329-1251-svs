#!/usr/bin/env python3
import pandas as pd
import json
import os

def extract_scoreboard_data():
    """Extract player data from Excel and create proper scoreboard JSON"""
    
    excel_file = "Sunday, 16 November 2025 1329+1251 v 3144363.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"ERROR: Excel file not found: {excel_file}")
        return
    
    print(f"Reading Excel file: {excel_file}")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        print(f"Excel columns found: {list(df.columns)}")
        print(f"Total rows: {len(df)}")
        
        # Look for player data columns
        player_data = []
        
        # Try to identify the correct columns
        name_col = None
        score_col = None
        alliance_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'name' in col_lower or 'spieler' in col_lower or 'player' in col_lower:
                name_col = col
            elif 'score' in col_lower or 'punkte' in col_lower or 'total' in col_lower:
                score_col = col
            elif 'alliance' in col_lower or 'allianz' in col_lower or 'team' in col_lower:
                alliance_col = col
        
        print(f"Identified columns - Name: {name_col}, Score: {score_col}, Alliance: {alliance_col}")
        
        # If no clear columns found, try to use first few columns
        if name_col is None and len(df.columns) >= 1:
            name_col = df.columns[0]
        if score_col is None and len(df.columns) >= 2:
            score_col = df.columns[1]
        if alliance_col is None and len(df.columns) >= 3:
            alliance_col = df.columns[2]
        
        # Process each row
        for idx, row in df.iterrows():
            if pd.isna(row[name_col]) or str(row[name_col]).strip() == '':
                continue
                
            player_name = str(row[name_col]).strip()
            if player_name.lower() in ['name', 'player', 'spieler', '', 'nan']:
                continue
            
            try:
                score = float(row[score_col]) if score_col and pd.notna(row[score_col]) else 0.0
            except (ValueError, TypeError):
                score = 0.0
                
            alliance = str(row[alliance_col]).strip() if alliance_col and pd.notna(row[alliance_col]) else "Unaligned"
            if alliance.lower() in ['nan', '', 'none']:
                alliance = "Unaligned"
            
            player_data.append({
                "name": player_name,
                "score": score,
                "alliance": alliance,
                "rank": 0  # Will be calculated
            })
        
        # Sort by score (descending) and assign ranks
        player_data.sort(key=lambda x: x["score"], reverse=True)
        
        for idx, player in enumerate(player_data):
            player["rank"] = idx + 1
        
        # Create the final JSON structure
        scoreboard_data = {
            "last_updated": pd.Timestamp.now().isoformat(),
            "total_players": len(player_data),
            "players": player_data
        }
        
        # Write to JSON file
        with open("scoreboard-data.json", "w", encoding="utf-8") as f:
            json.dump(scoreboard_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created scoreboard with {len(player_data)} players")
        print(f"Top 5 players:")
        for i, player in enumerate(player_data[:5]):
            print(f"   {i+1}. {player['name']}: {player['score']} ({player['alliance']})")
        
        return True
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return False

if __name__ == "__main__":
    extract_scoreboard_data()