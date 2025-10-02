import pandas as pd

# Read the existing Excel file
try:
    df = pd.read_excel('Saudi_Youth_Leagues.xlsx')
    
    # Remove existing U-21 teams
    df = df[df['League'] != 'Saudi Elite League U-21']
    
    # List of updated U-21 teams
    u21_teams = [
        'Al-Hilal', 'Al-Nassr', 'Al-Ittihad', 'Al-Ahli', 'Al-Shabab',
        'Al-Fateh', 'Al-Taawoun', 'Al-Wehda', 'Al-Khaleej', 'Al-Raed',
        'Al-Tai', 'Abha', 'Al-Fayha', 'Al-Riyadh', 'Al-Okhdood',
        'Al-Hazem', 'Al-Akhdoud', 'Al-Adalah', 'Al-Jabalain', 'Al-Qadsiah'
    ]
    
    # Create a new DataFrame with the updated teams
    u21_df = pd.DataFrame({
        'Team Name': u21_teams,
        'League': 'Saudi Elite League U-21'
    })
    
    # Combine with original data
    updated_df = pd.concat([df, u21_df], ignore_index=True)
    
    # Save back to Excel
    updated_df.to_excel('Saudi_Youth_Leagues.xlsx', index=False)
    print("Successfully updated Saudi Elite League U-21 teams!")
    print("\nUpdated U-21 Teams:")
    print(u21_df.to_string(index=False))
    
except Exception as e:
    print(f"An error occurred: {e}")
