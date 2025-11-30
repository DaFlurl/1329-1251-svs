#!/usr/bin/env python3
"""
Debug extraction process
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.excel_processor import ExcelProcessor

def debug_extraction():
    """Debug the extraction process"""
    processor = ExcelProcessor()
    
    # Process the Excel file
    data = processor.process_excel_file('test_gaming_data.xlsx')
    
    logger.info("Processed data structure:")
    logger.info(f"Keys: {list(data.keys())}")
    logger.info(f"Data records: {len(data.get('data', []))}")
    
    # Extract player data
    players = processor.extract_player_data(data)
    
    logger.info(f"/nExtracted {len(players)} players:")
    for i, player in enumerate(players):
        logger.info(f"Player {i+1}: {player}")
    
    # Debug first record extraction
    if data.get('data'):
        first_record = data['data'][0]
        logger.info(f"/nFirst record keys: {list(first_record.keys())}")
        logger.info(f"First record: {first_record}")
        
        # Test _get_value_by_key method
        name = processor._get_value_by_key(first_record, ['Spieler', 'name', 'player', 'spieler', 'Name'])
        logger.info(f"Extracted name: '{name}'")

if __name__ == "__main__":
    debug_extraction()