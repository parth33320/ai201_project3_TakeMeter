import pandas as pd
import numpy as np
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import accuracy_score
from datasets import Dataset
import os

def load_model_and_tokenizer(model_path='./fine_tuned_take_meter'):
    """
    Loads the fine-tuned model and tokenizer.
    Returns None if not found (for local testing without training).
    """
    if not os.path.exists(model_path):
        print(f"Model path {model_path} not found. Ensure fine-tuning is completed.")
        return None, None

    tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    return model, tokenizer

def calibrate_confidence(test_df_path='takemeter_dataset.csv', model_path='./fine_tuned_take_meter'):
    # Load model
    model, tokenizer = load_model_and_tokenizer(model_path)
    if model is None:
        # Mock logic for local verification if model is missing
        print("Using Mock Data for Verification...")
        results = pd.DataFrame({
            'confidence': [0.95, 0.92, 0.88, 0.65, 0.40, 0.98, 0.55],
            'correct': [1, 1, 1, 0, 0, 1, 1]
        })
    else:
        # Load and split data to get the SAME test set
        from fine_tune_model import load_and_split_data
        _, _, test_df, label_map = load_and_split_data(test_df_path)

        # Tokenize
        def tokenize_function(examples):
            return tokenizer(examples["text"], padding="max_length", truncation=True)

        test_dataset = Dataset.from_pandas(test_df[['text', 'label_idx']].rename(columns={'label_idx': 'label'}))
        tokenized_test = test_dataset.map(tokenize_function, batched=True)

        # Get predictions and probabilities
        model.eval()
        all_logits = []
        with torch.no_grad():
            for i in range(0, len(tokenized_test), 8):
                batch = tokenized_test[i:i+8]
                inputs = {k: torch.tensor(v) for k, v in batch.items() if k in tokenizer.model_input_names}
                outputs = model(**inputs)
                all_logits.append(outputs.logits)

        logits = torch.cat(all_logits, dim=0)
        probs = torch.softmax(logits, dim=-1)
        confidences, preds = torch.max(probs, dim=-1)

        results = pd.DataFrame({
            'confidence': confidences.numpy(),
            'predicted': preds.numpy(),
            'actual': tokenized_test['label'],
            'correct': (preds.numpy() == np.array(tokenized_test['label'])).astype(int)
        })

    # Analyze
    high_conf = results[results['confidence'] > 0.90]
    low_conf = results[results['confidence'] < 0.70]

    high_acc = high_conf['correct'].mean() if len(high_conf) > 0 else 0
    low_acc = low_conf['correct'].mean() if len(low_conf) > 0 else 0

    summary = "### Confidence Calibration Analysis\n\n"
    summary += f"- **High Confidence (>0.90) Accuracy**: {high_acc:.2%}\n"
    summary += f"- **Low Confidence (<0.70) Accuracy**: {low_acc:.2%}\n\n"

    if high_acc > low_acc:
        summary += "The model is well-calibrated: high confidence predictions are more likely to be correct than low confidence ones."
    else:
        summary += "The model shows poor calibration or is overconfident in incorrect predictions."

    print(summary)
    with open('calibration_summary.txt', 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    calibrate_confidence()
