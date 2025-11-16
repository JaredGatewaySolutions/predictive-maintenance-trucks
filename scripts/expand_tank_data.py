import csv
import random

def add_fuzz(value, variance=0.15):
    """Add random fuzziness to a value."""
    return round(value * (1 + random.uniform(-variance, variance)), 1)

def expand_csv(input_file, output_file, target_count):
    """Expand CSV file to target_count rows with fuzzy data."""
    # Read existing data
    with open(input_file, 'r', newline='') as f:
        content = f.read()
        lines = content.strip().split('\n')
        headers = lines[0].split(',')
        existing_rows = []
        
        for line in lines[1:]:
            values = line.split(',')
            row_dict = dict(zip(headers, values))
            existing_rows.append(row_dict)
    
    current_count = len(existing_rows)
    print(f"Current rows: {current_count}, Target: {target_count}")
    
    if current_count >= target_count:
        print(f"Already have {current_count} rows, no expansion needed")
        return current_count
    
    # Calculate statistics for realistic ranges
    stats = {}
    for header in headers[1:]:  # Skip TANK_ID
        values = [float(row[header]) for row in existing_rows]
        stats[header] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
    
    # Generate new rows
    new_rows = []
    for i in range(current_count + 1, target_count + 1):
        new_row = {'TANK_ID': f'TANK{i:03d}'}
        
        # Use existing patterns with random variation
        base_row = random.choice(existing_rows)
        for header in headers[1:]:
            base_value = float(base_row[header])
            # Add random fuzziness (±20%)
            new_value = add_fuzz(base_value, variance=0.20)
            # Ensure it stays within reasonable bounds
            new_value = max(stats[header]['min'] * 0.8, min(stats[header]['max'] * 1.2, new_value))
            new_row[header] = str(new_value)
        
        new_rows.append(new_row)
    
    # Write combined data
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(existing_rows)
        writer.writerows(new_rows)
    
    final_count = current_count + len(new_rows)
    print(f"Added {len(new_rows)} rows. Final count: {final_count}")
    return final_count

if __name__ == '__main__':
    print("=" * 60)
    print("Expanding tank data with fuzzy variations")
    print("=" * 60)
    
    print("\n1ABCT 'Ironhorse' Brigade:")
    count1 = expand_csv('data/examples/1ABCT_1CD_Ironhorse_tanks.csv', 
                        'data/examples/1ABCT_1CD_Ironhorse_tanks.csv', 
                        87)
    
    print("\n2ABCT 'BlackJack' Brigade:")
    count2 = expand_csv('data/examples/2ABCT_1CD_BlackJack_tanks.csv', 
                        'data/examples/2ABCT_1CD_BlackJack_tanks.csv', 
                        83)
    
    print("\n3ABCT 'Greywolf' Brigade:")
    count3 = expand_csv('data/examples/3ABCT_1CD_Greywolf_tanks.csv', 
                        'data/examples/3ABCT_1CD_Greywolf_tanks.csv', 
                        85)
    
    print("\n" + "=" * 60)
    print("FINAL TANK COUNTS:")
    print("=" * 60)
    print(f"1ABCT 'Ironhorse': {count1} tanks")
    print(f"2ABCT 'BlackJack': {count2} tanks")
    print(f"3ABCT 'Greywolf': {count3} tanks")
    print(f"TOTAL: {count1 + count2 + count3} tanks")
    print("=" * 60)
