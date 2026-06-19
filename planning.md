# Project Planning: TakeMeter - Gen Alpha Literacy Crisis Analysis

## 1. Community Choice
We have selected the Reddit thread **"Teachers of Reddit: Is the 'Gen Alpha can't read (write, or do math ext)' crisis real? If so how bad is it?"** ([Link](https://www.reddit.com/r/AskReddit/comments/1u5ku71/teachers_of_reddit_is_the_gen_alpha_cant_read/)) as our primary data source.

This community is a good fit for this project because it provides high-volume, varied discourse. The thread captures a wide spectrum of perspectives, ranging from rigorous pedagogical data provided by educators to emotional venting and anecdotal observations from parents and concerned community members. This diversity ensures our model is exposed to varied linguistic patterns and sentiment levels.

## 2. Labels
We have defined three distinct labels to categorize the discourse in this thread. Definitions and examples are pulled directly from our Annotated Dataset Report:

*   **`professional_obs`**: Assigned to text providing specific, empirical metrics of classroom or workplace performance, such as grade-level assessments or specific skill deficits (e.g., inability to read an analog clock).
    *   *Example 1*: "Im a dance teacher and a big thing I notice is that kids and teens dont know how to read analog clocks. They also dont know their left from their right" — **lightsyouonfire**
    *   *Example 2*: "I’m a nanny and I’ve worked with 9 year olds who are in school full time yet can barely get through a book meant for a kindergarten reading level." — **deleteurkneecaps**
*   **`emotional_reaction`**: Assigned to text emphasizing the speaker's internal state, personal distress, or visceral response, including expressions of heartbreak, venting about job difficulty, or descriptions of "zombie-like" behavior.
    *   *Example 1*: "As someone who was a kid who loved reading growing up, it’s sad." — **deleteurkneecaps**
    *   *Example 2*: "Where people in the future are brain dead zombies who want for nothing, but don't know anything or how to do anything but be food for the Morlocks" — **Afraid-Dealer-5172**
*   **`systemic_critique`**: Assigned to text attributing the crisis to external institutional, cultural, or socio-economic forces, such as "No Child Left Behind," iPad parenting, or corporate influence on curriculum.
    *   *Example 1*: "It was the iPad, almost entirely. Easily the most destructive experiment inflicted on children since thalidomide." — **oe_kintaro**
    *   *Example 2*: "Blame ipads or social media all you want. Its the parents responsibility to get their children ready." — **MutedEar1412**

## 3. Hard Edge Case
A significant challenge in our annotation process was addressing the boundary between detailed anecdotes from non-professionals (such as parents or spouses) and tactical data traditionally expected from teachers.

**Decision Rule**: We decided to label observations from parents/spouses as `professional_obs` if they provide specific, verifiable behavioral data or skill metrics, prioritizing the tactical nature of the observation over the vocation of the taker [History alignment]. This ensures that high-quality data is captured regardless of the speaker's self-identified role.

## 4. Data Collection Plan
Our dataset consists of 200+ labeled examples collected from the provided Reddit documents. This task is completed; data was extracted from the source documents and manually reviewed by humans (validated via a "human verified input data sheet"). During the collection process, we ensured a balanced distribution across our three labels, with approximately 33% representation for each class to prevent model bias toward any single discourse type.

## 5. Evaluation Metrics
We are using **per-class F1 scores** and a **Confusion Matrix** to evaluate our model's performance, rather than relying solely on overall accuracy.

Community discourse often contains nuances and imbalances that accuracy alone cannot capture. Per-class F1 scores allow us to see if the model is disproportionately failing on one specific category (e.g., confusing emotional venting with systemic critique), while the Confusion Matrix provides a visual map of these misclassifications, highlighting exactly where the model's decision boundaries are blurry.

## 6. Definition of Success
Our concrete performance threshold for success is an **F1 score > 0.75** [History alignment, 1734]. Meeting this threshold will indicate that the model has successfully learned the nuances of the community discourse and can reliably distinguish between professional observations, emotional reactions, and systemic critiques.

## AI Tool Plan
Our project utilized a two-part workflow for AI integration:
1.  **Annotation Assistance**: An LLM was used for initial annotation assistance to pre-label the 200 examples. These pre-labels were subsequently reviewed and validated by a human to ensure strict adherence to our label taxonomy.
2.  **Failure Pattern Analysis**: We intend to use AI tools to perform failure pattern analysis on the model's wrong predictions. This involves identifying if the model struggles with specific linguistic features, such as short, sarcastic posts or posts that blend multiple categories, which will inform our final evaluation report.
