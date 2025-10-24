"""Generated item bank with examples for all sections of the adaptive test."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from app.cat_engine import Item


def _rotate_options(options: Sequence[str], shift: int) -> Tuple[List[str], int]:
    """Rotate a list of options and return the new list and index of the original first element."""

    if not options:
        raise ValueError("options must not be empty")
    shift = shift % len(options)
    rotated = list(options[shift:]) + list(options[:shift])
    return rotated, rotated.index(options[0])


# --- Vocabulary -------------------------------------------------------------------------------


@dataclass
class VocabularyBase:
    word: str
    synonym: str
    base_b: float
    a: float


VOCABULARY_BASES: List[VocabularyBase] = [
    VocabularyBase("serene", "calm", -1.8, 1.15),
    VocabularyBase("robust", "strong", -0.9, 1.05),
    VocabularyBase("elated", "joyful", -0.6, 1.1),
    VocabularyBase("meticulous", "careful", 0.2, 1.25),
    VocabularyBase("perplexed", "confused", 0.4, 1.2),
    VocabularyBase("obsolete", "outdated", 0.5, 1.1),
    VocabularyBase("resilient", "flexible", -0.4, 1.1),
    VocabularyBase("candid", "honest", -1.0, 1.05),
    VocabularyBase("tedious", "boring", -0.3, 1.15),
    VocabularyBase("frugal", "thrifty", -1.1, 1.05),
    VocabularyBase("ambiguous", "unclear", 0.6, 1.2),
    VocabularyBase("vivid", "bright", -0.7, 1.0),
    VocabularyBase("adhere", "follow", -0.5, 1.05),
    VocabularyBase("alleviate", "relieve", 0.1, 1.2),
    VocabularyBase("contemplate", "consider", 0.0, 1.15),
    VocabularyBase("deteriorate", "worsen", 0.7, 1.2),
    VocabularyBase("hinder", "obstruct", 0.4, 1.1),
    VocabularyBase("immerse", "engage", -0.2, 1.15),
    VocabularyBase("scrutinize", "examine", 0.8, 1.25),
    VocabularyBase("foster", "encourage", -0.3, 1.1),
    VocabularyBase("diligent", "hardworking", -0.6, 1.2),
    VocabularyBase("succinct", "concise", 0.1, 1.25),
    VocabularyBase("inevitable", "unavoidable", 0.9, 1.3),
    VocabularyBase("transform", "change", -0.8, 1.05),
    VocabularyBase("commend", "praise", -0.7, 1.15),
    VocabularyBase("mitigate", "lessen", 0.5, 1.2),
    VocabularyBase("precise", "exact", 0.2, 1.2),
    VocabularyBase("relevant", "applicable", -0.2, 1.1),
    VocabularyBase("scarce", "limited", 0.6, 1.2),
    VocabularyBase("versatile", "adaptable", 0.0, 1.15),
]

VOCABULARY_CONTEXTS: List[Dict[str, str]] = [
    {
        "topic": "travel diary",
        "stem": "[Vocabulary • {topic}] Choose the closest synonym for '{word}' to describe a journey.",
        "difficulty": "A2",
    },
    {
        "topic": "business briefing",
        "stem": "[Vocabulary • {topic}] Which option best replaces '{word}' in a professional report?",
        "difficulty": "B1",
    },
    {
        "topic": "university lecture",
        "stem": "[Vocabulary • {topic}] Select the term that conveys the same meaning as '{word}'.",
        "difficulty": "B2",
    },
    {
        "topic": "scientific article",
        "stem": "[Vocabulary • {topic}] Pick the most precise synonym for '{word}' in formal writing.",
        "difficulty": "C1",
    },
    {
        "topic": "community podcast",
        "stem": "[Vocabulary • {topic}] Identify the word that naturally substitutes '{word}'.",
        "difficulty": "B2",
    },
]


def _vocabulary_options(base_index: int, variant: int) -> Tuple[List[str], int]:
    correct = VOCABULARY_BASES[base_index].synonym
    distractors: List[str] = []
    total = len(VOCABULARY_BASES)
    cursor = 1
    while len(distractors) < 3:
        candidate = VOCABULARY_BASES[(base_index + variant + cursor) % total].synonym
        if candidate not in distractors and candidate != correct:
            distractors.append(candidate)
        cursor += 1
    ordered = [correct] + distractors
    rotated, correct_index = _rotate_options(ordered, base_index + variant)
    return rotated, correct_index


def build_vocabulary_items() -> List[Item]:
    items: List[Item] = []
    contexts_count = len(VOCABULARY_CONTEXTS)
    for base_index, base in enumerate(VOCABULARY_BASES):
        for variant, context in enumerate(VOCABULARY_CONTEXTS):
            options, correct_index = _vocabulary_options(base_index, variant)
            item_id = f"vocabulary_{base_index * contexts_count + variant + 1:03d}"
            stem = context["stem"].format(word=base.word, topic=context["topic"])
            items.append(
                Item(
                    id=item_id,
                    domain="vocabulary",
                    stem=stem,
                    options=options,
                    correct_key=correct_index,
                    model="3pl",
                    irt_a=round(base.a + 0.05 * variant, 2),
                    irt_b=round(base.base_b + 0.35 * (variant - (contexts_count - 1) / 2), 2),
                    irt_c=0.2,
                    metadata={
                        "word": base.word,
                        "synonym": base.synonym,
                        "topic": context["topic"],
                        "difficulty": context["difficulty"],
                    },
                )
            )
    return items


# --- Grammar -----------------------------------------------------------------------------------


@dataclass
class GrammarPattern:
    stem_template: str
    options: List[str]
    correct_index: int
    base_b: float
    a: float


GRAMMAR_PATTERNS: List[GrammarPattern] = [
    GrammarPattern(
        "[Grammar • {context}] Choose the correct verb form: \"If {subject} ____ the instructions, {pronoun} would have avoided the issue.\"",
        ["follows", "had followed", "would follow", "was following"],
        1,
        -0.4,
        1.25,
    ),
    GrammarPattern(
        "[Grammar • {context}] Select the correct sentence describing an ongoing conference call.",
        [
            "The team discusses the agenda right now.",
            "The team is discussing the agenda right now.",
            "The team discuss the agenda now.",
            "The team has discussing the agenda now.",
        ],
        1,
        -1.0,
        1.1,
    ),
    GrammarPattern(
        "[Grammar • {context}] Fill the blank: \"The analyst, ____ report impressed everyone, joined the call.\"",
        ["whose", "who", "which", "whom"],
        0,
        0.2,
        1.2,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct passive construction about a product launch.",
        [
            "They announced the feature yesterday.",
            "The feature announced yesterday.",
            "The feature was announced yesterday.",
            "The feature is announce yesterday.",
        ],
        2,
        -0.6,
        1.1,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the sentence: \"Participants ____ submit their feedback forms by Friday.\"",
        ["must", "could", "might", "used to"],
        0,
        -0.2,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct reported speech option for the sentence: \"{subject} said, 'I am reviewing the plan.'\"",
        [
            "{subject} said that {pronoun} was reviewing the plan.",
            "{subject} said that {pronoun} is reviewing the plan.",
            "{subject} said that {pronoun} reviewed the plan.",
            "{subject} said that {pronoun} has reviewing the plan.",
        ],
        0,
        0.1,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Decide whether a gerund or infinitive fits: \"{subject} avoided ____ late to the keynote.\"",
        ["to arrive", "arriving", "arrive", "to arriving"],
        1,
        -0.5,
        1.1,
    ),
    GrammarPattern(
        "[Grammar • {context}] Pick the correct article usage: \"It was ____ honor to host the symposium.\"",
        ["a", "an", "the", "no article"],
        1,
        -1.4,
        0.95,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct preposition: \"The results differ significantly ____ last year's numbers.\"",
        ["from", "of", "in", "to"],
        0,
        -0.3,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Identify the correct inversion: \"Rarely ____ such engaged participants.\"",
        ["we see", "do we see", "we are seeing", "are we see"],
        1,
        0.8,
        1.3,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the mixed conditional: \"If the prototype were ready, we ____ it tomorrow.\"",
        ["would launch", "launch", "launched", "would have launched"],
        0,
        0.4,
        1.25,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct phrasal verb completion: \"The coach urged the team to ____ their notes for clarity.\"",
        ["run into", "write out", "hand over", "look after"],
        1,
        -0.1,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Select the correct subjunctive form: \"It is essential that each delegate ____ on time.\"",
        ["arrives", "arrive", "arrived", "has arrived"],
        1,
        0.3,
        1.2,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the emphatic statement: \"{subject} ____ finish the presentation on time!\"",
        ["did", "does", "do", "done"],
        0,
        -0.1,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct reduced relative clause: \"The report ____ yesterday needs a final review.\"",
        ["completing", "completed", "complete", "completion"],
        1,
        0.2,
        1.2,
    ),
    GrammarPattern(
        "[Grammar • {context}] Select the correct question tag: \"{subject} will attend the networking event, ____?\"",
        ["will {pronoun}", "does {pronoun}", "won't {pronoun}", "isn't {pronoun}"],
        2,
        -0.6,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct tense consistency: \"{subject} said {pronoun} ____ the draft by noon.\"",
        ["will finish", "would finish", "finished", "is finishing"],
        1,
        -0.2,
        1.1,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the sentence with the correct perfect aspect: \"By the time the keynote begins, we ____ all tests.\"",
        ["complete", "will have completed", "will complete", "have completed"],
        1,
        0.6,
        1.2,
    ),
    GrammarPattern(
        "[Grammar • {context}] Identify the correctly punctuated indirect question.",
        [
            "Could you tell me, where is the shuttle stop?",
            "Could you tell me where the shuttle stop is?",
            "Could you tell me where is the shuttle stop.",
            "Could you tell me where the shuttle stop is!",
        ],
        1,
        -0.9,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Select the appropriate relative pronoun for a company description.",
        ["whom", "what", "that", "whichever"],
        2,
        -0.1,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct quantifier: \"There are ____ opportunities to practice speaking during the retreat.\"",
        ["few", "a few", "little", "many"],
        1,
        -1.2,
        0.95,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the participle clause: \"____ the feedback, the facilitator adjusted the schedule.\"",
        ["Receiving", "Received", "Having received", "Receives"],
        2,
        0.1,
        1.2,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct zero conditional sentence.",
        [
            "If participants will arrive early, they enjoy the tour.",
            "If participants arrive early, they enjoy the tour.",
            "If participants arriving early, they enjoy the tour.",
            "If participants arrived early, they enjoyed the tour.",
        ],
        1,
        -1.0,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Select the correct cleft sentence to emphasize the keynote speaker.",
        [
            "It was the keynote speaker that inspired everyone.",
            "It is the keynote speaker inspired everyone.",
            "It were the keynote speaker who inspired everyone.",
            "It the keynote speaker was who inspired everyone.",
        ],
        0,
        -0.4,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct agreement with either/or: \"Either the coaches or the manager ____ the briefing.\"",
        ["conduct", "conducts", "conducting", "have conducted"],
        1,
        0.5,
        1.15,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the recommendation: \"{subject} ____ leave before the roads get crowded.\"",
        ["had better", "has better", "had rather", "better had"],
        0,
        0.0,
        1.05,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct expression about past habits.",
        [
            "We use to practice presentations weekly.",
            "We used to practice presentations weekly.",
            "We are used to practice presentations weekly.",
            "We were use to practice presentations weekly.",
        ],
        1,
        -0.8,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Complete the inversion after 'no sooner': \"No sooner ____ the session begun than the lights went out.\"",
        ["had", "has", "did", "having"],
        0,
        0.7,
        1.3,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct comparative structure with 'as...as'.",
        [
            "This activity is as engaging as the previous one.",
            "This activity is as engaging than the previous one.",
            "This activity is so engaging as the previous one.",
            "This activity engaging as the previous one.",
        ],
        0,
        -0.9,
        1.0,
    ),
    GrammarPattern(
        "[Grammar • {context}] Choose the correct modal for deduction: \"The facilitator ____ be new; I haven't seen them before.\"",
        ["must", "can", "should", "might"],
        0,
        0.3,
        1.1,
    ),
]

GRAMMAR_CONTEXTS: List[Dict[str, str]] = [
    {"context": "project debrief", "subject": "Ava", "pronoun": "she", "difficulty_adj": -1.0},
    {"context": "research symposium", "subject": "Noah", "pronoun": "he", "difficulty_adj": -0.4},
    {"context": "community workshop", "subject": "Mia", "pronoun": "she", "difficulty_adj": 0.0},
    {"context": "leadership summit", "subject": "Ethan", "pronoun": "he", "difficulty_adj": 0.5},
    {"context": "innovation forum", "subject": "Olivia", "pronoun": "she", "difficulty_adj": 0.9},
]


def build_grammar_items() -> List[Item]:
    items: List[Item] = []
    contexts_count = len(GRAMMAR_CONTEXTS)
    for pattern_index, pattern in enumerate(GRAMMAR_PATTERNS):
        for variant, context in enumerate(GRAMMAR_CONTEXTS):
            stem = pattern.stem_template.format(**context)
            options = [option.format(**context) for option in pattern.options]
            item_id = f"grammar_{pattern_index * contexts_count + variant + 1:03d}"
            items.append(
                Item(
                    id=item_id,
                    domain="grammar",
                    stem=stem,
                    options=options,
                    correct_key=pattern.correct_index,
                    model="2pl",
                    irt_a=round(pattern.a + 0.05 * variant, 2),
                    irt_b=round(pattern.base_b + context.get("difficulty_adj", 0.0) + 0.3 * (variant - (contexts_count - 1) / 2), 2),
                )
            )
    return items


# --- Listening ---------------------------------------------------------------------------------


@dataclass
class ListeningScenario:
    topic: str
    transcript: str
    difficulty: str
    base_b: float
    facts: Dict[str, str]


LISTENING_AUDIO_URLS: List[str] = [
    "https://cdn.jsdelivr.net/gh/anars/blank-audio/5-seconds-of-silence.mp3",
    "https://cdn.jsdelivr.net/gh/anars/blank-audio/10-seconds-of-silence.mp3",
    "https://cdn.jsdelivr.net/gh/anars/blank-audio/15-seconds-of-silence.mp3",
]

LISTENING_FOCUSES: List[str] = [
    "main advice",
    "key detail",
    "numerical fact",
    "speaker attitude",
    "next step",
]

LISTENING_TEMPLATES: Dict[str, str] = {
    "main advice": "[Listening • {topic}] After hearing the clip, what is the speaker's main advice?",
    "key detail": "[Listening • {topic}] Which detail does the speaker highlight?",
    "numerical fact": "[Listening • {topic}] What number or statistic does the speaker mention?",
    "speaker attitude": "[Listening • {topic}] How does the speaker sound about the topic?",
    "next step": "[Listening • {topic}] What next step does the speaker ask listeners to take?",
}

LISTENING_SCENARIOS: List[ListeningScenario] = [
    ListeningScenario(
        "sustainable travel briefing",
        "A travel coach explains how to lower emissions by choosing regional trains, reusable bottles, and planning buffer time.",
        "B1",
        -0.6,
        {
            "main advice": "Opt for regional trains instead of short flights to reduce emissions.",
            "key detail": "She urges listeners to book seats in advance to avoid last-minute fares.",
            "numerical fact": "The speaker states that trains emit roughly one-third the CO₂ of comparable flights.",
            "speaker attitude": "She sounds optimistic that small adjustments can meaningfully cut footprints.",
            "next step": "She recommends downloading the new eco-route planner app before traveling.",
        },
    ),
    ListeningScenario(
        "remote onboarding call",
        "An HR specialist walks new hires through workspace setup, introduces mentorship calls, and stresses camera etiquette.",
        "B2",
        -0.2,
        {
            "main advice": "Set up a quiet workspace before day one to stay focused.",
            "key detail": "The speaker reminds everyone to test microphones at least an hour ahead.",
            "numerical fact": "New hires are told that orientation includes three mentor check-ins in the first month.",
            "speaker attitude": "The HR specialist sounds reassuring and patient with questions.",
            "next step": "She asks participants to confirm their welcome kit delivery by tonight.",
        },
    ),
    ListeningScenario(
        "wellness podcast",
        "A nutritionist describes balanced snacks, hydration cues, and the value of brief stretching during intense study weeks.",
        "A2",
        -1.2,
        {
            "main advice": "Balance snacks with protein and fruit to stay energized.",
            "key detail": "She suggests setting a repeating reminder to drink water every hour.",
            "numerical fact": "Listeners hear that even five-minute stretch breaks can improve focus by 20 percent.",
            "speaker attitude": "She sounds encouraging and upbeat about small lifestyle tweaks.",
            "next step": "She invites listeners to download a printable snack planner from her site.",
        },
    ),
    ListeningScenario(
        "innovation pitch",
        "A startup founder outlines a language-learning app, highlights adaptive AI, early tester feedback, and future roadmap milestones.",
        "C1",
        0.8,
        {
            "main advice": "Investors should focus on adaptive practice that personalizes difficulty in real time.",
            "key detail": "He mentions that teachers requested analytics to track learner confidence dips.",
            "numerical fact": "The founder reports a 42 percent increase in retention among beta testers.",
            "speaker attitude": "He sounds energized and determined to scale internationally.",
            "next step": "He asks listeners to join the pilot program feedback session next Tuesday.",
        },
    ),
    ListeningScenario(
        "museum audio guide",
        "A curator describes a new exhibit on marine conservation, referencing sculptures, visitor interaction points, and research partners.",
        "B1",
        -0.4,
        {
            "main advice": "Visitors should engage with the interactive map to understand coral threats.",
            "key detail": "The guide notes that the projection room cycles every eight minutes.",
            "numerical fact": "She cites that the museum collaborated with 12 coastal labs for data.",
            "speaker attitude": "She sounds proud of community contributions to the exhibit.",
            "next step": "She encourages guests to leave audio reflections at the final station.",
        },
    ),
    ListeningScenario(
        "career coaching session",
        "A coach outlines networking strategies, emphasizes targeted messages, follow-up timing, and reflective journaling.",
        "B2",
        -0.1,
        {
            "main advice": "Craft tailored outreach messages instead of generic templates.",
            "key detail": "She highlights sending follow-ups within 48 hours of a conversation.",
            "numerical fact": "The coach mentions recording three insights after each meeting.",
            "speaker attitude": "She sounds pragmatic yet motivating about long-term goals.",
            "next step": "She asks attendees to draft a tracking spreadsheet before the weekend.",
        },
    ),
    ListeningScenario(
        "environmental town hall",
        "A city planner presents flood mitigation updates, funding grants, homeowner tips, and volunteer training dates.",
        "C1",
        0.6,
        {
            "main advice": "Residents should elevate basement utilities above predicted flood lines.",
            "key detail": "He references a state grant covering half the cost of flood barriers.",
            "numerical fact": "The planner notes that rainfall intensity has doubled over ten years.",
            "speaker attitude": "He sounds cautious yet collaborative about community resilience.",
            "next step": "He invites neighbors to register for Saturday's sandbag workshop.",
        },
    ),
    ListeningScenario(
        "student roundtable",
        "University leaders discuss peer mentoring, library renovations, mental health drop-ins, and internship pipelines.",
        "B1",
        -0.5,
        {
            "main advice": "Students should sign up for peer mentoring early in the semester.",
            "key detail": "The panel says the library quiet zones will reopen in October.",
            "numerical fact": "They share that 68 companies joined the internship network this year.",
            "speaker attitude": "They sound hopeful about expanding student support.",
            "next step": "They encourage students to complete the campus resources survey online.",
        },
    ),
    ListeningScenario(
        "language learning webinar",
        "A linguist explains spaced repetition, cultural immersion clips, community practice rooms, and pronunciation labs.",
        "C1",
        0.7,
        {
            "main advice": "Learners should schedule short review sessions twice a day.",
            "key detail": "She highlights uploading questions before the weekly lab livestream.",
            "numerical fact": "She reports that five-minute shadowing sessions boost recall by 35 percent.",
            "speaker attitude": "She sounds analytical but encouraging about consistent routines.",
            "next step": "She invites attendees to join a cultural exchange chat after the webinar.",
        },
    ),
    ListeningScenario(
        "innovation lab briefing",
        "Engineers summarize prototype sprints, testing feedback, budget reallocations, and security audits.",
        "C1",
        0.9,
        {
            "main advice": "Teams should prioritize accessibility fixes before aesthetic polish.",
            "key detail": "They mention consolidating sensors into one encrypted module.",
            "numerical fact": "The team reports a 15 percent error rate drop after firmware updates.",
            "speaker attitude": "They sound urgent yet confident about meeting launch targets.",
            "next step": "They call for volunteers to run overnight stress tests this Friday.",
        },
    ),
    ListeningScenario(
        "arts festival announcement",
        "An organizer covers workshop schedules, featured muralists, volunteer shifts, and sponsor showcases.",
        "B1",
        -0.3,
        {
            "main advice": "Visitors should check the morning schedule for hands-on workshops.",
            "key detail": "She points out that the mural tour departs from the east gate.",
            "numerical fact": "She shares that 24 local artists will present live demos.",
            "speaker attitude": "She sounds enthusiastic and welcoming to newcomers.",
            "next step": "She asks participants to confirm volunteer availability by Wednesday.",
        },
    ),
    ListeningScenario(
        "financial literacy seminar",
        "An advisor explains budgeting envelopes, emergency funds, credit score habits, and negotiation practice.",
        "B2",
        0.2,
        {
            "main advice": "Allocate savings to separate envelopes to visualize spending.",
            "key detail": "He advises automating deposits the morning after payday.",
            "numerical fact": "He notes that keeping a three-month emergency fund is a solid start.",
            "speaker attitude": "He sounds pragmatic and encouraging about gradual progress.",
            "next step": "He asks attendees to list negotiable expenses before the next session.",
        },
    ),
    ListeningScenario(
        "volunteer orientation",
        "A coordinator highlights community partners, safety briefings, supply checklists, and reflection circles.",
        "A2",
        -1.0,
        {
            "main advice": "Volunteers should review the safety checklist before every shift.",
            "key detail": "She reminds everyone to sign the attendance sheet upon arrival.",
            "numerical fact": "She mentions that each team supports 15 households per route.",
            "speaker attitude": "She sounds appreciative of everyone's commitment.",
            "next step": "She invites volunteers to share concerns during the closing circle.",
        },
    ),
    ListeningScenario(
        "academic writing clinic",
        "A tutor reviews thesis statements, citation habits, peer review swaps, and pacing for revisions.",
        "B2",
        -0.1,
        {
            "main advice": "Writers should outline arguments before drafting paragraphs.",
            "key detail": "He encourages scheduling peer review swaps every other week.",
            "numerical fact": "He notes that revision should take at least two focused sessions.",
            "speaker attitude": "He sounds methodical and supportive of gradual improvements.",
            "next step": "He asks students to upload outlines to the shared folder tonight.",
        },
    ),
    ListeningScenario(
        "eco start-up update",
        "A founder shares solar microgrid progress, customer pilots, supply delays, and mentorship opportunities.",
        "B2",
        0.1,
        {
            "main advice": "Partners should focus on building community training hubs.",
            "key detail": "She mentions batteries arriving two weeks behind schedule.",
            "numerical fact": "She reports that pilot villages cut diesel use by 60 percent.",
            "speaker attitude": "She sounds candid about hurdles but proud of impact.",
            "next step": "She invites supporters to attend the next investor Q&A.",
        },
    ),
    ListeningScenario(
        "conference closing remarks",
        "The host thanks volunteers, previews next year's theme, highlights scholarship winners, and shares survey links.",
        "B1",
        -0.7,
        {
            "main advice": "Attendees should complete the feedback survey before leaving.",
            "key detail": "She mentions next year's theme will explore inclusive design.",
            "numerical fact": "She celebrates funding 14 travel scholarships this season.",
            "speaker attitude": "She sounds grateful and inspired by the community.",
            "next step": "She invites everyone to the informal meetup in the lobby.",
        },
    ),
    ListeningScenario(
        "innovation incubator call",
        "Mentors recap sprint goals, share prototype insights, assign documentation duties, and announce demo days.",
        "C1",
        0.4,
        {
            "main advice": "Teams should document user interviews within 24 hours.",
            "key detail": "They note that demo day pitches are capped at five minutes.",
            "numerical fact": "They report onboarding 18 new testers this cycle.",
            "speaker attitude": "They sound focused and encouraging about iteration.",
            "next step": "They ask teams to upload sprint summaries by Friday noon.",
        },
    ),
    ListeningScenario(
        "study abroad briefing",
        "Advisors cover visa paperwork, housing placements, cultural orientation, and language exchange partners.",
        "B1",
        -0.6,
        {
            "main advice": "Students should submit visa photocopies before the end of the month.",
            "key detail": "She notes that housing confirmations arrive three weeks prior to departure.",
            "numerical fact": "She shares that 27 partner universities will host exchanges.",
            "speaker attitude": "She sounds organized and empathetic toward first-time travelers.",
            "next step": "She invites students to schedule a culture chat with alumni mentors.",
        },
    ),
    ListeningScenario(
        "health research update",
        "A doctor summarizes trial data, community outreach plans, funding pledges, and training for volunteers.",
        "C1",
        0.7,
        {
            "main advice": "Clinics should prioritize free screenings in rural areas first.",
            "key detail": "He references new training modules for volunteer nurses.",
            "numerical fact": "He states that the pilot served 1,200 patients last quarter.",
            "speaker attitude": "He sounds cautiously optimistic about scaling support.",
            "next step": "He encourages partners to attend Thursday's coordination call.",
        },
    ),
    ListeningScenario(
        "makerspace tutorial",
        "An instructor covers safety checks, tool orientation, project planning boards, and clean-up routines.",
        "A2",
        -1.1,
        {
            "main advice": "Members should inspect equipment before every session.",
            "key detail": "He reminds everyone to log materials on the whiteboard.",
            "numerical fact": "He mentions workshops cap at ten participants per slot.",
            "speaker attitude": "He sounds calm and encouraging for beginners.",
            "next step": "He asks participants to review the safety quiz tonight.",
        },
    ),
    ListeningScenario(
        "community garden briefing",
        "A coordinator discusses soil rotations, volunteer rosters, irrigation timers, and harvest festivals.",
        "A2",
        -0.8,
        {
            "main advice": "Gardeners should rotate crops every season to maintain soil health.",
            "key detail": "She notes the irrigation timers start at 6 a.m. daily.",
            "numerical fact": "She shares that 45 families share produce boxes.",
            "speaker attitude": "She sounds cheerful and collaborative.",
            "next step": "She invites volunteers to plan the autumn harvest festival.",
        },
    ),
    ListeningScenario(
        "tech support webinar",
        "A support lead explains troubleshooting steps, escalation paths, performance dashboards, and customer empathy tips.",
        "B2",
        0.0,
        {
            "main advice": "Agents should verify recent updates before escalating tickets.",
            "key detail": "He stresses logging every call within the CRM within ten minutes.",
            "numerical fact": "He notes that average resolution time dropped to 18 hours.",
            "speaker attitude": "He sounds solution-focused and calm under pressure.",
            "next step": "He asks staff to role-play tricky scenarios at the next stand-up.",
        },
    ),
    ListeningScenario(
        "parent-teacher forum",
        "Teachers share curriculum adjustments, social-emotional supports, reading milestones, and volunteer needs.",
        "A2",
        -1.0,
        {
            "main advice": "Families should read aloud together at least twice a week.",
            "key detail": "They mention workshops scheduled for the first Saturday monthly.",
            "numerical fact": "They highlight that 90 percent of students met reading goals.",
            "speaker attitude": "They sound appreciative of parental involvement.",
            "next step": "They encourage sign-ups for classroom helper rotations.",
        },
    ),
    ListeningScenario(
        "creative writing retreat",
        "Facilitators outline morning prompts, critique circles, sensory walks, and publication goals.",
        "B2",
        -0.2,
        {
            "main advice": "Writers should capture sensory details during the daily walks.",
            "key detail": "She describes critique groups rotating every two sessions.",
            "numerical fact": "She notes that the retreat spans 12 focused workshops.",
            "speaker attitude": "She sounds inspired and supportive of experimentation.",
            "next step": "She asks participants to submit a draft excerpt by Friday.",
        },
    ),
    ListeningScenario(
        "public speaking clinic",
        "A coach reviews breathing exercises, storytelling hooks, pacing, and slide simplification.",
        "B1",
        -0.5,
        {
            "main advice": "Speakers should open with a vivid story to engage the audience.",
            "key detail": "He asks everyone to rehearse while recording themselves once a week.",
            "numerical fact": "He explains that pausing for two seconds improves clarity.",
            "speaker attitude": "He sounds confident and encouraging about practice routines.",
            "next step": "He invites attendees to join the peer feedback circle next Monday.",
        },
    ),
    ListeningScenario(
        "urban planning podcast",
        "Experts discuss bike lane expansions, zoning updates, air quality sensors, and resident feedback apps.",
        "C1",
        0.5,
        {
            "main advice": "Residents should submit route suggestions through the planning app.",
            "key detail": "They reference installing sensors along the river corridor.",
            "numerical fact": "The episode notes that cycling increased by 28 percent last year.",
            "speaker attitude": "The panel sounds analytical yet hopeful about greener transit.",
            "next step": "They invite listeners to attend the zoning workshop next month.",
        },
    ),
    ListeningScenario(
        "culinary masterclass",
        "A chef demonstrates knife safety, seasonal pairings, plating styles, and mindful tasting notes.",
        "B1",
        -0.2,
        {
            "main advice": "Chefs should practice knife grips slowly before increasing speed.",
            "key detail": "She highlights pairing citrus glaze with roasted carrots.",
            "numerical fact": "She says the tasting lasts for six curated courses.",
            "speaker attitude": "She sounds passionate and precise about technique.",
            "next step": "She invites participants to upload photos of their plating practice.",
        },
    ),
    ListeningScenario(
        "library tech tour",
        "A librarian showcases media labs, booking kiosks, workshop pods, and archival digitization projects.",
        "A2",
        -0.9,
        {
            "main advice": "Visitors should reserve media labs online before arriving.",
            "key detail": "He notes that 3D printers require a short certification video first.",
            "numerical fact": "He mentions digitizing over 6,000 photos this year.",
            "speaker attitude": "He sounds welcoming and enthusiastic about exploration.",
            "next step": "He asks guests to share project ideas with staff mentors.",
        },
    ),
    ListeningScenario(
        "outdoor leadership briefing",
        "Guides explain trail pacing, weather checks, group signals, and debrief reflections.",
        "B1",
        -0.4,
        {
            "main advice": "Hikers should check mountain forecasts an hour before departure.",
            "key detail": "They demonstrate raising trekking poles to signal a stop.",
            "numerical fact": "They remind groups to carry two liters of water per person.",
            "speaker attitude": "They sound calm and attentive to safety.",
            "next step": "They request guides to log route notes after each trek.",
        },
    ),
    ListeningScenario(
        "startup stand-up",
        "Team leads share sprint blockers, marketing experiments, analytics wins, and investor follow-ups.",
        "C1",
        0.6,
        {
            "main advice": "Marketers should align experiments with the new positioning statement.",
            "key detail": "They mention that investor calls will run every Thursday afternoon.",
            "numerical fact": "They highlight a 12 percent rise in weekly active users.",
            "speaker attitude": "They sound driven and transparent about next steps.",
            "next step": "They ask product owners to sync roadmaps by tomorrow.",
        },
    ),
]


def build_listening_items() -> List[Item]:
    statements: Dict[str, List[str]] = {focus: [] for focus in LISTENING_FOCUSES}
    for scenario in LISTENING_SCENARIOS:
        for focus, sentence in scenario.facts.items():
            statements[focus].append(sentence)

    items: List[Item] = []
    audio_count = len(LISTENING_AUDIO_URLS)
    focuses_count = len(LISTENING_FOCUSES)
    true_false_counter = 1
    for scenario_index, scenario in enumerate(LISTENING_SCENARIOS):
        audio_url = LISTENING_AUDIO_URLS[scenario_index % audio_count]
        for focus_index, focus in enumerate(LISTENING_FOCUSES):
            correct = scenario.facts[focus]
            distractors = [text for text in statements[focus] if text != correct][:3]
            while len(distractors) < 3:
                other_focus = LISTENING_FOCUSES[(focus_index + len(distractors) + 1) % focuses_count]
                pool = [text for text in statements[other_focus] if text != correct]
                if pool:
                    distractors.append(pool[(scenario_index + len(distractors)) % len(pool)])
                else:
                    distractors.append("The speaker does not share this detail.")
            options = [correct] + distractors
            rotated, correct_index = _rotate_options(options, scenario_index + focus_index)
            item_id = f"listening_{scenario_index * focuses_count + focus_index + 1:03d}"
            items.append(
                Item(
                    id=item_id,
                    domain="listening",
                    stem=LISTENING_TEMPLATES[focus].format(topic=scenario.topic),
                    options=rotated,
                    correct_key=correct_index,
                    model="3pl",
                    irt_a=round(1.0 + 0.05 * focus_index, 2),
                    irt_b=round(scenario.base_b + 0.25 * (focus_index - (focuses_count - 1) / 2), 2),
                    irt_c=0.2,
                    max_plays=2,
                    metadata={
                        "audio_url": audio_url,
                        "transcript": scenario.transcript,
                        "difficulty": scenario.difficulty,
                        "topic": scenario.topic,
                        "question_type": "multiple_choice",
                    },
                )
            )

            # Generate a paired true/false question for the same scenario and focus
            pool_false = [text for text in statements[focus] if text != correct]
            if pool_false:
                false_statement = pool_false[(scenario_index + focus_index) % len(pool_false)]
            else:
                # fallback to any statement outside the current scenario
                fallback = [
                    text
                    for other_focus, texts in statements.items()
                    if other_focus != focus
                    for text in texts
                ]
                if not fallback:
                    fallback = [correct]
                false_statement = fallback[(scenario_index + focus_index) % len(fallback)]
            use_true = (scenario_index + focus_index) % 2 == 0
            statement = correct if use_true else false_statement
            correct_key = 0 if use_true else 1
            tf_item_id = f"listening_tf_{true_false_counter:03d}"
            true_false_counter += 1
            items.append(
                Item(
                    id=tf_item_id,
                    domain="listening",
                    stem=(
                        "[Listening • {topic}] The speaker states: \"{statement}\". "
                        "Is this true or false?"
                    ).format(topic=scenario.topic, statement=statement),
                    options=["True", "False"],
                    correct_key=correct_key,
                    model="3pl",
                    irt_a=round(0.95 + 0.04 * focus_index, 2),
                    irt_b=round(scenario.base_b + 0.2 * (focus_index - (focuses_count - 1) / 2), 2),
                    irt_c=0.5,
                    max_plays=2,
                    metadata={
                        "audio_url": audio_url,
                        "transcript": scenario.transcript,
                        "difficulty": scenario.difficulty,
                        "topic": scenario.topic,
                        "question_type": "true_false",
                        "statement": statement,
                    },
                )
            )
    return items


# --- English in Use ---------------------------------------------------------------------------


@dataclass
class UsageOption:
    text: str
    category: str


@dataclass
class UsageScenario:
    stem_template: str
    options: List[UsageOption]
    base_b: float
    a: float
    difficulty: str


USAGE_TASKS: List[Dict[str, object]] = [
    {"focus": "formal reassurance", "categories": ("formal", "support")},
    {"focus": "friendly encouragement", "categories": ("casual", "motivation")},
    {"focus": "outline next steps", "categories": ("action", "followup")},
    {"focus": "express gratitude", "categories": ("gratitude", "support")},
    {"focus": "clarify expectations", "categories": ("clarity", "action")},
]

USAGE_SCENARIO_DATA: List[Dict[str, object]] = [
    {
        "stem": "[English in Use • client apology] Select language to restore trust after a delayed shipment.",
        "difficulty": "B1",
        "base_b": -0.3,
        "a": 1.1,
        "formal": "I sincerely apologize for the delay with your order.",
        "support": "We value your patience while we resolve this.",
        "casual": "Thanks for sticking with us on this!",
        "motivation": "Your partnership motivates our whole team.",
        "action": "We will ship the revised package by Thursday.",
        "followup": "I'll send tracking updates tomorrow morning.",
        "gratitude": "Thank you again for your flexibility.",
        "clarity": "Does the adjusted delivery schedule meet your needs?",
    },
    {
        "stem": "[English in Use • leadership update] Choose statements that keep an executive summary focused and confident.",
        "difficulty": "B2",
        "base_b": 0.4,
        "a": 1.2,
        "formal": "The integration completed successfully ahead of schedule.",
        "support": "The team remains ready to assist with any escalations.",
        "casual": "We're pretty excited about how it all turned out!",
        "motivation": "Your guidance continues to push the project forward.",
        "action": "We will launch the analytics dashboard on Friday.",
        "followup": "I'll circulate a metrics snapshot after the next stand-up.",
        "gratitude": "Thank you for championing the work this quarter.",
        "clarity": "Are there additional priorities you'd like highlighted next report?",
    },
    {
        "stem": "[English in Use • mentoring chat] Pick supportive expressions for a mentee preparing for exams.",
        "difficulty": "A2",
        "base_b": -0.8,
        "a": 1.0,
        "formal": "I appreciate how thoroughly you're approaching your study plan.",
        "support": "I'm here whenever you want to practice sample questions.",
        "casual": "You've totally got this—deep breath!",
        "motivation": "Every session is building your confidence piece by piece.",
        "action": "Let's map out three mini-goals for this week together.",
        "followup": "I'll check in on Friday to see how the new routine feels.",
        "gratitude": "Thanks for trusting me with your goals.",
        "clarity": "Which topic would you like extra feedback on today?",
    },
    {
        "stem": "[English in Use • project retrospective] Choose wording that keeps a retrospective constructive.",
        "difficulty": "B2",
        "base_b": 0.1,
        "a": 1.15,
        "formal": "One improvement area is tightening our kickoff checklist.",
        "support": "I'm ready to pair on refining the sign-off process.",
        "casual": "We totally powered through the tough parts!",
        "motivation": "Our lessons learned can fuel an even stronger next sprint.",
        "action": "We'll pilot a shorter review cycle next iteration.",
        "followup": "I'll document the action items and share them by noon.",
        "gratitude": "Thank you for the honest feedback during this session.",
        "clarity": "Does this summary capture the blockers accurately?",
    },
    {
        "stem": "[English in Use • academic email] Select phrases that keep correspondence with a professor polite and clear.",
        "difficulty": "A2",
        "base_b": -0.9,
        "a": 0.95,
        "formal": "Dear Professor Reyes, I hope you're doing well.",
        "support": "I appreciate your guidance on the research outline.",
        "casual": "Hi there! Quick question for you.",
        "motivation": "Your seminar has inspired me to read more widely.",
        "action": "I'll submit the revised abstract by Wednesday afternoon.",
        "followup": "I'll confirm once the paper uploads successfully.",
        "gratitude": "Thank you for reviewing my draft so thoroughly.",
        "clarity": "Could you clarify the expected length for the literature review?",
    },
    {
        "stem": "[English in Use • webinar hosting] Pick expressions that create an organized and welcoming webinar introduction.",
        "difficulty": "B1",
        "base_b": -0.5,
        "a": 1.05,
        "formal": "We're delighted to welcome you to today's session.",
        "support": "Our moderation team is here to help at any time.",
        "casual": "Great to see so many of you joining live!",
        "motivation": "Your participation will make the activities richer.",
        "action": "We'll begin with a quick poll to learn about your roles.",
        "followup": "I'll email the slide deck and resources after we wrap up.",
        "gratitude": "Thanks for taking an hour to learn with us.",
        "clarity": "Can you pop questions into the Q&A tab as they arise?",
    },
    {
        "stem": "[English in Use • negotiation call] Choose language that balances firmness with collaboration.",
        "difficulty": "C1",
        "base_b": 0.8,
        "a": 1.25,
        "formal": "We appreciate the transparency in your pricing breakdown.",
        "support": "Our objective is to find terms that work for both teams.",
        "casual": "Let's figure this out together today.",
        "motivation": "Partnering with you can unlock significant reach for both sides.",
        "action": "We'll revise the onboarding plan based on today's decisions.",
        "followup": "I'll send a redlined agreement for review by tomorrow evening.",
        "gratitude": "Thank you for remaining flexible during the discussion.",
        "clarity": "Could you clarify the support hours included in the proposal?",
    },
    {
        "stem": "[English in Use • support chat] Select responses that calm and assist an upset customer.",
        "difficulty": "B1",
        "base_b": -0.4,
        "a": 1.1,
        "formal": "I understand how disruptive this issue is for you.",
        "support": "I'm here on the chat until we find a solution together.",
        "casual": "Thanks for hanging in there with me.",
        "motivation": "We'll get this sorted so you can get back on track.",
        "action": "Let's walk through the reset steps one by one now.",
        "followup": "I'll email you a summary once we've confirmed everything works.",
        "gratitude": "Thank you for the details you shared—they really help.",
        "clarity": "Does this troubleshoot step match what you're seeing on screen?",
    },
    {
        "stem": "[English in Use • research summary] Choose sentences that suit an academic abstract recap.",
        "difficulty": "C1",
        "base_b": 0.6,
        "a": 1.3,
        "formal": "The study evaluated learner outcomes across three cohorts.",
        "support": "The advisory board remains available to interpret the data with us.",
        "casual": "It was kind of wild watching the trends change!",
        "motivation": "These findings can inspire stronger interventions next term.",
        "action": "We will extend the survey to additional campuses next quarter.",
        "followup": "I'll circulate the full appendix once formatting is complete.",
        "gratitude": "Thank you to every participant who shared their time.",
        "clarity": "Do you need any definitions clarified before we publish?",
    },
    {
        "stem": "[English in Use • classroom management] Select phrases that maintain respect while guiding learners.",
        "difficulty": "B1",
        "base_b": -0.6,
        "a": 1.05,
        "formal": "Let's agree on a signal when you need clarification.",
        "support": "I appreciate how you're sharing ideas with the group.",
        "casual": "Thanks team, let's refocus for a minute.",
        "motivation": "Your questions show real curiosity—keep them coming.",
        "action": "We'll rotate discussion leaders every ten minutes.",
        "followup": "I'll check in after class to hear your suggestions.",
        "gratitude": "Thank you for bringing your full attention right now.",
        "clarity": "Is everyone clear on the next activity instructions?",
    },
    {
        "stem": "[English in Use • pitch deck] Choose expressions that highlight results for investors.",
        "difficulty": "C1",
        "base_b": 0.9,
        "a": 1.3,
        "formal": "Our platform reduced onboarding time by 37 percent this quarter.",
        "support": "Our advisory council remains engaged to guide expansion.",
        "casual": "We couldn't be more proud of this momentum!",
        "motivation": "Your backing can accelerate access for thousands of learners.",
        "action": "We will enter three additional markets over the next twelve months.",
        "followup": "I'll share due diligence documents immediately after this meeting.",
        "gratitude": "Thank you for considering partnership with our team.",
        "clarity": "What further metrics would you like to see before the next round?",
    },
    {
        "stem": "[English in Use • community outreach] Select wording that warmly invites volunteers.",
        "difficulty": "A2",
        "base_b": -0.7,
        "a": 1.0,
        "formal": "We would love your help welcoming new families this Saturday.",
        "support": "Our coordinators will be onsite to guide every role.",
        "casual": "Bring your friends—it's a cheerful morning together!",
        "motivation": "Your energy creates such a welcoming atmosphere.",
        "action": "We'll set up stations starting at 9 a.m. sharp.",
        "followup": "I'll confirm your assigned shift by Thursday afternoon.",
        "gratitude": "Thank you for giving your time to the community.",
        "clarity": "Do you prefer greeting guests or helping with setup?",
    },
    {
        "stem": "[English in Use • feedback request] Pick sentences that invite thoughtful input.",
        "difficulty": "B2",
        "base_b": 0.2,
        "a": 1.15,
        "formal": "I'd value any specific examples you can share about the prototype.",
        "support": "Your insights will shape how we iterate next sprint.",
        "casual": "Tell us what surprised you most!",
        "motivation": "Your perspective helps the team keep improving.",
        "action": "We'll gather comments into the backlog on Wednesday.",
        "followup": "I'll reach out if we need deeper context on any note.",
        "gratitude": "Thank you in advance for taking the time to respond.",
        "clarity": "Is there a specific area you'd like us to focus on further?",
    },
    {
        "stem": "[English in Use • design critique] Choose language that balances appreciation with next steps.",
        "difficulty": "B2",
        "base_b": 0.1,
        "a": 1.15,
        "formal": "I appreciate how the layout reflects the brand voice.",
        "support": "I'm happy to pair on color adjustments this afternoon.",
        "casual": "The animation really pops!",
        "motivation": "Your concept has strong potential for the launch demo.",
        "action": "We'll test increased contrast for accessibility in the next build.",
        "followup": "I'll compile user quotes and send them by end of day.",
        "gratitude": "Thanks for sharing the prototype with us early.",
        "clarity": "Would you like feedback on interaction flow or visuals first?",
    },
    {
        "stem": "[English in Use • study group] Select cooperative phrases for organizing shared tasks.",
        "difficulty": "A2",
        "base_b": -0.8,
        "a": 0.95,
        "formal": "Shall we divide the research into three sections?",
        "support": "I'm happy to review your notes before we meet again.",
        "casual": "Let's team up and make this painless!",
        "motivation": "We learn faster when we tackle it together.",
        "action": "We'll meet Tuesday evening to compile the summary.",
        "followup": "I'll message the group chat with reminders tomorrow.",
        "gratitude": "Thanks for contributing your insights every week.",
        "clarity": "Which section would you like to take the lead on?",
    },
    {
        "stem": "[English in Use • health consultation] Choose expressions that show empathy and direction.",
        "difficulty": "B1",
        "base_b": -0.3,
        "a": 1.05,
        "formal": "Thank you for describing your symptoms so clearly.",
        "support": "We'll navigate the next steps together.",
        "casual": "We're in this as a team, okay?",
        "motivation": "Following this plan can help you regain energy soon.",
        "action": "We'll start the treatment with a short course of medication.",
        "followup": "I'll call in two days to see how you're feeling.",
        "gratitude": "I appreciate your openness during today's visit.",
        "clarity": "Do you have any questions about the care plan we outlined?",
    },
    {
        "stem": "[English in Use • travel advisory] Select calm language for managing a sudden gate change.",
        "difficulty": "B1",
        "base_b": -0.2,
        "a": 1.05,
        "formal": "Please proceed to Gate 12 for the updated departure.",
        "support": "Our team is available nearby if you need assistance.",
        "casual": "Thanks for rolling with the change!",
        "motivation": "We'll do everything we can to keep you on schedule.",
        "action": "We'll begin boarding fifteen minutes earlier to stay on track.",
        "followup": "I'll announce again once seating groups are ready.",
        "gratitude": "Thank you for your patience this afternoon.",
        "clarity": "Is there anything we can clarify about the new boarding process?",
    },
    {
        "stem": "[English in Use • event planning] Pick expressions that coordinate a community festival team.",
        "difficulty": "B1",
        "base_b": -0.3,
        "a": 1.05,
        "formal": "We appreciate each crew confirming their arrival time.",
        "support": "Volunteer leads are on-site to help with setup.",
        "casual": "Let's make this our most vibrant festival yet!",
        "motivation": "Your creativity will set the tone for visitors.",
        "action": "We'll stage the booths starting at 7 a.m.",
        "followup": "I'll share a wrap-up email with photos on Monday.",
        "gratitude": "Thank you for bringing your talents to the neighborhood.",
        "clarity": "Do you need any supplies added to the checklist?",
    },
    {
        "stem": "[English in Use • scholarship announcement] Choose statements that celebrate recipients professionally.",
        "difficulty": "B1",
        "base_b": -0.4,
        "a": 1.05,
        "formal": "We are thrilled to congratulate this year's scholarship recipients.",
        "support": "Our advising office will assist you with travel arrangements.",
        "casual": "We can't wait to see what you achieve next!",
        "motivation": "Your dedication sets an inspiring example for peers.",
        "action": "We'll host an orientation session for awardees next week.",
        "followup": "I'll email details about reimbursement forms this afternoon.",
        "gratitude": "Thank you to everyone who supported the selection process.",
        "clarity": "Do you have questions about the timeline for disbursement?",
    },
    {
        "stem": "[English in Use • volunteer coordination] Select language that keeps volunteers informed and appreciated.",
        "difficulty": "A2",
        "base_b": -0.6,
        "a": 0.95,
        "formal": "Thank you for signing up to mentor on Saturday.",
        "support": "Team leads will greet you at the registration table.",
        "casual": "We're so happy you'll be on the crew!",
        "motivation": "Your support makes each session welcoming.",
        "action": "We'll walk through the orientation at 8:30 sharp.",
        "followup": "I'll text reminders with parking details on Friday.",
        "gratitude": "Thanks again for giving your time and energy.",
        "clarity": "Is there anything you need us to prepare before you arrive?",
    },
    {
        "stem": "[English in Use • daily stand-up] Choose concise statements for a morning sync.",
        "difficulty": "B1",
        "base_b": -0.2,
        "a": 1.05,
        "formal": "Yesterday I finalized the speaking task scripts.",
        "support": "I'm available to help anyone testing the audio player.",
        "casual": "Quick heads-up from me today!",
        "motivation": "Let's keep the momentum we built earlier in the week.",
        "action": "Today I'll pair with Marta on the reporting endpoint.",
        "followup": "I'll ping the channel once deployment finishes.",
        "gratitude": "Thanks for covering the backlog while I was out.",
        "clarity": "Anything blocking the translation upload I can help unblock?",
    },
    {
        "stem": "[English in Use • marketing brainstorm] Select wording that sparks creative collaboration.",
        "difficulty": "B2",
        "base_b": 0.3,
        "a": 1.15,
        "formal": "I appreciate the fresh campaign concepts everyone brought.",
        "support": "Our design partner is ready to mock up whichever idea we choose.",
        "casual": "Let's dream big for this launch!",
        "motivation": "Your insights can set us apart in a crowded space.",
        "action": "We'll shortlist three storylines before the hour ends.",
        "followup": "I'll gather references and share them by tomorrow.",
        "gratitude": "Thanks for contributing so openly today.",
        "clarity": "Which audience persona should we prioritize exploring first?",
    },
    {
        "stem": "[English in Use • performance review] Choose language that is honest and encouraging.",
        "difficulty": "C1",
        "base_b": 0.5,
        "a": 1.2,
        "formal": "Your strategic planning strengthened the entire program.",
        "support": "I'm here to back the leadership stretch goals you proposed.",
        "casual": "We're proud of how far you've taken the role!",
        "motivation": "Your curiosity sets a strong example for the team.",
        "action": "We'll focus next quarter on mentoring the new cohort.",
        "followup": "I'll schedule monthly check-ins to support the transition.",
        "gratitude": "Thank you for your dedication and openness this year.",
        "clarity": "Is there training you would like prioritized for you or your team?",
    },
    {
        "stem": "[English in Use • coaching email] Select expressions that nudge a coachee toward action.",
        "difficulty": "B1",
        "base_b": -0.3,
        "a": 1.05,
        "formal": "I appreciate the reflections you shared after our session.",
        "support": "I'm cheering for you as you experiment with the new strategy.",
        "casual": "You've got this—I'll be cheering from the sidelines!",
        "motivation": "Your progress shows you're building sustainable habits.",
        "action": "We'll try the new routine three times before we meet again.",
        "followup": "I'll send a reminder next Wednesday to see how it's going.",
        "gratitude": "Thank you for your openness to feedback.",
        "clarity": "Is there any part of the plan you'd like to adjust before next week?",
    },
    {
        "stem": "[English in Use • partnership outreach] Choose language for a warm collaboration proposal.",
        "difficulty": "B2",
        "base_b": 0.2,
        "a": 1.15,
        "formal": "We're impressed by the mentoring initiatives your team leads.",
        "support": "Our specialists can co-host sessions to support your coaches.",
        "casual": "It would be fantastic to create something together!",
        "motivation": "A partnership could expand impact for both communities.",
        "action": "We'll draft a pilot outline for your review next week.",
        "followup": "I'll follow up Friday with available meeting times.",
        "gratitude": "Thank you for considering a collaboration with us.",
        "clarity": "Are there particular goals you want to make sure we include?",
    },
    {
        "stem": "[English in Use • research collaboration] Select phrases that set up a joint study respectfully.",
        "difficulty": "C1",
        "base_b": 0.4,
        "a": 1.2,
        "formal": "We're grateful for your interest in co-authoring this study.",
        "support": "Our data team can share instruments to streamline setup.",
        "casual": "Excited to learn from your expertise!",
        "motivation": "Together we can highlight best practices for adaptive testing.",
        "action": "We'll align on research questions during next week's call.",
        "followup": "I'll send a draft protocol for comments by Monday.",
        "gratitude": "Thank you for contributing your time to the project.",
        "clarity": "Do you have preferences for the participant sample we recruit?",
    },
    {
        "stem": "[English in Use • customer success newsletter] Choose wording that celebrates milestones and guides readers.",
        "difficulty": "B1",
        "base_b": -0.1,
        "a": 1.05,
        "formal": "We're thrilled to share the latest learning milestones from our community.",
        "support": "Our coaches remain available for personalized check-ins.",
        "casual": "We love seeing your wins roll in!",
        "motivation": "Your dedication keeps inspiring new learners.",
        "action": "We'll launch the conversational skills track next Tuesday.",
        "followup": "I'll send a reminder when registration opens tomorrow.",
        "gratitude": "Thank you for growing with us each month.",
        "clarity": "Which topics would you like featured in the next edition?",
    },
    {
        "stem": "[English in Use • community survey follow-up] Choose language that closes the feedback loop.",
        "difficulty": "A2",
        "base_b": -0.5,
        "a": 0.95,
        "formal": "Thank you for completing our recent community survey.",
        "support": "We're already planning improvements based on your ideas.",
        "casual": "We appreciate you taking a few minutes for us!",
        "motivation": "Your suggestions will shape next season's programs.",
        "action": "We'll introduce extended hours beginning in May.",
        "followup": "I'll update you once the new schedules are finalized.",
        "gratitude": "Thanks again for sharing such thoughtful responses.",
        "clarity": "Is there anything else you'd like us to explore further?",
    },
    {
        "stem": "[English in Use • teacher-parent update] Select phrases that keep families informed and supported.",
        "difficulty": "A2",
        "base_b": -0.6,
        "a": 0.95,
        "formal": "Thank you for encouraging nightly reading at home.",
        "support": "I'm here to collaborate on any strategies you need.",
        "casual": "We love hearing about family story time!",
        "motivation": "Your involvement makes a huge difference in progress.",
        "action": "We'll send home new leveled books each Monday.",
        "followup": "I'll check in during conferences to share updated goals.",
        "gratitude": "Thanks for being such active partners in learning.",
        "clarity": "Are there skills you'd like us to practice more at school?",
    },
    {
        "stem": "[English in Use • internship introduction] Choose language that welcomes interns professionally.",
        "difficulty": "B1",
        "base_b": -0.4,
        "a": 1.05,
        "formal": "Welcome to the adaptive learning internship cohort.",
        "support": "Your mentors are ready to guide you through the first sprint.",
        "casual": "We're excited to work alongside you!",
        "motivation": "Your curiosity will fuel meaningful contributions.",
        "action": "We'll kick off with orientation at 9 a.m. Monday.",
        "followup": "I'll send your project briefs later today.",
        "gratitude": "Thank you for choosing to build with our team.",
        "clarity": "Do you have any questions before the onboarding session?",
    },
]

USAGE_SCENARIOS: List[UsageScenario] = [
    UsageScenario(
        stem_template=data["stem"],
        options=[
            UsageOption(str(data["formal"]), "formal"),
            UsageOption(str(data["support"]), "support"),
            UsageOption(str(data["casual"]), "casual"),
            UsageOption(str(data["motivation"]), "motivation"),
            UsageOption(str(data["action"]), "action"),
            UsageOption(str(data["followup"]), "followup"),
            UsageOption(str(data["gratitude"]), "gratitude"),
            UsageOption(str(data["clarity"]), "clarity"),
        ],
        base_b=float(data["base_b"]),
        a=float(data["a"]),
        difficulty=str(data["difficulty"]),
    )
    for data in USAGE_SCENARIO_DATA
]


def _usage_correct_indices(options: List[UsageOption], categories: Sequence[str]) -> Tuple[int, ...]:
    indices: List[int] = []
    for category in categories:
        for index, option in enumerate(options):
            if option.category == category:
                indices.append(index)
                break
        else:  # pragma: no cover - ensures data integrity during development
            raise ValueError(f"Missing category {category} in options")
    return tuple(indices)


def build_usage_items() -> List[Item]:
    items: List[Item] = []
    task_count = len(USAGE_TASKS)
    for scenario_index, scenario in enumerate(USAGE_SCENARIOS):
        for variant, task in enumerate(USAGE_TASKS):
            categories = task["categories"]
            correct_indices = _usage_correct_indices(scenario.options, categories)
            options = [option.text for option in scenario.options]
            item_id = f"english_use_{scenario_index * task_count + variant + 1:03d}"
            metadata = {
                "context": scenario.stem_template,
                "focus": task["focus"],
                "difficulty": scenario.difficulty,
            }
            step_difficulties = [round(scenario.base_b + 0.35 * step, 2) for step in range(len(correct_indices))]
            items.append(
                Item(
                    id=item_id,
                    domain="english_in_use",
                    stem=scenario.stem_template,
                    options=options,
                    correct_key=correct_indices,
                    model="gpcm",
                    irt_a=round(scenario.a + 0.05 * variant, 2),
                    irt_b=scenario.base_b,
                    step_difficulties=step_difficulties,
                    metadata=metadata,
                )
            )
    return items


# --- Aggregate ---------------------------------------------------------------------------------


def build_items() -> List[Item]:
    vocabulary = build_vocabulary_items()
    grammar = build_grammar_items()
    listening = build_listening_items()
    usage = build_usage_items()
    return vocabulary + grammar + listening + usage


ITEMS: List[Item] = []


def _initialize() -> None:
    global ITEMS
    if ITEMS:
        return
    ITEMS = build_items()


_initialize()

