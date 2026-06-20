# TakeMeter: Demo Video Narration Script (3-5 Minutes)

## 1. Introduction (0:00 - 0:45)
"Welcome to the TakeMeter project walkthrough. Our goal is to provide educational policy-makers with a 'Discourse Quality Dashboard' by analyzing Reddit conversations about the Gen Alpha literacy crisis.

We focused on the 'Teachers of Reddit' community to capture ground-truth classroom experiences. To filter this data effectively, we defined three distinct labels: **Professional Observations** for empirical metrics, **Emotional Reactions** for internal venting, and **Systemic Critiques** for institutional and cultural factors. Our aim is to separate actionable classroom data from general emotional noise."

## 2. Taxonomy & Reliability (0:45 - 1:30)
[Visual: Scrolling through README Inter-Annotator Reliability section]
"A core pillar of this project is taxonomic precision. We achieved an Inter-Annotator Reliability score—measured via Cohen's Kappa—of **0.95**. This indicates that our definitions are incredibly robust. Out of 30 independent samples, there was only one minor disagreement where a 'high-end daycare' was flagged as systemic rather than professional.

[Visual: Scrolling through Confidence Calibration]
Our model is also well-calibrated. Predictions made with high confidence—over 90%—show 100% accuracy in our tests, ensuring that policy-makers can trust the signals the dashboard provides."

## 3. Performance & The Fine-Tuning Journey (1:30 - 2:15)
[Visual: Scrolling through Fine-Tuning Results / Confusion Matrix]
"Now, let’s talk about performance. We transitioned from a large baseline model—Llama-3.3—to a smaller, fine-tuned DistilBERT model. While the baseline excelled at general knowledge with 96% accuracy, our fine-tuned model reached **70% overall accuracy**.

The model successfully met our success threshold of **F1 > 0.75** for the critical 'Professional Observations' class. However, we identified a systematic pattern: the model is over-sensitive to 'institutional' keywords like 'college' or 'school', which led to some misclassifications in the other categories. With only 200 examples, learning these subtle boundaries was a significant challenge for the smaller architecture."

## 4. Live Classification: Correct Prediction (2:15 - 3:00)
[Visual: Inputting u/unlovelyladybartleby]
"Let’s see it in action. First, we have a post from u/unlovelyladybartleby: *'Online fan theories that are simply the basic, explicit plot points of the movie.'*

The model correctly classifies this as a **Professional Observation** with high confidence. This is a perfect example of a 'tactical' observation—it highlights a specific cognitive deficit in identifying plot points, providing clear, empirical data for the dashboard."

## 5. Live Classification: Further Examples (3:00 - 3:45)
[Visual: Inputting u/deleteurkneecaps and u/Afraid-Dealer-5172]
"Next, u/deleteurkneecaps notes a 9-year-old struggling with kindergarten books—another clear **Professional Observation**.

In contrast, u/Afraid-Dealer-5172 describes people as 'brain dead zombies.' The model identifies this as an **Emotional Reaction**. While the sentiment is strong, it provides no specific skill metrics, so it’s correctly filtered as venting."

## 6. The Systematic Error (3:45 - 4:30)
[Visual: Inputting u/igotshadowbaned]
"Finally, we look at the 'baseline error' case from u/igotshadowbaned: *'College programs adding two levels of remedial math previously unnecessary for entry.'*

Even after fine-tuning, the model labels this as a **Systemic Critique**. Why? Because it is still over-weighting the keyword 'College programs.' While 'remedial math levels' is a specific skill metric that *should* make this a professional observation, the institutional context currently dominates the model's logic. This highlights the need for more diverse training data to break these keyword-based associations."

## 7. Conclusion (4:30 - 5:00)
"In summary, TakeMeter successfully created a reliable taxonomy and a model that captures professional observations at a high level of quality. While DistilBERT didn't match the baseline's accuracy, it provided a lightweight, interpretable solution that meets our core success threshold. This project proves that even with limited data, we can start to extract high-quality, actionable insights from the complex landscape of community discourse. Thank you."
