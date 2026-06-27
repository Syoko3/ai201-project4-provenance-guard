# Provenance Guard - planning.md

Required Features:
Content Submission Endpoint: Build an API endpoint that accepts a piece of text-based content (a poem, a short story excerpt, a blog post) for attribution analysis. The endpoint must return a structured response including the attribution result, confidence score, and the transparency label text that would be shown to the user.
Multi-Signal Detection Pipeline: Your detection pipeline must use at least 2 distinct signals to classify content. Single-signal detection is not acceptable. Your planning.md and README must explain what each signal captures and why you chose them.
Confidence Scoring with Uncertainty: Your system must return a confidence score, not just a binary label. The score should reflect genuine uncertainty — a 0.51 confidence should produce a meaningfully different transparency label than a 0.95. Your README must explain how you approached this and how you tested whether your scores are meaningful.
Transparency Label: Design and implement the label that would be displayed to a reader on the platform. It must communicate the attribution result in plain language and make the confidence level meaningful to a non-technical reader. Include a typed description of all three label variants (high-confidence AI, high-confidence human, uncertain) in your README — write out the exact text each one displays. You're welcome to include a screenshot or mockup as well, but the written description is what's required.
Appeals Workflow: Implement a mechanism for creators to contest a classification. At minimum, an appeal must: capture the creator's reasoning, log the appeal alongside the original decision, and update the content's status to "under review." Automated re-classification is not required.
Rate Limiting: Implement rate limiting on your submission endpoint. Your README must document the limits you chose and your reasoning for those specific values.
Audit Log: Every attribution decision — including confidence score, signals used, and any appeals — must be captured in a structured audit log. Document the log in your README (or via the GET /log output) with at least 3 entries visible.

---

## Detection Signals
<!--- What are your 2+ signals? What does each one measure? What does each signal's output look like (a score between 0–1? a binary flag?), and how will you combine them into a single confidence score? --->
| Signal | What does the signal measure | Output |
|--------|------------------------------|--------|
| Groq | "Vibe" and semantic coherence of the text | JSON object |
| Stylometric Heuristics | Type-Token Ratio, Sentence Length Variance, Punctuation Density | Set of raw numerical values |

**Combination into a single confidence score:** These two signals will be combined into a single confidence score by defining the weights of each signal, calculating the weighted mean, and finding the absolute difference between the signals. The final confidence score will be the absolute difference between the signals times 0.5 subtracted from the calculated weighted mean (Weighted_Mean - (0.5 * (abs(Groq_Score - Stylometric_Score)))).

---

## Uncertainty Representation
<!--- What does a confidence score of 0.6 mean to your system? How will you map raw signal outputs to a calibrated score? What threshold separates "likely AI" from "uncertain" from "likely human"? --->
A confidence score of 0.6 means that the system is mostly classified as AI but with low certainty. I will map raw signal outputs to a calibrated score by 0-1 scale, while 0.0 is classified as human and 1.0 is classified as AI. After that, I will calculate the base score as the weighted mean, and if the signals disagree significantly (|P-S| > 0.3), then I will put the final score toward 0.5. The confidence score range that shows "likely AI" will be between 0.0 and 0.4. The confidence score range that shows "uncertain" will be between 0.4 and 0.7. The confidence score range that shows "likely human" will be between 0.7 and 1.0.

---

## Transparency Label Design
<!--- What exact text will the label show for a high-confidence AI result? A high-confidence human result? An uncertain result? Write out the three label variants now, before you build the UI. --->
| Transparency Label | Confidence Score Range | Display Text |
|--------------------|------------------------|--------------|
| High-Confidence Human | 0.0 <= Score < 0.4 | Human-Authored Content |
| Uncertain Result | 0.4 <= Score < 0.7 | Attribution Uncertain |
| High-Confidence AI | 0.7 <= Score <= 1.0 | AI-Generated Content |

---

## Appeals Workflow
<!--- Who can submit an appeal? What information do they provide? What does the system do when an appeal is received — what status changes, what gets logged? What would a human reviewer see when they open the appeal queue? --->
The registered creator associated with an author_id of the specific piece of content can submit an appeal. They need to provide the content ID, the text field for the explanation why the classification of the content is incorrect, and optional evidence to show that this content is human-authored content. When an appeal is received, the content's status changes from "Public" to "Under Review", and the UI replaces the transparency label that is visible to the readers to a notice that this content is currently under review. There is no reclassification needed for this. For the audit log, the new entry is logged with the link to the Appeal to the original content ID. It is also logged for timestamp of the appeal, the creator's provided reasoning, and the system status change event. When a human reviewer open the appeal queue, they would see the comparison view by side-by-side display of the original text and the system's original signal metadata, the creator's reasoning and evidence, the decision console, and the decision history. For the decision console, there will be 3 buttons to show: upload attribution button to keep the label as-is and return the status to "Public", override button to force a "Human-Written" label manually and return the status to "Public", and request more info button for requesting any specific documentation to the creator. The decision history shows the read-only view of the Audit Log to show all automated decisions and the reasons of the system flagging the content.

---

## Anticipated Edge Cases
<!--- What types of content will your system handle poorly? Name at least two specific scenarios — not generic risks like "inaccurate detection," but specific cases like "a poem with heavy use of repetition and simple vocabulary that your heuristics might score as AI-generated." --->
| Scenario | Reason of Failure (Groq) | Reason of Failure (Stylometric Heuristics) |
|----------|--------------------------|--------------------------------------------|
| Poem that has single vocabulary, heavy reputation, or intentional fragmentation | If the poem lacks complex semantic flow, it will interpret the lack of logical progression as an AI failing to "reason" through a narrative. | Using a restricted word set will show an artifically low Type-Token Ratio. |
| Domain-specific technical documentation | Since LLMs encountered thousands of technical structures (e.g. manuals, documentation, academic papers), it will view the content as "AI-generated content" because the structure of the text is identical from the "technical" style the model itself is capable of producing. | Technical documentation will include repetitive terminology, structured and uniform sentence lengths to ensure clarity and avoid ambiguity, which will cause the signal to classify the content as "AI-generated content". |

---

## Architecture
<!---
Milestone 1: Sketch (on paper or in a text file) your API surface: what endpoints do you need? What does each one accept and return? You're not writing code yet — you're defining the contract that all other code will implement.
Draw the two main flows: (1) submission flow — POST /submit → signal 1 → signal 2 → confidence scoring → transparency label → audit log → response; (2) appeal flow — POST /appeal → status update → audit log → response. Label each arrow with what passes between components (raw text, signal score, combined score, label text).

Milestone 2: Include the diagram you drew in Milestone 1 (ASCII art is fine) and a 2–3 sentence narrative describing the submission and appeal flows. This section travels with you into Milestones 3–5 as the reference diagram for AI code generation.
--->
**Submission Flow:**

POST /submit ---> Rate Limiter ---> Detection Pipeline -----> Groq --> Score 1 --------------------─┐
                                                         |                                          |
                                                         └--> Stylometric Heuristics --> Score 2 ------> Score 1 + Score 2
                                                                                                               |
                                                                                                               v
Response (Confidence Score, Label) <--- Audit Log (Text, Scores, Label) <--- Transparency Label <--- Combined Confidence Score
          |
          └-----> User

Explanation: When a user submits content, the Rate Limiter verifies the request volume before passing the text to the detection pipeline. The pipeline contains 2 signals, Groq API and Stylometric Heuristics, and these two scores send to the arbiter. The arbiter calculates the combined confidence score, generates the correct transparency label, logs the entire transaction to the Audit Log, and returns the final result to the user.

**Appeal Flow:**

POST /appeal ---> Database ---> Status Update: "Under Review" ---> Audit Log (Append Appeal Entry) ---> Response (Confirmation Message) ---> User

Explanation: If a creator disagrees the result, the POST /appeal request initiates a workflow that updates the content’s status to "Under Review" in the Database. This action is recorded in the Audit Log alongside the creator’s provided reasoning, and a confirmation is returned to the user, showing that the content is now queued for human moderation.

---

## AI Tool Plan

**M3 (submission endpoint + first signal):**
<!--- Which spec sections you'll provide to the AI tool (hint: your detection signals section + the diagram), what you'll ask it to generate (Flask app skeleton + the first signal function), and how you'll verify the output (test with a few inputs directly before wiring into the endpoint). --->
I will give Claude my detection signals section and the submission flow of the architecture diagram and ask it to generate the Flask app skeleton and the first signal function. I will then test with a few inputs directly to verify the Flask app and the first signal function work correctly.

**M4 (second signal + confidence scoring):**
<!--- Which spec sections you'll provide (detection signals + uncertainty representation + diagram), what you'll ask for (second signal function + scoring logic), and what you'll check (do scores vary meaningfully between clearly AI and clearly human text?). --->
I will give Claude my detection signals section, uncertainty representation section, and the submission flow of the architecture diagram and ask it to generate the second signal function and the scoring logic. I will then check the scores that are correctly vary between clearly AI and clearly human text.

**M5 (production layer):**
<!--- Which spec sections you'll provide (label variants + appeals workflow + diagram), what you'll ask for (label generation logic + the /appeal endpoint), and how you'll verify (test all three label variants are reachable and that an appeal updates status correctly). --->
I will give Claude my transparency label design section, appeals workflow section, and the appeal flow of the architecture diagram and ask for generating the label generation logic and the /appeal endpoint. I will then test to ensure all three label variants are reachable, an appeal updates the status correctly, and the Audit Log adds this action with correct information.