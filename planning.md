# Provenance Guard - planning.md

---

## Detection Signals
<!--- What are your 2+ signals? What does each one measure? What does each signal's output look like (a score between 0–1? a binary flag?), and how will you combine them into a single confidence score? --->
| Signal | What does the signal measure | Output |
|--------|------------------------------|--------|
|  |  |  |
|  |  |  |

---

## Uncertainty Representation
<!--- What does a confidence score of 0.6 mean to your system? How will you map raw signal outputs to a calibrated score? What threshold separates "likely AI" from "uncertain" from "likely human"? --->


---

## Transparency Label Design
<!--- What exact text will the label show for a high-confidence AI result? A high-confidence human result? An uncertain result? Write out the three label variants now, before you build the UI. --->


---

## Appeals Workflow
<!--- Who can submit an appeal? What information do they provide? What does the system do when an appeal is received — what status changes, what gets logged? What would a human reviewer see when they open the appeal queue? --->


---

## Anticipated Edge Cases
<!--- What types of content will your system handle poorly? Name at least two specific scenarios — not generic risks like "inaccurate detection," but specific cases like "a poem with heavy use of repetition and simple vocabulary that your heuristics might score as AI-generated." --->
| Edge Case | Scenario #1 | Scenario #2 |
|-----------|-------------|-------------|
|  |  |  |

---

## Architecture
<!---
Milestone 1: Sketch (on paper or in a text file) your API surface: what endpoints do you need? What does each one accept and return? You're not writing code yet — you're defining the contract that all other code will implement.
Draw the two main flows: (1) submission flow — POST /submit → signal 1 → signal 2 → confidence scoring → transparency label → audit log → response; (2) appeal flow — POST /appeal → status update → audit log → response. Label each arrow with what passes between components (raw text, signal score, combined score, label text).

Milestone 2: Include the diagram you drew in Milestone 1 (ASCII art is fine) and a 2–3 sentence narrative describing the submission and appeal flows. This section travels with you into Milestones 3–5 as the reference diagram for AI code generation.
--->


---

## AI Tool Plan

**M3 (submission endpoint + first signal):**
<!--- Which spec sections you'll provide to the AI tool (hint: your detection signals section + the diagram), what you'll ask it to generate (Flask app skeleton + the first signal function), and how you'll verify the output (test with a few inputs directly before wiring into the endpoint). --->


**M4 (second signal + confidence scoring):**
<!--- Which spec sections you'll provide (detection signals + uncertainty representation + diagram), what you'll ask for (second signal function + scoring logic), and what you'll check (do scores vary meaningfully between clearly AI and clearly human text?). --->


**M5 (production layer):**
<!--- Which spec sections you'll provide (label variants + appeals workflow + diagram), what you'll ask for (label generation logic + the /appeal endpoint), and how you'll verify (test all three label variants are reachable and that an appeal updates status correctly). --->
