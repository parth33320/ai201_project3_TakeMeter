import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

# SECTION 1: Data Loading & Splitting (Shared with Baseline)
def load_and_split_data(filepath='takemeter_dataset.csv'):
    """
    Loads the dataset and performs a deterministic 70/15/15 split.
    Uses random_state=42 and stratifies by label.
    """
    df = pd.read_csv(filepath)

    # Map labels to integers
    label_map = {
        'professional_obs': 0,
        'emotional_reaction': 1,
        'systemic_critique': 2
    }
    df['label_idx'] = df['label'].map(label_map)

    # 70% train, 30% temp (for val and test)
    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=42, stratify=df['label']
    )

    # Split temp into 50% val, 50% test (which is 15% of total each)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df['label']
    )

    return train_df, val_df, test_df, label_map

# SECTION 3: Training
def train_model(train_df, val_df):
    """
    Fine-tunes distilbert-base-uncased.
    """
    model_name = "distilbert-base-uncased"
    tokenizer = DistilBertTokenizerFast.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    train_dataset = Dataset.from_pandas(train_df[['text', 'label_idx']].rename(columns={'label_idx': 'label'}))
    val_dataset = Dataset.from_pandas(val_df[['text', 'label_idx']].rename(columns={'label_idx': 'label'}))

    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_val = val_dataset.map(tokenize_function, batched=True)

    model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=3)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        weight_decay=0.01,
        logging_dir='./logs',
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        acc = accuracy_score(labels, predictions)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        compute_metrics=compute_metrics,
    )

    print("Starting training...")
    trainer.train()

    return trainer, tokenizer

# SECTION 4: Evaluation
def evaluate_model(trainer, test_df, label_map):
    """
    Evaluates the model on the test set and generates reports.
    """
    tokenizer = trainer.tokenizer
    test_dataset = Dataset.from_pandas(test_df[['text', 'label_idx']].rename(columns={'label_idx': 'label'}))

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_test = test_dataset.map(tokenize_function, batched=True)

    predictions = trainer.predict(tokenized_test)
    preds = np.argmax(predictions.predictions, axis=-1)
    labels = predictions.label_ids

    # Classification Report
    target_names = [k for k, v in sorted(label_map.items(), key=lambda item: item[1])]
    report = classification_report(labels, preds, target_names=target_names)
    print("\nClassification Report:\n")
    print(report)

    # Confusion Matrix Markdown Table
    cm = confusion_matrix(labels, preds)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)

    print("\nConfusion Matrix (Markdown):\n")
    markdown_cm = "| | " + " | ".join(target_names) + " |\n"
    markdown_cm += "|---|" + "|".join(["---"] * len(target_names)) + "|\n"
    for i, row in enumerate(cm):
        markdown_cm += f"| **{target_names[i]}** | " + " | ".join(map(str, row)) + " |\n"
    print(markdown_cm)

    return report, markdown_cm

# SECTION 6: Comparison (Stub for Colab Workflow)
def compare_with_baseline(fine_tuned_results, baseline_results_path='evaluation_results.json'):
    """
    Logic to compare fine-tuned performance against baseline results.
    """
    try:
        import json
        with open(baseline_results_path, 'r') as f:
            baseline = json.load(f)

        print("\n=== Performance Comparison ===")
        print(f"Baseline Accuracy: {baseline['metrics']['overall_accuracy']:.4f}")
        # In a real scenario, we'd pull the fine-tuned accuracy from the report or trainer
        print("Comparison complete. Check classification reports for per-class F1 details.")
    except FileNotFoundError:
        print("\nBaseline results not found. Skipping comparison.")

if __name__ == "__main__":
    # Main execution flow for Colab
    train_df, val_df, test_df, label_map = load_and_split_data()

    trainer, tokenizer = train_model(train_df, val_df)

    report, markdown_cm = evaluate_model(trainer, test_df, label_map)

    # Save the model
    trainer.save_model('./fine_tuned_take_meter')
    tokenizer.save_pretrained('./fine_tuned_take_meter')

    compare_with_baseline(report)
