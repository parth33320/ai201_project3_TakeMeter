# Project Planning: TakeMeter - Gen Alpha Literacy Crisis Analysis

## 1. Community Choice
We have selected the Reddit thread **"Teachers of Reddit: Is the 'Gen Alpha can't read (write, or do math ext)' crisis real? If so how bad is it?"** ([Link](https://www.reddit.com/r/AskReddit/comments/1u5ku71/teachers_of_reddit_is_the_gen_alpha_cant_read/)) as our primary data source.

With 8,401 comments, this high-volume community provides a rich environment for analyzing varied perspectives on the literacy crisis. This specific community is uniquely meaningful for our analysis because the distinction between professional data, emotional reactions, and systemic blaming directly impacts educational policy and classroom management. By classifying these linguistic patterns, we help teachers and school administrators identify whether classroom struggles are isolated pedagogical issues or symptoms of larger institutional and policy failures. This clarity is essential for moving beyond "venting" and toward actionable institutional change.

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

**Specific Example**: Consider a post by **u/beckster**: *"Tbh, my 77 yo husband is like this and it isn't dementia, rather what I like to call 'weaponized incompetence.' With sufficient motivation (e.g. sports, cars) he can YouTube himself into a more informed - and less irritating - state."* This post sits between `professional_obs` and `emotional_reaction`. While it identifies a specific behavioral pattern ("weaponized incompetence" linked to selective motivation), it is delivered with a high degree of personal irritation.

**Decision Rule**: We decided to label observations from non-professionals as `professional_obs` if they provide specific, verifiable behavioral data or skill metrics, prioritizing the tactical nature of the observation over the vocation of the speaker. This ensures that high-quality data is captured regardless of the speaker's self-identified role, provided the observation is empirical rather than purely emotive.

## 4. Data Collection Plan
Our dataset consists of 200+ labeled examples collected from the 8,401 comments in the source Reddit thread. While initial data extraction was manually reviewed to ensure balanced distribution, we have established a clear **Imbalance Mitigation Strategy**: If any label exceeds 70% of the dataset during future scaling, we will perform targeted sampling of the 8,000+ available Reddit comments to specifically hunt for the minority class until a ~33% balance is restored. This ensures the model remains robust across all discourse types and avoids bias toward the most common sentiment (often emotional venting).

## 5. Evaluation Metrics
We are using **per-class F1 scores** and a **Confusion Matrix** to evaluate our model's performance, rather than relying solely on overall accuracy.

Community discourse often contains nuances and imbalances that accuracy alone cannot capture. Per-class F1 scores allow us to see if the model is disproportionately failing on one specific category (e.g., confusing emotional venting with systemic critique), while the Confusion Matrix provides a visual map of these misclassifications, highlighting exactly where the model's decision boundaries are blurry.

## 6. Definition of Success
Our concrete performance threshold for success is an **F1 score > 0.75**. This threshold is necessary for a practical deployment use-case: a **"Discourse Quality Dashboard"** for educational policy-makers.

Policy-makers need to separate actionable classroom performance data from general emotional venting to make informed decisions about curriculum and funding. An F1 score below 0.75 would risk flooding the dashboard with "noise" (emotional reactions) or missing critical "signals" (professional observations), rendering the tool unreliable for institutional planning. Achieving this threshold indicates the model can reliably distinguish these categories for high-stakes decision-making.

## AI Tool Plan
Our project utilizes a two-part workflow for AI integration:
1.  **Annotation Assistance**: An AI agent was used for initial annotation assistance to pre-label the 200 examples. These pre-labels were subsequently reviewed and validated by a human to ensure strict adherence to our label taxonomy.
2.  **Failure Analysis Workflow**: Following model evaluation, the AI system will perform a detailed failure analysis on any misclassifications. Specifically, the system will be provided with the specific misclassifications identified in the Evaluation Report to categorize them by linguistic features such as sarcasm, post length, or ambiguous vocation. This systematic breakdown allows us to identify if the model's errors are due to inherent linguistic complexity or gaps in the training data.
