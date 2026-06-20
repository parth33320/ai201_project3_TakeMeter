import pandas as pd
from sklearn.metrics import cohen_kappa_score

def calculate_reliability():
    # 1. Load Claude's independent labels from Excel
    excel_path = 'Claude Project 3 TakeMeter_ Annotated Dataset Report (2).xlsx'
    claude_df = pd.read_excel(excel_path, sheet_name='human verified input data')

    # Standardize columns for Claude's data
    # Columns are likely: 'User Handle', 'Text', 'Text Label' (based on previous head() check)
    claude_df = claude_df[['User Handle', 'Text Label']].copy()
    claude_df.columns = ['user', 'claude_label']
    claude_df['user'] = claude_df['user'].astype(str).str.strip()
    claude_df['claude_label'] = claude_df['claude_label'].astype(str).str.strip().str.lower()

    # 2. Load Human-validated labels from CSV
    csv_path = 'takemeter_dataset.csv'
    human_df = pd.read_csv(csv_path)
    human_df = human_df[['user', 'label']].copy()
    human_df.columns = ['user', 'human_label']
    human_df['user'] = human_df['user'].astype(str).str.strip()
    human_df['human_label'] = human_df['human_label'].astype(str).str.strip().str.lower()

    # 3. Merge datasets on user and text to ensure exact match
    # First, need to get text from both sources
    claude_full = pd.read_excel(excel_path, sheet_name='human verified input data')
    claude_full.columns = ['user', 'text', 'claude_label']
    claude_full['user'] = claude_full['user'].astype(str).str.strip()
    claude_full['text'] = claude_full['text'].astype(str).str.strip()
    claude_full['claude_label'] = claude_full['claude_label'].astype(str).str.strip().str.lower()

    human_full = pd.read_csv(csv_path)
    human_full['user'] = human_full['user'].astype(str).str.strip()
    human_full['text'] = human_full['text'].astype(str).str.strip()
    human_full['label'] = human_full['label'].astype(str).str.strip().str.lower()

    merged_df = pd.merge(claude_full, human_full, on=['user', 'text'], how='inner')

    if len(merged_df) == 0:
        print("Error: No matching users found between Excel and CSV.")
        return

    # 4. Calculate Cohen's Kappa
    kappa = cohen_kappa_score(merged_df['claude_label'], merged_df['label'])

    print(f"Inter-Annotator Reliability Results:")
    print(f"Total overlapping samples: {len(merged_df)}")
    print(f"Cohen's Kappa: {kappa:.4f}")

    # 5. Analyze Disagreements
    disagreements = merged_df[merged_df['claude_label'] != merged_df['label']]

    summary = f"### Inter-Annotator Reliability (Cohen's Kappa)\n\n"
    summary += f"- **Kappa Score**: {kappa:.4f}\n"
    summary += f"- **Total Samples Compared**: {len(merged_df)}\n"
    summary += f"- **Total Disagreements**: {len(disagreements)}\n\n"

    if len(disagreements) > 0:
        summary += "#### Disagreement Analysis\n\n"
        summary += "| User | Claude Label | Human Label |\n"
        summary += "| --- | --- | --- |\n"
        for _, row in disagreements.iterrows():
            summary += f"| {row['user']} | {row['claude_label']} | {row['label']} |\n"

        summary += "\n**Analysis**: "
        if any('alexbgoode84' in user for user in disagreements['user'].values):
            summary += "The disagreement for `u/alexbgoode84` (4-year-old in high-end daycare) illustrates a subtle edge case. Claude identified the 'high-end daycare' as a systemic/institutional factor (`systemic_critique`), whereas the human label prioritized the 'outperforming peers' observation (`professional_obs`)."
        else:
            summary += "Disagreements often occur where systemic critiques are phrased as performance observations or vice-versa."
    else:
        summary += "\n**Analysis**: Perfect agreement between the automated baseline logic and human verification on this subset."

    print("\nREADME Summary Fragment:")
    print(summary)

    # Save results for later use by README generator
    with open('reliability_summary.txt', 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    calculate_reliability()
