import pandas as pd
import numpy as np
import json
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

# Attempt to import groq, handle if not in local environment
try:
    from groq import Groq
except ImportError:
    # This is expected in local env if not installed, but will be installed in Colab
    pass

# SECTION 1: Data Loading & Splitting
def load_and_split_data(filepath='takemeter_dataset.csv'):
    """
    Loads the dataset and performs a deterministic 70/15/15 split.
    """
    df = pd.read_csv(filepath)

    # 70% train, 30% temp (for val and test)
    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=42, stratify=df['label']
    )

    # Split temp into 50% val, 50% test (which is 15% of total each)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df['label']
    )

    return train_df, val_df, test_df

# SECTION 2: Baseline Classification (Zero-Shot)
class GroqClassifier:
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        if api_key is None:
            try:
                from google.colab import userdata
                self.api_key = userdata.get('GROQ_API_KEY')
            except (ImportError, ModuleNotFoundError):
                # For local testing if key is provided via env
                self.api_key = os.environ.get('GROQ_API_KEY')
        else:
            self.api_key = api_key

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in Colab Secrets or as an environment variable.")

        self.client = Groq(api_key=self.api_key)
        self.model = model

    def get_zero_shot_prompt(self, text):
        definitions = {
            "professional_obs": "Assigned to text providing specific, empirical metrics of classroom or workplace performance. This includes grade-level assessments (e.g., 6th graders at 2nd-grade levels), specific skill deficits (analog clocks, alphabetizing, math facts), or direct reports of workplace output quality.",
            "emotional_reaction": "Assigned to text emphasizing the speaker's internal state, personal distress, or visceral response to the crisis. This includes expressions of heartbreak, shock, venting about job difficulty, crying, feelings of doom, or anecdotal descriptions of 'zombie-like' behavior.",
            "systemic_critique": "Assigned to text attributing the crisis to external institutional, cultural, or socio-economic forces. This includes mentions of 'No Child Left Behind,' iPad parenting, corporate influence on curriculum, property-tax funding, and shifts in administrative policy (e.g., the '50% rule')."
        }

        examples = (
            "Example 1: 'High school students using fingers to add and unable to do multiplication or division at age 17.' -> professional_obs\n"
            "Example 2: 'Canadian teacher feels like a complete failure after trying to help students stop surrendering to challenges.' -> emotional_reaction\n"
            "Example 3: 'Parents in Sweden failing kids by providing social media and phones over books.' -> systemic_critique\n"
        )

        prompt = f"""Classify the following Reddit comment into one of these three categories: professional_obs, emotional_reaction, or systemic_critique.

Definitions:
- professional_obs: {definitions['professional_obs']}
- emotional_reaction: {definitions['emotional_reaction']}
- systemic_critique: {definitions['systemic_critique']}

{examples}

Comment: "{text}"

Output ONLY the label name (professional_obs, emotional_reaction, or systemic_critique) without any preamble, explanation, or punctuation."""
        return prompt

    def classify(self, text, retries=3):
        prompt = self.get_zero_shot_prompt(text)

        for i in range(retries + 1):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    temperature=0.0, # Deterministic for baseline
                )
                label = chat_completion.choices[0].message.content.strip().lower()
                # Simple validation of label
                valid_labels = ['professional_obs', 'emotional_reaction', 'systemic_critique']
                for valid in valid_labels:
                    if valid in label:
                        return valid
                return "unknown"
            except Exception as e:
                if i < retries:
                    wait_time = 2 ** i # Exponential backoff
                    print(f"Error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {retries} retries for text: {text[:50]}...")
                    return "error"

# SECTION 5: Evaluation & Export
def evaluate_baseline(test_df, classifier):
    print(f"Classifying {len(test_df)} test examples...")
    predictions = []

    for idx, row in test_df.iterrows():
        pred = classifier.classify(row['text'])
        predictions.append(pred)
        # Avoid hitting rate limits too hard even with backoff
        time.sleep(0.5)

    test_df['predicted_label'] = predictions

    # Filter out errors/unknowns for metric calculation if any
    valid_mask = test_df['predicted_label'].isin(['professional_obs', 'emotional_reaction', 'systemic_critique'])
    eval_df = test_df[valid_mask]

    y_true = eval_df['label']
    y_pred = eval_df['predicted_label']

    accuracy = accuracy_score(y_true, y_pred)
    f1_per_class = f1_score(y_true, y_pred, average=None, labels=['professional_obs', 'emotional_reaction', 'systemic_critique'])
    report = classification_report(y_true, y_pred, output_dict=True)

    metrics = {
        "overall_accuracy": accuracy,
        "per_class_f1": {
            "professional_obs": f1_per_class[0],
            "emotional_reaction": f1_per_class[1],
            "systemic_critique": f1_per_class[2]
        },
        "full_report": report
    }

    # Export results
    results = {
        "metrics": metrics,
        "predictions": test_df[['user', 'text', 'label', 'predicted_label']].to_dict(orient='records')
    }

    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("\nBaseline Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 professional_obs: {metrics['per_class_f1']['professional_obs']:.4f}")
    print(f"F1 emotional_reaction: {metrics['per_class_f1']['emotional_reaction']:.4f}")
    print(f"F1 systemic_critique: {metrics['per_class_f1']['systemic_critique']:.4f}")

    return results

if __name__ == "__main__":
    # This block is for running the pipeline
    # In Colab, you would install dependencies first:
    # !pip install groq pandas scikit-learn

    try:
        train, val, test = load_and_split_data()
        print(f"Split complete: Train={len(train)}, Val={len(val)}, Test={len(test)}")

        # Initialize classifier (will try to use Colab Secrets)
        # For local execution, ensure GROQ_API_KEY is in environment
        clf = GroqClassifier()

        results = evaluate_baseline(test, clf)
        print("\nEvaluation results saved to evaluation_results.json")
    except Exception as e:
        print(f"An error occurred: {e}")
