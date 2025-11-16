import csv
import random
import sys
import os
import json

# Add parent directory to path to import feature_mapper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.feature_mapper import ALL_ABRAMS_FEATURES, ABRAMS_TO_SCANIA

# Load failure patterns from analysis
PATTERNS_FILE = 'data/analysis/failure_patterns.json'
with open(PATTERNS_FILE, 'r') as f:
    FAILURE_PATTERNS = json.load(f)

def sample_from_distribution(scania_code, risk_tier, noise_factor=0.1):
    """
    Sample a value from the actual Scania distribution for the given risk tier.
    
    Args:
        scania_code: Scania feature code (e.g., '158_9')
        risk_tier: 'high', 'medium', or 'low'
        noise_factor: Amount of random noise to add (0.0-0.2)
    
    Returns:
        Float value sampled from appropriate distribution
    """
    pattern = FAILURE_PATTERNS[scania_code]
    
    if risk_tier == 'high':
        # Sample from failed vehicle distribution (p50 to p95 range for variety)
        dist = pattern['failed']
        min_val = dist['p50']
        max_val = dist['p95']
    elif risk_tier == 'medium':
        # Sample from overlap zone between failed and healthy
        failed_dist = pattern['failed']
        healthy_dist = pattern['healthy']
        # Use p25 of failed to p75 of healthy
        min_val = min(failed_dist['p25'], healthy_dist['p50'])
        max_val = max(failed_dist['p75'], healthy_dist['p75'])
    else:  # 'low'
        # Sample from healthy vehicle distribution (p25 to p75 for typical values)
        dist = pattern['healthy']
        min_val = dist['p25']
        max_val = dist['p75']
    
    # Generate base value
    base_value = random.uniform(min_val, max_val)
    
    # Add some noise for variety
    noise = random.uniform(-noise_factor, noise_factor) * base_value
    final_value = max(0, base_value + noise)
    
    return round(final_value, 1)

def determine_risk_tier(tank_id, brigade_seed):
    """
    Determine risk tier for this tank based on deterministic distribution.
    
    Returns:
        'high': 10-12% of tanks - Multiple elevated risk factors
        'medium': 20-25% of tanks - Some concerning metrics
        'low': 65-70% of tanks - Normal operation
    """
    random.seed(brigade_seed * 1000 + tank_id)
    roll = random.random()
    
    if roll < 0.11:  # 11% high risk
        return 'high'
    elif roll < 0.34:  # 23% medium risk (0.11 + 0.23)
        return 'medium'
    else:  # 66% low risk
        return 'low'

def generate_tank_row(tank_id, variation_seed=0, brigade_seed=0):
    """
    Generate a single tank data row using REAL failure patterns from Scania data.
    Samples from actual failed/healthy distributions based on risk tier.
    """
    # Determine risk tier for this tank
    risk_tier = determine_risk_tier(tank_id, brigade_seed)
    
    # Set seed for consistency
    random.seed(variation_seed)
    
    # Generate row by sampling from real distributions
    row = {'TANK_ID': f'TANK{tank_id:03d}'}
    
    # Generate each feature by sampling from appropriate distribution
    for abrams_name in ALL_ABRAMS_FEATURES:
        scania_code = ABRAMS_TO_SCANIA[abrams_name]
        value = sample_from_distribution(scania_code, risk_tier, noise_factor=0.15)
        row[abrams_name] = value
    
    return row, risk_tier

def generate_brigade_data(output_file, tank_count, brigade_seed=0):
    """Generate a complete brigade CSV file with realistic risk distribution."""
    # Headers match ALL_ABRAMS_FEATURES plus TANK_ID
    headers = ['TANK_ID'] + ALL_ABRAMS_FEATURES
    
    rows = []
    risk_counts = {'high': 0, 'medium': 0, 'low': 0}
    
    for i in range(1, tank_count + 1):
        # Use different seed for each tank to get variation
        seed = brigade_seed * 1000 + i
        row, risk_tier = generate_tank_row(i, seed, brigade_seed)
        rows.append(row)
        risk_counts[risk_tier] += 1
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated {tank_count} tanks:")
    print(f"  🔴 High Risk: {risk_counts['high']} ({risk_counts['high']/tank_count*100:.1f}%)")
    print(f"  🟡 Medium Risk: {risk_counts['medium']} ({risk_counts['medium']/tank_count*100:.1f}%)")
    print(f"  🟢 Low Risk: {risk_counts['low']} ({risk_counts['low']/tank_count*100:.1f}%)")
    
    return tank_count, risk_counts

if __name__ == '__main__':
    print("=" * 80)
    print("Generating Tank Data with REAL SCANIA FAILURE PATTERNS")
    print("=" * 80)
    print(f"\n✓ Using {len(ALL_ABRAMS_FEATURES)} features from feature_mapper.py")
    print(f"✓ Loaded failure patterns from: {PATTERNS_FILE}")
    print("\n📊 Risk Profile Distribution:")
    print("  • High Risk (10-12%): Sample from FAILED vehicle distributions (p50-p95)")
    print("  • Medium Risk (20-25%): Sample from overlap zone (failed p25 - healthy p75)")
    print("  • Low Risk (65-70%): Sample from HEALTHY vehicle distributions (p25-p75)")
    print("\n" + "=" * 80 + "\n")
    
    print("1ABCT 'Ironhorse' Brigade (full MTOE - recently reset from Europe):")
    count1, risks1 = generate_brigade_data('data/examples/1ABCT_1CD_Ironhorse_tanks.csv', 87, brigade_seed=1)
    
    print("\n2ABCT 'BlackJack' Brigade (mid-modernization to SEPv3):")
    count2, risks2 = generate_brigade_data('data/examples/2ABCT_1CD_BlackJack_tanks.csv', 83, brigade_seed=2)
    
    print("\n3ABCT 'Greywolf' Brigade (active training cycle):")
    count3, risks3 = generate_brigade_data('data/examples/3ABCT_1CD_Greywolf_tanks.csv', 85, brigade_seed=3)
    
    # Calculate totals
    total_tanks = count1 + count2 + count3
    total_high = risks1['high'] + risks2['high'] + risks3['high']
    total_medium = risks1['medium'] + risks2['medium'] + risks3['medium']
    total_low = risks1['low'] + risks2['low'] + risks3['low']
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY:")
    print("=" * 80)
    print(f"Total Tanks Generated: {total_tanks}")
    print(f"\n🔴 High Risk Tanks: {total_high} ({total_high/total_tanks*100:.1f}%)")
    print(f"🟡 Medium Risk Tanks: {total_medium} ({total_medium/total_tanks*100:.1f}%)")
    print(f"🟢 Low Risk Tanks: {total_low} ({total_low/total_tanks*100:.1f}%)")
    print("\n💡 These tanks use REAL failure signatures from Scania training data!")
    print("   The model should now recognize high-risk patterns and predict varied risks")
    print("   Features match the 20 optimal features from feature_mapper.py")
    print("=" * 80)
