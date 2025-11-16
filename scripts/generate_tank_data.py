import csv
import random

def generate_fuzzy_value(base_min, base_max):
    """Generate a realistic fuzzy value within a range."""
    return round(random.uniform(base_min, base_max), 1)

def generate_tank_row(tank_id, variation_seed=0):
    """Generate a single tank data row with realistic fuzzy values."""
    random.seed(variation_seed)
    
    # Base ranges for each feature (mimicking realistic military vehicle usage)
    row = {
        'TANK_ID': f'TANK{tank_id:03d}',
        'TRACK_MILES': generate_fuzzy_value(700, 2200),
        'ENGINE_HOURS': generate_fuzzy_value(550, 1750),
        'MAIN_GUN_ROUNDS': generate_fuzzy_value(400, 1200),
        'FIRE_CONTROL_SYSTEM_FAULTS': generate_fuzzy_value(500, 1450),
        'ELECTRICAL_SYSTEM_FAULTS': generate_fuzzy_value(200, 850),
        'POWERTRAIN_FAILURES': generate_fuzzy_value(130, 550),
        'HYDRAULIC_SYSTEM_FAILURES': generate_fuzzy_value(350, 1200),
        'ROADWHEEL_ARM_WEAR': generate_fuzzy_value(550, 1600),
        'TRACK_LINK_WEAR': generate_fuzzy_value(250, 750),
        'TORSION_BAR_DEGRADATION': generate_fuzzy_value(170, 680),
        'EXTREME_COLD_MILES': generate_fuzzy_value(100, 430),
        'EXTREME_HEAT_MILES': generate_fuzzy_value(80, 380),
        'TERRAIN_SEVERE_MILES': generate_fuzzy_value(60, 310),
        'UP_ARMOR_LOAD_HOURS': generate_fuzzy_value(40, 200),
        'COMBAT_OPERATIONS_COUNT': generate_fuzzy_value(60, 220),
        'IDLE_HOURS': generate_fuzzy_value(300, 850),
        'TURRET_SLEW_CYCLES': generate_fuzzy_value(210, 600),
        'FAULT_CODES_ACCUMULATED': generate_fuzzy_value(180, 490),
        'TRANSMISSION_TEMP_EVENTS': generate_fuzzy_value(24, 96),
        'FUEL_EFFICIENCY_DEGRADATION': generate_fuzzy_value(35, 145)
    }
    
    return row

def generate_brigade_data(output_file, tank_count, brigade_seed=0):
    """Generate a complete brigade CSV file."""
    headers = [
        'TANK_ID', 'TRACK_MILES', 'ENGINE_HOURS', 'MAIN_GUN_ROUNDS',
        'FIRE_CONTROL_SYSTEM_FAULTS', 'ELECTRICAL_SYSTEM_FAULTS',
        'POWERTRAIN_FAILURES', 'HYDRAULIC_SYSTEM_FAILURES',
        'ROADWHEEL_ARM_WEAR', 'TRACK_LINK_WEAR', 'TORSION_BAR_DEGRADATION',
        'EXTREME_COLD_MILES', 'EXTREME_HEAT_MILES', 'TERRAIN_SEVERE_MILES',
        'UP_ARMOR_LOAD_HOURS', 'COMBAT_OPERATIONS_COUNT', 'IDLE_HOURS',
        'TURRET_SLEW_CYCLES', 'FAULT_CODES_ACCUMULATED',
        'TRANSMISSION_TEMP_EVENTS', 'FUEL_EFFICIENCY_DEGRADATION'
    ]
    
    rows = []
    for i in range(1, tank_count + 1):
        # Use different seed for each tank to get variation
        seed = brigade_seed * 1000 + i
        row = generate_tank_row(i, seed)
        rows.append(row)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated {tank_count} tanks")
    return tank_count

if __name__ == '__main__':
    print("=" * 60)
    print("Generating Tank Data with Fuzzy Variations")
    print("=" * 60)
    
    print("\n1ABCT 'Ironhorse' Brigade (full MTOE - recently reset from Europe):")
    count1 = generate_brigade_data('data/examples/1ABCT_1CD_Ironhorse_tanks.csv', 87, brigade_seed=1)
    
    print("\n2ABCT 'BlackJack' Brigade (mid-modernization to SEPv3):")
    count2 = generate_brigade_data('data/examples/2ABCT_1CD_BlackJack_tanks.csv', 83, brigade_seed=2)
    
    print("\n3ABCT 'Greywolf' Brigade (active training cycle):")
    count3 = generate_brigade_data('data/examples/3ABCT_1CD_Greywolf_tanks.csv', 85, brigade_seed=3)
    
    print("\n" + "=" * 60)
    print("FINAL TANK COUNTS:")
    print("=" * 60)
    print(f"1ABCT 'Ironhorse': {count1} tanks")
    print(f"2ABCT 'BlackJack': {count2} tanks")
    print(f"3ABCT 'Greywolf': {count3} tanks")
    print(f"TOTAL: {count1 + count2 + count3} tanks")
    print("=" * 60)
